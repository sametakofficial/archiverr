# integrations/tmdb/client.py
from __future__ import annotations
import requests
from typing import Any, Dict, List, Optional
from core.matcher.api_normalizer import make_tv, make_season, make_episode, make_movie
from integrations.tmdb.extras import TMDbExtras

TMDB_BASE = 'https://api.themoviedb.org/3'
IMG = 'https://image.tmdb.org/t/p'

class TMDbClient:
    def __init__(self, api_key: str, region: str = 'US', extras_config: Optional[Dict[str, bool]] = None):
        """
        Args:
            api_key: TMDb API key
            region: Region code for watch providers (e.g., 'US', 'TR')
            extras_config: Global extras configuration dict
        """
        if not api_key:
            raise RuntimeError('TMDB API key required')
        self.api_key = api_key
        self.region = region
        
        # Initialize extras client
        self.extras = TMDbExtras(api_key)
        
        # Global extras config (passed from main config)
        self.extras_config = extras_config or {}

    def _get(self, path: str, params: dict):
        params = dict(params or {})
        params['api_key'] = self.api_key
        url = TMDB_BASE + path
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    # -------- MOVIE --------
    def search_movie(self, title: str, year: int = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {'query': title, 'page': 1, 'include_adult': False}
        if year: params['year'] = year
        data = self._get('/search/movie', params)
        out = []
        for it in data.get('results', [])[:max_results]:
            out.append(make_movie(
                ids={"tmdb": str(it.get("id"))},
                title=it.get("title"),
                original_title=it.get("original_title"),
                overview=it.get("overview"),
                release_date=it.get("release_date"),
                poster=f"{IMG}/w342{it['poster_path']}" if it.get("poster_path") else None,
                backdrop=f"{IMG}/w780{it['backdrop_path']}" if it.get("backdrop_path") else None,
                ratings={"tmdb": {"vote_average": it.get("vote_average"), "vote_count": it.get("vote_count")}}
            ))
        return out

    def movie_details(self, movie_id: int) -> Dict[str, Any]:
        raw = self._get(f'/movie/{movie_id}', {'append_to_response': 'credits,external_ids,images,releases'})
        return make_movie(
            ids={"tmdb": str(raw.get("id")), "imdb": (raw.get("external_ids") or {}).get("imdb_id")},
            title=raw.get("title"),
            original_title=raw.get("original_title"),
            overview=raw.get("overview"),
            release_date=raw.get("release_date"),
            runtime=raw.get("runtime"),
            genres=[g.get("name") for g in (raw.get("genres") or []) if g.get("name")],
            spoken_languages=[l.get("iso_639_1") for l in (raw.get("spoken_languages") or []) if l.get("iso_639_1")],
            original_language=raw.get("original_language"),
            production_companies=[c.get("name") for c in (raw.get("production_companies") or []) if c.get("name")],
            homepage=raw.get("homepage"),
            poster=f"{IMG}/w500{raw['poster_path']}" if raw.get("poster_path") else None,
            backdrop=f"{IMG}/w1280{raw['backdrop_path']}" if raw.get("backdrop_path") else None,
            images={
                "posters": [{"url": f"{IMG}/original{p['file_path']}", "width": p.get("width"), "height": p.get("height")} for p in (raw.get("images") or {}).get("posters", [])],
                "backdrops": [{"url": f"{IMG}/original{b['file_path']}", "width": b.get("width"), "height": b.get("height")} for b in (raw.get("images") or {}).get("backdrops", [])],
            },
            ratings={"tmdb": {"vote_average": raw.get("vote_average"), "vote_count": raw.get("vote_count")}},
            external_urls={
                "tmdb": f"https://www.themoviedb.org/movie/{raw.get('id')}",
                "imdb": f"https://www.imdb.com/title/{(raw.get('external_ids') or {}).get('imdb_id')}/" if (raw.get("external_ids") or {}).get("imdb_id") else None
            },
            credits={
                "cast": [{"name": c.get("name"), "character": c.get("character"), "order": c.get("order")} for c in (raw.get("credits") or {}).get("cast", [])],
                "crew": [{"name": c.get("name"), "job": c.get("job"), "department": c.get("department")} for c in (raw.get("credits") or {}).get("crew", [])],
            }
        )

    # -------- TV --------
    def search_tv(self, title: str, first_air_year: int = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {'query': title, 'page': 1}
        if first_air_year: params['first_air_date_year'] = first_air_year
        data = self._get('/search/tv', params)
        out: List[Dict[str, Any]] = []
        for it in data.get('results', [])[:max_results]:
            out.append(make_tv(
                ids={"tmdb": str(it.get("id"))},
                name=it.get("name"),
                original_name=it.get("original_name"),
                overview=it.get("overview"),
                first_air_date=it.get("first_air_date"),
                poster=f"{IMG}/w342{it['poster_path']}" if it.get("poster_path") else None,
                ratings={"tmdb": {"vote_average": it.get("vote_average"), "vote_count": it.get("vote_count")}}
            ))
        return out

    def tv_details(self, tv_id: int) -> Dict[str, Any]:
        raw = self._get(f'/tv/{tv_id}', {'append_to_response': 'aggregate_credits,content_ratings,external_ids,images'})
        return make_tv(
            ids={"tmdb": str(raw.get("id")), "imdb": (raw.get("external_ids") or {}).get("imdb_id")},
            name=raw.get("name"),
            original_name=raw.get("original_name"),
            overview=raw.get("overview"),
            first_air_date=raw.get("first_air_date"),
            last_air_date=raw.get("last_air_date"),
            status=raw.get("status"),
            in_production=raw.get("in_production"),
            episode_run_time=raw.get("episode_run_time"),
            genres=[g.get("name") for g in (raw.get("genres") or []) if g.get("name")],
            poster=f"{IMG}/w500{raw['poster_path']}" if raw.get("poster_path") else None,
            backdrop=f"{IMG}/w1280{raw['backdrop_path']}" if raw.get("backdrop_path") else None,
            seasons=[{"season_number": s.get("season_number"), "episode_count": s.get("episode_count")} for s in (raw.get("seasons") or [])],
            ratings={"tmdb": {"vote_average": raw.get("vote_average"), "vote_count": raw.get("vote_count")}},
            external_urls={"tmdb": f"https://www.themoviedb.org/tv/{raw.get('id')}"}
        )

    def tv_season(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        raw = self._get(f'/tv/{tv_id}/season/{season_number}', {'append_to_response': 'images,credits,external_ids'})
        episodes = []
        for e in (raw.get("episodes") or []):
            episodes.append(make_episode(
                ids={"tmdb": str(e.get("id")), "imdb": e.get("imdb_id")},
                season_number=e.get("season_number"),
                episode_number=e.get("episode_number"),
                name=e.get("name"),
                overview=e.get("overview"),
                air_date=e.get("air_date"),
                runtime=e.get("runtime"),
                still=f"{IMG}/w780{e['still_path']}" if e.get("still_path") else None,
                ratings={"tmdb": {"vote_average": e.get("vote_average"), "vote_count": e.get("vote_count")}},
            ))
        return make_season(
            ids={"tmdb": str(raw.get("id"))},
            season_number=raw.get("season_number"),
            overview=raw.get("overview"),
            air_date=raw.get("air_date"),
            poster=f"{IMG}/w342{raw['poster_path']}" if raw.get("poster_path") else None,
            episodes=episodes or None
        )

    def tv_episode(self, tv_id: int, season_number: int, episode_number: int) -> Dict[str, Any]:
        raw = self._get(f'/tv/{tv_id}/season/{season_number}/episode/{episode_number}', {'append_to_response': 'credits,external_ids,images'})
        return make_episode(
            ids={"tmdb": str(raw.get("id")), "imdb": raw.get("imdb_id")},
            season_number=raw.get("season_number"),
            episode_number=raw.get("episode_number"),
            name=raw.get("name"),
            overview=raw.get("overview"),
            air_date=raw.get("air_date"),
            runtime=raw.get("runtime"),
            still=f"{IMG}/w780{raw['still_path']}" if raw.get("still_path") else None,
            ratings={"tmdb": {"vote_average": raw.get("vote_average"), "vote_count": raw.get("vote_count")}},
            external_urls={"tmdb": f"https://www.themoviedb.org/tv/{tv_id}/season/{season_number}/episode/{episode_number}"}
        )

    # Compatibility alias
    def get_episode(self, tv_id: int, season: int, episode: int):
        return self.tv_episode(tv_id, season, episode)
    
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
    ) -> Dict[str, Any]:
        """
        Fetch extra metadata based on config.
        
        Args:
            item_type: 'movie', 'tv', 'season', 'episode'
            item_id: TMDb ID
            season: Season number (for season/episode)
            episode: Episode number (for episode)
            override_config: Override config extras (for CLI manual fetch)
        
        Returns:
            Dict with extras data
        """
        config = override_config if override_config is not None else self.extras_config
        extras_data = {}
        
        if item_type == 'movie':
            if config.get('movie_credits'):
                extras_data['credits'] = self.extras.movie_credits(item_id)
            if config.get('movie_images'):
                extras_data['images'] = self.extras.movie_images(item_id)
            if config.get('movie_videos'):
                extras_data['videos'] = self.extras.movie_videos(item_id)
            if config.get('movie_keywords'):
                extras_data['keywords'] = self.extras.movie_keywords(item_id)
            if config.get('movie_external_ids'):
                extras_data['external_ids'] = self.extras.movie_external_ids(item_id)
            if config.get('movie_watch_providers'):
                extras_data['watch_providers'] = self.extras.movie_watch_providers(item_id, self.region)
        
        elif item_type == 'tv':
            if config.get('tv_credits'):
                extras_data['credits'] = self.extras.tv_credits(item_id)
            if config.get('tv_aggregate_credits'):
                extras_data['aggregate_credits'] = self.extras.tv_aggregate_credits(item_id)
            if config.get('tv_images'):
                extras_data['images'] = self.extras.tv_images(item_id)
            if config.get('tv_videos'):
                extras_data['videos'] = self.extras.tv_videos(item_id)
            if config.get('tv_keywords'):
                extras_data['keywords'] = self.extras.tv_keywords(item_id)
            if config.get('tv_external_ids'):
                extras_data['external_ids'] = self.extras.tv_external_ids(item_id)
            if config.get('tv_content_ratings'):
                extras_data['content_ratings'] = self.extras.tv_content_ratings(item_id)
            if config.get('tv_watch_providers'):
                extras_data['watch_providers'] = self.extras.tv_watch_providers(item_id, self.region)
        
        elif item_type == 'season' and season is not None:
            if config.get('season_credits'):
                extras_data['credits'] = self.extras.season_credits(item_id, season)
            if config.get('season_images'):
                extras_data['images'] = self.extras.season_images(item_id, season)
            if config.get('season_videos'):
                extras_data['videos'] = self.extras.season_videos(item_id, season)
        
        elif item_type == 'episode' and season is not None and episode is not None:
            if config.get('episode_credits'):
                extras_data['credits'] = self.extras.episode_credits(item_id, season, episode)
            if config.get('episode_images'):
                extras_data['images'] = self.extras.episode_images(item_id, season, episode)
            if config.get('episode_videos'):
                extras_data['videos'] = self.extras.episode_videos(item_id, season, episode)
        
        return extras_data if extras_data else None
