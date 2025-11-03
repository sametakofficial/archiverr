# integrations/tvmaze/client.py
from __future__ import annotations
import requests
from typing import List, Dict, Any, Optional
from core.matcher.api_normalizer import make_tv, make_season, make_episode
from integrations.tvmaze.extras import TVMazeExtras

TVMAZE_BASE = 'https://api.tvmaze.com'

class TVMazeClient:
    def __init__(self, api_key: Optional[str] = None, extras_config: Optional[Dict[str, bool]] = None):
        """
        Args:
            api_key: Not used (TVMaze is public API)
            extras_config: Global extras configuration dict
        """
        # Global extras config (passed from main config)
        self.extras_config = extras_config or {}
        
        # Initialize extras client
        self.extras = TVMazeExtras()
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = TVMAZE_BASE + path
        r = requests.get(url, params=params or {}, timeout=15)
        r.raise_for_status()
        return r.json()
    
    def search_tv(self, title: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results = self._get('/search/shows', {'q': title})[:max_results]
        out: List[Dict[str, Any]] = []
        for item in results:
            show = item.get("show") or {}
            out.append(make_tv(
                ids={"tvmaze": str(show.get("id")), "imdb": (show.get("externals") or {}).get("imdb")},
                name=show.get("name"),
                original_name=show.get("name"),
                first_air_date=show.get("premiered"),
                overview=_strip_html(show.get("summary")) if show.get("summary") else None,
                poster=(show.get("image") or {}).get("original") or (show.get("image") or {}).get("medium")
            ))
        return out
    
    def get_show(self, show_id: int) -> Dict[str, Any]:
        show = self._get(f'/shows/{show_id}')
        return make_tv(
            ids={"tvmaze": str(show.get("id")), "imdb": (show.get("externals") or {}).get("imdb")},
            name=show.get("name"),
            original_name=show.get("name"),
            first_air_date=show.get("premiered"),
            overview=_strip_html(show.get("summary")) if show.get("summary") else None,
            poster=(show.get("image") or {}).get("original") or (show.get("image") or {}).get("medium"),
            external_urls={"tvmaze": show.get("url")}
        )
    
    def get_season(self, show_id: int, season: int) -> Dict[str, Any]:
        eps = self._get(f'/shows/{show_id}/episodes')
        selected = [e for e in eps if e.get("season")==season]
        mapped = []
        for e in selected:
            mapped.append(make_episode(
                ids={"tvmaze": str(e.get("id"))},
                season_number=e.get("season"),
                episode_number=e.get("number"),
                name=e.get("name"),
                overview=_strip_html(e.get("summary")) if e.get("summary") else None,
                air_date=e.get("airdate"),
                runtime=e.get("runtime"),
                still=(e.get("image") or {}).get("original") or (e.get("image") or {}).get("medium")
            ))
        return make_season(ids={"tvmaze": str(show_id)}, season_number=season, episodes=mapped or None)
    
    def get_episode_by_number(self, show_id: int, season: int, episode: int) -> Optional[Dict[str, Any]]:
        e = self._get(f'/shows/{show_id}/episodebynumber', {'season': season, 'number': episode})
        return make_episode(
            ids={"tvmaze": str(e.get("id"))},
            season_number=e.get("season"),
            episode_number=e.get("number"),
            name=e.get("name"),
            overview=_strip_html(e.get("summary")) if e.get("summary") else None,
            air_date=e.get("airdate"),
            runtime=e.get("runtime"),
            still=(e.get("image") or {}).get("original") or (e.get("image") or {}).get("medium"),
            external_urls={"tvmaze": e.get("url")}
        )
    
    # ========================================================================
    # EXTRAS FETCHER
    # ========================================================================
    
    def fetch_extras(
        self,
        item_type: str,  # 'movie', 'tv', 'season', 'episode'
        item_id: int,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        override_config: Optional[Dict[str, bool]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch extra metadata based on global config.
        
        TVMaze supports:
        - TV cast (/shows/{id}/cast)
        - TV crew (/shows/{id}/crew)
        - TV images (/shows/{id}/images)
        - Episode guest cast (embed)
        
        Args:
            item_type: 'movie', 'tv', 'season', 'episode'
            item_id: TVMaze show/episode ID
            season: Season number (not used by TVMaze)
            episode: Episode number (for episode guest cast)
            override_config: Override config extras (for CLI manual fetch)
        
        Returns:
            Dict with extras data
        """
        config = override_config if override_config is not None else self.extras_config
        extras_data = {}
        
        # TVMaze doesn't support movie extras
        
        if item_type == 'tv':
            # TV series extras
            if config.get('tv_credits'):
                # Combine cast and crew into credits
                cast_data = self.extras.tv_cast(item_id)
                crew_data = self.extras.tv_crew(item_id)
                
                extras_data['credits'] = {
                    'cast': cast_data.get('cast', []),
                    'crew': crew_data.get('crew', []),
                }
            
            if config.get('tv_images'):
                images = self.extras.tv_images(item_id)
                if images:
                    extras_data['images'] = images
            
            if config.get('tv_external_ids'):
                # TVMaze provides external IDs in main show endpoint
                try:
                    show = self._get(f'/shows/{item_id}')
                    externals = show.get('externals', {})
                    if externals:
                        extras_data['external_ids'] = {
                            'imdb_id': externals.get('imdb', ''),
                            'tvdb_id': str(externals.get('thetvdb', '')) if externals.get('thetvdb') else '',
                            'tvmaze_id': str(show.get('id', '')),
                            'tvrage_id': str(externals.get('tvrage', '')) if externals.get('tvrage') else ''
                        }
                except Exception:
                    pass
            
            # TVMaze doesn't have:
            # - videos
            # - keywords
            # - watch_providers
            # - aggregate_credits
            # - content_ratings
            # - content_ratings (only single rating field)
            
            # External IDs are in main response already
        
        elif item_type == 'episode' and episode is not None:
            # Episode extras
            if config.get('episode_credits'):
                # Guest cast
                guests = self.extras.episode_guest_cast(item_id)
                if guests:
                    extras_data['credits'] = {'guest_cast': guests}
            
            # Episode images not available as separate endpoint
        
        return extras_data if extras_data else None

def _strip_html(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s)
