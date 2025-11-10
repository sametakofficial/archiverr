"""TVMaze Plugin - Clean orchestration layer"""
from typing import Dict, Any
from datetime import datetime
from .extras import TVMazeExtras
from .normalize.normalizer import TVMazeNormalizer
from .utils.api import TVMazeAPI
from archiverr.utils.debug import get_debugger


class TVMazePlugin:
    """TVMaze metadata plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.include_raw = config.get('include-raw', False)  # Default: no raw data
        self.debugger = get_debugger()
        
        # Initialize components
        self.api = TVMazeAPI(timeout=5)
        self.extras_client = TVMazeExtras()
        self.normalizer = TVMazeNormalizer()
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch metadata from TVMaze"""
        start_time = datetime.now()
        renamer_data = match_data.get('renamer', {})
        parsed_data = renamer_data.get('parsed', {})
        
        if not parsed_data:
            return self._error_result()
        
        # TVMaze only supports TV shows
        show_data = parsed_data.get('show')
        if not show_data or not show_data.get('name'):
            self.debugger.debug("tvmaze", "Not a TV show, skipping")
            return self._not_supported_result()
        
        try:
            return self._fetch_show(show_data, start_time)
        except Exception as e:
            self.debugger.error("tvmaze", "Execution failed", error=str(e))
            return self._error_result()
    
    def _fetch_show(self, show_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Fetch TV show metadata"""
        show_name = show_data.get('name')
        season_num = show_data.get('season')
        episode_num = show_data.get('episode')
        
        # Search show
        search_results = self.api.search_shows(show_name)
        
        if not search_results or len(search_results) == 0:
            return self._error_result()
        
        show_info = search_results[0]['show']
        show_id = show_info.get('id')
        self.debugger.info("tvmaze", "TV show found", tvmaze_id=show_id, title=show_info.get('name'))
        
        # Get episode if provided
        episode_info = None
        if season_num and episode_num:
            try:
                episode_info = self.api.get_episode_by_number(show_id, season_num, episode_num)
            except Exception:
                pass
        
        # Fetch extras
        raw_extras = self._fetch_extras(show_id, episode_info)
        
        # Normalize (DEFAULT OUTPUT)
        normalized_show = self.normalizer.normalize_show(show_info, raw_extras)
        
        # Build result
        end_time = datetime.now()
        result = {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': int((end_time - start_time).total_seconds() * 1000)
            },
            'show': normalized_show,  # NORMALIZED by default
            'episode': None,
            'season': None,
            'movie': None
        }
        
        # Add RAW data ONLY if requested
        if self.include_raw:
            result['raw'] = {
                'show': {
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
                },
                'episode': {
                    'id': episode_info.get('id'),
                    'name': episode_info.get('name'),
                    'season': episode_info.get('season'),
                    'number': episode_info.get('number'),
                    'airdate': episode_info.get('airdate'),
                    'runtime': episode_info.get('runtime'),
                    'summary': episode_info.get('summary')
                } if episode_info else None,
                'extras': raw_extras
            }
        
        self.debugger.debug("tvmaze", "TV show normalized",
                           tvmaze_id=show_id,
                           title=normalized_show['title']['primary'],
                           cast_count=len(normalized_show.get('people', {}).get('cast', [])),
                           include_raw=self.include_raw)
        
        return result
    
    def _fetch_extras(self, show_id: int, episode_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch all enabled extras"""
        extras = {}
        
        # Shows Cast
        if self.extras_config.get('shows_cast'):
            data = self.extras_client.shows_cast(show_id)
            if data:
                extras['shows_cast'] = data
                self.debugger.debug("tvmaze", "Fetched shows_cast",
                                   endpoint="/shows/{id}/cast",
                                   count=len(data))
        
        # Shows Crew
        if self.extras_config.get('shows_crew'):
            data = self.extras_client.shows_crew(show_id)
            if data:
                extras['shows_crew'] = data
                self.debugger.debug("tvmaze", "Fetched shows_crew",
                                   endpoint="/shows/{id}/crew",
                                   count=len(data))
        
        # Shows Images
        if self.extras_config.get('shows_images'):
            data = self.extras_client.shows_images(show_id)
            if data:
                extras['shows_images'] = data
                self.debugger.debug("tvmaze", "Fetched shows_images",
                                   endpoint="/shows/{id}/images",
                                   count=len(data))
        
        # Episode extras
        if episode_info:
            episode_id = episode_info.get('id')
            
            if self.extras_config.get('episodes_single'):
                data = self.extras_client.episodes_single(episode_id)
                if data:
                    extras['episodes_single'] = data
                    self.debugger.debug("tvmaze", "Fetched episodes_single",
                                       endpoint="/episodes/{id}")
            
            if self.extras_config.get('episodes_guestcast'):
                data = self.extras_client.episodes_guestcast(episode_id)
                if data:
                    extras['episodes_guestcast'] = data
                    self.debugger.debug("tvmaze", "Fetched episodes_guestcast",
                                       endpoint="/episodes/{id}/guestcast",
                                       count=len(data))
            
            if self.extras_config.get('episodes_guestcrew'):
                data = self.extras_client.episodes_guestcrew(episode_id)
                if data:
                    extras['episodes_guestcrew'] = data
                    self.debugger.debug("tvmaze", "Fetched episodes_guestcrew",
                                       endpoint="/episodes/{id}/guestcrew",
                                       count=len(data))
        
        return extras
    
    def _not_supported_result(self) -> Dict[str, Any]:
        """Return not supported result"""
        now = datetime.now().isoformat()
        return {
            'status': {
                'success': False,
                'not_supported': True,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0
            },
            'movie': None,
            'show': None,
            'season': None,
            'episode': None,
            'extras': {},
            'normalized': {}
        }
    
    def _error_result(self) -> Dict[str, Any]:
        """Return error result"""
        now = datetime.now().isoformat()
        return {
            'status': {
                'success': False,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0
            },
            'movie': None,
            'show': None,
            'season': None,
            'episode': None,
            'extras': {},
            'normalized': {}
        }
