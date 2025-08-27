import asyncio
import json
import re
import gzip
import brotli
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote
import aiohttp
import platform


JSON_TYPE_REGEX = re.compile(r'^(?:application/json|application/(?:[a-z0-9.+-]*\+json))\b', re.IGNORECASE)
BASE64_STANDARD_REGEX = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
BASE64_URL_REGEX = re.compile(r'^[A-Za-z0-9_-]*={0,2}$')

MAX_RESPONSE_SIZE = 10 * 1024 * 1024
API_VERSION = 'v4'
BUFFER_POOL_SIZE = 16
INITIAL_BUFFER_SIZE = 8192

EMPTY_STRING = ''
UTF8_ENCODING = 'utf-8'
JSON_CONTENT_TYPE = 'application/json'


class MagmaError(Exception):
    """Base exception for Magma errors."""
    pass


class NoSessionError(MagmaError):
    """Raised when session ID is required but not provided."""
    def __init__(self):
        super().__init__('Session ID required')


class InvalidTrackError(MagmaError):
    """Raised when track format is invalid."""
    def __init__(self):
        super().__init__('Invalid encoded track format')


class InvalidTracksError(MagmaError):
    """Raised when one or more tracks have invalid format."""
    def __init__(self):
        super().__init__('One or more tracks have invalid format')


class ResponseTooLargeError(MagmaError):
    """Raised when response is too large."""
    def __init__(self):
        super().__init__('Response too large')


class ResponseAbortedError(MagmaError):
    """Raised when response is aborted."""
    def __init__(self):
        super().__init__('Response aborted')


def is_valid_base64(s: str) -> bool:
    """Check if a string is valid base64."""
    if not isinstance(s, str) or len(s) == 0:
        return False

    length = len(s)
    has_url_chars = s.startswith(('-', '_')) or '-' in s or '_' in s

    if has_url_chars:
        return length % 4 != 1 and BASE64_URL_REGEX.match(s) is not None
    else:
        return length % 4 == 0 and BASE64_STANDARD_REGEX.match(s) is not None


def fast_bool(b: Any) -> bool:
    """Fast boolean conversion."""
    return bool(b)


class BufferPool:
    """Simple buffer pool for memory management."""
    
    def __init__(self, size: int = BUFFER_POOL_SIZE):
        self.pool: List[bytearray] = []
        self.max_size = size
    
    def get(self, size: int = INITIAL_BUFFER_SIZE) -> bytearray:
        """Get a buffer from the pool or create a new one."""
        if self.pool:
            return self.pool.pop()
        return bytearray(size)
    
    def release(self, buffer: bytearray) -> None:
        """Release a buffer back to the pool."""
        if len(self.pool) < self.max_size and len(buffer) <= 65536:
            self.pool.append(buffer)


