import asyncio
import random
from pyee import EventEmitter
from .Connection import Connection
from .Queue import Queue
from .Filters import Filters
from .autoplay import sp_auto_play, sc_auto_play

class LOOP_MODES:
    NONE = 0
    TRACK = 1
    QUEUE = 2

LOOP_MODE_NAMES = ['none', 'track', 'queue']
EVENT_HANDLERS = {
    'TrackStartEvent': 'track_start',
    'TrackEndEvent': 'track_end',
    'TrackExceptionEvent': 'track_error',
    'TrackStuckEvent': 'track_stuck',
    'TrackChangeEvent': 'track_change',
    'WebSocketClosedEvent': 'socket_closed',
    'LyricsLineEvent': 'lyrics_line',
    'LyricsFoundEvent': 'lyrics_found',
    'LyricsNotFoundEvent': 'lyrics_not_found'
}

def _clamp(v):
    n = float(v)
    if 0 <= n <= 200:
        return n
    return 100 if n != n else 0 if n < 0 else 200

def _valid_vol(v):
    return isinstance(v, (int, float)) and 0 <= v <= 200

def _rand_idx(length):
    return random.randint(0, length - 1)

def _to_id(v):
    if not v:
        return None
    if isinstance(v, str):
        return v
    return getattr(v, 'id', None)

async def _safe_del(msg):
    if msg:
        try:
            await msg.delete()
        except Exception:
            pass

class MicrotaskUpdateBatcher:
    def __init__(self, player):
        self.player = player
        self.updates = None
        self.is_scheduled = False

    async def batch(self, data, immediate=False):
        if not self.player:
            raise Exception('Player is destroyed')
        if not self.updates:
            self.updates = {}
        self.updates.update(data)

        if immediate or 'track' in data or 'paused' in data or 'position' in data:
            self.is_scheduled = False
            return await self._flush()

        if not self.is_scheduled:
            self.is_scheduled = True
            asyncio.create_task(self._flush())

    async def _flush(self):
        if not self.updates or not self.player:
            self.updates = None
            self.is_scheduled = False
            return

        updates = self.updates
        self.updates = None
        self.is_scheduled = False

        try:
            await self.player.update_player(updates)
        except Exception as err:
            if self.player and self.player.Magma:
                self.player.Magma.emit('error', Exception(f"Update player error: {err}"))
            raise

    def destroy(self):
        self.updates = None
        self.is_scheduled = False
        self.player = None

class CircularBuffer:
    def __init__(self, size=50):
        self.buffer = [None] * size
        self.size = size
        self.index = 0
        self.count = 0

    def push(self, item):
        if not item:
            return
        self.buffer[self.index] = item
        self.index = (self.index + 1) % self.size
        if self.count < self.size:
            self.count += 1

    def get_last(self):
        if not self.count:
            return None
        return self.buffer[(self.index - 1 + self.size) % self.size]

    def clear(self):
        if self.count == 0:
            return
        self.buffer = [None] * self.size
        self.count = 0
        self.index = 0

    def to_array(self):
        if not self.count:
            return []
        start = self.index if self.count == self.size else 0
        return [self.buffer[(start + i) % self.size] for i in range(self.count) if self.buffer[(start + i) % self.size] is not None]

