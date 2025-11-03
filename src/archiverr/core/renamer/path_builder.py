# core/renamer/path_builder.py
"""Hedef path oluşturma - pattern rendering ile."""
import os
import re
from typing import Dict, Any, Tuple, Optional


def best_year(date_str: str) -> Optional[int]:
    """YYYY-MM-DD formatından yıl çıkar."""
    if not date_str:
        return None
    try:
        return int(date_str[:4])
    except:
        return None


def tmdb_link(item: Dict[str, Any], media_type: str) -> Optional[str]:
    """TMDb link oluştur."""
    _id = item.get('id')
    if not _id:
        return None
    return f"https://www.themoviedb.org/{'movie' if media_type=='movie' else 'tv'}/{_id}"


def pattern_needs_ffprobe(pattern: str) -> bool:
    """Pattern ffprobe verisi gerektiriyor mu?"""
    return bool(pattern and re.search(r"\{(video|audio|subs)\.", pattern))


def pattern_needs_episode_details(pattern: str) -> bool:
    """Pattern episode detayları gerektiriyor mu?"""
    return ("{episodeName}" in pattern) or bool(re.search(r"\{tmdb\.episode\.", pattern))


def build_movie_path(config, movie_tmdb: Dict[str, Any], ffenv: Dict[str, Any], 
                     render_func) -> Tuple[str, str]:
    """
    Film için hedef path oluştur.
    
    Args:
        config: AppConfig
        movie_tmdb: TMDb movie details
        ffenv: FFprobe parsed data
        render_func: Pattern render fonksiyonu
    
    Returns:
        (parent_dir, filename) tuple
    """
    name = movie_tmdb.get("title") or movie_tmdb.get("original_title")
    year = best_year(movie_tmdb.get("release_date") or "")
    
    # Environment oluştur
    env = {
        "name": name,
        "movieYear": year,
        "tmdb": movie_tmdb,
        "video": ffenv.get("video", {}),
        "audio": ffenv.get("audio", []),
        "audio_count": ffenv.get("audio_count", 0),
        "subs": ffenv.get("subs", {"count": 0, "languages": []}),
    }
    
    # Query config'den pattern al (yeni sistem) veya fallback legacy
    query_cfg = config.rename.movies or {}
    pattern = query_cfg.get('save', config.rename.movie_pattern or '').strip()
    
    if not pattern:
        # Fallback pattern
        base = f"{name} ({year})" if year else str(name)
        return config.rename.movies_dst or ".", base
    
    # Pattern render
    rel = render_func(pattern, env)
    parent, fname = os.path.split(rel)
    root = config.rename.movies_dst or ""
    
    return os.path.join(root, parent), fname


def build_tv_path(config, show_tmdb: Dict[str, Any], ep_tmdb: Optional[Dict[str, Any]],
                  parsed: Dict[str, Any], ffenv: Dict[str, Any], render_func) -> Tuple[str, str]:
    """
    Dizi için hedef path oluştur.
    
    Args:
        config: AppConfig
        show_tmdb: TMDb show details
        ep_tmdb: TMDb episode details (optional)
        parsed: Parsed info (season, episode)
        ffenv: FFprobe parsed data
        render_func: Pattern render fonksiyonu
    
    Returns:
        (parent_dir, filename) tuple
    """
    show_name = show_tmdb.get("name") or show_tmdb.get("original_name") or parsed.get("parsed_show")
    season = parsed.get("parsed_season")
    episode = parsed.get("parsed_episode")
    first_air = show_tmdb.get("first_air_date") or ""
    
    # Environment oluştur
    env = {
        "showName": show_name,
        "seasonNumber": season,  # Integer olarak - filter'da pad yapılacak
        "episodeNumber": episode,  # Integer olarak - filter'da pad yapılacak
        "episodeName": (ep_tmdb or {}).get("name") or "",
        "year": best_year(first_air),
        "tmdb": dict(show_tmdb, episode=ep_tmdb or {}, first_air_date=first_air),
        "video": ffenv.get("video", {}),
        "audio": ffenv.get("audio", []),
        "audio_count": ffenv.get("audio_count", 0),
        "subs": ffenv.get("subs", {"count": 0, "languages": []}),
    }
    
    # Query config'den pattern al (yeni sistem) veya fallback legacy
    query_cfg = config.rename.series or {}
    pattern = query_cfg.get('save', config.rename.series_pattern or '').strip()
    
    if not pattern:
        # Fallback pattern
        base = f"{show_name} - S{season:02d}E{episode:02d}"
        return config.rename.series_dst or ".", base
    
    # Pattern render
    rel = render_func(pattern, env)
    parent, fname = os.path.split(rel)
    root = config.rename.series_dst or ""
    
    return os.path.join(root, parent), fname
