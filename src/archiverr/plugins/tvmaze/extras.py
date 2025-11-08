# plugins/tvmaze/extras.py
"""
TVMaze Extra Metadata Fetcher - Endpoint-Based System

Each method returns RAW API response without normalization.
Designed for extensibility - easy to add new endpoints.

Endpoint List:
  - /shows/{id}/cast
  - /shows/{id}/crew
  - /shows/{id}/images
  - /shows/{id}/episodes
  - /shows/{id}/seasons
  - /episodes/{id}
  - /episodes/{id}/guestcast
  - /episodes/{id}/guestcrew
"""
from __future__ import annotations
from typing import Dict, Any, List
import requests

TVMAZE_BASE = "https://api.tvmaze.com"


class TVMazeExtras:
    """
    TVMaze Extra Metadata API wrapper.
    Returns RAW API responses for each endpoint.
    No API key required for TVMaze.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def _get(self, endpoint: str) -> Any:
        """Make GET request to TVMaze API and return RAW response"""
        url = f"{TVMAZE_BASE}/{endpoint.lstrip('/')}"
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}
    
    # ========================================================================
    # TV SHOWS EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def shows_cast(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /shows/{id}/cast
        Returns: RAW TVMaze API response - array of cast objects with person and character info
        """
        return self._get(f"shows/{show_id}/cast")
    
    def shows_crew(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /shows/{id}/crew
        Returns: RAW TVMaze API response - array of crew objects with person and type info
        """
        return self._get(f"shows/{show_id}/crew")
    
    def shows_images(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /shows/{id}/images
        Returns: RAW TVMaze API response - array of image objects with type and resolutions
        """
        return self._get(f"shows/{show_id}/images")
    
    def shows_episodes(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /shows/{id}/episodes
        Returns: RAW TVMaze API response - array of all episodes for the show
        """
        return self._get(f"shows/{show_id}/episodes")
    
    def shows_seasons(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /shows/{id}/seasons
        Returns: RAW TVMaze API response - array of season objects
        """
        return self._get(f"shows/{show_id}/seasons")
    
    # ========================================================================
    # EPISODE EXTRAS - RAW API RESPONSES
    # ========================================================================
    
    def episodes_single(self, episode_id: int) -> Dict[str, Any]:
        """
        Endpoint: GET /episodes/{id}
        Returns: RAW TVMaze API response - full episode object with all metadata
        """
        return self._get(f"episodes/{episode_id}")
    
    def episodes_guestcast(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /episodes/{id}/guestcast
        Returns: RAW TVMaze API response - array of guest cast for specific episode
        """
        return self._get(f"episodes/{episode_id}/guestcast")
    
    def episodes_guestcrew(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Endpoint: GET /episodes/{id}/guestcrew
        Returns: RAW TVMaze API response - array of guest crew for specific episode
        """
        return self._get(f"episodes/{episode_id}/guestcrew")
