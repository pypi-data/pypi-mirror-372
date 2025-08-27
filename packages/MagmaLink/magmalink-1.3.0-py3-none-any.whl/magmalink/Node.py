import asyncio
import json
import time
import random
from typing import Optional, Dict, Any, Union
from enum import IntEnum
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException


class WSStates(IntEnum):
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3


FATAL_CLOSE_CODES = {4003, 4004, 4010, 4011, 4012, 4015}
OPEN_BRACE = 123
LYRICS_PREFIX = 'Lyrics'
LYRICS_PREFIX_LEN = len(LYRICS_PREFIX)


class Node:
    BACKOFF_MULTIPLIER = 1.5
    MAX_BACKOFF = 60_000
    DEFAULT_RECONNECT_TIMEOUT = 2_000
    DEFAULT_RESUME_TIMEOUT = 60
    JITTER_MAX = 2_000
    JITTER_FACTOR = 0.2
    WS_CLOSE_NORMAL = 1000
    DEFAULT_MAX_PAYLOAD = 1_048_576
    DEFAULT_HANDSHAKE_TIMEOUT = 15_000

    def __init__(self, Magma, conn_options: Dict[str, Any], options: Dict[str, Any] = None):
        if options is None:
            options = {}
            
        self.Magma = Magma
        
        self.host = conn_options.get('host', 'localhost')
        self.name = conn_options.get('name', self.host)
        self.port = conn_options.get('port', 2333)
        self.password = conn_options.get('password', 'youshallnotpass')
        self.session_id = conn_options.get('sessionId')
        self.regions = conn_options.get('regions', [])
        self.secure = bool(conn_options.get('secure', False))
        
        self.ws_url = f"ws{'s' if self.secure else ''}://{self.host}:{self.port}/v4/websocket"
        
        self.rest = None
        
        self.resume_timeout = options.get('resumeTimeout', self.DEFAULT_RESUME_TIMEOUT)
        self.auto_resume = options.get('autoResume', False)
        self.reconnect_timeout = options.get('reconnectTimeout', self.DEFAULT_RECONNECT_TIMEOUT)
        self.reconnect_tries = options.get('reconnectTries', 3)
        self.infinite_reconnects = options.get('infiniteReconnects', False)
        self.timeout = options.get('timeout', self.DEFAULT_HANDSHAKE_TIMEOUT)
        self.max_payload = options.get('maxPayload', self.DEFAULT_MAX_PAYLOAD)
        self.skip_utf8_validation = options.get('skipUTF8Validation', True)
        
        self.connected = False
        self.info = None
        self.ws = None
        self.reconnect_attempted = 0
        self.reconnect_task = None
        self.is_destroyed = False
        self._is_connecting = False
        
        self.stats = {
            'players': 0,
            'playingPlayers': 0,
            'uptime': 0,
            'ping': 0,
            'memory': {'free': 0, 'used': 0, 'allocated': 0, 'reservable': 0},
            'cpu': {'cores': 0, 'systemLoad': 0, 'lavalinkLoad': 0},
            'frameStats': {'sent': 0, 'nulled': 0, 'deficit': 0}
        }
        
        self._client_name = f"Magma/{getattr(self.Magma, 'version', '1.0.0')} https://github.com/southctrl/MagmaLink"
        self._headers = self._build_headers()
        
        self._debug_enabled = False
        self._check_debug_status()

    def _reset_stats(self):
        s = self.stats
        s['players'] = 0
        s['playingPlayers'] = 0
        s['uptime'] = 0
        s['ping'] = 0
        
        m = s['memory']
        m['free'] = m['used'] = m['allocated'] = m['reservable'] = 0
        
        c = s['cpu']
        c['cores'] = c['systemLoad'] = c['lavalinkLoad'] = 0
        
        f = s['frameStats']
        f['sent'] = f['nulled'] = f['deficit'] = 0

    def _build_headers(self):
        headers = {
            'Authorization': self.password,
            'User-Id': str(getattr(self.Magma, 'client_id', '')),
            'Client-Name': self._client_name
        }
        if self.session_id:
            headers['Session-Id'] = self.session_id
        return headers

    async def _handle_open(self):
        self.connected = True
        self._is_connecting = False
        self.reconnect_attempted = 0
        self._emit_debug('WebSocket connection established')

        if not getattr(self.Magma, 'bypass_checks', {}).get('node_fetch_info', False) and not self.info:
            try:
                if self.rest:
                    self.info = await self.rest.make_request('GET', '/v4/info')
            except Exception as err:
                self.info = None
                self._emit_error(f"Failed to fetch node info: {str(err)}")

        await self.Magma.emit('nodeConnected', self)

    async def _handle_error(self, error):
        self._is_connecting = False
        err = error if isinstance(error, Exception) else Exception(str(error))
        await self.Magma.emit('nodeError', self, err)

    def _data_to_string_or_none(self, data):
        if isinstance(data, str):
            if len(data) == 0 or ord(data[0]) != OPEN_BRACE:
                return None
            return data
        
        if isinstance(data, bytes):
            if len(data) == 0 or data[0] != OPEN_BRACE:
                return None
            try:
                return data.decode('utf-8')
            except:
                return None
        
        return None

    def _try_parse_json(self, string):
        try:
            return {'ok': True, 'value': json.loads(string)}
        except Exception as err:
            return {'ok': False, 'err': err}

    async def _handle_message(self, data):
        string = self._data_to_string_or_none(data)
        if not string:
            self._emit_debug('Ignored non-JSON or invalid message frame')
            return

        parsed = self._try_parse_json(string)
        if not parsed['ok']:
            self._emit_debug(lambda: f"JSON parse failed: {getattr(parsed['err'], 'message', 'Unknown error')}")
            return

        payload = parsed['value']
        op = payload.get('op')
        if not op:
            return

        if op == 'stats':
            self._update_stats(payload)
        elif op == 'ready':
            await self._handle_ready(payload)
        elif op == 'playerUpdate':
            await self._handle_player_update(payload)
        elif op == 'event':
            await self._handle_player_event(payload)
        else:
            await self._handle_custom_string_op(op, payload)

    async def _handle_player_update(self, payload):
        guild_id = payload.get('guildId')
        if not guild_id:
            return
        player = self.Magma.players.get(guild_id)
        if player:
            await player.emit('playerUpdate', payload)

    async def _handle_player_event(self, payload):
        guild_id = payload.get('guildId')
        if not guild_id:
            return
        player = self.Magma.players.get(guild_id)
        if player:
            await player.emit('event', payload)

    async def _handle_custom_string_op(self, op, payload):
        if len(op) >= LYRICS_PREFIX_LEN and op.startswith(LYRICS_PREFIX):
            player = self.Magma.players.get(payload['guildId']) if payload.get('guildId') else None
            await self.Magma.emit(op, player, payload.get('track'), payload)
            return

        await self.Magma.emit('nodeCustomOp', self, op, payload)
        self._emit_debug(lambda: f"Unknown string op from Lavalink: {op}")

    async def _handle_close(self, code, reason=None):
        self.connected = False
        self._is_connecting = False

        reason_str = reason if isinstance(reason, str) else str(reason) if reason else 'No reason provided'
        await self.Magma.emit('nodeDisconnect', self, {'code': code, 'reason': reason_str})

        if self.is_destroyed:
            return

        if not self._should_reconnect(code):
            if code == 4011:
                self.session_id = None
                if 'Session-Id' in self._headers:
                    del self._headers['Session-Id']
            self._emit_error(Exception(f"WebSocket closed (code {code}). Not reconnecting."))
            await self.destroy(True)
            return

        if hasattr(self.Magma, 'handle_node_failover'):
            await self.Magma.handle_node_failover(self)
        await self._schedule_reconnect()

    def _should_reconnect(self, code):
        return code != self.WS_CLOSE_NORMAL and code not in FATAL_CLOSE_CODES

    async def _schedule_reconnect(self):
        self._clear_reconnect_timeout()

        if self.infinite_reconnects:
            self.reconnect_attempted += 1
            backoff_time = 10.0
            await self.Magma.emit('nodeReconnect', self, {'infinite': True, 'attempt': self.reconnect_attempted, 'backoffTime': backoff_time})
            self.reconnect_task = asyncio.create_task(self._delayed_connect(backoff_time))
            return

        if self.reconnect_attempted >= self.reconnect_tries:
            self._emit_error(Exception(f"Max reconnection attempts reached ({self.reconnect_tries})"))
            await self.destroy(True)
            return

        self.reconnect_attempted += 1
        backoff_time = self._calc_backoff(self.reconnect_attempted)

        await self.Magma.emit('nodeReconnect', self, {
            'infinite': False,
            'attempt': self.reconnect_attempted,
            'backoffTime': backoff_time
        })

        self.reconnect_task = asyncio.create_task(self._delayed_connect(backoff_time / 1000.0))

    async def _delayed_connect(self, delay):
        await asyncio.sleep(delay)
        await self.connect()

    def _calc_backoff(self, attempt):
        exp = min(attempt, 10)
        base_backoff = self.reconnect_timeout * (self.BACKOFF_MULTIPLIER ** exp)
        max_jitter = min(self.JITTER_MAX, base_backoff * self.JITTER_FACTOR)
        jitter = random.random() * max_jitter
        return min(base_backoff + jitter, self.MAX_BACKOFF)

    def _clear_reconnect_timeout(self):
        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()
        self.reconnect_task = None

    async def connect(self):
        if self.is_destroyed or self._is_connecting:
            return

        if self.ws and not self.ws.closed:
            self._emit_debug('WebSocket already connected')
            return

        self._is_connecting = True
        await self._cleanup()

        try:
            websocket_kwargs = {
                'max_size': self.max_payload,
                'timeout': self.timeout / 1000.0
            }
            
            try:
                websocket_kwargs['additional_headers'] = self._headers
                self.ws = await websockets.connect(self.ws_url, **websocket_kwargs)
            except TypeError:
                try:
                    del websocket_kwargs['additional_headers']
                    websocket_kwargs['extra_headers'] = self._headers
                    self.ws = await websockets.connect(self.ws_url, **websocket_kwargs)
                except TypeError:
                    del websocket_kwargs['extra_headers']
                    self.ws = await websockets.connect(self.ws_url, **websocket_kwargs)

            await self._handle_open()
            
            async for message in self.ws:
                await self._handle_message(message)

        except ConnectionClosed as e:
            await self._handle_close(e.code, e.reason)
        except Exception as err:
            self._is_connecting = False
            self._emit_error(f"Failed to create WebSocket: {str(err)}")
            await self._schedule_reconnect()

    async def _cleanup(self):
        if self.ws and not self.ws.closed:
            try:
                await self.ws.close(self.WS_CLOSE_NORMAL)
            except Exception as err:
                self._emit_error(f"Failed to cleanup WebSocket: {str(err)}")
        self.ws = None

    async def destroy(self, clean=False):
        if self.is_destroyed:
            return

        self.is_destroyed = True
        self._is_connecting = False
        self._clear_reconnect_timeout()
        await self._cleanup()

        if not clean and hasattr(self.Magma, 'handle_node_failover'):
            await self.Magma.handle_node_failover(self)

        self.connected = False
        if hasattr(self.Magma, 'destroy_node'):
            await self.Magma.destroy_node(self.name)
        await self.Magma.emit('nodeDestroy', self)

        self.info = None

    async def get_stats(self):
        if self.connected:
            return self.stats

        try:
            if self.rest:
                new_stats = await self.rest.get_stats()
                if new_stats:
                    self._update_stats(new_stats)
        except Exception as err:
            self._emit_error(f"Failed to fetch node stats: {str(err)}")
        return self.stats

    def _update_stats(self, payload):
        if not payload:
            return

        s = self.stats

        if 'players' in payload:
            s['players'] = payload['players']
        if 'playingPlayers' in payload:
            s['playingPlayers'] = payload['playingPlayers']
        if 'uptime' in payload:
            s['uptime'] = payload['uptime']
        if 'ping' in payload:
            s['ping'] = payload['ping']

        pm = payload.get('memory')
        if pm:
            m = s['memory']
            if 'free' in pm:
                m['free'] = pm['free']
            if 'used' in pm:
                m['used'] = pm['used']
            if 'allocated' in pm:
                m['allocated'] = pm['allocated']
            if 'reservable' in pm:
                m['reservable'] = pm['reservable']

        pc = payload.get('cpu')
        if pc:
            c = s['cpu']
            if 'cores' in pc:
                c['cores'] = pc['cores']
            if 'systemLoad' in pc:
                c['systemLoad'] = pc['systemLoad']
            if 'lavalinkLoad' in pc:
                c['lavalinkLoad'] = pc['lavalinkLoad']

        pf = payload.get('frameStats')
        if pf:
            f = s['frameStats']
            if 'sent' in pf:
                f['sent'] = pf['sent']
            if 'nulled' in pf:
                f['nulled'] = pf['nulled']
            if 'deficit' in pf:
                f['deficit'] = pf['deficit']

    async def _handle_ready(self, payload):
        session_id = payload.get('sessionId')
        if not session_id:
            self._emit_error('Ready payload missing sessionId')
            return

        self.session_id = session_id
        if self.rest:
            self.rest.set_session_id(session_id)
        self._headers['Session-Id'] = session_id

        await self.Magma.emit('nodeReady', self, {'resumed': bool(payload.get('resumed'))})
        await self.Magma.emit('nodeConnect', self)

        if self.auto_resume:
            try:
                await self._resume_players()
            except Exception as err:
                self._emit_error(f"_resume_players failed: {str(err)}")

    async def _resume_players(self):
        if not self.session_id:
            return

        try:
            if self.rest:
                await self.rest.make_request('PATCH', f'/v4/sessions/{self.session_id}', {
                    'resuming': True,
                    'timeout': self.resume_timeout
                })

            if hasattr(self.Magma, 'load_players'):
                await self.Magma.load_players()

            self._emit_debug('Session resumed successfully')
        except Exception as err:
            self._emit_error(f"Failed to resume session: {str(err)}")
            raise err

    def _check_debug_status(self):
        self._debug_enabled = getattr(self.Magma, 'listener_count', lambda x: 0)('debug') > 0

    def _should_debug(self):
        if self._debug_enabled:
            return True
        self._check_debug_status()
        return self._debug_enabled

    def _emit_error(self, error):
        error_obj = error if isinstance(error, Exception) else Exception(str(error))
        print(f"[Magma] [{self.name}] Error: {error_obj}")
        asyncio.create_task(self.Magma.emit('error', self, error_obj))

    def _emit_debug(self, message):
        if not self._should_debug():
            return
        out = message() if callable(message) else message
        asyncio.create_task(self.Magma.emit('debug', self.name, out))