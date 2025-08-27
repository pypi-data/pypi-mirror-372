import asyncio
import json
import re
import time
from urllib.parse import urlparse, quote

from pyee import EventEmitter

from .Node import Node
from .Player import Player
from .SearchPlatforms import SearchPlatforms
from .Track import Track

pkg_version = "1.0.0"

SEARCH_PREFIX = ':'
EMPTY_ARRAY = tuple()
EMPTY_TRACKS_RESPONSE = {
    'loadType': 'empty',
    'exception': None,
    'playlistInfo': None,
    'pluginInfo': {},
    'tracks': EMPTY_ARRAY
}

DEFAULT_OPTIONS = {
    'shouldDeleteMessage': False,
    'defaultSearchPlatform': 'ytsearch',
    'leaveOnEnd': False,
    'restVersion': 'v4',
    'plugins': [],
    'autoResume': True,
    'infiniteReconnects': True,
    'urlFilteringEnabled': False,
    'restrictedDomains': [],
    'allowedDomains': [],
    'failoverOptions': {
        'enabled': True,
        'maxRetries': 3,
        'retryDelay': 1000,
        'preservePosition': True,
        'resumePlayback': True,
        'cooldownTime': 5000,
        'maxFailoverAttempts': 5
    }
}

CLEANUP_INTERVAL = 180
MAX_CONCURRENT_OPS = 10
BROKEN_PLAYER_TTL = 300
FAILOVER_CLEANUP_TTL = 600
PLAYER_BATCH_SIZE = 20
SEEK_DELAY = 0.12
RECONNECT_DELAY = 0.4
CACHE_VALID_TIME = 12
NODE_TIMEOUT = 30
URL_PATTERN = re.compile(r'^https?:\/\/', re.IGNORECASE)


def _normalize_host(h):
    if not h:
        return ''
    h = h.lower()
    if h.startswith('www.'):
        h = h.slice(4)
    return h[:-1] if h.endswith('.') else h


def _host_matches_suffix(host, suffix):
    host = _normalize_host(host)
    suffix = _normalize_host(suffix)
    return host == suffix or host.endswith('.' + suffix)


def _is_probably_url(s):
    return isinstance(s, str) and len(s) > 8 and URL_PATTERN.match(s)


async def _delay(ms):
    await asyncio.sleep(ms / 1000)


def _range(start, end, step=1):
    return range(start, end, step)


def _safe_get_hostname(url):
    try:
        return _normalize_host(urlparse(url).hostname)
    except Exception:
        return None


def _safe_parse_url(url):
    try:
        u = urlparse(url)
        return {'host': _normalize_host(u.hostname), 'path': u.path.lower()}
    except Exception:
        return None


