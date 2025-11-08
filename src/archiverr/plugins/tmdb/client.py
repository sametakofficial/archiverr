"""TMDb Plugin - Fetch metadata from The Movie Database"""
import requests
from typing import Dict, Any
from datetime import datetime
from .extras import TMDbExtras
from archiverr.utils.debug import get_debugger


class TMDbPlugin:
    """Output plugin that fetches movie/show metadata from TMDb API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "tmdb"
        self.category = "output"
        self.api_key = config.get('api_key', '')
        self.lang = config.get('language', config.get('lang', 'en-US'))
        self.region = config.get('region', 'TR')
        self.debugger = get_debugger()
        
        # Initialize extras client with language support
        self.extras_client = TMDbExtras(self.api_key, self.lang)
        
        # Get extras configuration - endpoint-based
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch metadata from TMDb.
        
        Args:
            match_data: Must contain 'renamer.parsed' with show or movie info
            
        Returns:
            {status, episode, season, show, movie, extras}
        """
        start_time = datetime.now()
        if not self.api_key:
            return self._error_result()
        
        # Get parsed data
        renamer = match_data.get('renamer', {})
        parsed = renamer.get('parsed', {})
        
        show_data = parsed.get('show')
        movie_data = parsed.get('movie')
        
        # Try movie FIRST (year is strong indicator)
        if movie_data and movie_data.get('name') and movie_data.get('year'):
            self.debugger.debug("tmdb", "Processing as movie", name=movie_data['name'], year=movie_data.get('year'))
            return self._fetch_movie(movie_data)
        
        # Try show
        if show_data and show_data.get('name'):
            self.debugger.debug("tmdb", "Processing as show", name=show_data['name'], 
                              season=show_data.get('season'), episode=show_data.get('episode'))
            return self._fetch_show(show_data)
        
        return self._error_result()
    
    def _fetch_show(self, show_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch TV show metadata"""
        start_time = datetime.now()
        show_name = show_data.get('name')
        season_num = show_data.get('season', 1)
        episode_num = show_data.get('episode', 1)
        
        try:
            # Search for show
            search_url = f"{self.BASE_URL}/search/tv"
            search_params = {
                'api_key': self.api_key,
                'language': self.lang,
                'query': show_name
            }
            
            search_resp = requests.get(search_url, params=search_params, timeout=10)
            search_resp.raise_for_status()
            search_data = search_resp.json()
            
            if not search_data.get('results'):
                self.debugger.warn("tmdb", "No TV show found", query=show_name)
                return self._error_result()
            
            show = search_data['results'][0]
            show_id = show['id']
            self.debugger.info("tmdb", "TV show match found", tmdb_id=show_id, name=show.get('name'))
            
            # Get episode details
            episode_url = f"{self.BASE_URL}/tv/{show_id}/season/{season_num}/episode/{episode_num}"
            episode_params = {
                'api_key': self.api_key,
                'language': self.lang
            }
            
            episode_resp = requests.get(episode_url, params=episode_params, timeout=10)
            episode_resp.raise_for_status()
            episode = episode_resp.json()
            
            # Get season details
            season_url = f"{self.BASE_URL}/tv/{show_id}/season/{season_num}"
            season_params = episode_params
            season_resp = requests.get(season_url, params=season_params, timeout=10)
            season_resp.raise_for_status()
            season = season_resp.json()
            
            # Get show details
            show_url = f"{self.BASE_URL}/tv/{show_id}"
            show_resp = requests.get(show_url, params=episode_params, timeout=10)
            show_resp.raise_for_status()
            show_details = show_resp.json()
            
            # Fetch extras - Endpoint-Based System (RAW API responses)
            extras = {}
            
            # TV Credits Endpoint
            if self.extras_config.get('tv_credits'):
                data = self.extras_client.tv_credits(show_id)
                if data:
                    extras['tv_credits'] = data
            
            # TV Images Endpoint
            if self.extras_config.get('tv_images'):
                data = self.extras_client.tv_images(show_id)
                if data:
                    extras['tv_images'] = data
            
            # TV Videos Endpoint
            if self.extras_config.get('tv_videos'):
                data = self.extras_client.tv_videos(show_id)
                if data:
                    extras['tv_videos'] = data
            
            # TV Keywords Endpoint
            if self.extras_config.get('tv_keywords'):
                data = self.extras_client.tv_keywords(show_id)
                if data:
                    extras['tv_keywords'] = data
            
            # TV Season Images Endpoint
            if self.extras_config.get('tv_season_images'):
                data = self.extras_client.tv_season_images(show_id, season_num)
                if data:
                    extras['tv_season_images'] = data
            
            # TV Episode Credits Endpoint
            if self.extras_config.get('tv_episode_credits'):
                data = self.extras_client.tv_episode_credits(show_id, season_num, episode_num)
                if data:
                    extras['tv_episode_credits'] = data
            
            # TV Episode Images Endpoint
            if self.extras_config.get('tv_episode_images'):
                data = self.extras_client.tv_episode_images(show_id, season_num, episode_num)
                if data:
                    extras['tv_episode_images'] = data
            
            end_time = datetime.now()
            return {
                'status': {
                    'success': True,
                    'started_at': start_time.isoformat(),
                    'finished_at': end_time.isoformat(),
                    'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                },
                'episode': {
                    'name': episode.get('name', ''),
                    'number': episode.get('episode_number', 0),
                    'season': episode.get('season_number', 0),
                    'overview': episode.get('overview', ''),
                    'air_date': episode.get('air_date', ''),
                    'runtime': episode.get('runtime', 0),
                    'vote_average': episode.get('vote_average', 0),
                    'vote_count': episode.get('vote_count', 0)
                },
                'season': {
                    'number': season.get('season_number', 0),
                    'name': season.get('name', ''),
                    'overview': season.get('overview', ''),
                    'air_date': season.get('air_date', ''),
                    'episode_count': season.get('episode_count', 0)
                },
                'show': {
                    'name': show_details.get('name', ''),
                    'original_name': show_details.get('original_name', ''),
                    'overview': show_details.get('overview', ''),
                    'first_air_date': show_details.get('first_air_date', ''),
                    'vote_average': show_details.get('vote_average', 0),
                    'vote_count': show_details.get('vote_count', 0),
                    'genres': [g['name'] for g in show_details.get('genres', [])],
                    'networks': show_details.get('networks', []),
                    'number_of_seasons': show_details.get('number_of_seasons', 0),
                    'number_of_episodes': show_details.get('number_of_episodes', 0)
                },
                'movie': None,
                'extras': extras
            }
            
        except Exception:
            return self._error_result()
    
    def _fetch_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch movie metadata"""
        start_time = datetime.now()
        movie_name = movie_data.get('name')
        movie_year = movie_data.get('year')
        
        try:
            # Search for movie
            search_url = f"{self.BASE_URL}/search/movie"
            search_params = {
                'api_key': self.api_key,
                'language': self.lang,
                'query': movie_name
            }
            
            if movie_year:
                search_params['year'] = movie_year
            
            search_resp = requests.get(search_url, params=search_params, timeout=10)
            search_resp.raise_for_status()
            search_data = search_resp.json()
            
            if not search_data.get('results'):
                self.debugger.warn("tmdb", "No movie found", query=movie_name, year=movie_year)
                return self._error_result()
            
            movie = search_data['results'][0]
            movie_id = movie['id']
            self.debugger.info("tmdb", "Movie match found", tmdb_id=movie_id, title=movie.get('title'))
            
            # Get movie details
            movie_url = f"{self.BASE_URL}/movie/{movie_id}"
            movie_params = {
                'api_key': self.api_key,
                'language': self.lang
            }
            
            movie_resp = requests.get(movie_url, params=movie_params, timeout=10)
            movie_resp.raise_for_status()
            movie_details = movie_resp.json()
            
            # Fetch extras - Endpoint-Based System (RAW API responses)
            extras = {}
            
            # Movie Credits Endpoint
            if self.extras_config.get('movie_credits'):
                data = self.extras_client.movie_credits(movie_id)
                if data:
                    extras['movie_credits'] = data
            
            # Movie Images Endpoint
            if self.extras_config.get('movie_images'):
                data = self.extras_client.movie_images(movie_id)
                if data:
                    extras['movie_images'] = data
            
            # Movie Videos Endpoint
            if self.extras_config.get('movie_videos'):
                data = self.extras_client.movie_videos(movie_id)
                if data:
                    extras['movie_videos'] = data
            
            # Movie Keywords Endpoint
            if self.extras_config.get('movie_keywords'):
                data = self.extras_client.movie_keywords(movie_id)
                if data:
                    extras['movie_keywords'] = data
            
            end_time = datetime.now()
            return {
                'status': {
                    'success': True,
                    'started_at': start_time.isoformat(),
                    'finished_at': end_time.isoformat(),
                    'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                },
                'movie': {
                    'name': movie_details.get('title', ''),
                    'original_name': movie_details.get('original_title', ''),
                    'overview': movie_details.get('overview', ''),
                    'release_date': movie_details.get('release_date', ''),
                    'runtime': movie_details.get('runtime', 0),
                    'vote_average': movie_details.get('vote_average', 0),
                    'vote_count': movie_details.get('vote_count', 0),
                    'genres': [g['name'] for g in movie_details.get('genres', [])]
                },
                'episode': None,
                'season': None,
                'show': None,
                'extras': extras
            }
            
        except Exception:
            return self._error_result()
    
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
            'extras': {}
        }
