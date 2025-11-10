"""TVMaze API request utilities"""
import requests
from typing import Dict, Any, List


class TVMazeAPI:
    """Low-level TVMaze API request handler"""
    
    BASE_URL = "https://api.tvmaze.com"
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Make GET request to TVMaze API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def search_shows(self, query: str) -> List[Dict[str, Any]]:
        """Search for TV shows"""
        return self.get('/search/shows', params={'q': query})
    
    def get_show(self, show_id: int) -> Dict[str, Any]:
        """Get show details"""
        return self.get(f'/shows/{show_id}')
    
    def get_episode_by_number(self, show_id: int, season: int, episode: int) -> Dict[str, Any]:
        """Get episode by season and episode number"""
        return self.get(f'/shows/{show_id}/episodebynumber', 
                       params={'season': season, 'number': episode})
    
    def get_show_cast(self, show_id: int) -> List[Dict[str, Any]]:
        """Get show cast"""
        return self.get(f'/shows/{show_id}/cast')
    
    def get_show_crew(self, show_id: int) -> List[Dict[str, Any]]:
        """Get show crew"""
        return self.get(f'/shows/{show_id}/crew')
    
    def get_show_images(self, show_id: int) -> List[Dict[str, Any]]:
        """Get show images"""
        return self.get(f'/shows/{show_id}/images')
    
    def get_episode(self, episode_id: int) -> Dict[str, Any]:
        """Get episode details"""
        return self.get(f'/episodes/{episode_id}')
    
    def get_episode_guestcast(self, episode_id: int) -> List[Dict[str, Any]]:
        """Get episode guest cast"""
        return self.get(f'/episodes/{episode_id}/guestcast')
    
    def get_episode_guestcrew(self, episode_id: int) -> List[Dict[str, Any]]:
        """Get episode guest crew"""
        return self.get(f'/episodes/{episode_id}/guestcrew')
