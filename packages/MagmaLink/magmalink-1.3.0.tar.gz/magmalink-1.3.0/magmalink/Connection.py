import asyncio
import re
import time

POOL_SIZE = 10
LISTENER_CHECK_INTERVAL = 5
UPDATE_TIMEOUT = 5

ENDPOINT_PATTERN = re.compile(r'^([a-z-]+)', re.IGNORECASE)

class STATE_FLAGS:
    CONNECTED = 1 << 0
    PAUSED = 1 << 1
    SELF_DEAF = 1 << 2
    SELF_MUTE = 1 << 3
    HAS_DEBUG_LISTENERS = 1 << 4
    HAS_MOVE_LISTENERS = 1 << 5
    UPDATE_SCHEDULED = 1 << 6

class UpdatePayloadPool:
    def __init__(self):
        self.pool = [self._create_payload() for _ in range(POOL_SIZE)]
        self.size = POOL_SIZE

    def _create_payload(self):
        return {
            'guildId': None,
            'data': {
                'voice': {
                    'token': None,
                    'endpoint': None,
                    'sessionId': None,
                    'resume': None,
                    'sequence': None
                },
                'volume': None
            }
        }

    def acquire(self):
        if self.size > 0:
            self.size -= 1
            return self.pool[self.size]
        return self._create_payload()

    def release(self, payload):
        if not payload or self.size >= POOL_SIZE:
            return

        payload['guildId'] = None
        voice = payload['data']['voice']
        voice['token'] = None
        voice['endpoint'] = None
        voice['sessionId'] = None
        voice['resume'] = None
        voice['sequence'] = None
        payload['data']['volume'] = None

        self.pool[self.size] = payload
        self.size += 1

shared_payload_pool = UpdatePayloadPool()

