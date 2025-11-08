# plugins/tmdb/extras.py
"""
TMDb Extra Metadata Fetcher - Endpoint-Based System

Each method returns RAW API response without normalization.
Designed for extensibility - easy to add new endpoints.

Endpoint List:
  - /tv/{tv_id}/credits
  - /tv/{tv_id}/images
  - /tv/{tv_id}/videos
  - /tv/{tv_id}/keywords
  - /tv/{tv_id}/season/{season_number}/images
  - /tv/{tv_id}/season/{season}/episode/{episode}/credits
  - /tv/{tv_id}/season/{season}/episode/{episode}/images
  - /movie/{movie_id}/credits
  - /movie/{movie_id}/images
  - /movie/{movie_id}/videos
  - /movie/{movie_id}/keywords
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import requests

TMDB_BASE = "https://api.themoviedb.org/3"


class TMDbExtras:
    """
    TMDb Extra Metadata API wrapper.
    Returns RAW API responses for each endpoint.
    """
    
    def __init__(self, api_key: str, lang: str = "en-US", timeout: int = 10):
        self.api_key = api_key
        self.lang = lang
        self.timeout = timeout
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to TMDb API and return RAW response"""
        url = f"{TMDB_BASE}/{endpoint.lstrip('/')}"
        params = params or {}
        params['api_key'] = self.api_key
        params['language'] = self.lang
        
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}
    
    # ========================================================================
    # MOVIE EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /movie/{movie_id}/credits
        Returns: RAW TMDb API response with 'cast' and 'crew' arrays
        """
        return self._get(f"movie/{movie_id}/credits")
    
    def movie_images(self, movie_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /movie/{movie_id}/images
        Returns: RAW TMDb API response with 'backdrops', 'posters', 'logos' arrays
        """
        return self._get(f"movie/{movie_id}/images")
    
    def movie_videos(self, movie_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /movie/{movie_id}/videos
        Returns: RAW TMDb API response with 'results' array containing video objects
        """
        return self._get(f"movie/{movie_id}/videos")
    
    def movie_keywords(self, movie_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /movie/{movie_id}/keywords
        Returns: RAW TMDb API response with 'keywords' array
        """
        return self._get(f"movie/{movie_id}/keywords")
    
    # ========================================================================
    # TV SERIES EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def tv_credits(self, tv_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/credits
        Returns: RAW TMDb API response with 'cast' and 'crew' arrays
        """
        return self._get(f"tv/{tv_id}/credits")
    
    def tv_images(self, tv_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/images
        Returns: RAW TMDb API response with 'backdrops', 'posters', 'logos' arrays
        """
        return self._get(f"tv/{tv_id}/images")
    
    def tv_videos(self, tv_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/videos
        Returns: RAW TMDb API response with 'results' array containing video objects
        """
        return self._get(f"tv/{tv_id}/videos")
    
    def tv_keywords(self, tv_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/keywords
        Returns: RAW TMDb API response with 'results' array containing keyword objects
        """
        return self._get(f"tv/{tv_id}/keywords")
    
    # ========================================================================
    # TV SEASON EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def tv_season_images(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/season/{season_number}/images
        Returns: RAW TMDb API response with 'posters' array
        """
        return self._get(f"tv/{tv_id}/season/{season_number}/images")
    
    # ========================================================================
    # TV EPISODE EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def tv_episode_credits(self, tv_id: int, season: int, episode: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/season/{season}/episode/{episode}/credits
        Returns: RAW TMDb API response with 'cast', 'crew', and 'guest_stars' arrays
        """
        return self._get(f"tv/{tv_id}/season/{season}/episode/{episode}/credits")
    
    def tv_episode_images(self, tv_id: int, season: int, episode: int) -> Dict[str, Any]:
        """
        Endpoint: GET /tv/{tv_id}/season/{season}/episode/{episode}/images
        Returns: RAW TMDb API response with 'stills' array
        """
        return self._get(f"tv/{tv_id}/season/{season}/episode/{episode}/images")
