# integrations/tvdb/client.py
"""
TVDb API v4 Client - Movies + TV Shows support.
"""
from __future__ import annotations
import requests
from typing import List, Dict, Any, Optional
from archiverr.core.matcher.api_normalizer import make_tv, make_season, make_episode, make_movie
from archiverr.integrations.tvdb.extras import TVDbExtras
from archiverr.utils.structured_logger import get_logger

TVDB_BASE = "https://api4.thetvdb.com/v4"

class TVDbClient:
    def __init__(self, api_key: str, timeout: int = 15, extras_config: Optional[Dict[str, bool]] = None):
        """
        Args:
            api_key: TVDb API key
            timeout: Request timeout in seconds
            extras_config: Global extras configuration dict
        """
        if not api_key:
            raise RuntimeError("TVDb API key required")
        self.api_key = api_key
        self.timeout = timeout
        self.token: Optional[str] = None
        self.logger = get_logger()
        
        # Global extras config (passed from main config)
        self.extras_config = extras_config or {}
        
        # Initialize extras client
        self.extras = TVDbExtras(api_key, timeout=timeout)
        
        self._authenticate()

    def _authenticate(self) -> None:
        url = f"{TVDB_BASE}/login"
        resp = requests.post(url, json={"apikey": self.api_key}, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        token = (data or {}).get("data", {}).get("token")
        if not token:
            raise RuntimeError("TVDb authentication failed: no token in response")
        self.token = token

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError("TVDb token missing; call _authenticate()")
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Accept-Language": "eng"
        }

    def _get(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = f"{TVDB_BASE}/{endpoint.lstrip('/')}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        if resp.status_code == 401:
            self._authenticate()
            resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data.get("status") == "failure":
            raise RuntimeError(f"TVDb API error: {data.get('message', 'unknown error')}")
        return data

    # -------- MOVIE --------
    def search_movie(self, title: str, year: Optional[int] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"query": title, "type": "movie"}
        if year: params["year"] = year
        data = self._get("search", params)
        out: List[Dict[str, Any]] = []
        for it in (data.get("data") or [])[:max_results]:
            if it.get("type") != "movie":
                continue
            out.append(make_movie(
                ids={"tvdb": it.get("tvdb_id")},
                title=it.get("name"),
                original_title=it.get("name"),
                release_date=it.get("firstRelease") or it.get("releaseDate"),
                overview=it.get("overview")
            ))
        return out

    def movie_details(self, movie_id: int) -> Dict[str, Any]:
        raw = self._get(f"movies/{movie_id}").get("data", {}) or {}
        # Some fields require /movies/{id}/extended, keeping basic to avoid extra roundtrips here
        return make_movie(
            ids={"tvdb": str(raw.get("id"))},
            title=raw.get("name"),
            original_title=raw.get("name"),
            overview=raw.get("overview"),
            release_date=raw.get("firstRelease") or raw.get("releaseDate"),
            runtime=(raw.get("runtime")),
            genres=[g.get("name") for g in (raw.get("genres") or []) if g.get("name")],
            poster=(raw.get("image") or raw.get("poster")),
            external_urls=None
        )

    # -------- TV --------
    def search_tv(self, title: str, first_air_year: Optional[int] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"query": title, "type": "series"}
        if first_air_year: params["year"] = first_air_year
        data = self._get("search", params)
        out: List[Dict[str, Any]] = []
        for it in (data.get("data") or [])[:max_results]:
            if it.get("type") != "series":
                continue
            out.append(make_tv(
                ids={"tvdb": it.get("tvdb_id")},
                name=it.get("name"),
                original_name=it.get("name"),
                first_air_date=it.get("firstAired") or None,
                overview=it.get("overview") or None
            ))
        return out

    def get_series_details(self, series_id: int) -> Dict[str, Any]:
        data = self._get(f"series/{series_id}/extended").get("data", {}) or {}
        
        # Filter only official seasons (exclude specials with type != official)
        all_seasons = data.get("seasons") or []
        official_seasons = []
        for s in all_seasons:
            s_type = s.get("type", {})
            # Check if type.type == "official" or if it's a numbered season > 0
            is_official = False
            if isinstance(s_type, dict):
                if s_type.get("type") == "official" or s_type.get("name") == "Aired Order":
                    is_official = True
            elif s.get("number", 0) > 0:
                is_official = True
            if not is_official:
                continue
            season_entry = {"season_number": s.get("number"), "episode_count": 0}
            # If season id exists, fetch extended to count episodes reliably
            sid = s.get("id")
            if sid:
                try:
                    season_ext = self._get(f"seasons/{sid}/extended").get("data", {}) or {}
                    eps = season_ext.get("episodes") or []
                    season_entry["episode_count"] = len(eps)
                except Exception:
                    season_entry["episode_count"] = s.get("episodesCount", 0) or 0
            else:
                season_entry["episode_count"] = s.get("episodesCount", 0) or 0
            official_seasons.append(season_entry)
        
        # Extract genres
        genres = [g.get("name") for g in (data.get("genres") or []) if g.get("name")]
        
        # Extract networks from companies (originalNetwork or network type)
        networks = []
        companies = data.get("companies") or []
        for company in companies:
            if isinstance(company, dict):
                comp_type = company.get("companyType", {})
                if isinstance(comp_type, dict) and comp_type.get("companyTypeName") in ["Network", "Original Broadcaster"]:
                    networks.append(company.get("name"))
        
        # Fallback to originalNetwork field if available
        if not networks and data.get("originalNetwork"):
            networks.append(data.get("originalNetwork"))
        
        # Extract status string from object if needed
        status_obj = data.get("status")
        if isinstance(status_obj, dict):
            status_str = status_obj.get("name", "")
        else:
            status_str = str(status_obj) if status_obj else ""
        
        # TVDb doesn't provide ratings in series endpoint, skip it
        ratings = None
        
        return make_tv(
            ids={"tvdb": str(data.get("id"))},
            name=data.get("name"),
            original_name=data.get("nativeName") or data.get("name"),
            overview=data.get("overview"),
            first_air_date=data.get("firstAired"),
            last_air_date=data.get("lastAired"),
            status=status_str,
            in_production=(status_str == "Continuing"),
            poster=(data.get("image") or data.get("poster")),
            seasons=official_seasons or None,
            genres=genres or None,
            networks=networks or None,
            ratings=ratings
        )

    def _resolve_season_id(self, series_id: int, season_number: int) -> Optional[int]:
        # Use extended endpoint to get seasons (same as get_series_details)
        self.logger.debug(
            "client.resolve_season",
            client="tvdb",
            series_id=series_id,
            season=season_number,
            message=f"Resolving season ID for S{season_number}"
        )
        try:
            data = self._get(f"series/{series_id}/extended").get("data", {}) or {}
            seasons = data.get("seasons") or []
            self.logger.debug(
                "client.seasons_found",
                client="tvdb",
                count=len(seasons),
                message=f"Found {len(seasons)} seasons in extended data"
            )
        except Exception as e:
            self.logger.error(
                "client.extended_failed",
                client="tvdb",
                error=str(e),
                message=f"Failed to get extended data: {e}"
            )
            return None
        
        # First pass: prefer official/aired order seasons
        for s in seasons:
            if s.get("number") == season_number:
                s_type = s.get("type", {})
                if isinstance(s_type, dict):
                    type_name = s_type.get("type") or s_type.get("name", "")
                    if type_name in ["official", "Aired Order", "aired"]:
                        self.logger.debug(
                            "client.season_resolved",
                            client="tvdb",
                            season=season_number,
                            season_id=s.get("id"),
                            type=type_name,
                            message=f"✓ Season {season_number} is official"
                        )
                        return s.get("id")
                else:
                    self.logger.debug(
                        "client.season_resolved",
                        client="tvdb",
                        season=season_number,
                        season_id=s.get("id"),
                        message=f"✓ Season {season_number} has no type info"
                    )
                    return s.get("id")
        
        # Second pass: return any season with matching number
        for s in seasons:
            if s.get("number") == season_number:
                self.logger.debug(
                    "client.season_fallback",
                    client="tvdb",
                    season=season_number,
                    season_id=s.get("id"),
                    message=f"✓ Fallback: Using season {season_number}"
                )
                return s.get("id")
        
        self.logger.warn(
            "client.season_not_found",
            client="tvdb",
            season=season_number,
            message=f"✗ Season {season_number} not found in extended data"
        )
        return None

    def get_season_episodes(self, series_id: int, season: int) -> Dict[str, Any]:
        season_id = self._resolve_season_id(series_id, season)
        if not season_id:
            return make_season(ids={"tvdb": None}, season_number=season)
        data = self._get(f"seasons/{season_id}/extended").get("data", {}) or {}
        episodes = []
        for ep in (data.get("episodes") or []):
            episodes.append(make_episode(
                ids={"tvdb": str(ep.get("id"))},
                season_number=ep.get("seasonNumber"),
                episode_number=ep.get("number"),
                name=ep.get("name"),
                overview=ep.get("overview"),
                air_date=ep.get("aired"),
                runtime=ep.get("runtime"),
                still=ep.get("image"),
            ))
        return make_season(ids={"tvdb": str(season_id)}, season_number=season, episodes=episodes or None)

    def get_episode(self, series_id: int, season: int, episode: int) -> Optional[Dict[str, Any]]:
        self.logger.debug(
            "client.get_episode",
            client="tvdb",
            series_id=series_id,
            season=season,
            episode=episode,
            message=f"Fetching episode S{season}E{episode}"
        )
        season_payload = self.get_season_episodes(series_id, season)
        episodes = season_payload.get("episodes") or []
        self.logger.debug(
            "client.episodes_fetched",
            client="tvdb",
            count=len(episodes),
            message=f"Season has {len(episodes)} episodes"
        )
        for ep in episodes:
            ep_num = ep.get("episode_number")
            if ep_num == episode:
                self.logger.debug(
                    "client.episode_found",
                    client="tvdb",
                    season=season,
                    episode=episode,
                    name=ep.get("name"),
                    message=f"✓ Found episode: {ep.get('name')}"
                )
                return ep
        self.logger.warn(
            "client.episode_not_found",
            client="tvdb",
            season=season,
            episode=episode,
            total_episodes=len(episodes),
            message=f"✗ Episode S{season}E{episode} not found"
        )
        return None
    
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
        Fetch extra metadata based on global config.
        
        TVDb has limited extra endpoints compared to TMDb.
        Most data is in /extended endpoint already.
        
        Args:
            item_type: 'movie', 'tv', 'season', 'episode'
            item_id: TVDb series/movie ID
            season: Season number (for season/episode)
            episode: Episode number (for episode)
            override_config: Override config extras (for CLI manual fetch)
        
        Returns:
            Dict with extras data
        """
        config = override_config if override_config is not None else self.extras_config
        extras_data = {}
        
        # TVDb doesn't support movie extras in the same way
        # Most movie data is in the main endpoint
        
        if item_type == 'tv':
            # TV series extras
            if config.get('tv_credits'):
                credits = self.extras.tv_credits(item_id)
                if credits:
                    extras_data['credits'] = credits
            
            if config.get('tv_images'):
                images = self.extras.tv_images(item_id)
                if images:
                    extras_data['images'] = images
            
            if config.get('tv_external_ids'):
                external_ids = self.extras.tv_external_ids(item_id)
                if external_ids:
                    extras_data['external_ids'] = external_ids
            
            if config.get('tv_content_ratings'):
                content_ratings = self.extras.tv_content_ratings(item_id)
                if content_ratings:
                    extras_data['content_ratings'] = content_ratings
            
            # Note: TVDb doesn't have separate endpoints for:
            # - videos - not available
            # - keywords - not available
            # - watch_providers - not available
        
        elif item_type == 'episode' and season is not None and episode is not None:
            # Episode extras
            if config.get('episode_images'):
                images = self.extras.episode_images(item_id, season, episode)
                if images:
                    extras_data['images'] = images
            
            # Note: TVDb episode images are included in episode details
            # No separate videos, credits endpoints for episodes
        
        # Season and movie extras not well-supported by TVDb API v4
        
        return extras_data if extras_data else None