class Rest:
    """REST client for Lavalink API."""
    
    def __init__(self, Magma, node):
        self.Magma = Magma
        self.node = node
        self.session_id = node.session_id
        self.timeout = getattr(node, 'timeout', 15.0)
        
        protocol = 'https' if getattr(node, 'secure', False) else 'http'
        host = node.host
        if ':' in host and not host.startswith('['):
            host = f'[{host}]'
        self.base_url = f'{protocol}://{host}:{node.port}'
        self._api_base = f'/{API_VERSION}'
        
        self._session_path = (
            f'{self._api_base}/sessions/{self.session_id}' 
            if self.session_id else None
        )
        
        self._endpoints = {
            'loadtracks': f'{self._api_base}/loadtracks?identifier=',
            'decodetrack': f'{self._api_base}/decodetrack?encodedTrack=',
            'decodetracks': f'{self._api_base}/decodetracks',
            'stats': f'{self._api_base}/stats',
            'info': f'{self._api_base}/info',
            'version': f'{self._api_base}/version',
            'routeplanner': {
                'status': f'{self._api_base}/routeplanner/status',
                'free_address': f'{self._api_base}/routeplanner/free/address',
                'free_all': f'{self._api_base}/routeplanner/free/all'
            },
            'lyrics': f'{self._api_base}/lyrics'
        }
        
        self.default_headers = {
            'Authorization': str(getattr(node, 'password', EMPTY_STRING)),
            'Accept': 'application/json, */*;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': f'Magma-Lavalink/{API_VERSION} (Python {platform.python_version()})'
        }
        
        connector_kwargs = {
            'limit': getattr(node, 'max_sockets', 128),
            'limit_per_host': getattr(node, 'max_free_sockets', 64),
            'keepalive_timeout': getattr(node, 'free_socket_timeout', 15.0),
            'enable_cleanup_closed': True
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(**connector_kwargs)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.default_headers
        )
        
        self.buffer_pool = BufferPool()
        self._reusable_headers = {}
    
    def set_session_id(self, session_id: str) -> None:
        """Set the session ID."""
        self.session_id = session_id
        self._session_path = (
            f'{self._api_base}/sessions/{session_id}' 
            if session_id else None
        )
    
    def _get_session_path(self) -> str:
        """Get the session path, raising error if no session."""
        if not self._session_path:
            if not self.session_id:
                raise NoSessionError()
            self._session_path = f'{self._api_base}/sessions/{self.session_id}'
        return self._session_path
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        body: Optional[Union[str, Dict, List]] = None
    ) -> Any:
        """Make an HTTP request to the Lavalink API."""
        url = f'{self.base_url}{endpoint}'
        headers = dict(self.default_headers)
        
        if body is not None:
            if isinstance(body, str):
                data = body
            else:
                data = json.dumps(body)
            headers['Content-Type'] = JSON_CONTENT_TYPE
            headers['Content-Length'] = str(len(data.encode(UTF8_ENCODING)))
        else:
            data = None
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                data=data,
                headers=headers
            ) as response:
                
                if response.status == 204:
                    return None
                
                content_length = response.headers.get('content-length')
                if content_length == '0':
                    return None
                
                if content_length:
                    size = int(content_length)
                    if size > MAX_RESPONSE_SIZE:
                        raise ResponseTooLargeError()
                
                content = await response.read()
                
                if len(content) > MAX_RESPONSE_SIZE:
                    raise ResponseTooLargeError()
                
                if len(content) == 0:
                    return None
                
                encoding = response.headers.get('content-encoding', '').split(',')[0].strip()
                if encoding == 'br':
                    content = brotli.decompress(content)
                elif encoding in ('gzip', 'deflate'):
                    content = gzip.decompress(content)
                
                text = content.decode(UTF8_ENCODING)
                result = text
                
                content_type = response.headers.get('content-type', EMPTY_STRING)
                if JSON_TYPE_REGEX.match(content_type):
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError as e:
                        raise ValueError(f'JSON parse error: {e}')
                
                if response.status >= 400:
                    error = aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=response.reason,
                        headers=response.headers
                    )
                    error.body = result
                    error.url = url
                    raise error
                
                return result
                
        except asyncio.TimeoutError:
            raise TimeoutError(f'Request timeout: {self.timeout}s')
        except aiohttp.ClientError as e:
            if 'aborted' in str(e).lower():
                raise ResponseAbortedError()
            raise
    
    async def update_player(
        self, 
        guild_id: str, 
        data: Dict, 
        no_replace: bool = False
    ) -> Any:
        """Update a player."""
        base = self._get_session_path()
        query = '?noReplace=true' if no_replace else '?noReplace=false'
        return await self.make_request('PATCH', f'{base}/players/{guild_id}{query}', data)
    
    async def get_player(self, guild_id: str) -> Any:
        """Get a player."""
        return await self.make_request('GET', f'{self._get_session_path()}/players/{guild_id}')
    
    async def get_players(self) -> Any:
        """Get all players."""
        return await self.make_request('GET', f'{self._get_session_path()}/players')
    
    async def destroy_player(self, guild_id: str) -> Any:
        """Destroy a player."""
        return await self.make_request('DELETE', f'{self._get_session_path()}/players/{guild_id}')
    
    async def load_tracks(self, identifier: str) -> Any:
        """Load tracks by identifier."""
        return await self.make_request('GET', f'{self._endpoints["loadtracks"]}{quote(identifier)}')
    
    async def decode_track(self, encoded_track: str) -> Any:
        """Decode a single track."""
        if not is_valid_base64(encoded_track):
            raise InvalidTrackError()
        return await self.make_request('GET', f'{self._endpoints["decodetrack"]}{quote(encoded_track)}')
    
    async def decode_tracks(self, encoded_tracks: List[str]) -> Any:
        """Decode multiple tracks."""
        if not isinstance(encoded_tracks, list) or len(encoded_tracks) == 0:
            raise InvalidTracksError()
        
        for track in encoded_tracks:
            if not is_valid_base64(track):
                raise InvalidTracksError()
        
        return await self.make_request('POST', self._endpoints['decodetracks'], encoded_tracks)
    
    async def get_stats(self) -> Any:
        """Get server stats."""
        return await self.make_request('GET', self._endpoints['stats'])
    
    async def get_info(self) -> Any:
        """Get server info."""
        return await self.make_request('GET', self._endpoints['info'])
    
    async def get_version(self) -> Any:
        """Get server version."""
        return await self.make_request('GET', self._endpoints['version'])
    
    async def get_route_planner_status(self) -> Any:
        """Get route planner status."""
        return await self.make_request('GET', self._endpoints['routeplanner']['status'])
    
    async def free_route_planner_address(self, address: str) -> Any:
        """Free a route planner address."""
        return await self.make_request('POST', self._endpoints['routeplanner']['free_address'], {'address': address})
    
    async def free_all_route_planner_addresses(self) -> Any:
        """Free all route planner addresses."""
        return await self.make_request('POST', self._endpoints['routeplanner']['free_all'])
    
    async def get_lyrics(
        self, 
        track: Dict, 
        skip_track_source: bool = False
    ) -> Optional[Any]:
        """Get lyrics for a track."""
        gid = track.get('guild_id') or track.get('guildId')
        encoded = track.get('encoded')
        has_encoded = (
            isinstance(encoded, str) and 
            len(encoded) > 0 and 
            is_valid_base64(encoded)
        )
        title = track.get('info', {}).get('title') if track.get('info') else None
        
        if not track or (not gid and not has_encoded and not title):
            if hasattr(self.Magma, 'emit'):
                self.Magma.emit('error', '[Magma/Lyrics] Invalid track object')
            return None
        
        skip_param = fast_bool(skip_track_source)
        
        if gid:
            try:
                lyrics = await self.make_request(
                    'GET',
                    f'{self._get_session_path()}/players/{gid}/track/lyrics?skipTrackSource={skip_param}'
                )
                if self._is_valid_lyrics(lyrics):
                    return lyrics
            except Exception:
                pass
        
        if has_encoded:
            try:
                lyrics = await self.make_request(
                    'GET',
                    f'{self._endpoints["lyrics"]}?track={quote(encoded)}&skipTrackSource={skip_param}'
                )
                if self._is_valid_lyrics(lyrics):
                    return lyrics
            except Exception:
                pass
        
        if title:
            author = track.get('info', {}).get('author') if track.get('info') else None
            query = f'{title} {author}' if author else title
            try:
                lyrics = await self.make_request(
                    'GET',
                    f'{self._endpoints["lyrics"]}/search?query={quote(query)}'
                )
                if self._is_valid_lyrics(lyrics):
                    return lyrics
            except Exception:
                pass
        
        return None
    
    def _is_valid_lyrics(self, response: Any) -> bool:
        """Check if lyrics response is valid."""
        if not response:
            return False
        
        if isinstance(response, str):
            return len(response) > 0
        elif isinstance(response, (list, dict)):
            if isinstance(response, list):
                return len(response) > 0
            else:
                return len(response.keys()) > 0
        
        return False
    
    async def subscribe_live_lyrics(
        self, 
        guild_id: str, 
        skip_track_source: bool = False
    ) -> bool:
        """Subscribe to live lyrics."""
        try:
            result = await self.make_request(
                'POST',
                f'{self._get_session_path()}/players/{guild_id}/lyrics/subscribe?skipTrackSource={fast_bool(skip_track_source)}'
            )
            return result is None
        except Exception:
            return False
    
    async def unsubscribe_live_lyrics(self, guild_id: str) -> bool:
        """Unsubscribe from live lyrics."""
        try:
            result = await self.make_request(
                'DELETE',
                f'{self._get_session_path()}/players/{guild_id}/lyrics/subscribe'
            )
            return result is None
        except Exception:
            return False
    
    async def destroy(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'session') and self.session:
            await self.session.close()
            self.session = None
        
        if hasattr(self, 'buffer_pool') and self.buffer_pool:
            self.buffer_pool.pool.clear()
            self.buffer_pool = None
        
        self._reusable_headers = None