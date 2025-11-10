"""TVDb API request utilities"""
import requests
from typing import Dict, Any


class TVDbAPI:
    """Low-level TVDb API request handler"""
    
    BASE_URL = "https://api4.thetvdb.com/v4"
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.token = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate and get bearer token"""
        url = f"{self.BASE_URL}/login"
        resp = requests.post(url, json={"apikey": self.api_key}, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        token = (data or {}).get("data", {}).get("token")
        if not token:
            raise RuntimeError("TVDb authentication failed: no token in response")
        self.token = token
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with bearer token"""
        if not self.token:
            raise RuntimeError("TVDb token missing")
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Accept-Language": "eng"
        }
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make GET request to TVDb API"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def search_series(self, query: str) -> Dict[str, Any]:
        """Search for TV series"""
        return self.get('/search', params={'query': query, 'type': 'series'})
    
    def search_movie(self, query: str) -> Dict[str, Any]:
        """Search for movies"""
        return self.get('/search', params={'query': query, 'type': 'movie'})
    
    def get_series_extended(self, series_id: int) -> Dict[str, Any]:
        """Get series extended info"""
        return self.get(f'/series/{series_id}/extended')
    
    def get_movie_extended(self, movie_id: int) -> Dict[str, Any]:
        """Get movie extended info"""
        return self.get(f'/movies/{movie_id}/extended')
    
    def get_season_extended(self, season_id: int) -> Dict[str, Any]:
        """Get season extended info"""
        return self.get(f'/seasons/{season_id}/extended')
    
    def get_episode_extended(self, episode_id: int) -> Dict[str, Any]:
        """Get episode extended info"""
        return self.get(f'/episodes/{episode_id}/extended')