class Connection:
    def __init__(self, player):
        if not getattr(player, 'Magma', None) or not player.Magma.client_id or not player.node:
            raise TypeError('Invalid player configuration')

        self._player = player
        self._Magma = player.Magma
        self._node = player.node
        self._guild_id = player.guild_id
        self._client_id = player.Magma.client_id

        self.voice_channel = player.voice_channel
        self.session_id = None
        self.endpoint = None
        self.token = None
        self.region = None
        self.sequence = 0
        self._last_endpoint = None
        self._pending_update = None

        self._state_flags = 0
        self._last_listener_check = 0

        self._payload_pool = shared_payload_pool

        self._check_listeners()

    def _check_listeners(self):
        now = time.time()
        if now - self._last_listener_check < LISTENER_CHECK_INTERVAL:
            return

        flags = self._state_flags
        flags = flags | STATE_FLAGS.HAS_DEBUG_LISTENERS if self._Magma.listeners('debug') else flags & ~STATE_FLAGS.HAS_DEBUG_LISTENERS
        flags = flags | STATE_FLAGS.HAS_MOVE_LISTENERS if self._Magma.listeners('playerMove') else flags & ~STATE_FLAGS.HAS_MOVE_LISTENERS

        self._state_flags = flags
        self._last_listener_check = now

    def _extract_region(self, endpoint):
        if not endpoint or not isinstance(endpoint, str):
            return None
        
        match = ENDPOINT_PATTERN.match(endpoint)
        return match.group(1) if match else None

    def set_server_update(self, data):
        if not data or not data.get('endpoint') or not data.get('token'):
            return

        trimmed_endpoint = data['endpoint'].strip()
        if self._last_endpoint == trimmed_endpoint and self.token == data['token']:
            return

        new_region = self._extract_region(trimmed_endpoint)
        has_region_change = self.region != new_region
        has_endpoint_change = self._last_endpoint != trimmed_endpoint

        if has_region_change or has_endpoint_change:
            if has_region_change and (self._state_flags & STATE_FLAGS.HAS_DEBUG_LISTENERS):
                self._Magma.emit('debug', f"[Player {self._guild_id}] Region: {self.region or 'none'} -> {new_region}")
            if has_endpoint_change:
                self.sequence = 0
                self._last_endpoint = trimmed_endpoint
            self.endpoint = trimmed_endpoint
            self.region = new_region

        self.token = data['token']
        if self._player.paused:
            self._player.paused = False
        
        self._schedule_voice_update()

    def resend_voice_update(self, resume=False):
        if not (self.session_id and self.endpoint and self.token):
            return False
        self._schedule_voice_update(resume)
        return True

    def set_state_update(self, data):
        if not data or data.get('user_id') != self._client_id:
            return

        session_id = data.get('session_id')
        channel_id = data.get('channel_id')
        self_deaf = data.get('self_deaf')
        self_mute = data.get('self_mute')

        if channel_id:
            needs_update = False
            if self.voice_channel != channel_id:
                if self._state_flags & STATE_FLAGS.HAS_MOVE_LISTENERS:
                    self._Magma.emit('playerMove', self.voice_channel, channel_id)
                self.voice_channel = channel_id
                self._player.voice_channel = channel_id
                needs_update = True
            
            if self.session_id != session_id:
                self.session_id = session_id
                needs_update = True

            self._player.self_deaf = bool(self_deaf)
            self._player.self_mute = bool(self_mute)
            self._player.connected = True

            if needs_update:
                self._schedule_voice_update()
        else:
            self._handle_disconnect()

    def _handle_disconnect(self):
        if not self._player or not self._player.connected:
            return

        if self._state_flags & STATE_FLAGS.HAS_DEBUG_LISTENERS:
            self._Magma.emit('debug', f"[Player {self._guild_id}] Disconnected")

        self._clear_pending_update()
        self.voice_channel = None
        self.session_id = None
        self.sequence = 0

        try:
            self._player.destroy()
        except Exception as error:
            self._Magma.emit('error', Exception(f"Player destroy failed: {error}"))

    async def attempt_resume(self):
        if not (self.session_id and self.endpoint and self.token):
            raise Exception('Missing required voice state')

        payload = self._payload_pool.acquire()
        try:
            payload['guildId'] = self._guild_id
            voice = payload['data']['voice']
            voice['token'] = self.token
            voice['endpoint'] = self.endpoint
            voice['sessionId'] = self.session_id
            voice['resume'] = True
            payload['data']['volume'] = self._player.volume
            if self.sequence >= 0:
                voice['sequence'] = self.sequence
            
            await self._send_update(payload)
            return True
        except Exception as error:
            if self._state_flags & STATE_FLAGS.HAS_DEBUG_LISTENERS:
                self._Magma.emit('debug', f"[Player {self._guild_id}] Resume update failed: {error}")
            return False
        finally:
            self._payload_pool.release(payload)

    def update_sequence(self, seq):
        if isinstance(seq, int) and seq >= 0:
            self.sequence = max(seq, self.sequence)

    def _clear_pending_update(self):
        self._state_flags &= ~STATE_FLAGS.UPDATE_SCHEDULED
        if self._pending_update and self._pending_update.get('payload'):
            self._payload_pool.release(self._pending_update['payload'])
        self._pending_update = None

    def _schedule_voice_update(self, is_resume=False):
        if not (self.session_id and self.endpoint and self.token):
            return
        if self._state_flags & STATE_FLAGS.UPDATE_SCHEDULED:
            return

        self._clear_pending_update()
        payload = self._payload_pool.acquire()
        payload['guildId'] = self._guild_id
        voice = payload['data']['voice']
        voice['token'] = self.token
        voice['endpoint'] = self.endpoint
        voice['sessionId'] = self.session_id
        payload['data']['volume'] = self._player.volume

        if is_resume:
            voice['resume'] = True
            voice['sequence'] = self.sequence

        self._pending_update = {
            'is_resume': is_resume,
            'payload': payload,
            'timestamp': time.time()
        }
        self._state_flags |= STATE_FLAGS.UPDATE_SCHEDULED
        asyncio.create_task(self._execute_voice_update())

    async def _execute_voice_update(self):
        self._state_flags &= ~STATE_FLAGS.UPDATE_SCHEDULED
        pending = self._pending_update
        if not pending:
            return

        if time.time() - pending['timestamp'] > UPDATE_TIMEOUT:
            self._payload_pool.release(pending['payload'])
            self._pending_update = None
            return

        payload = pending['payload']
        self._pending_update = None

        try:
            await self._send_update(payload)
        finally:
            self._payload_pool.release(payload)

    async def _send_update(self, payload):
        if not self._node or not self._node.rest:
            raise Exception('Node or REST interface not available')
        try:
            await self._node.rest.update_player(payload)
        except Exception as error:
            if self._state_flags & STATE_FLAGS.HAS_DEBUG_LISTENERS:
                self._Magma.emit('debug', f"[Player {self._guild_id}] Update failed: {error}")
            raise error

    def destroy(self):
        self._clear_pending_update()
        self._player = None
        self._Magma = None
        self._node = None
        self._payload_pool = None
        self.voice_channel = None
        self.session_id = None
        self.endpoint = None
        self.token = None
        self.region = None
        self._last_endpoint = None
        self._state_flags = 0
