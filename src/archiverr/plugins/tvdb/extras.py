# plugins/tvdb/extras.py
"""
TVDb Extra Metadata Fetcher - Endpoint-Based System

Each method returns RAW API response without normalization.
Designed for extensibility - easy to add new endpoints.

Endpoint List:
  - /series/{id}/extended
  - /series/{id}/artworks
  - /seasons/{id}/extended
  - /episodes/{id}/extended
  - /movies/{id}/extended
  - /tags/options
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import requests

TVDB_BASE = "https://api4.thetvdb.com/v4"


class TVDbExtras:
    """
    TVDb Extra Metadata API wrapper.
    Returns RAW API responses for each endpoint.
    """
    
    def __init__(self, token: str, timeout: int = 10):
        self.token = token
        self.timeout = timeout
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to TVDb API and return RAW response"""
        url = f"{TVDB_BASE}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # TVDb wraps responses in {"data": ...}
            return data
        except Exception:
            return {}
    
    # ========================================================================
    # TV SERIES EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def series_extended(self, series_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /series/{id}/extended
        Returns: RAW TVDb API response with full series metadata including characters, trailers, tags, etc.
        """
        return self._get(f"series/{series_id}/extended")
    
    def series_artworks(self, series_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /series/{id}/artworks
        Returns: RAW TVDb API response with artworks array (posters, backgrounds, banners)
        """
        return self._get(f"series/{series_id}/artworks")
    
    # ========================================================================
    # TV SEASON EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def seasons_extended(self, season_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /seasons/{id}/extended
        Returns: RAW TVDb API response with full season metadata including artwork and episodes
        """
        return self._get(f"seasons/{season_id}/extended")
    
    # ========================================================================
    # TV EPISODE EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def episodes_extended(self, episode_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /episodes/{id}/extended
        Returns: RAW TVDb API response with full episode metadata including characters and image
        """
        return self._get(f"episodes/{episode_id}/extended")
    
    # ========================================================================
    # MOVIE EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def movies_extended(self, movie_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /movies/{id}/extended
        Returns: RAW TVDb API response with full movie metadata including characters, artworks, genres, tags
        """
        return self._get(f"movies/{movie_id}/extended")
    
    # ========================================================================
    # GLOBAL EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def tags_options(self) -> Dict[str, Any]:
        """
        Endpoint: GET /tags/options
        Returns: RAW TVDb API response with available tag options
        """
        return self._get("tags/options")
