"""OMDb Plugin - Movie & Show Metadata"""
from typing import Dict, Any
import requests
from datetime import datetime
from archiverr.utils.debug import get_debugger


class OMDbPlugin:
    """Output plugin that fetches metadata from OMDb API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "omdb"
        self.category = "output"
        self.api_key = config.get('api_key', '')
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
                    result['movie'] = {
                        'name': data.get('Title'),
                        'year': data.get('Year'),
                        'rated': data.get('Rated'),
                        'runtime': data.get('Runtime'),
                        'genre': data.get('Genre'),
                        'director': data.get('Director'),
                        'actors': data.get('Actors'),
                        'plot': data.get('Plot'),
                        'imdb_rating': data.get('imdbRating'),
                        'imdb_id': data.get('imdbID'),
                        'box_office': data.get('BoxOffice'),
                        'awards': data.get('Awards')
                    }
                    result['status']['success'] = True
                    self.debugger.info("omdb", "Movie found", title=data.get('Title'), imdb_rating=data.get('imdbRating'))
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
                    result['show'] = {
                        'name': data.get('Title'),
                        'year': data.get('Year'),
                        'genre': data.get('Genre'),
                        'actors': data.get('Actors'),
                        'plot': data.get('Plot'),
                        'imdb_rating': data.get('imdbRating'),
                        'imdb_id': data.get('imdbID'),
                        'total_seasons': data.get('totalSeasons'),
                        'awards': data.get('Awards')
                    }
                    result['status']['success'] = True
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
