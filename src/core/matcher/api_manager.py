# api_manager.py
"""
Simple API Manager - handles fallback logic based on config priority.
Each API client normalizes its own data, so no normalization here.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from utils.structured_logger import get_logger

class APIManager:
    """Manages multiple API clients with priority-based fallback"""
    
    def __init__(self, config):
        """
        Initialize API Manager.
        
        Args:
            config: AppConfig instance
        """
        self.config = config
        self._clients: Dict[str, Any] = {}
        self.logger = get_logger()
    
    def register_client(self, name: str, client: Any):
        """Register an API client"""
        self._clients[name] = client
    
    def search_movie(self, title: str, year: Optional[int] = None, max_results: int = 5) -> tuple[List[Dict[str, Any]], str]:
        """
        Search for movie using priority fallback (duck typing, no hardcoded checks).
        Returns (results, api_source)
        """
        # Get priority from config, no hardcoded defaults
        priority = getattr(self.config, 'movie_priority', [])
        if not priority:
            # Fallback: use all registered clients
            priority = list(self._clients.keys())
        
        for api_name in priority:
            client = self._clients.get(api_name)
            if not client:
                continue
            
            # Duck typing: try common movie search method names
            for method_name in ['search_movie', 'movie_search', 'search']:
                if not hasattr(client, method_name):
                    continue
                try:
                    method = getattr(client, method_name)
                    results = method(title, year=year, max_results=max_results)
                    if results:
                        return results, api_name
                except TypeError:
                    # Try without year parameter
                    try:
                        results = method(title, max_results=max_results)
                        if results:
                            return results, api_name
                    except Exception:
                        continue
                except Exception:
                    continue
        
        return [], 'unknown'
    
    def search_tv(self, title: str, first_air_year: Optional[int] = None, max_results: int = 5) -> tuple[List[Dict[str, Any]], str]:
        """
        Search for TV show using priority fallback (duck typing, no hardcoded checks).
        Returns (results, api_source)
        """
        # Get priority from config, no hardcoded defaults
        priority = getattr(self.config, 'tv_priority', [])
        if not priority:
            # Fallback: use all registered clients
            priority = list(self._clients.keys())
        
        for api_name in priority:
            client = self._clients.get(api_name)
            if not client:
                continue
            
            # Duck typing: try common TV search method names
            for method_name in ['search_tv', 'tv_search', 'search_series', 'search']:
                if not hasattr(client, method_name):
                    continue
                try:
                    method = getattr(client, method_name)
                    results = method(title, first_air_year=first_air_year, max_results=max_results)
                    if results:
                        return results, api_name
                except TypeError:
                    # Try without first_air_year parameter
                    try:
                        results = method(title, max_results=max_results)
                        if results:
                            return results, api_name
                    except Exception:
                        continue
                except Exception:
                    continue
        
        return [], 'unknown'
    
    def get_movie_details(self, movie_id: Any, api_name: str) -> Optional[Dict[str, Any]]:
        """Get movie details from specific API (generic, duck typing)"""
        client = self._clients.get(api_name)
        if not client:
            return None
        
        try:
            # Try common method names
            for method_name in ['movie_details', 'get_movie_details', 'get_movie', 'get_details']:
                if hasattr(client, method_name):
                    return getattr(client, method_name)(movie_id)
        except Exception:
            return None
        
        return None
    
    def get_tv_details(self, series_id: Any, api_name: str) -> Optional[Dict[str, Any]]:
        """Get TV show details from specific API (generic, no hardcoded API names)"""
        client = self._clients.get(api_name)
        if not client:
            return None
        
        try:
            # Try common method names (duck typing)
            for method_name in ['get_series_details', 'tv_details', 'get_show', 'get_details']:
                if hasattr(client, method_name):
                    return getattr(client, method_name)(series_id)
        except Exception as e:
            self.logger.error(
                "api.tv_details_error",
                api=api_name,
                error=str(e),
                message=f"get_tv_details failed for {api_name}: {e}"
            )
            return None
        
        return None
    
    def get_episode_details(self, series_id: Any, season: int, episode: int, api_name: str) -> Optional[Dict[str, Any]]:
        """Get episode details from specific API (generic, no hardcoded API names)"""
        client = self._clients.get(api_name)
        if not client:
            self.logger.warn(
                "api.client_not_found",
                api=api_name,
                message=f"No client registered for {api_name}"
            )
            return None
        
        self.logger.debug(
            "api.get_episode",
            api=api_name,
            series_id=series_id,
            season=season,
            episode=episode,
            message=f"Fetching episode S{season}E{episode} from {api_name}"
        )
        
        try:
            # Try common method names (duck typing)
            for method_name in ['get_episode', 'tv_episode', 'get_episode_by_number']:
                if hasattr(client, method_name):
                    self.logger.debug(
                        "api.calling_method",
                        api=api_name,
                        method=method_name,
                        message=f"Calling {api_name}.{method_name}()"
                    )
                    result = getattr(client, method_name)(series_id, season, episode)
                    if result:
                        self.logger.debug(
                            "api.episode_success",
                            api=api_name,
                            name=result.get('name'),
                            air_date=result.get('air_date'),
                            message=f"✓ Got episode: {result.get('name')}"
                        )
                    else:
                        self.logger.debug(
                            "api.episode_none",
                            api=api_name,
                            method=method_name,
                            message=f"✗ {method_name} returned None"
                        )
                    return result
            self.logger.warn(
                "api.no_method",
                api=api_name,
                message=f"✗ No episode method found on {api_name} client"
            )
        except Exception as e:
            self.logger.error(
                "api.episode_error",
                api=api_name,
                error=str(e),
                message=f"✗ get_episode_details failed for {api_name}: {e}"
            )
            return None
        
        return None
    
    def fetch_extras(
        self,
        item_type: str,
        item_id: int,
        api_name: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        override_config: Optional[Dict[str, bool]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch extra metadata from specified API client.
        
        Args:
            item_type: 'movie', 'tv', 'season', 'episode'
            item_id: Item ID
            api_name: API client name
            season: Season number (for season/episode)
            episode: Episode number (for episode)
            override_config: Override extras config
        
        Returns:
            Dict with extras or None
        """
        client = self._clients.get(api_name)
        if not client:
            self.logger.warn(
                "api.no_client",
                api=api_name,
                message=f"✗ No client registered: {api_name}"
            )
            return None
        
        # Duck typing: check if client has fetch_extras method
        if not hasattr(client, 'fetch_extras'):
            self.logger.debug(
                "api.no_extras",
                api=api_name,
                message=f"{api_name} client doesn't support extras"
            )
            return None
        
        try:
            self.logger.debug(
                "api.fetching_extras",
                api=api_name,
                item_type=item_type,
                item_id=item_id,
                message=f"Fetching {item_type} extras from {api_name}"
            )
            
            # Debug: log extras config being passed
            actual_config = override_config if override_config is not None else (
                client.extras_config if hasattr(client, 'extras_config') else {}
            )
            self.logger.debug(
                "api.extras_config",
                api=api_name,
                config_keys=[k for k, v in actual_config.items() if v] if actual_config else [],
                message=f"Extras config: {len([k for k, v in actual_config.items() if v]) if actual_config else 0} enabled"
            )
            
            result = client.fetch_extras(
                item_type=item_type,
                item_id=item_id,
                season=season,
                episode=episode,
                override_config=override_config
            )
            
            if result:
                self.logger.debug(
                    "api.extras_success",
                    api=api_name,
                    extras_keys=list(result.keys()),
                    message=f"✓ Fetched extras: {', '.join(result.keys())}"
                )
            else:
                self.logger.debug(
                    "api.extras_empty",
                    api=api_name,
                    message="fetch_extras returned None or empty"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "api.extras_error",
                api=api_name,
                error=str(e),
                message=f"✗ fetch_extras failed for {api_name}: {e}"
            )
            return None
