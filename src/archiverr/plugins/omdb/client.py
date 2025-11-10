"""OMDb Plugin - Movie & Show Metadata"""
from typing import Dict, Any
import requests
from datetime import datetime
from .normalize.normalizer import OMDbNormalizer
from archiverr.utils.debug import get_debugger
from archiverr.plugins.base import OutputPlugin


class OMDbPlugin(OutputPlugin):
    """Output plugin that fetches metadata from OMDb API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "omdb"
        self.api_key = config.get('api_key', '')
        self.include_raw = config.get('include-raw', False)  # Default: no raw data
        self.normalizer = OMDbNormalizer()
        self.debugger = get_debugger()
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch metadata from OMDb.
        
        Args:
            match_data: Must contain category in input and renamer parsed data
            
        Returns:
            {status, movie: {...}, show: {...}}
        """
        if not self.api_key:
            return self._not_supported_result()
        
        # Check category - OMDb only supports movie and show
        input_metadata = match_data.get('input', {})
        category = input_metadata.get('category', 'unknown')
        
        if category not in ['movie', 'show']:
            self.debugger.debug("omdb", "Category not supported", category=category)
            return self._not_supported_result()
        
        start_time = datetime.now()
        
        parsed = match_data.get('renamer', {}).get('parsed', {})
        movie_data = parsed.get('movie')
        show_data = parsed.get('show')
        
        self.debugger.debug("omdb", "Processing request", category=category)
        
        result = {
            'status': {
                'success': False,
                'started_at': start_time.isoformat(),
                'finished_at': '',
                'duration_ms': 0
            },
            'movie': None,
            'show': None
        }
        
        # Search movie
        if category == 'movie' and movie_data and movie_data.get('name'):
            movie_name = movie_data.get('name')
            year = movie_data.get('year')
            
            try:
                params = {'apikey': self.api_key, 't': movie_name, 'type': 'movie'}
                if year:
                    params['y'] = year
                
                response = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
                data = response.json()
                
                if data.get('Response') == 'True':
                    # Normalize (DEFAULT OUTPUT)
                    normalized_movie = self.normalizer.normalize_movie(data)
                    result['movie'] = normalized_movie
                    
                    # Add RAW data ONLY if requested (ALL OMDb fields)
                    if self.include_raw:
                        result['raw'] = {
                            'movie': data  # Complete raw response
                        }
                    
                    result['status']['success'] = True
                    
                    # Add validation
                    result['validation'] = self._perform_validation(match_data, data)
                    
                    self.debugger.info("omdb", "Movie found", title=data.get('Title'), imdb_rating=data.get('imdbRating'))
                    self.debugger.debug("omdb", "Movie normalized", imdb_id=data.get('imdbID'), title=normalized_movie['title']['primary'], include_raw=self.include_raw)
                else:
                    # Movie not found in OMDb - this is expected, not an error
                    result['status']['success'] = True  # Still success, just no data
                    self.debugger.debug("omdb", "Movie not found in OMDb", title=movie_name)
            except Exception:
                # Real error (network, timeout, etc.) - mark as failed
                result['status']['success'] = False
        
        # Search show
        elif category == 'show' and show_data and show_data.get('name'):
            show_name = show_data.get('name')
            
            try:
                params = {'apikey': self.api_key, 't': show_name, 'type': 'series'}
                
                response = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
                data = response.json()
                
                if data.get('Response') == 'True':
                    # Normalize (DEFAULT OUTPUT)
                    normalized_show = self.normalizer.normalize_show(data)
                    result['show'] = normalized_show
                    
                    # Add RAW data ONLY if requested (ALL OMDb fields)
                    if self.include_raw:
                        result['raw'] = {
                            'show': data  # Complete raw response
                        }
                    
                    result['status']['success'] = True
                    self.debugger.debug("omdb", "TV show normalized", imdb_id=data.get('imdbID'), title=normalized_show['title']['primary'], include_raw=self.include_raw)
                else:
                    # Show not found in OMDb - this is expected, not an error
                    result['status']['success'] = True  # Still success, just no data
            except Exception:
                # Real error (network, timeout, etc.) - mark as failed
                result['status']['success'] = False
        
        # Set finished time and duration
        end_time = datetime.now()
        result['status']['finished_at'] = end_time.isoformat()
        result['status']['duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
        
        return result
    
    def _perform_validation(self, match_data: Dict[str, Any], omdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation tests (duration matching)
        
        Returns:
            {tests_passed, tests_total, details}
        """
        tests = {}
        tests_passed = 0
        tests_total = 0
        
        # Duration validation
        ffprobe_data = match_data.get('ffprobe', {})
        container = ffprobe_data.get('container', {})
        ffprobe_duration = container.get('duration', 0)
        
        if ffprobe_duration > 0:
            # Parse runtime from OMDb ("120 min" -> 120)
            runtime_str = omdb_data.get('Runtime', '')
            runtime_minutes = None
            
            if runtime_str and 'min' in runtime_str:
                try:
                    runtime_minutes = int(runtime_str.replace('min', '').strip())
                except (ValueError, AttributeError):
                    pass
            
            # Perform validation
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
            'show': None
        }
