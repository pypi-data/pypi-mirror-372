import random
import re
import aiohttp

SOUNDCLOUD_REGEX = re.compile(r'<a\s+itemprop="url"\s+href="(\/[^"]+)"')

def shuffle_array(arr):
    random.shuffle(arr)
    return arr

async def fast_fetch(session, url):
    async with session.get(url, timeout=8) as response:
        response.raise_for_status()
        return await response.text()

async def sound_auto_play(base_url):
    try:
        async with aiohttp.ClientSession() as session:
            html = await fast_fetch(session, f"{base_url}/recommended")

        links = [f"https://soundcloud.com{match.group(1)}" for match in SOUNDCLOUD_REGEX.finditer(html)]
        
        if not links:
            raise ValueError("No tracks found")

        return shuffle_array(links[:50])
    except Exception as err:
        print(f"SoundCloud error: {err}")
        return []

async def spotify_auto_play(seed, player, requester, excluded_identifiers=None):
    if excluded_identifiers is None:
        excluded_identifiers = []
        
    try:
        track_id = seed.get('trackId')
        if not track_id:
            return None

        artist_ids = seed.get('artistIds')
        
        prev_identifier = getattr(player.current, 'identifier', None)
        
        seed_query = f"seed_tracks={track_id}"
        if artist_ids:
            seed_query += f"&seed_artists={artist_ids}"
        
        print(f'Seed query: {seed_query}')

        response = await player.Magma.resolve({
            'query': seed_query,
            'source': 'spsearch',
            'requester': requester
        })
        
        candidates = response.get('tracks', []) if response else []

        seen_ids = set(excluded_identifiers)
        if prev_identifier:
            seen_ids.add(prev_identifier)

        result = []
        for track in candidates:
            identifier = track.get('identifier')
            if identifier in seen_ids:
                continue
            
            seen_ids.add(identifier)
            
            plugin_info = track.get('pluginInfo', {})
            plugin_info['clientData'] = {'fromAutoplay': True}
            track['pluginInfo'] = plugin_info
            
            result.append(track)
            if len(result) == 5:
                break

        return result

    except Exception as err:
        print(f'Spotify autoplay error: {err}')
        return None

sc_auto_play = sound_auto_play
sp_auto_play = spotify_auto_play