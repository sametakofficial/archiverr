"""TVDb Plugin - Clean orchestration layer"""
from typing import Dict, Any
from datetime import datetime
from .extras import TVDbExtras
from .normalize.normalizer import TVDbNormalizer
from .utils.api import TVDbAPI
from archiverr.utils.debug import get_debugger
from archiverr.plugins.base import OutputPlugin


class TVDbPlugin(OutputPlugin):
    """TVDb metadata plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.timeout = 10
        self.include_raw = config.get('include-raw', False)  # Default: no raw data
        self.debugger = get_debugger()
        
        # Initialize components
        self.api = TVDbAPI(self.api_key, self.timeout)
        self.extras_client = TVDbExtras(self.api.token, self.timeout)
        self.normalizer = TVDbNormalizer()
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch metadata from TVDb"""
        start_time = datetime.now()
        renamer_data = match_data.get('renamer', {})
        parsed_data = renamer_data.get('parsed', {})
        
        if not parsed_data:
            return self._error_result()
        
        movie_data = parsed_data.get('movie')
        show_data = parsed_data.get('show')
        
        try:
            if movie_data and movie_data.get('name'):
                result = self._fetch_movie(movie_data, start_time)
                
                # Add validation for movies
                if result.get('status', {}).get('success'):
                    validation = self._perform_validation(match_data, result)
                    result['validation'] = validation
                
                return result
            elif show_data and show_data.get('name'):
                result = self._fetch_show(show_data, start_time)
                
                # Add validation for episodes (if episode data available)
                if result.get('status', {}).get('success') and result.get('episode'):
                    validation = self._perform_validation(match_data, result)
                    result['validation'] = validation
                
                return result
            else:
                return self._error_result()
        except Exception as e:
            self.debugger.error("tvdb", "Execution failed", error=str(e))
            return self._error_result()
    
    def _fetch_movie(self, movie_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Fetch movie metadata"""
        movie_name = movie_data.get('name')
        year = movie_data.get('year')
        
        # Search movie
        search_results = self.api.search_movie(movie_name)
        
        if not search_results.get('data'):
            return self._error_result()
        
        movie_id = search_results['data'][0]['tvdb_id']
        self.debugger.info("tvdb", "Movie found", tvdb_id=movie_id, title=movie_name)
        
        # Get extended info
        raw_movie_extended = self.api.get_movie_extended(movie_id)
        
        # Fetch extras
        raw_extras = {}
        if self.extras_config.get('movies_extended'):
            raw_extras['movies_extended'] = raw_movie_extended
            self.debugger.debug("tvdb", "Fetched movies_extended", endpoint="/movies/{id}/extended")
        
        # Normalize (DEFAULT OUTPUT)
        normalized_movie = self.normalizer.normalize_movie(raw_movie_extended)
        
        end_time = datetime.now()
        result = {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': int((end_time - start_time).total_seconds() * 1000)
            },
            'movie': normalized_movie,  # NORMALIZED by default
            'show': None,
            'season': None,
            'episode': None
        }
        
        # Add RAW data ONLY if requested
        if self.include_raw:
            result['raw'] = {
                'movie': {
                    'name': raw_movie_extended.get('data', {}).get('name'),
                    'year': year,
                    'tvdb_id': movie_id,
                    'overview': raw_movie_extended.get('data', {}).get('overview'),
                    'runtime': raw_movie_extended.get('data', {}).get('runtime')
                },
                'extras': raw_extras
            }
        
        self.debugger.debug("tvdb", "Movie normalized",
                           tvdb_id=movie_id,
                           title=normalized_movie['title']['primary'],
                           include_raw=self.include_raw)
        
        return result
    
    def _perform_validation(self, match_data: Dict[str, Any], tvdb_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation tests (duration matching)
        
        Returns:
            {tests_passed, tests_total, details}
        """
        tests = {}
        tests_passed = 0
        tests_total = 0
        
        # Get ffprobe duration
        ffprobe_data = match_data.get('ffprobe', {})
        container = ffprobe_data.get('container', {})
        ffprobe_duration = container.get('duration', 0)
        
        if ffprobe_duration > 0:
            runtime_minutes = None
            
            # Check movie runtime
            if tvdb_result.get('movie'):
                runtime_minutes = tvdb_result['movie'].get('runtime')
            
            # Check episode runtime
            elif tvdb_result.get('episode'):
                runtime_minutes = tvdb_result['episode'].get('runtime')
            
            # Perform validation if runtime available
            if runtime_minutes:
                validation_result = self._validate_duration(
                    ffprobe_duration,
                    runtime_minutes,
                    tolerance_seconds=600  # 10 minutes
                )
                
                tests['duration_match'] = validation_result.details
                tests_total += 1
                if validation_result.passed:
                    tests_passed += 1
        
        return {
            'tests_passed': tests_passed,
            'tests_total': tests_total,
            'details': tests
        }
    
    def _fetch_show(self, show_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Fetch TV show metadata"""
        show_name = show_data.get('name')
        season_num = show_data.get('season')
        episode_num = show_data.get('episode')
        
        # Search series
        search_results = self.api.search_series(show_name)
        
        if not search_results.get('data'):
            return self._error_result()
        
        series_id = search_results['data'][0]['tvdb_id']
        self.debugger.info("tvdb", "TV show found", tvdb_id=series_id, title=show_name)
        
        # Get extended info
        raw_series_extended = self.api.get_series_extended(series_id)
        
        # Fetch extras
        raw_extras = {}
        if self.extras_config.get('series_extended'):
            raw_extras['series_extended'] = raw_series_extended
            self.debugger.debug("tvdb", "Fetched series_extended", endpoint="/series/{id}/extended")
        
        if self.extras_config.get('series_artworks'):
            artworks = self.extras_client.series_artworks(series_id)
            if artworks:
                raw_extras['series_artworks'] = artworks
                self.debugger.debug("tvdb", "Fetched series_artworks", endpoint="/series/{id}/artworks")
        
        # Normalize (DEFAULT OUTPUT)
        normalized_show = self.normalizer.normalize_show(raw_series_extended)
        
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
            'season': None,
            'episode': None,
            'movie': None
        }
        
        # Add RAW data ONLY if requested
        if self.include_raw:
            result['raw'] = {
                'show': {
                    'name': raw_series_extended.get('data', {}).get('name'),
                    'tvdb_id': str(series_id)
                },
                'season': {'number': season_num},
                'episode': {'number': episode_num},
                'extras': raw_extras
            }
        
        self.debugger.debug("tvdb", "TV show normalized",
                           tvdb_id=series_id,
                           title=normalized_show['title']['primary'],
                           include_raw=self.include_raw)
        
        return result
    
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