class Magma(EventEmitter):
    def __init__(self, client, nodes, options={}):
        super().__init__()
        if not client:
            raise ValueError('Client is required')
        if not isinstance(nodes, list) or not nodes:
            raise TypeError('Nodes must be a non-empty list')

        self.client = client
        self.nodes_config = nodes
        self.node_map = {}
        self.players = {}
        self.client_id = None
        self.initiated = False
        self.version = pkg_version

        self.options = {**DEFAULT_OPTIONS, **options}
        self.failover_options = {**DEFAULT_OPTIONS['failoverOptions'], **options.get('failoverOptions', {})}
        self.should_delete_message = self.options['shouldDeleteMessage']
        self.default_search_platform = self.options['defaultSearchPlatform']
        self.leave_on_end = self.options['leaveOnEnd']
        self.rest_version = self.options.get('restVersion', 'v4')
        self.plugins = self.options['plugins']
        self.auto_resume = self.options['autoResume']
        self.infinite_reconnects = self.options['infiniteReconnects']
        self.url_filtering_enabled = self.options['urlFilteringEnabled']
        self.restricted_domains = self.options.get('restrictedDomains', [])
        self.allowed_domains = self.options.get('allowedDomains', [])
        self.send = self.options.get('send', self._create_default_send())

        self._node_states = {}
        self._failover_queue = {}
        self._last_failover_attempt = {}
        self._broken_players = {}
        self._rebuild_locks = set()
        self._least_used_nodes_cache = None
        self._least_used_nodes_cache_time = 0
        self._node_load_cache = {}
        self._node_load_cache_time = {}
        self._domain_lists = None
        self._cleanup_timer = None

        self.on('nodeReady', self._on_node_ready)

        self._bind_event_handlers()
        self._start_cleanup_timer()

    def _on_node_ready(self, node, payload):
        resumed = payload.get('resumed', False)
        for player in self.players.values():
            if player.node == node and player.connection:
                player.connection.resend_voice_update({'resume': resumed})

    def _get_domain_lists(self):
        if self._domain_lists:
            return self._domain_lists

        allowed_host_suffixes = []
        allowed_regexes = []
        for d in self.allowed_domains:
            if not d:
                continue
            if isinstance(d, re.Pattern):
                allowed_regexes.append(d)
            else:
                allowed_host_suffixes.append(_normalize_host(str(d)))

        restricted_host_suffixes = []
        restricted_regexes = []
        for d in self.restricted_domains:
            if not d:
                continue
            if isinstance(d, re.Pattern):
                restricted_regexes.append(d)
            else:
                restricted_host_suffixes.append(_normalize_host(str(d)))

        self._domain_lists = {
            'allowedHostSuffixes': allowed_host_suffixes,
            'allowedRegexes': allowed_regexes,
            'restrictedHostSuffixes': restricted_host_suffixes,
            'restrictedRegexes': restricted_regexes
        }
        return self._domain_lists

    def _create_default_send(self):
        def send(packet):
            guild_id = packet.get('d', {}).get('guild_id')
            if not guild_id:
                return
            # This part is highly dependent on the discord library used (e.g., discord.py, py-cord)
            # The following is a generic placeholder.
            # You will need to adapt this to your specific library.
            # guild = self.client.get_guild(int(guild_id))
            # if guild and hasattr(guild.shard, 'send'):
            #     guild.shard.send(packet)
            pass
        return send

    def _bind_event_handlers(self):
        if not self.auto_resume:
            return
        
        def on_node_connect(node):
            asyncio.create_task(self._on_node_connect_async(node))
        
        def on_node_disconnect(node):
            asyncio.create_task(self._on_node_disconnect_async(node))

        self._on_node_connect_handler = on_node_connect
        self._on_node_disconnect_handler = on_node_disconnect
        
        self.on('nodeConnect', self._on_node_connect_handler)
        self.on('nodeDisconnect', self._on_node_disconnect_handler)

    async def _on_node_connect_async(self, node):
        self._invalidate_cache()
        await self._rebuild_broken_players(node)

    async def _on_node_disconnect_async(self, node):
        self._invalidate_cache()
        self._store_broken_players(node)

    def _start_cleanup_timer(self):
        loop = asyncio.get_event_loop()
        self._cleanup_timer = loop.call_later(CLEANUP_INTERVAL, self._perform_cleanup)

    @property
    def least_used_nodes(self):
        now = time.time()
        if self._least_used_nodes_cache and (now - self._least_used_nodes_cache_time) < CACHE_VALID_TIME:
            return self._least_used_nodes_cache
        
        connected = [node for node in self.node_map.values() if node.connected]
        connected.sort(key=lambda a: self._get_cached_node_load(a))
        
        self._least_used_nodes_cache = tuple(connected)
        self._least_used_nodes_cache_time = now
        return self._least_used_nodes_cache

    def _invalidate_cache(self):
        self._least_used_nodes_cache = None
        self._least_used_nodes_cache_time = 0

    def _get_cached_node_load(self, node):
        node_id = node.name or node.host
        now = time.time()
        cache_time = self._node_load_cache_time.get(node_id)
        
        if cache_time and (now - cache_time) < 5:
            return self._node_load_cache.get(node_id, 0)
            
        load = self._calculate_node_load(node)
        self._node_load_cache[node_id] = load
        self._node_load_cache_time[node_id] = now
        return load

    def _calculate_node_load(self, node):
        stats = node.stats
        if not stats:
            return 0
        
        cpu = stats.get('cpu', {})
        cores = max(1, cpu.get('cores', 1))
        cpu_load = cpu.get('systemLoad', 0) / cores
        
        playing = stats.get('playingPlayers', 0)
        
        memory = stats.get('memory', {})
        memory_usage = memory.get('used', 0) / max(1, memory.get('reservable', 1))
        
        rest_calls = getattr(node.rest, 'calls', 0)
        
        return (cpu_load * 100) + (playing * 0.75) + (memory_usage * 40) + (rest_calls * 0.001)

    async def init(self, client_id):
        if self.initiated:
            return self
        self.client_id = client_id
        if not self.client_id:
            return
        
        tasks = [asyncio.wait_for(self._create_node(n), timeout=NODE_TIMEOUT) for n in self.nodes_config]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        if not success_count:
            raise ConnectionError('No nodes connected')
            
        await self._load_plugins()
        self.initiated = True
        return self

    async def _load_plugins(self):
        if not self.plugins:
            return
        
        tasks = []
        for plugin in self.plugins:
            async def load_plugin(p):
                try:
                    await p.load(self)
                except Exception as err:
                    self.emit('error', None, Exception(f"Plugin error: {err}"))
            tasks.append(load_plugin(plugin))
        
        await asyncio.gather(*tasks)

    async def _create_node(self, options):
        node_id = options.get('name') or options.get('host')
        self._destroy_node(node_id)
        
        node = Node(self, options, self.options)
        node.players = set()
        self.node_map[node_id] = node
        self._node_states[node_id] = {'connected': False, 'failoverInProgress': False}
        
        try:
            await node.connect()
            self._node_states[node_id]['connected'] = True
            self._invalidate_cache()
            self.emit('nodeCreate', node)
            return node
        except Exception as error:
            self._cleanup_node(node_id)
            raise error

    def _destroy_node(self, identifier):
        node = self.node_map.get(identifier)
        if node:
            try:
                node.destroy()
            except Exception:
                pass
            self._cleanup_node(identifier)
            self.emit('nodeDestroy', node)

    def _cleanup_node(self, node_id):
        node = self.node_map.pop(node_id, None)
        if node:
            node.remove_all_listeners()
            if hasattr(node, 'players'):
                node.players.clear()
        
        self._node_states.pop(node_id, None)
        self._failover_queue.pop(node_id, None)
        self._last_failover_attempt.pop(node_id, None)
        self._node_load_cache.pop(node_id, None)
        self._node_load_cache_time.pop(node_id, None)
        
        if self._least_used_nodes_cache and any((n.name or n.host) == node_id for n in self._least_used_nodes_cache):
            self._invalidate_cache()

    def _store_broken_players(self, node):
        node_id = node.name or node.host
        now = time.time()
        for player in self.players.values():
            if player.node != node:
                continue
            state = self._capture_player_state(player)
            if state:
                state['originalNodeId'] = node_id
                state['brokenAt'] = now
                self._broken_players[player.guild_id] = state

    async def _rebuild_broken_players(self, node):
        node_id = node.name or node.host
        rebuilds = []
        now = time.time()
        
        for guild_id, broken_state in self._broken_players.items():
            if broken_state['originalNodeId'] != node_id:
                continue
            if now - broken_state['brokenAt'] > BROKEN_PLAYER_TTL:
                continue
            rebuilds.append({'guildId': guild_id, 'brokenState': broken_state})
            
        if not rebuilds:
            return
            
        batch_size = min(MAX_CONCURRENT_OPS, len(rebuilds))
        successes = []
        
        for i in _range(0, len(rebuilds), batch_size):
            batch = rebuilds[i:i + batch_size]
            tasks = [self._rebuild_player(item['brokenState'], node).then(lambda: item['guildId']) for item in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for r in results:
                if not isinstance(r, Exception):
                    successes.append(r)
                    
        for guild_id in successes:
            self._broken_players.pop(guild_id, None)
            
        if successes:
            self.emit('playersRebuilt', node, len(successes))

    async def _rebuild_player(self, broken_state, target_node):
        guild_id = broken_state['guildId']
        lock_key = f"rebuild_{guild_id}"
        if lock_key in self._rebuild_locks:
            return
        self._rebuild_locks.add(lock_key)
        
        try:
            existing = self.players.get(guild_id)
            if existing:
                await self.destroy_player(guild_id)
                await _delay(RECONNECT_DELAY * 1000)
                
            player = self.create_player(target_node, {
                'guildId': guild_id,
                'textChannel': broken_state['textChannel'],
                'voiceChannel': broken_state['voiceChannel'],
                'defaultVolume': broken_state.get('volume', 65),
                'deaf': broken_state.get('deaf', True)
            })
            
            current = broken_state.get('current')
            if current and hasattr(player.queue, 'add'):
                player.queue.add(current)
                await player.play()
                if broken_state.get('position', 0) > 0:
                    await asyncio.sleep(SEEK_DELAY)
                    if hasattr(player, 'seek'):
                        await player.seek(broken_state['position'])
                if broken_state.get('paused'):
                    await player.pause(True)
            return player
        finally:
            self._rebuild_locks.remove(lock_key)
    
    async def handle_node_failover(self, failed_node):
        if not self.failover_options['enabled']:
            return
        node_id = failed_node.name or failed_node.host
        now = time.time()
        node_state = self._node_states.get(node_id)
        if node_state and node_state['failoverInProgress']:
            return
        last_attempt = self._last_failover_attempt.get(node_id)
        if last_attempt and (now - last_attempt) < self.failover_options['cooldownTime'] / 1000:
            return
        attempts = self._failover_queue.get(node_id, 0)
        if attempts >= self.failover_options['maxFailoverAttempts']:
            return
        
        self._node_states[node_id] = {'connected': False, 'failoverInProgress': True}
        self._last_failover_attempt[node_id] = now
        self._failover_queue[node_id] = attempts + 1
        
        try:
            self.emit('nodeFailover', failed_node)
            affected_players = list(failed_node.players or [])
            if not affected_players:
                self._node_states[node_id]['failoverInProgress'] = False
                return
            
            available_nodes = self._get_available_nodes(failed_node)
            if not available_nodes:
                raise Exception('No failover nodes available')
            
            results = await self._migrate_players_optimized(affected_players, available_nodes)
            successful = sum(1 for r in results if r['success'])
            if successful:
                self.emit('nodeFailoverComplete', failed_node, successful, len(results) - successful)
        except Exception as error:
            self.emit('error', None, Exception(f"Failover failed: {error}"))
        finally:
            self._node_states[node_id]['failoverInProgress'] = False

    async def _migrate_players_optimized(self, players, available_nodes):
        base_loads = {n: self._get_cached_node_load(n) for n in available_nodes}
        assigned_counts = {n: 0 for n in available_nodes}

        def pick_node():
            best = min(available_nodes, key=lambda n: base_loads[n] + assigned_counts[n])
            assigned_counts[best] += 1
            return best

        results = []
        for i in _range(0, len(players), MAX_CONCURRENT_OPS):
            batch = players[i:i + MAX_CONCURRENT_OPS]
            tasks = [self._migrate_player(p, pick_node) for p in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend([{'success': not isinstance(r, Exception), 'error': r if isinstance(r, Exception) else None} for r in batch_results])
        return results

    async def _migrate_player(self, player, pick_node_func):
        player_state = self._capture_player_state(player)
        if not player_state:
            raise Exception('Failed to capture state')
        
        for retry in _range(0, self.failover_options['maxRetries']):
            try:
                target_node = pick_node_func()
                new_player = await self._create_player_on_node(target_node, player_state)
                await self._restore_player_state(new_player, player_state)
                self.emit('playerMigrated', player, new_player, target_node)
                return new_player
            except Exception as error:
                if retry == self.failover_options['maxRetries'] - 1:
                    raise error
                await _delay(self.failover_options['retryDelay'] * (1.5 ** retry))

    def _capture_player_state(self, player):
        if not player:
            return None
        return {
            'guildId': player.guild_id,
            'textChannel': player.text_channel,
            'voiceChannel': player.voice_channel,
            'volume': player.volume,
            'paused': player.paused,
            'position': player.position,
            'current': player.current,
            'queue': player.queue.tracks[:50],
            'repeat': player.loop,
            'shuffle': player.shuffle,
            'deaf': player.deaf,
            'connected': player.connected
        }

    async def _create_player_on_node(self, target_node, player_state):
        return self.create_player(target_node, {
            'guildId': player_state['guildId'],
            'textChannel': player_state['textChannel'],
            'voiceChannel': player_state['voiceChannel'],
            'defaultVolume': player_state.get('volume', 100),
            'deaf': player_state.get('deaf', False)
        })

    async def _restore_player_state(self, new_player, player_state):
        operations = []
        if player_state.get('volume') is not None:
            if hasattr(new_player, 'set_volume'):
                operations.append(new_player.set_volume(player_state['volume']))
            else:
                new_player.volume = player_state['volume']
        
        if player_state.get('queue') and hasattr(new_player.queue, 'add'):
            new_player.queue.add(*player_state['queue'])
            
        if player_state.get('current') and self.failover_options['preservePosition']:
            if hasattr(new_player.queue, 'add'):
                new_player.queue.add(player_state['current'], to_front=True)
            if self.failover_options['resumePlayback']:
                operations.append(new_player.play())
                if player_state.get('position', 0) > 0:
                    async def seek_after_delay():
                        await _delay(SEEK_DELAY * 1000)
                        if hasattr(new_player, 'seek'):
                            await new_player.seek(player_state['position'])
                    operations.append(seek_after_delay())
                if player_state.get('paused'):
                    operations.append(new_player.pause(True))
                    
        new_player.repeat = player_state.get('repeat')
        new_player.shuffle = player_state.get('shuffle')
        await asyncio.gather(*[op for op in operations if asyncio.iscoroutine(op)])

    def update_voice_state(self, data):
        d = data.get('d', {})
        t = data.get('t')
        if not d.get('guild_id'):
            return
        if t not in ('VOICE_STATE_UPDATE', 'VOICE_SERVER_UPDATE'):
            return
        
        player = self.players.get(d['guild_id'])
        if not player:
            return
            
        if t == 'VOICE_STATE_UPDATE':
            if d.get('user_id') != self.client_id:
                return
            if not d.get('channel_id'):
                self.destroy_player(d['guild_id'])
                return
            if player.connection:
                player.connection.session_id = d.get('session_id')
                player.connection.set_state_update(d)
        else:
            if player.connection:
                player.connection.set_server_update(d)

    def fetch_region(self, region):
        if not region:
            return self.least_used_nodes
        lower_region = region.lower()
        filtered = [node for node in self.node_map.values() if node.connected and lower_region in node.regions]
        filtered.sort(key=lambda a: self._get_cached_node_load(a))
        return tuple(filtered)

    def create_connection(self, options):
        if not self.initiated:
            raise Exception('Magma not initialized')
        
        guild_id = options['guildId']
        existing = self.players.get(guild_id)
        if existing:
            if options.get('voiceChannel') and existing.voice_channel != options['voiceChannel']:
                try:
                    existing.connect(options)
                except Exception:
                    pass
            return existing
            
        candidate_nodes = self.fetch_region(options.get('region')) if options.get('region') else self.least_used_nodes
        if not candidate_nodes:
            raise Exception('No nodes available')
            
        node = self._choose_least_busy_node(candidate_nodes)
        if not node:
            raise Exception('No suitable node found')
            
        return self.create_player(node, options)

    def create_player(self, node, options):
        guild_id = options['guildId']
        existing = self.players.get(guild_id)
        if existing:
            try:
                existing.destroy()
            except Exception:
                pass
                
        player = Player(self, node, options)
        self.players[guild_id] = player
        if hasattr(node, 'players'):
            node.players.add(player)
            
        player.once('destroy', lambda: self._handle_player_destroy(player))
        player.connect(options)
        self.emit('playerCreate', player)
        return player

    def _handle_player_destroy(self, player):
        node = player.node
        if node and hasattr(node, 'players'):
            node.players.discard(player)
        if self.players.get(player.guild_id) == player:
            self.players.pop(player.guild_id, None)
        self.emit('playerDestroy', player)

    async def destroy_player(self, guild_id):
        player = self.players.get(guild_id)
        if not player:
            return
        try:
            self.players.pop(guild_id, None)
            player.remove_all_listeners()
            await player.destroy()
        finally:
            pass

    def _is_url_allowed(self, url):
        if not self.url_filtering_enabled or not _is_probably_url(url):
            return True
        hostname = _safe_get_hostname(url)
        if not hostname:
            return False
        
        lists = self._get_domain_lists()
        allowed_suffixes = lists['allowedHostSuffixes']
        allowed_regexes = lists['allowedRegexes']
        restricted_suffixes = lists['restrictedHostSuffixes']
        restricted_regexes = lists['restrictedRegexes']

        if allowed_suffixes or allowed_regexes:
            return any(rx.search(hostname) for rx in allowed_regexes) or \
                   any(_host_matches_suffix(hostname, s) for s in allowed_suffixes)
                   
        if restricted_suffixes or restricted_regexes:
            return not (any(rx.search(hostname) for rx in restricted_regexes) or \
                        any(_host_matches_suffix(hostname, s) for s in restricted_suffixes))
                        
        return True

    def _resolve_search_platform(self, source):
        if not source:
            return self.default_search_platform
        normalized = source.lower().strip()
        return SearchPlatforms.SEARCH_PLATFORMS.get(normalized, source)

    def _validate_source_regex(self, url_str):
        if not _is_probably_url(url_str):
            return None
        parsed = _safe_parse_url(url_str)
        if not parsed:
            return None
        
        host, path = parsed['host'], parsed['path']
        if re.search(r'\.(mp3|m3u8?|mp4|m4a|wav|aacp)(?:$|\?)', path, re.I):
            return 'http'
            
        host_mapping = {
            'music.youtube.com': 'ytmsearch',
            'youtu.be': 'ytsearch',
            'youtube.com': 'ytsearch',
            'soundcloud.com': 'scsearch',
            'soundcloud.app.goo.gl': 'scsearch',
            'open.spotify.com': 'spsearch',
            'deezer.com': 'dzsearch',
            'deezer.page.link': 'dzsearch',
            'music.apple.com': 'amsearch',
            'tidal.com': 'tdsearch',
            'listen.tidal.com': 'tdsearch',
            'jiosaavn.com': 'jssearch',
            'music.yandex.ru': 'ymsearch',
            'bandcamp.com': 'bcsearch'
        }
        for host_suffix, platform in host_mapping.items():
            if host == host_suffix or _host_matches_suffix(host, host_suffix):
                return platform
                
        link_hosts = ['twitch.tv', 'vimeo.com', 'tiktok.com', 'mixcloud.com', 'radiohost.de']
        for link_host in link_hosts:
            if _host_matches_suffix(host, link_host):
                return 'link'
                
        return None

    async def resolve(self, query, source=None, requester=None, nodes=None):
        if not self.initiated:
            raise Exception('Magma not initialized')
        
        source = source or self.default_search_platform
        request_node = self._get_request_node(nodes)
        if not request_node:
            raise Exception('No nodes available')
            
        if self.restricted_domains:
            if _is_probably_url(query) and not self._is_url_allowed(query):
                self.emit('debug', f"Blocked URL by domain restrictions: {query}")
                return EMPTY_TRACKS_RESPONSE
                
        formatted_query = query if _is_probably_url(query) else f"{source}{SEARCH_PREFIX}{query}"
        
        try:
            endpoint = f"/{self.rest_version}/loadtracks?identifier={quote(formatted_query)}"
            response = await request_node.rest.make_request('GET', endpoint)
            if not response or response.get('loadType') in ('empty', 'NO_MATCHES'):
                return EMPTY_TRACKS_RESPONSE
            return self._construct_response(response, requester, request_node)
        except Exception as error:
            if isinstance(error, asyncio.TimeoutError):
                raise Exception('Request timeout')
            raise Exception(f"Resolve failed: {error}")

    def _get_request_node(self, nodes):
        if not nodes:
            chosen = self._choose_least_busy_node(self.least_used_nodes)
            if not chosen:
                raise Exception('No nodes available')
            return chosen
            
        if isinstance(nodes, Node):
            return nodes
            
        if isinstance(nodes, list):
            candidates = [n for n in nodes if n and n.connected]
            chosen = self._choose_least_busy_node(candidates or self.least_used_nodes)
            if not chosen:
                raise Exception('No nodes available')
            return chosen
            
        if isinstance(nodes, str):
            node = self.node_map.get(nodes)
            if node and node.connected:
                return node
            chosen = self._choose_least_busy_node(self.least_used_nodes)
            if not chosen:
                raise Exception('No nodes available')
            return chosen
            
        raise TypeError(f"Invalid nodes parameter: {type(nodes)}")

    def _choose_least_busy_node(self, nodes):
        if not nodes:
            return None
        if len(nodes) == 1:
            return nodes[0]
        return min(nodes, key=lambda n: self._get_cached_node_load(n))

    def _construct_response(self, response, requester, request_node):
        load_type = response.get('loadType')
        data = response.get('data')
        root_plugin_info = response.get('pluginInfo', {})
        
        base_response = {
            'loadType': load_type,
            'exception': None,
            'playlistInfo': None,
            'pluginInfo': root_plugin_info,
            'tracks': []
        }
        
        if load_type in ('error', 'LOAD_FAILED'):
            base_response['exception'] = data or response.get('exception')
            return base_response
            
        def make_track(t):
            return Track(t, requester, request_node)
            
        if load_type == 'track':
            if data:
                base_response['pluginInfo'] = data.get('info', {}).get('pluginInfo') or data.get('pluginInfo') or base_response['pluginInfo']
                base_response['tracks'].append(make_track(data))
        elif load_type == 'playlist':
            if data:
                info = data.get('info')
                thumbnail = data.get('pluginInfo', {}).get('artworkUrl') or (data.get('tracks', [{}])[0].get('info', {}).get('artworkUrl'))
                if info:
                    base_response['playlistInfo'] = {'name': info.get('name') or info.get('title'), 'thumbnail': thumbnail, **info}
                base_response['pluginInfo'] = data.get('pluginInfo', base_response['pluginInfo'])
                base_response['tracks'] = [make_track(t) for t in data.get('tracks', [])]
        elif load_type == 'search':
            base_response['tracks'] = [make_track(t) for t in (data or [])]
            
        return base_response

    def get(self, guild_id):
        player = self.players.get(guild_id)
        if not player:
            raise Exception(f"Player not found: {guild_id}")
        return player

    async def search(self, query, requester, source=None):
        if not query or not requester:
            return None
        try:
            source = source or self.default_search_platform
            resolved_source = self._resolve_search_platform(source)
            result = await self.resolve(query=query, source=resolved_source, requester=requester)
            return result.get('tracks')
        except Exception:
            return None

    def _perform_cleanup(self):
        now = time.time()
        
        expired_guilds = [guild_id for guild_id, state in self._broken_players.items() if now - state['brokenAt'] > BROKEN_PLAYER_TTL]
        for g in expired_guilds:
            self._broken_players.pop(g, None)
            
        expired_nodes = [node_id for node_id, ts in self._last_failover_attempt.items() if now - ts > FAILOVER_CLEANUP_TTL]
        for n in expired_nodes:
            self._last_failover_attempt.pop(n, None)
            self._failover_queue.pop(n, None)
            
        if len(self._node_load_cache) > 50:
            self._node_load_cache.clear()
            self._node_load_cache_time.clear()
            
        loop = asyncio.get_event_loop()
        self._cleanup_timer = loop.call_later(CLEANUP_INTERVAL, self._perform_cleanup)

    def _get_available_nodes(self, exclude_node):
        return [node for node in self.node_map.values() if node != exclude_node and node.connected]

    async def destroy(self):
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
            self._cleanup_timer = None
            
        if hasattr(self, '_on_node_connect_handler'):
            self.remove_listener('nodeConnect', self._on_node_connect_handler)
            self.remove_listener('nodeDisconnect', self._on_node_disconnect_handler)
            
        tasks = []
        for player in self.players.values():
            player.remove_all_listeners()
            tasks.append(player.destroy())
            
        for node in self.node_map.values():
            tasks.append(node.destroy())
            
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.players.clear()
        self.node_map.clear()
        self._node_states.clear()
        self._failover_queue.clear()
        self._last_failover_attempt.clear()
        self._broken_players.clear()
        self._node_load_cache.clear()
        self._node_load_cache_time.clear()
        self._least_used_nodes_cache = None
        self.remove_all_listeners()
