# integrations/tvmaze/extras.py
"""
TVMaze Extra Metadata Fetcher
Handles optional metadata endpoints for TVMaze API.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
from archiverr.utils.structured_logger import get_logger

TVMAZE_BASE = "https://api.tvmaze.com"


class TVMazeExtras:
    """
    TVMaze Extra Metadata API wrapper.
    Fetches optional metadata like cast, crew, images.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.logger = get_logger()
    
    def _get(self, endpoint: str) -> Any:
        """Make GET request to TVMaze API"""
        import requests
        url = f"{TVMAZE_BASE}/{endpoint.lstrip('/')}"
        
        self.logger.debug(
            "tvmaze.extras.request",
            endpoint=endpoint,
            message=f"Fetching extra: {endpoint}"
        )
        
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    # ========================================================================
    # TV SERIES EXTRAS
    # ========================================================================
    
    def tv_cast(self, show_id: int) -> Dict[str, Any]:
        """
        Get TV series main cast.
        Returns normalized cast dict.
        """
        data = self._get(f"shows/{show_id}/cast")
        return self._normalize_cast(data)
    
    def tv_crew(self, show_id: int) -> Dict[str, Any]:
        """
        Get TV series crew.
        Returns normalized crew dict.
        """
        data = self._get(f"shows/{show_id}/crew")
        return self._normalize_crew(data)
    
    def tv_images(self, show_id: int) -> Dict[str, Any]:
        """
        Get TV series images.
        Returns normalized images dict.
        """
        data = self._get(f"shows/{show_id}/images")
        return self._normalize_images(data)
    
    def episode_guest_cast(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Get episode guest cast.
        Returns list of guest cast members.
        """
        # TVMaze uses embed for guest cast
        data = self._get(f"episodes/{episode_id}?embed=guestcast")
        embedded = data.get('_embedded', {})
        guest_cast = embedded.get('guestcast', [])
        return self._normalize_guest_cast(guest_cast)
    
    # ========================================================================
    # NORMALIZATION HELPERS
    # ========================================================================
    
    def _normalize_cast(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize TVMaze cast response.
        
        Returns:
            {
                'cast': [{'name': str, 'character': str, 'image': str}, ...]
            }
        """
        cast = []
        for item in data:
            person = item.get('person', {})
            character = item.get('character', {})
            
            cast.append({
                'name': person.get('name'),
                'character': character.get('name'),
                'image': person.get('image', {}).get('medium') if person.get('image') else None,
                'id': person.get('id'),
            })
        
        return {'cast': cast}
    
    def _normalize_crew(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize TVMaze crew response.
        
        Returns:
            {
                'crew': [{'name': str, 'type': str, 'image': str}, ...]
            }
        """
        crew = []
        for item in data:
            person = item.get('person', {})
            crew_type = item.get('type')
            
            crew.append({
                'name': person.get('name'),
                'job': crew_type or 'Unknown',
                'department': crew_type or 'Unknown',
                'profile_path': person.get('image', {}).get('medium') if person.get('image') else None,
                'id': person.get('id'),
            })
        
        return {'crew': crew}
    
    def _normalize_images(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize TVMaze images response.
        
        Returns:
            {
                'posters': [...],
                'backgrounds': [...],
                'banners': [...],
            }
        """
        posters = []
        backgrounds = []
        banners = []
        
        for img in data:
            img_type = img.get('type', '').lower()
            resolutions = img.get('resolutions', {})
            
            # Get the original or medium resolution
            url = resolutions.get('original') or resolutions.get('medium')
            
            normalized = {
                'file_path': url,
                'type': img_type,
            }
            
            if img_type == 'poster':
                posters.append(normalized)
            elif img_type == 'background':
                backgrounds.append(normalized)
            elif img_type == 'banner':
                banners.append(normalized)
        
        return {
            'posters': posters,
            'backdrops': backgrounds,  # Match TMDb naming
            'stills': [],
        }
    
    def _normalize_guest_cast(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize guest cast response.
        
        Returns:
            [{'name': str, 'character': str, 'image': str}, ...]
        """
        guests = []
        for item in data:
            person = item.get('person', {})
            character = item.get('character', {})
            
            guests.append({
                'name': person.get('name'),
                'character': character.get('name'),
                'image': person.get('image', {}).get('medium') if person.get('image') else None,
                'id': person.get('id'),
            })
        
        return guests
