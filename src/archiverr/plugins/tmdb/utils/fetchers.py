"""TMDb data fetchers - High-level fetch operations"""
from typing import Dict, Any
from datetime import datetime
from .api import TMDbAPI
from ..extras import TMDbExtras
from ..normalize.normalizer import TMDbNormalizer
from archiverr.utils.debug import get_debugger


class TMDbMovieFetcher:
    """Fetch and process movie metadata"""
    
    def __init__(self, api: TMDbAPI, extras_client: TMDbExtras, normalizer: TMDbNormalizer, 
                 extras_config: Dict[str, Any], include_raw: bool, debugger):
        self.api = api
        self.extras_client = extras_client
        self.normalizer = normalizer
        self.extras_config = extras_config
        self.include_raw = include_raw
        self.debugger = debugger
    
    def fetch(self, movie_name: str, movie_year: int = None) -> Dict[str, Any]:
        """Fetch complete movie metadata with extras and normalization"""
        start_time = datetime.now()
        
        # Search movie
        search_results = self.api.search_movie(movie_name, movie_year, timeout=10)
        
        if not search_results.get('results'):
            return self._error_result(start_time)
        
        # Get first result
        movie_id = search_results['results'][0]['id']
        self.debugger.info("tmdb", "Movie found", tmdb_id=movie_id, title=movie_name)
        
        # Get movie details
        raw_movie_details = self.api.get_movie(movie_id, timeout=10)
        
        # Fetch extras
        raw_extras = self._fetch_extras(movie_id)
        
        # Normalize (THIS IS THE DEFAULT OUTPUT)
        normalized_movie = self.normalizer.normalize_movie(raw_movie_details, raw_extras)
        
        # Build result - NORMALIZED IS DEFAULT
        end_time = datetime.now()
        result = {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': int((end_time - start_time).total_seconds() * 1000)
            },
            'movie': normalized_movie,  # NORMALIZED by default
            'episode': None,
            'season': None,
            'show': None
        }
        
        # Add RAW data ONLY if requested
        if self.include_raw:
            result['raw'] = {
                'movie': {
                    'name': raw_movie_details.get('title', ''),
                    'original_name': raw_movie_details.get('original_title', ''),
                    'overview': raw_movie_details.get('overview', ''),
                    'release_date': raw_movie_details.get('release_date', ''),
                    'runtime': raw_movie_details.get('runtime', 0),
                    'vote_average': raw_movie_details.get('vote_average', 0),
                    'vote_count': raw_movie_details.get('vote_count', 0),
                    'genres': [g['name'] for g in raw_movie_details.get('genres', [])]
                },
                'extras': raw_extras
            }
        
        self.debugger.debug("tmdb", "Movie normalized",
                           tmdb_id=movie_id,
                           title=normalized_movie['title']['primary'],
                           cast_count=len(normalized_movie.get('people', {}).get('cast', [])),
                           crew_count=len(normalized_movie.get('people', {}).get('crew', [])),
                           include_raw=self.include_raw)
        
        return result
    
    def _fetch_extras(self, movie_id: int) -> Dict[str, Any]:
        """Fetch all enabled movie extras"""
        extras = {}
        
        # Movie Credits
        if self.extras_config.get('movie_credits'):
            data = self.extras_client.movie_credits(movie_id)
            if data:
                extras['movie_credits'] = data
                self.debugger.debug("tmdb", "Fetched movie_credits",
                                   endpoint="/movie/{id}/credits",
                                   cast=len(data.get('cast', [])),
                                   crew=len(data.get('crew', [])))
        
        # Movie Images
        if self.extras_config.get('movie_images'):
            data = self.extras_client.movie_images(movie_id)
            if data:
                extras['movie_images'] = data
                self.debugger.debug("tmdb", "Fetched movie_images",
                                   endpoint="/movie/{id}/images",
                                   posters=len(data.get('posters', [])),
                                   backdrops=len(data.get('backdrops', [])))
        
        # Movie Videos
        if self.extras_config.get('movie_videos'):
            data = self.extras_client.movie_videos(movie_id)
            if data:
                extras['movie_videos'] = data
                self.debugger.debug("tmdb", "Fetched movie_videos",
                                   endpoint="/movie/{id}/videos",
                                   count=len(data.get('results', [])))
        
        # Movie Keywords
        if self.extras_config.get('movie_keywords'):
            data = self.extras_client.movie_keywords(movie_id)
            if data:
                extras['movie_keywords'] = data
                self.debugger.debug("tmdb", "Fetched movie_keywords",
                                   endpoint="/movie/{id}/keywords",
                                   count=len(data.get('keywords', [])))
        
        return extras
    
    def _error_result(self, start_time: datetime) -> Dict[str, Any]:
        """Return error result"""
        now = datetime.now()
        return {
            'status': {
                'success': False,
                'started_at': start_time.isoformat(),
                'finished_at': now.isoformat(),
                'duration_ms': int((now - start_time).total_seconds() * 1000)
            },
            'movie': None,
            'episode': None,
            'season': None,
            'show': None,
            'extras': {}
        }


