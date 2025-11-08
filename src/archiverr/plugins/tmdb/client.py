"""TMDb Plugin - Fetch metadata from The Movie Database"""
import requests
from typing import Dict, Any
from datetime import datetime
from .extras import TMDbExtras


class TMDbPlugin:
    """Output plugin that fetches movie/show metadata from TMDb API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "tmdb"
        self.category = "output"
        self.api_key = config.get('api_key', '')
        self.lang = config.get('lang', 'en-US')
        self.region = config.get('region', 'TR')
        
        # Initialize extras client
        self.extras_client = TMDbExtras(self.api_key)
        
        # Get extras configuration
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
            return self._fetch_movie(movie_data)
        
        # Try show
        if show_data and show_data.get('name'):
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
                return self._error_result()
            
            show = search_data['results'][0]
            show_id = show['id']
            
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
            
            # Fetch extras for TV show
            extras = {}
            episode_id = episode.get('id')
            
            if self.extras_config.get('episode_credits') and episode_id:
                credits = self.extras_client.episode_credits(show_id, season_num, episode_num)
                if credits:
                    extras['episode_cast'] = credits.get('cast', [])[:10]
                    extras['episode_crew'] = credits.get('crew', [])[:10]
            
            if self.extras_config.get('episode_images') and episode_id:
                images = self.extras_client.episode_images(show_id, season_num, episode_num)
                if images:
                    extras['episode_images'] = images
            
            if self.extras_config.get('show_images'):
                images = self.extras_client.tv_images(show_id)
                if images:
                    extras['show_images'] = images
            
            if self.extras_config.get('show_videos'):
                videos = self.extras_client.tv_videos(show_id)
                if videos:
                    extras['show_videos'] = videos
            
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
                return self._error_result()
            
            movie = search_data['results'][0]
            movie_id = movie['id']
            
            # Get movie details
            movie_url = f"{self.BASE_URL}/movie/{movie_id}"
            movie_params = {
                'api_key': self.api_key,
                'language': self.lang
            }
            
            movie_resp = requests.get(movie_url, params=movie_params, timeout=10)
            movie_resp.raise_for_status()
            movie_details = movie_resp.json()
            
            extras = {}
            
            # Fetch extras using extras client
            if self.extras_config.get('movie_credits'):
                credits = self.extras_client.movie_credits(movie_id)
                if credits:
                    extras['cast'] = credits.get('cast', [])[:10]
                    extras['crew'] = credits.get('crew', [])[:10]
            
            if self.extras_config.get('movie_images'):
                images = self.extras_client.movie_images(movie_id)
                if images:
                    extras['images'] = images
            
            if self.extras_config.get('movie_videos'):
                videos = self.extras_client.movie_videos(movie_id)
                if videos:
                    extras['videos'] = videos
            
            if self.extras_config.get('movie_keywords'):
                keywords = self.extras_client.movie_keywords(movie_id)
                if keywords:
                    extras['keywords'] = [k['name'] for k in keywords[:10]]
            
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
