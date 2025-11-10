"""TMDb Plugin - Clean orchestration layer"""
from typing import Dict, Any
from datetime import datetime
from .extras import TMDbExtras
from .normalize.normalizer import TMDbNormalizer
from .utils.api import TMDbAPI
from .utils.fetchers import TMDbMovieFetcher, TMDbShowFetcher
from archiverr.utils.debug import get_debugger
from archiverr.plugins.base import OutputPlugin


class TMDbPlugin(OutputPlugin):
    """
    TMDb metadata plugin - Orchestrates data fetching, extras, and normalization
    
    Architecture:
    - utils/api.py: Low-level API requests
    - utils/fetchers.py: High-level data fetching + extras
    - normalize/normalizer.py: Response normalization to community standard
    - extras.py: Raw endpoint calls
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.lang = config.get('language', config.get('lang', 'en-US'))
        self.region = config.get('region', 'TR')
        self.include_raw = config.get('include-raw', False)  # Default: no raw data
        self.debugger = get_debugger()
        
        # Initialize components
        self.api = TMDbAPI(self.api_key, self.lang, self.region)
        self.extras_client = TMDbExtras(self.api_key, self.lang)
        self.normalizer = TMDbNormalizer()
        
        # Get extras configuration
        self.extras_config = config.get('extras', {})
        
        # Initialize fetchers
        self.movie_fetcher = TMDbMovieFetcher(
            self.api, self.extras_client, self.normalizer,
            self.extras_config, self.include_raw, self.debugger
        )
        self.show_fetcher = TMDbShowFetcher(
            self.api, self.extras_client, self.normalizer,
            self.extras_config, self.include_raw, self.debugger
        )
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch metadata from TMDb
        
        Args:
            match_data: Must contain 'renamer.parsed' with show or movie info
            
        Returns:
            {status, episode, season, show, movie, extras, normalized}
        """
        # Get parsed data
        renamer_data = match_data.get('renamer', {})
        parsed_data = renamer_data.get('parsed', {})
        
        if not parsed_data:
            return self._error_result()
        
        # Route to appropriate fetcher
        movie_data = parsed_data.get('movie')
        show_data = parsed_data.get('show')
        
        try:
            result = None
            if movie_data and movie_data.get('name'):
                result = self.movie_fetcher.fetch(
                    movie_data.get('name'),
                    movie_data.get('year')
                )
            elif show_data and show_data.get('name'):
                result = self.show_fetcher.fetch(
                    show_data.get('name'),
                    show_data.get('season'),
                    show_data.get('episode')
                )
            else:
                return self._error_result()
            
            # Add validation if result successful
            if result and result.get('status', {}).get('success'):
                result['validation'] = self._perform_validation(match_data, result)
            
            return result
                
        except Exception as e:
            self.debugger.error("tmdb", "Execution failed", error=str(e))
            return self._error_result()
    
    def _perform_validation(self, match_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation tests (e.g., duration matching)
        
        Returns:
            {tests_passed, tests_total, details}
        """
        tests = {}
        tests_passed = 0
        tests_total = 0
        
        # Duration validation (for movies and episodes)
        ffprobe_data = match_data.get('ffprobe', {})
        container = ffprobe_data.get('container', {})
        ffprobe_duration = container.get('duration', 0)
        
        if ffprobe_duration > 0:
            # Get runtime from result
            runtime_minutes = None
            if result.get('movie'):
                runtime_minutes = result['movie'].get('runtime')
            elif result.get('episode'):
                runtime_minutes = result['episode'].get('runtime')
            
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
            'episode': None,
            'season': None,
            'show': None,
            'extras': {},
            'normalized': {}
        }
