import re
from typing import Any, Dict, Optional, Union


YT_ID_RE = re.compile(r'(?:[?&]v=|youtu\.be\/|\/embed\/|\/shorts\/)([A-Za-z0-9_-]{11})')


class Track:
    def __init__(self, data: Dict[str, Any] = None, requester: Any = None, node: Any = None):
        if data is None:
            data = {}
        
        info = data.get('info', {})
        
        self.track = data.get('track') or data.get('encoded')
        
        self.identifier = info.get('identifier', '') if isinstance(info.get('identifier'), str) else ''
        self.is_seekable = bool(info.get('isSeekable', False))
        self.author = info.get('author', '') if isinstance(info.get('author'), str) else ''
        self.position = info.get('position', 0) if isinstance(info.get('position'), (int, float)) else 0
        self.duration = info.get('length', 0) if isinstance(info.get('length'), (int, float)) else 0
        self.is_stream = bool(info.get('isStream', False))
        self.title = info.get('title', '') if isinstance(info.get('title'), str) else ''
        self.uri = info.get('uri', '') if isinstance(info.get('uri'), str) else ''
        self.source_name = info.get('sourceName', '') if isinstance(info.get('sourceName'), str) else ''
        self.artwork_url = info.get('artworkUrl', '') if isinstance(info.get('artworkUrl'), str) else ''
        
        self.playlist = data.get('playlist')
        
        self.node = node or data.get('node')
        self.nodes = data.get('nodes')
        
        self.requester = requester
        
        self._info_cache = None
    
    @property
    def info(self) -> Dict[str, Any]:
        if self._info_cache:
            return self._info_cache
        
        artwork = self.artwork_url or self._compute_artwork_from_known_sources()
        self._info_cache = {
            'identifier': self.identifier,
            'isSeekable': self.is_seekable,
            'position': self.position,
            'author': self.author,
            'length': self.duration,
            'isStream': self.is_stream,
            'title': self.title,
            'uri': self.uri,
            'sourceName': self.source_name,
            'artworkUrl': artwork
        }
        return self._info_cache
    
    @property
    def length(self) -> Union[int, float]:
        return self.duration
    
    @property
    def thumbnail(self) -> Optional[str]:
        return self.artwork_url or self._compute_artwork_from_known_sources()
    
    async def resolve(self, Magma: Any, opts: Dict[str, Any] = None) -> Optional['Track']:
        if opts is None:
            opts = {}
        
        if self.track and isinstance(self.track, str):
            return self
        
        if not Magma or not hasattr(Magma, 'resolve') or not callable(Magma.resolve):
            return None
        
        platform = (
            opts.get('platform') or 
            getattr(Magma.options, 'default_search_platform', None) if hasattr(Magma, 'options') else None or
            'ytsearch'
        )
        node = opts.get('node') or self.node or self.nodes
        
        query = self.uri
        if not query:
            if self.title:
                query = f'{self.author} - {self.title}'.strip() if self.author else self.title.strip()
            elif self.identifier and self.source_name and 'youtube' in self.source_name.lower():
                query = self.identifier
        
        if not query:
            return None
        
        payload = {
            'query': query,
            'source': platform,
            'requester': self.requester
        }
        if node:
            payload['node'] = node
        
        try:
            result = await Magma.resolve(payload)
        except Exception:
            return None
        
        if not result or not result.get('tracks'):
            return None
        
        found = result['tracks'][0] if result['tracks'] else None
        if not found:
            return None
        
        found_info = found.get('info', {})
        self.track = (
            found.get('track') if isinstance(found.get('track'), str) else
            found.get('encoded', self.track)
        )
        
        self.identifier = found_info.get('identifier', self.identifier)
        self.title = found_info.get('title', self.title)
        self.author = found_info.get('author', self.author)
        self.uri = found_info.get('uri', self.uri)
        self.source_name = found_info.get('sourceName', self.source_name)
        self.artwork_url = found_info.get('artworkUrl', self.artwork_url)
        self.is_seekable = bool(found_info.get('isSeekable', self.is_seekable))
        self.is_stream = bool(found_info.get('isStream', self.is_stream))
        
        position = found_info.get('position')
        if isinstance(position, (int, float)):
            self.position = position
        
        length = found_info.get('length')
        if isinstance(length, (int, float)):
            self.duration = length
        
        self.playlist = found.get('playlist', self.playlist)
        self._info_cache = None
        
        return self
    
    def is_valid(self) -> bool:
        return (
            (isinstance(self.track, str) and len(self.track) > 0) or
            (isinstance(self.uri, str) and len(self.uri) > 0)
        )
    
    def dispose(self) -> None:
        self._info_cache = None
        self.requester = None
        self.node = None
        self.nodes = None
    
    def _compute_artwork_from_known_sources(self) -> Optional[str]:
        track_id = self.identifier
        if not track_id and self.uri:
            match = YT_ID_RE.search(str(self.uri))
            if match:
                track_id = match.group(1)
        
        return f'https://i.ytimg.com/vi/{track_id}/hqdefault.jpg' if track_id else None