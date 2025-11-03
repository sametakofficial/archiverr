# core/matcher/matcher.py
"""Matching logic - movie and TV show matching with multi-API support"""
from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, Any
from utils.structured_logger import get_logger

def match_movie(path: str, api_manager, config) -> Dict[str, Any]:
    """
    Match movie file using API Manager with priority fallback.
    
    Args:
        path: File path
        api_manager: APIManager instance
        config: AppConfig instance
    
    Returns:
        {
            "path": str,
            "parsed": {"parsed_title": str, "parsed_year": int | None},
            "best": dict | None (normalized by API client),
            "api_source": str,
            "took": float
        }
    """
    from utils.parser import parse_movie_name
    
    raw = Path(path).stem
    title, year, ignore = parse_movie_name(
        raw,
        config.scanner.delete_keywords,
        config.scanner.exclude_unparsed
    )
    
    t0 = time.time()
    
    # Search with fallback (already normalized by clients)
    results, api_source = api_manager.search_movie(title, year=year, max_results=3)
    best = results[0] if results else None
    
    took = time.time() - t0
    
    return {
        "path": path,
        "parsed": {
            "parsed_title": title,
            "parsed_year": year
        },
        "best": best,  # Already normalized by client
        "api_source": api_source,
        "took": took
    }


def match_tv(path: str, api_manager, config) -> Dict[str, Any]:
    """
    Match TV show file using API Manager with priority fallback.
    
    Args:
        path: File path
        api_manager: APIManager instance
        config: AppConfig instance
    
    Returns:
        {
            "path": str,
            "parsed": {"parsed_show": str, "parsed_season": int, "parsed_episode": int},
            "best": dict | None (normalized by API client),
            "ep_full": dict | None (normalized episode by API client),
            "api_source": str,
            "took": float
        }
    """
    from utils.parser import parse_episode_name
    
    raw = Path(path).stem
    show, season, episode, ignore = parse_episode_name(
        raw,
        config.scanner.delete_keywords,
        config.scanner.exclude_unparsed
    )
    
    t0 = time.time()
    
    # Search with fallback (already normalized by clients)
    results, api_source = api_manager.search_tv(show, first_air_year=None, max_results=3)
    best = results[0] if results else None
    
    # NOTE: Extra series details (seasons, networks, credits, etc.) will be fetched
    # later as optional metadata. For now, we only have search result + episode details.
    
    took = time.time() - t0
    
    # Fetch episode details if show matched
    logger = get_logger()
    ep_full = None
    if best and season and episode:
        logger.debug(
            "matcher.fetch_episode",
            season=season,
            episode=episode,
            api=api_source,
            message=f"Fetching episode S{season}E{episode} from {api_source}"
        )
        # Extract ID from normalized response (generic approach)
        series_id = None
        if best.get('ids'):
            ids = best['ids']
            # Try to match api_source key first
            if api_source in ids:
                series_id = ids[api_source]
                try:
                    series_id = int(series_id)
                except (ValueError, TypeError):
                    pass  # Keep as string if not convertible
            # Fallback: use first available ID
            elif ids:
                series_id = list(ids.values())[0]
                try:
                    series_id = int(series_id)
                except (ValueError, TypeError):
                    pass
            logger.debug(
                "matcher.series_id",
                series_id=series_id,
                ids=ids,
                message=f"Extracted series_id: {series_id}"
            )
        
        if series_id:
            ep_full = api_manager.get_episode_details(series_id, season, episode, api_source)
            if ep_full:
                logger.debug(
                    "matcher.episode_found",
                    name=ep_full.get('name'),
                    message=f"✓ Episode found: {ep_full.get('name')}"
                )
            else:
                logger.debug(
                    "matcher.episode_not_found",
                    message="✗ Episode not found"
                )
            
            # Fetch extras for TV series (not episode-specific for now)
            try:
                logger.debug(
                    "matcher.fetch_extras",
                    api=api_source,
                    item_type="tv",
                    message=f"Fetching extras from {api_source}"
                )
                extras = api_manager.fetch_extras('tv', series_id, api_source)
                if extras:
                    logger.debug(
                        "matcher.extras_found",
                        api=api_source,
                        keys=list(extras.keys()),
                        message=f"✓ Extras fetched: {', '.join(extras.keys())}"
                    )
                    # Merge extras into best result
                    if best:
                        best['extras'] = extras
                else:
                    logger.debug(
                        "matcher.no_extras",
                        api=api_source,
                        message="No extras fetched (none enabled or supported)"
                    )
            except Exception as e:
                logger.warn(
                    "matcher.extras_failed",
                    api=api_source,
                    error=str(e),
                    message=f"Failed to fetch extras: {e}"
                )
        else:
            logger.warn(
                "matcher.no_series_id",
                message="✗ No series_id found in best result"
            )
    
    return {
        "path": path,
        "parsed": {
            "parsed_show": show,
            "parsed_season": season,
            "parsed_episode": episode
        },
        "best": best,  # Already normalized by client
        "ep_full": ep_full,  # Already normalized by client
        "api_source": api_source,
        "took": took
    }
