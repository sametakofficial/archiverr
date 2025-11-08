# plugins/tmdb/extras.py
"""
TMDb Extra Metadata Fetcher
Handles optional metadata endpoints: credits, images, videos, keywords, etc.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List

TMDB_BASE = "https://api.themoviedb.org/3"


class TMDbExtras:
    """
    TMDb Extra Metadata API wrapper.
    Fetches optional metadata like credits, images, videos, keywords.
    """
    
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to TMDb API"""
        import requests
        url = f"{TMDB_BASE}/{endpoint.lstrip('/')}"
        params = params or {}
        params['api_key'] = self.api_key
        
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    # ========================================================================
    # MOVIE EXTRAS
    # ========================================================================
    
    def movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """
        Get movie credits (cast & crew).
        Returns normalized credits dict.
        """
        data = self._get(f"movie/{movie_id}/credits")
        return self._normalize_credits(data)
    
    def movie_images(self, movie_id: int) -> Dict[str, Any]:
        """
        Get movie images (posters, backdrops).
        Returns normalized images dict.
        """
        data = self._get(f"movie/{movie_id}/images")
        return self._normalize_images(data)
    
    def movie_videos(self, movie_id: int) -> Dict[str, Any]:
        """
        Get movie videos (trailers, teasers, clips).
        Returns normalized videos dict.
        """
        data = self._get(f"movie/{movie_id}/videos")
        return self._normalize_videos(data)
    
    def movie_keywords(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get movie keywords.
        Returns list of keyword dicts with name and id.
        """
        data = self._get(f"movie/{movie_id}/keywords")
        keywords = data.get('keywords', [])
        return [
            {
                'id': kw.get('id'),
                'name': kw.get('name')
            }
            for kw in keywords if kw.get('name')
        ]
    
    def movie_external_ids(self, movie_id: int) -> Dict[str, str]:
        """
        Get movie external IDs (IMDB, Facebook, Instagram, Twitter).
        Returns dict of external IDs.
        """
        data = self._get(f"movie/{movie_id}/external_ids")
        return {
            'imdb_id': data.get('imdb_id'),
            'facebook_id': data.get('facebook_id'),
            'instagram_id': data.get('instagram_id'),
            'twitter_id': data.get('twitter_id'),
        }
    
    def movie_watch_providers(self, movie_id: int, region: str = 'US') -> Dict[str, Any]:
        """
        Get movie watch providers (streaming, rent, buy).
        Returns normalized watch providers dict.
        """
        data = self._get(f"movie/{movie_id}/watch/providers")
        results = data.get('results', {})
        region_data = results.get(region, {})
        return self._normalize_watch_providers(region_data)
    
    # ========================================================================
    # TV SERIES EXTRAS
    # ========================================================================
    
    def tv_credits(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV series credits (cast & crew for the show).
        Returns normalized credits dict.
        """
        data = self._get(f"tv/{tv_id}/credits")
        return self._normalize_credits(data)
    
    def tv_aggregate_credits(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV series aggregate credits (all cast across all seasons).
        Returns normalized aggregate credits dict.
        """
        data = self._get(f"tv/{tv_id}/aggregate_credits")
        return self._normalize_aggregate_credits(data)
    
    def tv_images(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV series images (posters, backdrops).
        Returns normalized images dict.
        """
        data = self._get(f"tv/{tv_id}/images")
        return self._normalize_images(data)
    
    def tv_videos(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV series videos (trailers, teasers).
        Returns normalized videos dict.
        """
        data = self._get(f"tv/{tv_id}/videos")
        return self._normalize_videos(data)
    
    def tv_keywords(self, tv_id: int) -> List[Dict[str, Any]]:
        """
        Get TV series keywords.
        Returns list of keyword dicts with name and id.
        """
        data = self._get(f"tv/{tv_id}/keywords")
        keywords = data.get('results', [])
        return [
            {
                'id': kw.get('id'),
                'name': kw.get('name')
            }
            for kw in keywords if kw.get('name')
        ]
    
    def tv_external_ids(self, tv_id: int) -> Dict[str, str]:
        """
        Get TV series external IDs (IMDB, TVDB, Facebook, etc.).
        Returns dict of external IDs.
        """
        data = self._get(f"tv/{tv_id}/external_ids")
        return {
            'imdb_id': data.get('imdb_id'),
            'tvdb_id': str(data.get('tvdb_id')) if data.get('tvdb_id') else '',
            'facebook_id': data.get('facebook_id'),
            'instagram_id': data.get('instagram_id'),
            'twitter_id': data.get('twitter_id'),
        }
    
    def tv_content_ratings(self, tv_id: int) -> List[Dict[str, str]]:
        """
        Get TV series content ratings (age ratings by country).
        Returns list of rating dicts.
        """
        data = self._get(f"tv/{tv_id}/content_ratings")
        results = data.get('results', [])
        return [
            {
                'iso_3166_1': item.get('iso_3166_1'),
                'rating': item.get('rating')
            }
            for item in results
            if item.get('iso_3166_1') and item.get('rating')
        ]
    
    def tv_watch_providers(self, tv_id: int, region: str = 'US') -> Dict[str, Any]:
        """
        Get TV series watch providers (streaming, rent, buy).
        Returns normalized watch providers dict.
        """
        data = self._get(f"tv/{tv_id}/watch/providers")
        results = data.get('results', {})
        region_data = results.get(region, {})
        return self._normalize_watch_providers(region_data)
    
    # ========================================================================
    # TV SEASON EXTRAS
    # ========================================================================
    
    def season_credits(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        """
        Get TV season credits (cast & crew for specific season).
        Returns normalized credits dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/credits")
        return self._normalize_credits(data)
    
    def season_images(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        """
        Get TV season images (posters).
        Returns normalized images dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/images")
        return self._normalize_images(data)
    
    def season_videos(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        """
        Get TV season videos.
        Returns normalized videos dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/videos")
        return self._normalize_videos(data)
    
    # ========================================================================
    # TV EPISODE EXTRAS
    # ========================================================================
    
    def episode_credits(self, tv_id: int, season_number: int, episode_number: int) -> Dict[str, Any]:
        """
        Get TV episode credits (cast & crew for specific episode).
        Returns normalized credits dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/episode/{episode_number}/credits")
        return self._normalize_credits(data)
    
    def episode_images(self, tv_id: int, season_number: int, episode_number: int) -> Dict[str, Any]:
        """
        Get TV episode images (stills).
        Returns normalized images dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/episode/{episode_number}/images")
        return self._normalize_images(data)
    
    def episode_videos(self, tv_id: int, season_number: int, episode_number: int) -> Dict[str, Any]:
        """
        Get TV episode videos.
        Returns normalized videos dict.
        """
        data = self._get(f"tv/{tv_id}/season/{season_number}/episode/{episode_number}/videos")
        return self._normalize_videos(data)
    
    # ========================================================================
    # NORMALIZATION HELPERS
    # ========================================================================
    
    def _normalize_credits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize credits response.
        
        Returns:
            {
                'cast': [{'name': str, 'character': str, 'order': int, 'profile_path': str}, ...],
                'crew': [{'name': str, 'job': str, 'department': str, 'profile_path': str}, ...],
            }
        """
        cast = []
        for person in data.get('cast', []):
            cast.append({
                'name': person.get('name'),
                'character': person.get('character'),
                'order': person.get('order'),
                'profile_path': person.get('profile_path'),
                'id': person.get('id'),
            })
        
        crew = []
        for person in data.get('crew', []):
            crew.append({
                'name': person.get('name'),
                'job': person.get('job'),
                'department': person.get('department'),
                'profile_path': person.get('profile_path'),
                'id': person.get('id'),
            })
        
        return {'cast': cast, 'crew': crew}
    
    def _normalize_aggregate_credits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize aggregate credits (TV series all seasons).
        
        Returns:
            {
                'cast': [{'name': str, 'roles': [{'character': str, 'episode_count': int}], ...}],
                'crew': [{'name': str, 'jobs': [{'job': str, 'episode_count': int}], ...}],
            }
        """
        cast = []
        for person in data.get('cast', []):
            roles = []
            for role in person.get('roles', []):
                roles.append({
                    'character': role.get('character'),
                    'episode_count': role.get('episode_count'),
                })
            cast.append({
                'name': person.get('name'),
                'roles': roles,
                'total_episode_count': person.get('total_episode_count'),
                'profile_path': person.get('profile_path'),
                'id': person.get('id'),
            })
        
        crew = []
        for person in data.get('crew', []):
            jobs = []
            for job in person.get('jobs', []):
                jobs.append({
                    'job': job.get('job'),
                    'episode_count': job.get('episode_count'),
                })
            crew.append({
                'name': person.get('name'),
                'jobs': jobs,
                'total_episode_count': person.get('total_episode_count'),
                'profile_path': person.get('profile_path'),
                'id': person.get('id'),
            })
        
        return {'cast': cast, 'crew': crew}
    
    def _normalize_images(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize images response.
        
        Returns:
            {
                'posters': [{'path': str, 'width': int, 'height': int, 'aspect_ratio': float}, ...],
                'backdrops': [{'path': str, 'width': int, 'height': int, 'aspect_ratio': float}, ...],
            }
        """
        posters = []
        for img in data.get('posters', []):
            posters.append({
                'path': img.get('file_path'),
                'width': img.get('width'),
                'height': img.get('height'),
                'aspect_ratio': img.get('aspect_ratio'),
                'vote_average': img.get('vote_average'),
            })
        
        backdrops = []
        for img in data.get('backdrops', []):
            backdrops.append({
                'path': img.get('file_path'),
                'width': img.get('width'),
                'height': img.get('height'),
                'aspect_ratio': img.get('aspect_ratio'),
                'vote_average': img.get('vote_average'),
            })
        
        return {'posters': posters, 'backdrops': backdrops}
    
    def _normalize_videos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize videos response.
        
        Returns:
            {
                'trailers': [{'key': str, 'site': str, 'name': str, 'type': str}, ...],
                'teasers': [...],
                'clips': [...],
            }
        """
        videos_by_type = {'trailers': [], 'teasers': [], 'clips': [], 'other': []}
        
        for video in data.get('results', []):
            video_type = video.get('type', '').lower()
            normalized = {
                'key': video.get('key'),
                'site': video.get('site'),
                'name': video.get('name'),
                'type': video.get('type'),
                'size': video.get('size'),
            }
            
            if video_type == 'trailer':
                videos_by_type['trailers'].append(normalized)
            elif video_type == 'teaser':
                videos_by_type['teasers'].append(normalized)
            elif video_type == 'clip':
                videos_by_type['clips'].append(normalized)
            else:
                videos_by_type['other'].append(normalized)
        
        return videos_by_type
    
    def _normalize_watch_providers(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize watch providers response.
        
        Returns:
            {
                'link': str,
                'flatrate': [{'name': str, 'logo_path': str}, ...],  # Streaming
                'rent': [...],
                'buy': [...],
            }
        """
        def normalize_providers(providers):
            return [
                {'name': p.get('provider_name'), 'logo_path': p.get('logo_path'), 'id': p.get('provider_id')}
                for p in providers
            ]
        
        return {
            'link': region_data.get('link'),
            'flatrate': normalize_providers(region_data.get('flatrate', [])),
            'rent': normalize_providers(region_data.get('rent', [])),
            'buy': normalize_providers(region_data.get('buy', [])),
        }
