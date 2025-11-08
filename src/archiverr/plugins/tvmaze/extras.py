# plugins/tvmaze/extras.py
"""
TVMaze Extra Metadata Fetcher
Handles optional metadata endpoints for TVMaze API.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List

TVMAZE_BASE = "https://api.tvmaze.com"


class TVMazeExtras:
    """
    TVMaze Extra Metadata API wrapper.
    
    TVMaze API does not require authentication.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request to TVMaze API"""
        import requests
        
        url = f"{TVMAZE_BASE}/{endpoint.lstrip('/')}"
        
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    # ========================================================================
    # TV SERIES EXTRAS
    # ========================================================================
    
    def tv_cast(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Get TV series cast.
        
        TVMaze /shows/{id}/cast returns array of cast members.
        """
        try:
            data = self._get(f"shows/{show_id}/cast")
            
            cast_list = []
            for item in data:
                person = item.get('person', {})
                character = item.get('character', {})
                
                cast_list.append({
                    'name': person.get('name'),
                    'character': character.get('name'),
                    'order': len(cast_list),
                    'profile_path': person.get('image', {}).get('medium') if person.get('image') else None,
                    'id': person.get('id')
                })
            
            return cast_list
        except Exception:
            return []
    
    def tv_crew(self, show_id: int) -> List[Dict[str, Any]]:
        """
        Get TV series crew.
        
        TVMaze /shows/{id}/crew returns array of crew members.
        """
        try:
            data = self._get(f"shows/{show_id}/crew")
            
            crew_list = []
            for item in data:
                person = item.get('person', {})
                crew_type = item.get('type', 'Crew')
                
                crew_list.append({
                    'name': person.get('name'),
                    'job': crew_type,
                    'department': crew_type,
                    'profile_path': person.get('image', {}).get('medium') if person.get('image') else None,
                    'id': person.get('id')
                })
            
            return crew_list
        except Exception:
            return []
    
    def tv_images(self, show_id: int) -> Dict[str, Any]:
        """
        Get TV series images.
        
        TVMaze /shows/{id}/images returns array of images.
        """
        try:
            data = self._get(f"shows/{show_id}/images")
            
            posters = []
            backdrops = []
            
            for img in data:
                img_type = img.get('type', '').lower()
                resolution = img.get('resolutions', {})
                
                image_data = {
                    'path': resolution.get('original', {}).get('url') if resolution.get('original') else None,
                    'width': resolution.get('original', {}).get('width') if resolution.get('original') else None,
                    'height': resolution.get('original', {}).get('height') if resolution.get('original') else None
                }
                
                if img_type == 'poster':
                    posters.append(image_data)
                elif img_type == 'background':
                    backdrops.append(image_data)
                else:
                    backdrops.append(image_data)
            
            return {
                'posters': posters,
                'backdrops': backdrops,
                'stills': []
            }
        except Exception:
            return {'posters': [], 'backdrops': [], 'stills': []}
    
    def episode_guest_cast(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Get episode guest cast.
        
        TVMaze /episodes/{id}/guestcast returns array of guest cast.
        """
        try:
            data = self._get(f"episodes/{episode_id}/guestcast")
            
            guest_cast = []
            for item in data:
                person = item.get('person', {})
                character = item.get('character', {})
                
                guest_cast.append({
                    'name': person.get('name'),
                    'character': character.get('name'),
                    'profile_path': person.get('image', {}).get('medium') if person.get('image') else None,
                    'id': person.get('id')
                })
            
            return guest_cast
        except Exception:
            return []
    
    def episode_guest_crew(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Get episode guest crew.
        
        TVMaze /episodes/{id}/guestcrew returns array of guest crew.
        """
        try:
            data = self._get(f"episodes/{episode_id}/guestcrew")
            
            guest_crew = []
            for item in data:
                person = item.get('person', {})
                crew_type = item.get('type', 'Guest Crew')
                
                guest_crew.append({
                    'name': person.get('name'),
                    'job': crew_type,
                    'department': crew_type,
                    'profile_path': person.get('image', {}).get('medium') if person.get('image') else None,
                    'id': person.get('id')
                })
            
            return guest_crew
        except Exception:
            return []
