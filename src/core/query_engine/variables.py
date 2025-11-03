# engine/variables.py
"""
Değişken context builder - API Response + FFprobe + Global verilerden değişken ortamı oluşturur.
"""
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import re
import math


def build_variable_context(
    file_path: str,
    api_response_data: Optional[Dict[str, Any]] = None,
    ffprobe_data: Optional[Dict[str, Any]] = None,
    media_type: str = "movie",
    parsed_info: Optional[Dict[str, Any]] = None,
    config_globals: Optional[Dict[str, Any]] = None,
    root_paths: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Tüm değişkenleri içeren context oluştur.
    
    Args:
        file_path: Dosya yolu
        api_response_data: Normalized API response from any client (movie, tv, episode)
        ffprobe_data: FFprobe JSON output
        media_type: "movie" veya "tv"
        parsed_info: Sanitiser'dan gelen parse bilgisi (title, year, season, episode)
        config_globals: config.yml → query_engine.globals
        root_paths: movies_dst, series_dst gibi
    
    Returns:
        Tüm değişkenleri içeren dict
    """
    ctx = {}
    
    # --- PATH & FILE ---
    p = Path(file_path)
    ctx.update(_build_path_vars(p, root_paths or {}))
    
    # --- DATE/TIME ---
    ctx.update(_build_datetime_vars())
    
    # --- GLOBALS ---
    ctx['globals'] = config_globals or {}
    
    # --- FFPROBE ---
    if ffprobe_data:
        ctx.update(_build_ffprobe_vars(ffprobe_data, file_path))
        ctx['ffprobe'] = ffprobe_data  # Ham ağaç erişimi
    
    # --- API RESPONSE ---
    if api_response_data:
        ctx.update(_build_api_vars(api_response_data, media_type, parsed_info))
        # Ensure extras key exists for safe template access
        if 'extras' not in api_response_data:
            api_response_data['extras'] = {}
        ctx['apiResponse'] = api_response_data  # Ham ağaç erişimi (normalized)
    else:
        # Empty apiResponse for safe template access
        ctx['apiResponse'] = {'extras': {}}
    
    # --- PARSED INFO (sanitiser çıktısı) ---
    if parsed_info:
        ctx.update({
            'seasonNumber': f"{parsed_info.get('season', 1):02d}" if parsed_info.get('season') else '',
            'episodeNumber': f"{parsed_info.get('episode', 1):02d}" if parsed_info.get('episode') else '',
        })
        # Fallback names if API data missing or incomplete
        if media_type == 'tv':
            if not ctx.get('showName'):
                ctx['showName'] = parsed_info.get('title') or parsed_info.get('show') or ''
        elif media_type == 'movie':
            if not ctx.get('name'):
                ctx['name'] = parsed_info.get('title') or ''
    
    return ctx


def _build_path_vars(p: Path, root_paths: Dict[str, str]) -> Dict[str, Any]:
    """Yol ve dosya değişkenleri."""
    return {
        'path': str(p.absolute()),
        'dir': str(p.parent.absolute()),
        'fileName': p.name,
        'stem': p.stem,
        'ext': p.suffix,
        'rootMovies': root_paths.get('movies_dst', ''),
        'rootSeries': root_paths.get('series_dst', ''),
        'relPathFromRoot': '',  # TODO: Hesapla
    }


def _build_datetime_vars() -> Dict[str, Any]:
    """Tarih/zaman değişkenleri."""
    now = datetime.now()
    return {
        'nowIso': now.isoformat(),
        'nowDate': now.strftime('%d-%m-%Y'),
        'nowTime': now.strftime('%H:%M:%S'),
        'todayYear': now.year,
        'todayMonth': now.month,
        'todayDay': now.day,
        'epochSec': int(now.timestamp()),
    }


def _build_ffprobe_vars(ff: Dict[str, Any], file_path: str) -> Dict[str, Any]:
    """FFprobe normalize + derived değişkenleri."""
    ctx = {}
    
    # Container/Format
    fmt = ff.get('format', {})
    ctx['container'] = {
        'format': fmt.get('format_name', ''),
        'longName': fmt.get('format_long_name', ''),
        'bitRate': int(fmt.get('bit_rate', 0)),
        'tags': fmt.get('tags', {}),
    }
    
    size_bytes = int(fmt.get('size', 0))
    duration_sec = float(fmt.get('duration', 0))
    
    ctx['sizeInt'] = size_bytes
    ctx['sizeH'] = _human_size(size_bytes)
    ctx['sizeGiB'] = size_bytes / (1024**3)
    ctx['sizeBucket'] = _size_bucket(size_bytes)
    
    ctx['durationSec'] = duration_sec
    ctx['durationH'] = _seconds_to_hms(duration_sec)
    
    bitrate = int(fmt.get('bit_rate', 0)) or (int(size_bytes * 8 / duration_sec) if duration_sec > 0 else 0)
    ctx['totalBitrateBps'] = bitrate
    ctx['totalBitrateMbps'] = bitrate / 1_000_000
    ctx['bitrateBucket'] = _bitrate_bucket(bitrate)
    
    # Streams
    streams = ff.get('streams', [])
    
    # Video (ilk video stream)
    video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    if video_stream:
        ctx['video'] = _parse_video_stream(video_stream)
        ctx['videoBitDepth'] = ctx['video'].get('bitDepth', 8)
        ctx['videoQuality'] = ctx['video'].get('resolution', '')
    else:
        ctx['video'] = {}
        ctx['videoBitDepth'] = 0
        ctx['videoQuality'] = ''
    
    # Audio (tüm audio streams)
    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
    ctx['audioCount'] = len(audio_streams)
    ctx['audio'] = {}
    for i, a in enumerate(audio_streams, 1):
        ctx['audio'][i] = _parse_audio_stream(a)
    
    # Default audio index
    default_audio = next((i+1 for i, s in enumerate(audio_streams) if s.get('disposition', {}).get('default') == 1), 1)
    ctx['audioDefaultIndex'] = default_audio
    
    # Subtitle
    subtitle_streams = [s for s in streams if s.get('codec_type') == 'subtitle']
    ctx['subtitleCount'] = len(subtitle_streams)
    ctx['subtitle'] = {}
    for i, sub in enumerate(subtitle_streams, 1):
        ctx['subtitle'][i] = _parse_subtitle_stream(sub)
    
    return ctx


def _parse_video_stream(s: Dict[str, Any]) -> Dict[str, Any]:
    """Video stream normalize."""
    width = s.get('width', 0)
    height = s.get('height', 0)
    
    # Resolution
    resolution = ''
    if height >= 2160:
        resolution = '2160p'
    elif height >= 1440:
        resolution = '1440p'
    elif height >= 1080:
        resolution = '1080p'
    elif height >= 720:
        resolution = '720p'
    elif height >= 576:
        resolution = '576p'
    elif height > 0:
        resolution = f'{height}p'
    
    # FPS
    fps_str = s.get('r_frame_rate', '0/1')
    fps_float = _parse_fps(fps_str)
    
    # Bit depth
    bps = s.get('bits_per_raw_sample')
    pix_fmt = s.get('pix_fmt', '')
    bit_depth = int(bps) if bps else (10 if '10le' in pix_fmt else 8)
    
    # HDR detection
    hdr_format = _detect_hdr(s)
    
    # SAR/DAR
    sar = s.get('sample_aspect_ratio', '1:1')
    dar = s.get('display_aspect_ratio', '16:9')
    
    return {
        'codec': s.get('codec_name', ''),
        'width': width,
        'height': height,
        'resolution': resolution,
        'pixFmt': pix_fmt,
        'bitRate': int(s.get('bit_rate', 0)),
        'fps': fps_str,
        'fpsFloat': fps_float,
        'fpsBucket': _fps_bucket(fps_float),
        'level': s.get('level', 0),
        'profile': s.get('profile', ''),
        'sar': sar,
        'dar': dar,
        'fieldOrder': s.get('field_order', 'progressive'),
        'colorPrimaries': s.get('color_primaries', ''),
        'colorTransfer': s.get('color_transfer', ''),
        'colorSpace': s.get('color_space', ''),
        'hdrFormat': hdr_format,
        'bitDepth': bit_depth,
    }


def _parse_audio_stream(s: Dict[str, Any]) -> Dict[str, Any]:
    """Audio stream normalize."""
    tags = s.get('tags', {})
    channels = s.get('channels', 0)
    layout = s.get('channel_layout', '')
    
    # Layout normalize
    if not layout:
        if channels == 1:
            layout = 'mono'
        elif channels == 2:
            layout = 'stereo'
        elif channels == 6:
            layout = '5.1'
        elif channels == 8:
            layout = '7.1'
    
    return {
        'codec': s.get('codec_name', ''),
        'language': tags.get('language', ''),
        'channels': channels,
        'layout': layout,
        'sampleRate': s.get('sample_rate', 0),
        'bitRate': int(s.get('bit_rate', 0)),
    }


def _parse_subtitle_stream(s: Dict[str, Any]) -> Dict[str, Any]:
    """Subtitle stream normalize."""
    tags = s.get('tags', {})
    disposition = s.get('disposition', {})
    
    return {
        'codec': s.get('codec_name', ''),
        'language': tags.get('language', ''),
        'forced': disposition.get('forced', 0) == 1,
    }


def _build_api_vars(api_data: Dict[str, Any], media_type: str, parsed_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """API response (normalized) + alias değişkenleri."""
    import sys
    ctx = {}
    
    # Extract extras as direct variables
    extras = api_data.get('extras', {})
    
    try:
        if extras:
            # Credits - FULL LISTS (1-indexed for YAML engine)
            credits = extras.get('credits', {})
            if credits:
                cast_list = credits.get('cast', [])
                crew_list = credits.get('crew', [])
                
                # Convert to 1-indexed dicts for variable access
                ctx['cast'] = {i+1: c for i, c in enumerate(cast_list)}
                ctx['crew'] = {i+1: c for i, c in enumerate(crew_list)}
                
                # Counts and derived
                ctx['castCount'] = len(cast_list)
                ctx['crewCount'] = len(crew_list)
                ctx['topCast'] = ', '.join([c.get('name', '') for c in cast_list[:3]])
                ctx['director'] = next((c.get('name', '') for c in crew_list if c.get('job') == 'Director'), '')
            
            # Aggregate credits (TV only)
            agg_credits = extras.get('aggregate_credits', {})
            if agg_credits:
                agg_cast_list = agg_credits.get('cast', [])
                ctx['aggregateCast'] = {i+1: c for i, c in enumerate(agg_cast_list)}
                ctx['aggCastCount'] = len(agg_cast_list)
            
            # Images - FULL LISTS
            images = extras.get('images', {})
            if images:
                posters_list = images.get('posters', [])
                backdrops_list = images.get('backdrops', [])
                stills_list = images.get('stills', [])
                
                ctx['posters'] = {i+1: p for i, p in enumerate(posters_list)}
                ctx['backdrops'] = {i+1: b for i, b in enumerate(backdrops_list)}
                ctx['stills'] = {i+1: s for i, s in enumerate(stills_list)}
                
                ctx['postersCount'] = len(posters_list)
                ctx['backdropsCount'] = len(backdrops_list)
                ctx['stillsCount'] = len(stills_list)
            
            # Videos - FULL LISTS
            videos = extras.get('videos', {})
            if videos:
                trailers_list = videos.get('trailers', [])
                teasers_list = videos.get('teasers', [])
                clips_list = videos.get('clips', [])
                
                ctx['trailers'] = {i+1: t for i, t in enumerate(trailers_list)}
                ctx['teasers'] = {i+1: t for i, t in enumerate(teasers_list)}
                ctx['clips'] = {i+1: c for i, c in enumerate(clips_list)}
                
                ctx['trailersCount'] = len(trailers_list)
                ctx['teasersCount'] = len(teasers_list)
                ctx['clipsCount'] = len(clips_list)
            
            # Keywords - FULL LIST
            keywords = extras.get('keywords', [])
            if keywords:
                ctx['keywords'] = {i+1: k for i, k in enumerate(keywords)}
                ctx['keywordsCount'] = len(keywords)
                # Handle both dict and string keywords
                if keywords and isinstance(keywords[0], dict):
                    ctx['topKeywords'] = ', '.join([k.get('name', '') for k in keywords[:5]])
                else:
                    ctx['topKeywords'] = ', '.join([str(k) for k in keywords[:5]])
            
            # External IDs
            external_ids = extras.get('external_ids', {})
            if external_ids:
                ctx['imdbId'] = external_ids.get('imdb_id', '')
                ctx['tvdbId'] = external_ids.get('tvdb_id', '')
                ctx['facebookId'] = external_ids.get('facebook_id', '')
                ctx['instagramId'] = external_ids.get('instagram_id', '')
                ctx['twitterId'] = external_ids.get('twitter_id', '')
            
            # Content Ratings - FULL LIST
            content_ratings = extras.get('content_ratings', [])
            if content_ratings:
                ctx['contentRatings'] = {i+1: r for i, r in enumerate(content_ratings)}
                ctx['contentRatingsCount'] = len(content_ratings)
                # US rating - handle both dict and string
                if content_ratings and isinstance(content_ratings[0], dict):
                    us_rating = next((r.get('rating', '') for r in content_ratings if r.get('iso_3166_1') == 'US'), '')
                else:
                    us_rating = str(content_ratings[0]) if content_ratings else ''
                ctx['contentRatingUS'] = us_rating
            
            # Watch Providers
            watch_providers = extras.get('watch_providers', {})
            if watch_providers:
                flatrate = watch_providers.get('flatrate', [])
                rent = watch_providers.get('rent', [])
                buy = watch_providers.get('buy', [])
                
                ctx['watchProviders'] = {
                    'flatrate': {i+1: p for i, p in enumerate(flatrate)},
                    'rent': {i+1: p for i, p in enumerate(rent)},
                    'buy': {i+1: p for i, p in enumerate(buy)},
                }
                ctx['watchProvidersCount'] = len(flatrate)
    except Exception:
        # Silently ignore extras processing errors - extras are optional
        pass
    
    if media_type == "movie":
        # Movie aliases
        ctx['name'] = api_data.get('title', api_data.get('original_title', ''))
        ctx['movieAirDate'] = api_data.get('release_date', '')
        
        # Year
        release_date = api_data.get('release_date', '')
        year_match = re.match(r'(\d{4})', release_date)
        ctx['movieYear'] = year_match.group(1) if year_match else ''
        
        if ctx['movieYear']:
            ctx['yearBucket'] = _year_bucket(int(ctx['movieYear']))
        else:
            ctx['yearBucket'] = ''
    
    elif media_type == "tv":
        # TV aliases
        ctx['showName'] = api_data.get('name', api_data.get('original_name', ''))
        ctx['firstAirDate'] = api_data.get('first_air_date', '')
        
        # Note: episodeName is set by query_logger from ep_full, don't override here
        
        # Year
        first_air = api_data.get('first_air_date', '')
        year_match = re.match(r'(\d{4})', first_air)
        year = year_match.group(1) if year_match else ''
        
        if year:
            ctx['yearBucket'] = _year_bucket(int(year))
        else:
            ctx['yearBucket'] = ''
    
    return ctx


# --- HELPER FUNCTIONS ---

def _human_size(bytes_val: int) -> str:
    """Bayt → okunur boyut (MiB/GiB)."""
    if bytes_val == 0:
        return "0 B"
    
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    i = 0
    val = float(bytes_val)
    
    while val >= 1024 and i < len(units) - 1:
        val /= 1024
        i += 1
    
    return f"{val:.2f} {units[i]}"


def _size_bucket(bytes_val: int) -> str:
    """Boyut kovaları."""
    gib = bytes_val / (1024**3)
    if gib < 1:
        return "0-1 GiB"
    elif gib < 5:
        return "1-5 GiB"
    elif gib < 10:
        return "5-10 GiB"
    else:
        return ">10 GiB"


def _bitrate_bucket(bps: int) -> str:
    """Bitrate kovaları (Mbps)."""
    mbps = bps / 1_000_000
    if mbps < 2:
        return "<2"
    elif mbps < 5:
        return "2-5"
    elif mbps < 10:
        return "5-10"
    else:
        return ">10"


def _year_bucket(year: int) -> str:
    """Yıl kovaları."""
    if year <= 2000:
        return "<=2000"
    elif year <= 2010:
        return "2001-2010"
    elif year <= 2020:
        return "2011-2020"
    else:
        return ">=2021"


def _fps_bucket(fps: float) -> str:
    """FPS kovaları."""
    if fps <= 24:
        return "<=24"
    elif fps <= 30:
        return "25-30"
    else:
        return ">30"


def _parse_fps(fps_str: str) -> float:
    """FPS string → float (örn: "24000/1001" → 23.976)."""
    try:
        if '/' in fps_str:
            num, den = fps_str.split('/')
            return float(num) / float(den)
        return float(fps_str)
    except:
        return 0.0


def _seconds_to_hms(seconds: float) -> str:
    """Saniye → HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _detect_hdr(stream: Dict[str, Any]) -> str:
    """HDR format tespiti (heuristic)."""
    color_transfer = stream.get('color_transfer', '').lower()
    color_primaries = stream.get('color_primaries', '').lower()
    side_data = stream.get('side_data_list', [])
    
    # Dolby Vision check
    for sd in side_data:
        if 'dovi' in sd.get('side_data_type', '').lower():
            return "DolbyVision"
    
    # HDR10+ check (TODO: more precise check)
    if 'smpte2094' in color_transfer:
        return "HDR10+"
    
    # HLG check
    if 'arib-std-b67' in color_transfer or 'hlg' in color_transfer:
        return "HLG"
    
    # HDR10 check
    if ('smpte2084' in color_transfer or 'pq' in color_transfer) and 'bt2020' in color_primaries:
        return "HDR10"
    
    return ""
