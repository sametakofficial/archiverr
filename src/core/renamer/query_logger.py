# core/renamer/query_logger.py
"""Query-based logging system - config.yml'deki print formatlarını kullanır."""
from typing import Dict, Any, Optional
from pathlib import Path


def render_query_print(template: str, context: Dict[str, Any]) -> str:
    """
    Query print template'i render et.
    
    Önce variable_engine ile {var:filter} syntax'ı işle,
    sonra Python format string'leri için SafeFormatter kullan.
    
    Args:
        template: Print template (örn: "✓ {name} ({movieYear}) ({took:.2f}s)")
        context: Variable context
    
    Returns:
        Rendered string
    """
    # variable_engine'i import et (circular dependency önlemek için burada)
    from core.query_engine.variable_engine import render_template
    from string import Formatter
    
    # SafeFormatter: missing keys için empty string döndür
    class SafeFormatter(Formatter):
        def get_value(self, key, args, kwargs):
            if isinstance(key, str):
                return kwargs.get(key, '')
            return super().get_value(key, args, kwargs)
    
    # İlk önce variable_engine ile işle (filter'lar için)
    rendered = render_template(template, context)
    
    # Sonra Python format string'leri için SafeFormatter kullan
    # (took:.2f gibi format specifier'lar için)
    try:
        formatter = SafeFormatter()
        rendered = formatter.format(rendered, **context)
    except Exception:
        # Format hatası varsa orijinal string'i döndür
        pass
    
    return rendered


def build_print_context(
    best: Dict[str, Any],
    media_type: str,
    parsed: Dict[str, Any],
    ep_full: Optional[Dict[str, Any]] = None,
    took: float = 0.0,
    api_source: str = "tmdb"
) -> Dict[str, Any]:
    """
    Print template için context oluştur.
    
    Args:
        best: API match result
        media_type: "movie" | "tv"
        parsed: Parsed filename info
        ep_full: Episode details (TV için)
        took: İşlem süresi (saniye)
        api_source: Hangi API'den geldi (tmdb, tvmaze, tvdb, omdb)
    
    Returns:
        Context dict with flat + nested keys
    """
    ctx = {
        "took": took,  # İşlem süresi
        "apiSource": api_source,  # Hangi API kullanıldı
    }
    
    # Normalized common fields (all APIs provide these via normalizer)
    if media_type == "movie":
        ctx['title'] = best.get('title', '')
        ctx['originalTitle'] = best.get('original_title', '')
        ctx['year'] = _extract_year(best.get('release_date', ''))
        ctx['releaseDate'] = best.get('release_date', '')
        ctx['overview'] = best.get('overview', '')
        
        # Ratings (handle dict format)
        ratings = best.get('ratings', {})
        first_rating = list(ratings.values())[0] if ratings else {}
        ctx['voteAverage'] = first_rating.get('vote_average', 0.0) if isinstance(first_rating, dict) else 0.0
        ctx['voteCount'] = first_rating.get('vote_count', 0) if isinstance(first_rating, dict) else 0
        ctx['popularity'] = 0.0  # Not in new normalized format
        ctx['runtime'] = best.get('runtime', 0)
        ctx['imdbId'] = (best.get('ids') or {}).get('imdb', '')
        
        # Genres (list of strings in new format)
        genres = best.get('genres', [])
        ctx['genreName'] = genres[0] if genres and isinstance(genres[0], str) else ''
        
    else:  # TV
        ctx['showName'] = best.get('name', '')
        ctx['originalShowName'] = best.get('original_name', '')
        ctx['firstAirDate'] = best.get('first_air_date', '')
        ctx['lastAirDate'] = best.get('last_air_date', '')
        ctx['overview'] = best.get('overview', '')
        
        # Ratings (handle dict format)
        ratings = best.get('ratings', {})
        first_rating = list(ratings.values())[0] if ratings else {}
        ctx['voteAverage'] = first_rating.get('vote_average', 0.0) if isinstance(first_rating, dict) else 0.0
        ctx['voteCount'] = first_rating.get('vote_count', 0) if isinstance(first_rating, dict) else 0
        
        # Seasons info from seasons list
        seasons = best.get('seasons', [])
        ctx['numberOfSeasons'] = len([s for s in seasons if s.get('season_number', 0) > 0]) if seasons else 0
        ctx['numberOfEpisodes'] = sum(s.get('episode_count', 0) for s in seasons) if seasons else 0
        ctx['inProduction'] = best.get('in_production', False)
        # Handle status that might be a dict (TVDb returns object)
        status = best.get('status', '')
        if isinstance(status, dict):
            ctx['showType'] = status.get('name', '')
        else:
            ctx['showType'] = str(status)
        
        # Parsed from filename
        ctx['seasonNumber'] = parsed.get('parsed_season', 0)
        ctx['episodeNumber'] = parsed.get('parsed_episode', 0)
        
        # First air year
        ctx['firstAirYear'] = _extract_year(best.get('first_air_date', ''))
        
        # Networks (list of strings in new format)
        networks = best.get('networks', [])
        ctx['networkName'] = networks[0] if networks and isinstance(networks[0], str) else ''
        
        # Genres (list of strings in new format)
        genres = best.get('genres', [])
        ctx['genreName'] = genres[0] if genres and isinstance(genres[0], str) else ''
        
        # Episode details (normalized)
        if ep_full:
            ctx['episodeName'] = ep_full.get('name', '')
            ctx['episodeOverview'] = ep_full.get('overview', '')
            ctx['episodeAirDate'] = ep_full.get('air_date', '')
            ctx['episodeRuntime'] = ep_full.get('runtime', 0)
            
            # Episode ratings
            ep_ratings = ep_full.get('ratings', {})
            first_ep_rating = list(ep_ratings.values())[0] if ep_ratings else {}
            ctx['episodeVoteAverage'] = first_ep_rating.get('vote_average', 0.0) if isinstance(first_ep_rating, dict) else 0.0
            ctx['episodeVoteCount'] = first_ep_rating.get('vote_count', 0) if isinstance(first_ep_rating, dict) else 0
        else:
            ctx['episodeName'] = ''
            ctx['episodeOverview'] = ''
            ctx['episodeAirDate'] = ''
            ctx['episodeRuntime'] = 0
            ctx['episodeVoteAverage'] = 0.0
            ctx['episodeVoteCount'] = 0
    
    # Extras - use _build_api_vars to get all extras variables
    from core.query_engine.variables import _build_api_vars
    extras_vars = _build_api_vars(best, media_type, parsed)
    ctx.update(extras_vars)
    
    return ctx


def _extract_year(date_str: str) -> int:
    """Extract year from YYYY-MM-DD date string"""
    if not date_str:
        return 0
    try:
        return int(date_str[:4]) if len(date_str) >= 4 else 0
    except (ValueError, TypeError):
        return 0


def print_query_log(message: str, config):
    """Config'deki print template'ini kullanarak log bas."""
    # Renk ekle
    colored_msg = f"\033[32m{message}\033[0m"  # Green
    print(colored_msg)