class Player(EventEmitter):
    LOOP_MODES = LOOP_MODES
    EVENT_HANDLERS = EVENT_HANDLERS

    def __init__(self, Magma, node, options={}):
        super().__init__()
        if not Magma or not node or not options.get('guildId'):
            raise TypeError('Missing required parameters')

        self.Magma = Magma
        self.node = node
        self.guild_id = options['guildId']
        self.text_channel = options.get('textChannel')
        self.voice_channel = options.get('voiceChannel')
        self.playing = False
        self.paused = False
        self.connected = False
        self.destroyed = False
        self.is_autoplay_enabled = False
        self.is_autoplay = False
        self.autoplay_seed = None
        self.current = None
        self.position = 0
        self.timestamp = 0
        self.ping = 0
        self.now_playing_message = None
        self.deaf = options.get('deaf', True)
        self.mute = bool(options.get('mute'))
        self.autoplay_retries = 0
        self.reconnection_retries = 0
        self._voice_down_since = 0
        self._voice_recovering = False

        vol = options.get('defaultVolume', 100)
        self.volume = vol if _valid_vol(vol) else _clamp(vol)
        self.loop = self._parse_loop(options.get('loop'))

        Magma_opts = Magma.options or {}
        self.should_delete_message = bool(Magma_opts.get('shouldDeleteMessage'))
        self.leave_on_end = bool(Magma_opts.get('leaveOnEnd'))

        self.connection = Connection(self)
        self.filters = Filters(self)
        self.queue = Queue()
        self.previous_identifiers = set()
        self.previous_tracks = CircularBuffer(50)
        self._update_batcher = MicrotaskUpdateBatcher(self)
        self._data_store = None

        self._bind_events()
        self._start_watchdog()

    def _parse_loop(self, loop):
        if isinstance(loop, str):
            try:
                idx = LOOP_MODE_NAMES.index(loop)
                return idx if 0 <= idx <= 2 else LOOP_MODES.NONE
            except ValueError:
                return LOOP_MODES.NONE
        return loop if isinstance(loop, int) and 0 <= loop <= 2 else LOOP_MODES.NONE

    def _bind_events(self):
        self.on('playerUpdate', self._handle_player_update)
        self.on('event', self._handle_event)
        self.Magma.on('playerMove', self._handle_Magma_player_move)

    def _start_watchdog(self):
        loop = asyncio.get_event_loop()
        self._voice_watchdog_timer = loop.call_later(15, self._voice_watchdog)

    def _handle_player_update(self, packet):
        if self.destroyed or not packet or 'state' not in packet:
            return
        
        state = packet['state']
        self.position = state.get('position', 0)
        self.connected = bool(state.get('connected'))
        self.ping = state.get('ping', 0)
        self.timestamp = state.get('time', asyncio.get_event_loop().time())

        if not self.connected and not self._voice_down_since:
            self._voice_down_since = asyncio.get_event_loop().time()
            asyncio.create_task(asyncio.sleep(1).then(lambda: not self.connected and not self.destroyed and self.connection.attempt_resume()))
        elif self.connected:
            self._voice_down_since = 0
        
        self.Magma.emit('playerUpdate', self, packet)

    async def _handle_event(self, payload):
        if self.destroyed or not payload or 'type' not in payload:
            return
        
        handler_name = EVENT_HANDLERS.get(payload['type'])
        if not handler_name:
            self.Magma.emit('nodeError', self, Exception(f"Unknown event: {payload['type']}"))
            return
        
        handler = getattr(self, handler_name, None)
        if callable(handler):
            try:
                await handler(self, self.current, payload)
            except Exception as error:
                self.Magma.emit('error', error)

    @property
    def previous(self):
        return self.previous_tracks.get_last() if self.previous_tracks else None

    @property
    def current_track(self):
        return self.current

    def get_queue(self):
        return self.queue

    async def batch_update_player(self, data, immediate=False):
        return await self._update_batcher.batch(data, immediate)

    def set_autoplay(self, enabled):
        self.is_autoplay_enabled = bool(enabled)
        self.autoplay_retries = 0
        return self

    async def play(self):
        if self.destroyed or not self.connected or not self.queue or not self.queue.size:
            return self
        
        item = self.queue.shift()
        if not item:
            return self
        
        try:
            self.current = item if item.track else await item.resolve(self.Magma)
            if not self.current or not self.current.track:
                raise Exception('Failed to resolve track')
            
            self.playing = True
            self.paused = False
            self.position = 0
            await self.batch_update_player({'track': {'encoded': self.current.track}}, immediate=True)
            return self
        except Exception as error:
            self.Magma.emit('error', error)
            return await self.play() if self.queue and self.queue.size else self

    def connect(self, options={}):
        if self.destroyed:
            raise Exception('Cannot connect destroyed player')

        voice_channel = _to_id(options.get('voiceChannel') or self.voice_channel)
        if not voice_channel:
            raise TypeError('Voice channel is required')

        self.deaf = options.get('deaf', True)
        self.mute = bool(options.get('mute'))
        self.connected = True
        self.destroyed = False
        self.voice_channel = voice_channel

        self.send({
            'guild_id': options.get('guildId') or self.guild_id,
            'channel_id': voice_channel,
            'self_deaf': self.deaf,
            'self_mute': self.mute
        })
        return self

    async def _voice_watchdog(self):
        if self.destroyed or not self.voice_channel or self.connected or not self._voice_down_since or \
                (asyncio.get_event_loop().time() * 1000 - self._voice_down_since) < 10000 or self._voice_recovering:
            return

        self._voice_recovering = True
        try:
            try:
                if await self.connection.attempt_resume():
                    self.Magma.emit('debug', f'[Player {self.guild_id}] Watchdog: resume sent')
                    return
            except Exception as e:
                self.Magma.emit('debug', f'[Player {self.guild_id}] Watchdog: resume failed: {e}')

            toggle_mute = not self.mute
            self.send({'guild_id': self.guild_id, 'channel_id': self.voice_channel, 'self_deaf': self.deaf, 'self_mute': toggle_mute})
            
            async def delayed_send():
                await asyncio.sleep(0.3)
                if not self.destroyed:
                    self.send({'guild_id': self.guild_id, 'channel_id': self.voice_channel, 'self_deaf': self.deaf, 'self_mute': self.mute})
            
            asyncio.create_task(delayed_send())

            self.connection.resend_voice_update({'resume': False})
            self.Magma.emit('debug', f'[Player {self.guild_id}] Watchdog: forced voice update/rejoin')
        except Exception as err:
            self.Magma.emit('debug', f'[Player {self.guild_id}] Watchdog recover failed: {err}')
        finally:
            self._voice_recovering = False

    def destroy(self, preserve_client=True, skip_remote=False):
        if self.destroyed:
            return self

        if self._voice_watchdog_timer:
            self._voice_watchdog_timer.cancel()
            self._voice_watchdog_timer = None

        self.destroyed = True
        self.connected = False
        self.playing = False
        self.paused = False
        self.emit('destroy')

        if self.should_delete_message and self.now_playing_message:
            asyncio.create_task(_safe_del(self.now_playing_message))
            self.now_playing_message = None

        self.remove_all_listeners()

        if self._update_batcher:
            self._update_batcher.destroy()
            self._update_batcher = None

        if not skip_remote:
            try:
                self.send({'guild_id': self.guild_id, 'channel_id': None})
                if self.Magma:
                    self.Magma.destroy_player(self.guild_id)
                if self.node and self.node.connected:
                    asyncio.create_task(self.node.rest.destroy_player(self.guild_id))
            except Exception as error:
                print(f"[Player {self.guild_id}] Destroy error: {error}")

        self.voice_channel = None
        self.is_autoplay = False
        self.autoplay_retries = 0
        self.reconnection_retries = 0
        self.clear_data()

        self.queue = self.connection = self.filters = self._data_store = None
        if not preserve_client:
            self.Magma = self.node = None
        return self

    def pause(self, paused):
        if self.destroyed:
            return self
        state = bool(paused)
        if self.paused == state:
            return self
        self.paused = state
        self.batch_update_player({'paused': state}, True)
        return self

    def seek(self, position):
        if self.destroyed or not self.playing or not isinstance(position, (int, float)):
            return self
        max_pos = self.current.info.get('length') if self.current and self.current.info else None
        new_position = max(0, self.position + position)
        self.position = min(new_position, max_pos) if max_pos is not None else new_position
        self.batch_update_player({'position': self.position}, True)
        return self

    def stop(self):
        if self.destroyed or not self.playing:
            return self
        self.playing = False
        self.paused = False
        self.position = 0
        self.batch_update_player({'track': {'encoded': None}}, True)
        return self

    def set_volume(self, volume):
        if self.destroyed:
            return self
        vol = _clamp(volume)
        if self.volume == vol:
            return self
        self.volume = vol
        self.batch_update_player({'volume': vol})
        return self

    def set_loop(self, mode):
        if self.destroyed:
            return self
        if isinstance(mode, str):
            try:
                mode_index = LOOP_MODE_NAMES.index(mode)
            except ValueError:
                raise ValueError('Invalid loop mode. Use: none, track, or queue')
        else:
            mode_index = mode
        
        if not (0 <= mode_index <= 2):
            raise ValueError('Invalid loop mode. Use: none, track, or queue')
        
        self.loop = mode_index
        self.batch_update_player({'loop': LOOP_MODE_NAMES[mode_index]})
        return self

    def set_text_channel(self, channel):
        if self.destroyed:
            return self
        channel_id = _to_id(channel)
        if not channel_id:
            raise TypeError('Invalid text channel')
        self.text_channel = channel_id
        self.batch_update_player({'text_channel': channel_id})
        return self

    def set_voice_channel(self, channel):
        if self.destroyed:
            return self
        target_id = _to_id(channel)
        if not target_id:
            raise TypeError('Voice channel is required')
        if self.connected and target_id == _to_id(self.voice_channel):
            return self
        self.voice_channel = target_id
        self.connect(deaf=self.deaf, guildId=self.guild_id, voiceChannel=target_id, mute=self.mute)
        return self

    def disconnect(self):
        if self.destroyed or not self.connected:
            return self
        self.connected = False
        self.voice_channel = None
        self.send({'guild_id': self.guild_id, 'channel_id': None})
        return self

    def shuffle(self):
        if self.destroyed or not self.queue or not self.queue.size:
            return self
        items = self.queue.to_array()
        if len(items) <= 1:
            return self
        
        random.shuffle(items)
        
        self.queue.clear()
        for item in items:
            self.queue.push(item)
        return self

    def replay(self):
        return self.seek(0)

    def skip(self):
        return self.stop()

    async def get_lyrics(self, options={}):
        if self.destroyed or not self.node or not self.node.rest:
            return None
        
        query = options.get('query')
        use_current_track = options.get('useCurrentTrack', True)
        skip_track_source = options.get('skipTrackSource', False)

        if query:
            return await self.node.rest.get_lyrics(track={'info': {'title': query}}, skip_track_source=skip_track_source)

        if use_current_track and self.playing and self.current:
            current_info = self.current.info
            return await self.node.rest.get_lyrics(
                track={'info': current_info, 'encoded': self.current.track, 'identifier': current_info.get('identifier'), 'guild_id': self.guild_id},
                skip_track_source=skip_track_source
            )
        return None

    async def subscribe_live_lyrics(self):
        if self.destroyed:
            raise Exception('Player is destroyed')
        if self.node and self.node.rest:
            return await self.node.rest.subscribe_live_lyrics(self.guild_id, False)

    async def unsubscribe_live_lyrics(self):
        if self.destroyed:
            raise Exception('Player is destroyed')
        if self.node and self.node.rest:
            return await self.node.rest.unsubscribe_live_lyrics(self.guild_id)

    async def autoplay(self):
        if self.destroyed or not self.is_autoplay_enabled or not self.previous or (self.queue and self.queue.size):
            return self

        prev = self.previous
        prev_info = prev.info if prev else None
        if not prev_info or not prev_info.get('sourceName') or not prev_info.get('identifier'):
            return self

        source_name = prev_info['sourceName']
        identifier = prev_info['identifier']
        uri = prev_info.get('uri')
        requester = prev_info.get('requester')
        author = prev_info.get('author')
        self.is_autoplay = True

        if source_name == 'spotify' and prev.identifier:
            self.previous_identifiers.add(prev.identifier)
            if len(self.previous_identifiers) > 20:
                self.previous_identifiers.pop(0)
            if not self.autoplay_seed:
                self.autoplay_seed = {'trackId': identifier, 'artistIds': ','.join(author) if isinstance(author, list) else author}

        for attempts in range(3):
            if self.destroyed or (self.queue and self.queue.size):
                break
            
            try:
                track = None
                if source_name == 'youtube':
                    response = await self.Magma.resolve(
                        query=f"https://www.youtube.com/watch?v={identifier}&list=RD{identifier}",
                        source='ytmsearch',
                        requester=requester
                    )
                    if not self._is_invalid_response(response) and response.get('tracks'):
                        track = random.choice(response['tracks'])
                elif source_name == 'soundcloud':
                    sc_results = await sc_auto_play(uri)
                    if sc_results:
                        response = await self.Magma.resolve(query=sc_results[0], source='scsearch', requester=requester)
                        if not self._is_invalid_response(response) and response.get('tracks'):
                            track = random.choice(response['tracks'])
                elif source_name == 'spotify':
                    resolved = await sp_auto_play(self.autoplay_seed, self, requester, list(self.previous_identifiers))
                    if resolved:
                        track = random.choice(resolved)
                else:
                    break

                if track and track.info and track.info.get('title'):
                    self.autoplay_retries = 0
                    track.requester = prev.requester or {'id': 'Unknown'}
                    self.queue.push(track)
                    await self.play()
                    return self
            except Exception as err:
                self.Magma.emit('error', Exception(f"Autoplay attempt {attempts + 1} failed: {err}"))

        self.Magma.emit('autoplayFailed', self, Exception('Max autoplay retries reached'))
        self.stop()
        return self

    def _is_invalid_response(self, response):
        return not response or not response.get('tracks') or response.get('loadType') in ['error', 'empty', 'LOAD_FAILED', 'NO_MATCHES']

    async def track_start(self, player, track):
        if self.destroyed:
            return
        self.playing = True
        self.paused = False
        self.Magma.emit('trackStart', self, track)

    async def track_end(self, player, track, payload):
        if self.destroyed:
            return
        if track and self.previous_tracks:
            self.previous_tracks.push(track)
        if self.should_delete_message:
            await _safe_del(self.now_playing_message)

        reason = payload.get('reason')
        is_failure = reason in ['loadFailed', 'cleanup']
        is_replaced = reason == 'replaced'

        if is_failure:
            if not self.queue or not self.queue.size:
                self.clear_data()
                self.Magma.emit('queueEnd', self)
            else:
                self.Magma.emit('trackEnd', self, track, reason)
                await self.play()
            return

        if track and not is_replaced:
            if self.loop == LOOP_MODES.TRACK:
                self.queue.unshift(track)
            elif self.loop == LOOP_MODES.QUEUE:
                self.queue.push(track)

        if self.queue and self.queue.size:
            self.Magma.emit('trackEnd', self, track, reason)
            await self.play()
        elif self.is_autoplay_enabled and not is_replaced:
            await self.autoplay()
        else:
            self.playing = False
            if self.leave_on_end and not self.destroyed:
                self.clear_data()
                self.destroy()
            self.Magma.emit('queueEnd', self)

    async def track_error(self, player, track, payload):
        if self.destroyed:
            return
        self.Magma.emit('trackError', self, track, payload)
        return self.stop()

    async def track_stuck(self, player, track, payload):
        if self.destroyed:
            return
        self.Magma.emit('trackStuck', self, track, payload)
        return self.stop()

    async def track_change(self, player, track, payload):
        if self.destroyed:
            return
        self.Magma.emit('trackChange', self, track, payload)

    async def _attempt_voice_resume(self):
        if not self.connection or not self.connection.session_id:
            raise Exception('Missing connection or sessionId')
        if not await self.connection.attempt_resume():
            raise Exception('Resume request failed')

        future = asyncio.get_event_loop().create_future()
        
        def on_update(payload):
            if payload.get('state', {}).get('connected') or isinstance(payload.get('state', {}).get('time'), (int, float)):
                if not future.done():
                    future.set_result(True)
                self.off('playerUpdate', on_update)

        self.on('playerUpdate', on_update)
        
        try:
            await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
            self.off('playerUpdate', on_update)
            raise Exception('No resume confirmation')

    async def socket_closed(self, player, track, payload):
        if self.destroyed:
            return
        code = payload.get('code')

        if code == 4022:
            self.Magma.emit('socketClosed', self, payload)
            self.destroy()
            return

        if code == 4015:
            self.Magma.emit('debug', f'[Player {self.guild_id}] Voice server crashed (4015), attempting resume...')
            try:
                await self._attempt_voice_resume()
                self.Magma.emit('debug', f'[Player {self.guild_id}] Voice resume succeeded')
                return
            except Exception as err:
                self.Magma.emit('debug', f'[Player {self.guild_id}] Resume failed: {err}. Falling back to reconnect')

        if code not in [4015, 4009, 4006]:
            self.Magma.emit('socketClosed', self, payload)
            return

        Magma_ref = self.Magma
        voice_channel_id = _to_id(self.voice_channel)
        if not voice_channel_id:
            if Magma_ref:
                Magma_ref.emit('socketClosed', self, payload)
            return

        saved_state = {
            'volume': self.volume, 'position': self.position, 'paused': self.paused, 'loop': self.loop,
            'is_autoplay_enabled': self.is_autoplay_enabled, 'current_track': self.current, 'queue': self.queue.to_array() if self.queue else [],
            'previous_identifiers': list(self.previous_identifiers), 'autoplay_seed': self.autoplay_seed
        }

        self.destroy(preserve_client=True, skip_remote=True)

        async def try_reconnect(attempt):
            try:
                new_player = await Magma_ref.create_connection({
                    'guildId': self.guild_id, 'voiceChannel': voice_channel_id, 'textChannel': _to_id(self.text_channel),
                    'deaf': self.deaf, 'mute': self.mute, 'defaultVolume': saved_state['volume']
                })

                if not new_player:
                    raise Exception('Failed to create new player during reconnection')

                new_player.reconnection_retries = 0
                new_player.loop = saved_state['loop']
                new_player.is_autoplay_enabled = saved_state['is_autoplay_enabled']
                new_player.autoplay_seed = saved_state['autoplay_seed']
                new_player.previous_identifiers = set(saved_state['previous_identifiers'])

                if saved_state['current_track']:
                    new_player.queue.unshift(saved_state['current_track'])
                for item in saved_state['queue']:
                    if item != saved_state['current_track']:
                        new_player.queue.push(item)

                if saved_state['current_track']:
                    await new_player.play()
                    if saved_state['position'] > 5000:
                        await asyncio.sleep(0.8)
                        if not new_player.destroyed:
                            new_player.seek(saved_state['position'])
                    if saved_state['paused']:
                        await asyncio.sleep(1.2)
                        if not new_player.destroyed:
                            new_player.pause(True)

                Magma_ref.emit('playerReconnected', new_player, {'oldPlayer': self, 'restoredState': saved_state})
            except Exception as error:
                retries_left = 3 - attempt
                Magma_ref.emit('reconnectionFailed', self, {'error': error, 'code': code, 'payload': payload, 'retriesLeft': retries_left})
                if retries_left > 0:
                    await asyncio.sleep(1.5)
                    await try_reconnect(attempt + 1)
                else:
                    Magma_ref.emit('socketClosed', self, payload)

        asyncio.create_task(try_reconnect(1))

    async def lyrics_line(self, player, track, payload):
        if not self.destroyed:
            self.Magma.emit('lyricsLine', self, track, payload)

    async def lyrics_found(self, player, track, payload):
        if not self.destroyed:
            self.Magma.emit('lyricsFound', self, track, payload)

    async def lyrics_not_found(self, player, track, payload):
        if not self.destroyed:
            self.Magma.emit('lyricsNotFound', self, track, payload)

    def _handle_Magma_player_move(self, old_channel, new_channel):
        try:
            if _to_id(old_channel) == _to_id(self.voice_channel):
                self.voice_channel = _to_id(new_channel)
                self.connected = bool(new_channel)
                self.send({
                    'guild_id': self.guild_id, 'channel_id': self.voice_channel,
                    'self_deaf': self.deaf, 'self_mute': self.mute
                })
        except Exception:
            pass

    def send(self, data):
        try:
            self.Magma.send({'op': 4, 'd': data})
        except Exception as error:
            self.Magma.emit('error', Exception(f"Failed to send data: {error}"))

    def set(self, key, value):
        if self.destroyed:
            return
        if not self._data_store:
            self._data_store = {}
        self._data_store[key] = value

    def get(self, key):
        return self._data_store.get(key) if not self.destroyed and self._data_store else None

    def clear_data(self):
        if self.previous_tracks:
            self.previous_tracks.clear()
        if self._data_store:
            self._data_store.clear()
        if self.previous_identifiers:
            self.previous_identifiers.clear()
        self.current = None
        self.position = 0
        self.timestamp = 0
        return self

    async def update_player(self, data):
        return await self.node.rest.update_player(guild_id=self.guild_id, data=data)

    async def cleanup(self):
        if not self.playing and not self.paused and (not self.queue or self.queue.is_empty()):
            self.destroy()
