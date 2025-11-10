"""Renamer Plugin - Parse filenames and extract metadata"""
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import re
from .parser import sanitize_string, parse_show_name, parse_movie_name
from archiverr.utils.debug import get_debugger


class RenamerPlugin:
    """Output plugin that parses filenames to extract show/movie metadata"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "renamer"
        self.category = "output"
        self.media_type = config.get('media_type', 'auto')
        self.debugger = get_debugger()
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse filename and extract metadata.
        
        Args:
            match_data: Must contain 'input' with path
            
        Returns:
            {status, parsed: {show: {...}, movie: {...}}, category}
        """
        start_time = datetime.now()
        
        # Get input metadata from match
        input_metadata = match_data.get('input', {})
        input_path = input_metadata.get('path')
        
        if not input_path:
            return self._error_result()
        
        filename = Path(input_path).stem
        
        self.debugger.debug("renamer", "Parsing filename", filename=filename, mode=self.media_type)
        
        # Parse based on media_type config
        show_match = None
        movie_match = None
        
        if self.media_type == 'auto':
            # Try movie first (year is strong indicator)
            movie_match = self._parse_movie(filename)
            
            # Only try show if NO movie with year found
            if not (movie_match and movie_match.get('year')):
                show_match = self._parse_show(filename)
                movie_match = None  # Clear movie if we're treating as show
        elif self.media_type == 'show':
            # Only parse as TV show
            show_match = self._parse_show(filename)
        elif self.media_type == 'movie':
            # Only parse as movie
            movie_match = self._parse_movie(filename)
        
        # Determine category
        category = 'unknown'
        if movie_match and movie_match.get('name'):
            category = 'movie'
            self.debugger.info("renamer", "Detected movie", name=movie_match['name'], year=movie_match.get('year'))
        elif show_match and show_match.get('name'):
            category = 'show'
            self.debugger.info("renamer", "Detected show", name=show_match['name'], 
                             season=show_match.get('season'), episode=show_match.get('episode'))
        else:
            self.debugger.warn("renamer", "Could not detect category", filename=filename)
        
        # Calculate duration
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': duration_ms
            },
            'parsed': {
                'show': show_match,
                'movie': movie_match
            },
            'category': category
        }
    
    def _parse_show(self, filename: str) -> Dict[str, Any]:
        """Parse TV show format using parser.py"""
        try:
            show_name, season, episode, failed = parse_show_name(filename)
            if failed or not show_name:
                return None
            
            return {
                'name': show_name,
                'season': season,
                'episode': episode
            }
        except Exception:
            return None
    
    def _parse_movie(self, filename: str) -> Dict[str, Any]:
        """Parse movie format using parser.py"""
        try:
            movie_name, year = parse_movie_name(filename)
            if not movie_name:
                return None
            
            return {
                'name': movie_name,
                'year': year
            }
        except Exception:
            return None
    
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
            'parsed': {
                'show': None,
                'movie': None
            }
        }