class TMDbShowFetcher:
    """Fetch and process TV show metadata"""
    
    def __init__(self, api: TMDbAPI, extras_client: TMDbExtras, normalizer: TMDbNormalizer,
                 extras_config: Dict[str, Any], include_raw: bool, debugger):
        self.api = api
        self.extras_client = extras_client
        self.normalizer = normalizer
        self.extras_config = extras_config
        self.include_raw = include_raw
        self.debugger = debugger
    
    def fetch(self, show_name: str, season_num: int, episode_num: int) -> Dict[str, Any]:
        """Fetch complete TV show metadata with extras and normalization"""
        start_time = datetime.now()
        
        # Search show
        search_results = self.api.search_tv(show_name, timeout=10)
        
        if not search_results.get('results'):
            return self._error_result(start_time)
        
        # Get first result
        show_id = search_results['results'][0]['id']
        self.debugger.info("tmdb", "TV show found", tmdb_id=show_id, title=show_name)
        
        # Get details
        raw_show_details = self.api.get_tv(show_id, timeout=10)
        raw_season = self.api.get_season(show_id, season_num, timeout=10)
        raw_episode = self.api.get_episode(show_id, season_num, episode_num, timeout=10)
        
        # Fetch extras
        raw_extras = self._fetch_extras(show_id, season_num, episode_num)
        
        # Normalize (THIS IS THE DEFAULT OUTPUT)
        normalized_show = self.normalizer.normalize_show(raw_show_details, raw_season, raw_episode, raw_extras)
        
        # Build result - NORMALIZED IS DEFAULT
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
                    'name': raw_show_details.get('name', ''),
                    'original_name': raw_show_details.get('original_name', ''),
                    'overview': raw_show_details.get('overview', ''),
                    'first_air_date': raw_show_details.get('first_air_date', ''),
                    'vote_average': raw_show_details.get('vote_average', 0),
                    'vote_count': raw_show_details.get('vote_count', 0),
                    'genres': [g['name'] for g in raw_show_details.get('genres', [])],
                    'networks': raw_show_details.get('networks', []),
                    'number_of_seasons': raw_show_details.get('number_of_seasons', 0),
                    'number_of_episodes': raw_show_details.get('number_of_episodes', 0)
                },
                'season': {
                    'number': raw_season.get('season_number', 0),
                    'name': raw_season.get('name', ''),
                    'overview': raw_season.get('overview', ''),
                    'air_date': raw_season.get('air_date', ''),
                    'episode_count': raw_season.get('episode_count', 0)
                },
                'episode': {
                    'name': raw_episode.get('name', ''),
                    'number': raw_episode.get('episode_number', 0),
                    'season': raw_episode.get('season_number', 0),
                    'overview': raw_episode.get('overview', ''),
                    'air_date': raw_episode.get('air_date', ''),
                    'runtime': raw_episode.get('runtime', 0),
                    'vote_average': raw_episode.get('vote_average', 0),
                    'vote_count': raw_episode.get('vote_count', 0)
                },
                'extras': raw_extras
            }
        
        self.debugger.debug("tmdb", "TV show normalized",
                           tmdb_id=show_id,
                           title=normalized_show['title']['primary'],
                           seasons=normalized_show['seasons']['total'],
                           episodes=normalized_show['episodes']['total'],
                           cast_count=len(normalized_show.get('people', {}).get('cast', [])),
                           include_raw=self.include_raw)
        
        return result
    
    def _fetch_extras(self, show_id: int, season_num: int, episode_num: int) -> Dict[str, Any]:
        """Fetch all enabled TV extras"""
        extras = {}
        
        # TV Credits
        if self.extras_config.get('tv_credits'):
            data = self.extras_client.tv_credits(show_id)
            if data:
                extras['tv_credits'] = data
                self.debugger.debug("tmdb", "Fetched tv_credits",
                                   endpoint="/tv/{id}/credits",
                                   cast=len(data.get('cast', [])),
                                   crew=len(data.get('crew', [])))
        
        # TV Images
        if self.extras_config.get('tv_images'):
            data = self.extras_client.tv_images(show_id)
            if data:
                extras['tv_images'] = data
                self.debugger.debug("tmdb", "Fetched tv_images",
                                   endpoint="/tv/{id}/images",
                                   posters=len(data.get('posters', [])),
                                   backdrops=len(data.get('backdrops', [])))
        
        # TV Videos
        if self.extras_config.get('tv_videos'):
            data = self.extras_client.tv_videos(show_id)
            if data:
                extras['tv_videos'] = data
                self.debugger.debug("tmdb", "Fetched tv_videos",
                                   endpoint="/tv/{id}/videos",
                                   count=len(data.get('results', [])))
        
        # TV Keywords
        if self.extras_config.get('tv_keywords'):
            data = self.extras_client.tv_keywords(show_id)
            if data:
                extras['tv_keywords'] = data
                self.debugger.debug("tmdb", "Fetched tv_keywords",
                                   endpoint="/tv/{id}/keywords",
                                   count=len(data.get('results', [])))
        
        # TV Season Images
        if self.extras_config.get('tv_season_images'):
            data = self.extras_client.tv_season_images(show_id, season_num)
            if data:
                extras['tv_season_images'] = data
                self.debugger.debug("tmdb", "Fetched tv_season_images",
                                   endpoint="/tv/{id}/season/{n}/images",
                                   posters=len(data.get('posters', [])))
        
        # TV Episode Credits
        if self.extras_config.get('tv_episode_credits'):
            data = self.extras_client.tv_episode_credits(show_id, season_num, episode_num)
            if data:
                extras['tv_episode_credits'] = data
                self.debugger.debug("tmdb", "Fetched tv_episode_credits",
                                   endpoint="/tv/{id}/season/{s}/episode/{e}/credits",
                                   cast=len(data.get('cast', [])),
                                   guest_stars=len(data.get('guest_stars', [])))
        
        # TV Episode Images
        if self.extras_config.get('tv_episode_images'):
            data = self.extras_client.tv_episode_images(show_id, season_num, episode_num)
            if data:
                extras['tv_episode_images'] = data
                self.debugger.debug("tmdb", "Fetched tv_episode_images",
                                   endpoint="/tv/{id}/season/{s}/episode/{e}/images",
                                   stills=len(data.get('stills', [])))
        
        return extras
    
    def _error_result(self, start_time: datetime) -> Dict[str, Any]:
        """Return error result"""
        now = datetime.now()
        return {
            'status': {
                'success': False,
                'started_at': start_time.isoformat(),
                'finished_at': now.isoformat(),
                'duration_ms': int((now - start_time).total_seconds() * 1000)
            },
            'movie': None,
            'episode': None,
            'season': None,
            'show': None,
            'extras': {}
        }
