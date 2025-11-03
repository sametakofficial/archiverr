# integrations/tvdb/extras.py
"""
TVDb Extra Metadata Fetcher
Handles optional metadata endpoints for TVDb API v4.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
from utils.structured_logger import get_logger

TVDB_BASE = "https://api4.thetvdb.com/v4"


class TVDbExtras:
    """
    TVDb Extra Metadata API wrapper.
    
    Note: TVDb API v4 has limited extra endpoints compared to TMDb.
    Most metadata is included in the /extended endpoint.
    """
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.logger = get_logger()
        self._token = None
    
    def _ensure_auth(self):
        """Ensure we have a valid JWT token"""
        if not self._token:
            import requests
            url = f"{TVDB_BASE}/login"
            resp = requests.post(url, json={"apikey": self.api_key}, timeout=self.timeout)
            resp.raise_for_status()
            self._token = resp.json()["data"]["token"]
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to TVDb API"""
        import requests
        self._ensure_auth()
        
        url = f"{TVDB_BASE}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self._token}"}
        
        self.logger.debug(
            "tvdb.extras.request",
            endpoint=endpoint,
            message=f"Fetching extra: {endpoint}"
        )
        
        resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get("data", {})
    
    # ========================================================================
    # TV SERIES EXTRAS
    # ========================================================================
    
    def tv_credits(self, series_id: int) -> Dict[str, Any]:
        """
        Get TV series cast and crew.
        
        TVDb /series/{id}/extended includes characters array.
        """
        try:
            data = self._get(f"series/{series_id}/extended")
            characters = data.get("characters", [])
            
            cast_list = []
            for char in characters:
                person_name = char.get("personName")
                char_name = char.get("name")
                if person_name:
                    cast_list.append({
                        'name': person_name,
                        'character': char_name or '',
                        'order': len(cast_list),
                        'profile_path': char.get("image"),
                        'id': char.get("peopleId")
                    })
            
            return {
                'cast': cast_list,
                'crew': []  # TVDb doesn't provide crew in extended endpoint
            }
        except Exception as e:
            self.logger.warn(
                "tvdb.extras.failed",
                endpoint=f"series/{series_id}/extended",
                error=str(e),
                message="TVDb credits fetch failed"
            )
            return {}
    
    def tv_images(self, series_id: int) -> Dict[str, Any]:
        """
        Get TV series artwork (posters, backgrounds, banners).
        
        TVDb /series/{id}/artworks returns array of artwork objects.
        """
        try:
            # TVDb v4 returns data as array directly
            data = self._get(f"series/{series_id}/artworks")
            
            # If data is wrapped in 'data' key, unwrap it
            if isinstance(data, dict) and 'artworks' in data:
                artworks = data['artworks']
            elif isinstance(data, list):
                artworks = data
            else:
                artworks = []
            
            return self._normalize_images(artworks)
        except Exception as e:
            self.logger.warn(
                "tvdb.extras.failed",
                endpoint=f"series/{series_id}/artworks",
                error=str(e),
                message=f"TVDb artwork fetch failed: {e}"
            )
            return {}
    
    def tv_external_ids(self, series_id: int) -> Dict[str, str]:
        """
        Get TV series external IDs.
        
        TVDb /series/{id}/extended includes remote IDs.
        """
        try:
            data = self._get(f"series/{series_id}/extended")
            remote_ids = data.get("remoteIds", [])
            
            external_ids = {
                'imdb_id': '',
                'tvdb_id': str(series_id),
                'facebook_id': '',
                'instagram_id': '',
                'twitter_id': ''
            }
            
            for remote in remote_ids:
                source = remote.get("sourceName", "").lower()
                remote_id = str(remote.get("id", ""))
                if source and remote_id:
                    if 'imdb' in source:
                        external_ids['imdb_id'] = remote_id
                    elif 'facebook' in source:
                        external_ids['facebook_id'] = remote_id
                    elif 'instagram' in source:
                        external_ids['instagram_id'] = remote_id
                    elif 'twitter' in source:
                        external_ids['twitter_id'] = remote_id
            
            return external_ids
        except Exception as e:
            self.logger.warn(
                "tvdb.extras.failed",
                endpoint=f"series/{series_id}/extended",
                error=str(e),
                message="TVDb external IDs fetch failed"
            )
            return {}
    
    def tv_content_ratings(self, series_id: int) -> List[Dict[str, str]]:
        """
        Get TV series content ratings.
        
        TVDb /series/{id}/extended includes contentRatings array.
        """
        try:
            data = self._get(f"series/{series_id}/extended")
            ratings = data.get("contentRatings", [])
            
            normalized = []
            for rating in ratings:
                country = rating.get("country") or rating.get("countryCode")
                rating_value = rating.get("name") or rating.get("rating")
                
                if country and rating_value:
                    normalized.append({
                        'iso_3166_1': country,
                        'rating': rating_value
                    })
            
            return normalized
        except Exception as e:
            self.logger.warn(
                "tvdb.extras.failed",
                endpoint=f"series/{series_id}/extended",
                error=str(e),
                message="TVDb content ratings fetch failed"
            )
            return []
    
    def episode_images(self, series_id: int, season: int, episode: int) -> Dict[str, Any]:
        """
        Get episode images (stills).
        
        TVDb includes episode image in episode details.
        """
        # TVDb doesn't have a dedicated episode images endpoint
        # Images are included in episode details already
        return {}
    
    # ========================================================================
    # NORMALIZATION HELPERS
    # ========================================================================
    
    def _normalize_images(self, data: Any) -> Dict[str, Any]:
        """
        Normalize TVDb artwork response to match our schema.
        
        TVDb v4 API returns artworks with:
        - type: artwork type ID (need to check typeName or type field)
        - image: full URL
        - thumbnail: thumbnail URL
        
        Common types: poster, background, banner, clearlogo, etc.
        """
        if not isinstance(data, list):
            return {"posters": [], "backdrops": [], "stills": []}
        
        posters = []
        backdrops = []
        banners = []
        
        for art in data:
            if not isinstance(art, dict):
                continue
            
            # TVDb v4 uses 'image' field for URL
            image_url = art.get("image")
            if not image_url:
                continue
            
            # Get type - can be int or object with name
            art_type = art.get("type")
            type_name = ""
            
            if isinstance(art_type, dict):
                type_name = (art_type.get("name") or art_type.get("typeName") or "").lower()
            elif isinstance(art_type, int):
                # Legacy type IDs: 2=season, 3=series, 14=poster, 15=banner, 16=fanart
                type_id = art_type
                if type_id == 14 or type_id == 2:
                    type_name = "poster"
                elif type_id == 16 or type_id == 3:
                    type_name = "background"
                elif type_id == 15:
                    type_name = "banner"
            
            normalized = {
                "file_path": image_url,
                "thumbnail": art.get("thumbnail"),
                "width": art.get("width"),
                "height": art.get("height"),
            }
            
            # Categorize by type name
            if "poster" in type_name:
                posters.append(normalized)
            elif "background" in type_name or "fanart" in type_name:
                backdrops.append(normalized)
            elif "banner" in type_name:
                banners.append(normalized)
            else:
                # Default to backdrop for unknown types
                backdrops.append(normalized)
        
        return {
            "posters": posters,
            "backdrops": backdrops,
            "stills": [],
        }
