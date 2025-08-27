import asyncio
import re
from urllib.parse import quote
import aiohttp

YOUTUBE_QUALITIES = ['maxresdefault', 'hqdefault', 'mqdefault', 'default']
YOUTUBE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{11}$")
SPOTIFY_URI_REGEX = re.compile(r"^https:\/\/open\.spotify\.com\/(track|album|playlist)\/[a-zA-Z0-9]+")

async def get_image_url(info):
    if not info or not info.get('sourceName') or not info.get('uri'):
        return None
    
    source_name = info['sourceName'].lower()
    handler = source_handlers.get(source_name)
    
    if not handler:
        return None
    
    try:
        if source_name == 'spotify':
            param = info['uri']
        elif source_name == 'youtube':
            param = extract_youtube_id(info['uri'])
        else:
            param = info['uri']
            
        if not param:
            return None
            
        return await handler(param)
    except Exception as error:
        print(f"Error fetching {source_name} thumbnail: {error}")
        return None

def extract_youtube_id(uri):
    if not uri:
        return None
    
    id_ = None
    
    if 'youtube.com/watch?v=' in uri:
        try:
            id_ = uri.split('v=')[1].split('&')[0]
        except IndexError:
            pass
    elif 'youtu.be/' in uri:
        try:
            id_ = uri.split('youtu.be/')[1].split('?')[0]
        except IndexError:
            pass
    elif 'youtube.com/embed/' in uri:
        try:
            id_ = uri.split('embed/')[1].split('?')[0]
        except IndexError:
            pass
    elif YOUTUBE_ID_REGEX.match(uri):
        id_ = uri
        
    return id_ if id_ and YOUTUBE_ID_REGEX.match(id_) else None

async def fetch_spotify_thumbnail(uri):
    if not SPOTIFY_URI_REGEX.match(uri):
        raise ValueError('Invalid Spotify URI format')
        
    url = f"https://open.spotify.com/oembed?url={quote(uri)}"
    
    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch_json(session, url)
            return data.get('thumbnail_url')
    except Exception as error:
        raise Exception(f"Spotify fetch failed: {error}")

async def fetch_youtube_thumbnail(identifier):
    if not identifier or not YOUTUBE_ID_REGEX.match(identifier):
        raise ValueError('Invalid YouTube identifier')
        
    async with aiohttp.ClientSession() as session:
        for quality in YOUTUBE_QUALITIES:
            url = f"https://img.youtube.com/vi/{identifier}/{quality}.jpg"
            
            try:
                exists = await check_image_exists(session, url)
                if exists:
                    return url
            except Exception:
                continue
                
    return None

async def fetch_json(session, url):
    async with session.get(url, timeout=5) as response:
        response.raise_for_status()
        return await response.json()

async def check_image_exists(session, url):
    try:
        async with session.head(url, timeout=3) as response:
            return response.status == 200
    except asyncio.TimeoutError:
        return False
    except aiohttp.ClientError:
        return False

source_handlers = {
    'spotify': fetch_spotify_thumbnail,
    'youtube': fetch_youtube_thumbnail
}
