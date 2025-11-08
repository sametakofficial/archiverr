"""TVMaze Plugin - TV Show Metadata (TV Only)"""
from typing import Dict, Any
import requests
from datetime import datetime
from .extras import TVMazeExtras


class TVMazePlugin:
    """Output plugin that fetches TV show metadata from TVMaze (TV shows only)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "tvmaze"
        self.category = "output"
        
        # Initialize extras client
        self.extras_client = TVMazeExtras()
        
        # Extras configuration
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch TV show metadata from TVMaze.
        
        Args:
            match_data: Must contain 'renamer' with 'parsed.show'
            
        Returns:
            {status, show: {...}, episode: {...}}
        """
        parsed = match_data.get('renamer', {}).get('parsed', {})
        show_data = parsed.get('show')
        movie_data = parsed.get('movie')
        
        start_time = datetime.now()
        
        # TVMaze only supports TV shows - Check if it's a movie (has year)
        if movie_data and movie_data.get('year'):
            return self._not_supported_result("TVMaze only supports TV shows")
        
        if not show_data or not show_data.get('name'):
            return self._empty_result()
        
        show_name = show_data.get('name')
        season_number = show_data.get('season')
        episode_number = show_data.get('episode')
        
        result = {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': '',
                'duration_ms': 0,
                'not_supported': False
            },
            'show': None,
            'episode': None,
            'extras': {}
        }
        
        try:
            # Search show
            response = requests.get(
                'https://api.tvmaze.com/search/shows',
                params={'q': show_name},
                timeout=5
            )
            shows = response.json()
            
            if shows and len(shows) > 0:
                show_info = shows[0]['show']
                result['show'] = {
                    'name': show_info.get('name'),
                    'tvmaze_id': show_info.get('id'),
                    'url': show_info.get('url'),
                    'type': show_info.get('type'),
                    'language': show_info.get('language'),
                    'status': show_info.get('status'),
                    'premiered': show_info.get('premiered'),
                    'rating': show_info.get('rating', {}).get('average'),
                    'network': show_info.get('network', {}).get('name') if show_info.get('network') else None,
                    'summary': show_info.get('summary')
                }
                
                # Get episode if season and episode provided
                if season_number and episode_number:
                    show_id = show_info.get('id')
                    try:
                        ep_response = requests.get(
                            f'https://api.tvmaze.com/shows/{show_id}/episodebynumber',
                            params={'season': season_number, 'number': episode_number},
                            timeout=5
                        )
                        ep_info = ep_response.json()
                        
                        result['episode'] = {
                            'id': ep_info.get('id'),
                            'name': ep_info.get('name'),
                            'season': ep_info.get('season'),
                            'number': ep_info.get('number'),
                            'airdate': ep_info.get('airdate'),
                            'runtime': ep_info.get('runtime'),
                            'summary': ep_info.get('summary')
                        }
                    except Exception:
                        pass
                
                # Fetch extras if enabled
                show_id = show_info.get('id')
                episode_id = result.get('episode', {}).get('id')
                
                if self.extras_config.get('show_cast') and show_id:
                    cast = self.extras_client.tv_cast(show_id)
                    if cast:
                        result['extras']['cast'] = cast[:10]
                
                if self.extras_config.get('show_crew') and show_id:
                    crew = self.extras_client.tv_crew(show_id)
                    if crew:
                        result['extras']['crew'] = crew[:10]
                
                if self.extras_config.get('show_images') and show_id:
                    images = self.extras_client.tv_images(show_id)
                    if images:
                        result['extras']['images'] = images
                
                if self.extras_config.get('episode_guest_cast') and episode_id:
                    guest_cast = self.extras_client.episode_guest_cast(episode_id)
                    if guest_cast:
                        result['extras']['episode_guest_cast'] = guest_cast
                
                if self.extras_config.get('episode_guest_crew') and episode_id:
                    guest_crew = self.extras_client.episode_guest_crew(episode_id)
                    if guest_crew:
                        result['extras']['episode_guest_crew'] = guest_crew
        except Exception:
            result['status']['success'] = False
        
        # Set finished time and duration
        end_time = datetime.now()
        result['status']['finished_at'] = end_time.isoformat()
        result['status']['duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
        
        return result
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result"""
        now = datetime.now().isoformat()
        return {
            'status': {
                'success': False,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0,
                'not_supported': False
            },
            'show': None,
            'episode': None,
            'extras': {}
        }
    
    def _not_supported_result(self, reason: str = "") -> Dict[str, Any]:
        """Return not supported result"""
        now = datetime.now().isoformat()
        return {
            'status': {
                'success': False,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0,
                'not_supported': True,
                'reason': reason
            },
            'show': None,
            'episode': None,
            'extras': {}
        }
