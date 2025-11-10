"""TMDb API request utilities"""
import requests
from typing import Dict, Any


class TMDbAPI:
    """Low-level TMDb API request handler"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, api_key: str, language: str = "en-US", region: str = "US"):
        self.api_key = api_key
        self.language = language
        self.region = region
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, timeout: int = 10) -> Dict[str, Any]:
        """
        Make GET request to TMDb API
        
        Args:
            endpoint: API endpoint (e.g. "/search/movie")
            params: Query parameters (api_key and language added automatically)
            timeout: Request timeout in seconds
            
        Returns:
            JSON response as dict
        """
        if params is None:
            params = {}
        
        # Add default params
        params.setdefault('api_key', self.api_key)
        params.setdefault('language', self.language)
        
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        
        return response.json()
    
    def search_movie(self, query: str, year: int = None, timeout: int = 10) -> Dict[str, Any]:
        """Search for movies"""
        params = {'query': query}
        if year:
            params['year'] = year
        
        return self.get('/search/movie', params, timeout)
    
    def search_tv(self, query: str, timeout: int = 10) -> Dict[str, Any]:
        """Search for TV shows"""
        return self.get('/search/tv', {'query': query}, timeout)
    
    def get_movie(self, movie_id: int, timeout: int = 10) -> Dict[str, Any]:
        """Get movie details"""
        return self.get(f'/movie/{movie_id}', timeout=timeout)
    
    def get_tv(self, tv_id: int, timeout: int = 10) -> Dict[str, Any]:
        """Get TV show details"""
        return self.get(f'/tv/{tv_id}', timeout=timeout)
    
    def get_season(self, tv_id: int, season_number: int, timeout: int = 10) -> Dict[str, Any]:
        """Get season details"""
        return self.get(f'/tv/{tv_id}/season/{season_number}', timeout=timeout)
    
    def get_episode(self, tv_id: int, season_number: int, episode_number: int, timeout: int = 10) -> Dict[str, Any]:
        """Get episode details"""
        return self.get(f'/tv/{tv_id}/season/{season_number}/episode/{episode_number}', timeout=timeout)
