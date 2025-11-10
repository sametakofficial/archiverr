# plugins/tvdb/normalize/normalizer.py
"""TVDb Response Normalizer"""
from typing import Dict, Any, List


class TVDbNormalizer:
    """Normalize TVDb API responses to community standard format"""
    
    def normalize_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize movie response from /movies/{id}/extended"""
        if not movie_data or not movie_data.get('data'):
            return {}
        
        data = movie_data['data']
        
        # Extract IDs from remoteIds
        imdb_id = None
        tmdb_id = None
        for remote in data.get('remoteIds', []):
            if remote.get('sourceName') == 'IMDB':
                imdb_id = remote.get('id')
            elif remote.get('sourceName') == 'TheMovieDB.com':
                tmdb_id = remote.get('id')
        
        normalized = {
            'media_type': 'movie',
            'identifiers': {
                'tvdb_id': str(data.get('id', '')),
                'imdb_id': imdb_id,
                'tmdb_id': tmdb_id
            },
            'title': {
                'primary': data.get('name'),
                'original': data.get('name')
            },
            'release': {
                'year': int(data.get('year')) if data.get('year') else None,
                'status': data.get('status', {}).get('name')
            },
            'runtime': data.get('runtime'),
            'ratings': {
                'tvdb': {
                    'score': data.get('score')
                }
            },
            'genres': [g.get('name') for g in data.get('genres', [])],
            'people': self._normalize_characters(data.get('characters', []))
        }
        
        return normalized
    
    def normalize_show(self, show_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize show response from /series/{id}/extended"""
        if not show_data or not show_data.get('data'):
            return {}
        
        data = show_data['data']
        
        # Extract IDs
        imdb_id = None
        tmdb_id = None
        for remote in data.get('remoteIds', []):
            if remote.get('sourceName') == 'IMDB':
                imdb_id = remote.get('id')
            elif remote.get('sourceName') == 'TheMovieDB.com':
                tmdb_id = remote.get('id')
        
        normalized = {
            'media_type': 'show',
            'identifiers': {
                'tvdb_id': str(data.get('id', '')),
                'imdb_id': imdb_id,
                'tmdb_id': tmdb_id
            },
            'title': {
                'primary': data.get('name'),
                'original': data.get('name')
            },
            'air_dates': {
                'first': data.get('firstAired'),
                'last': data.get('lastAired'),
                'year': int(data.get('year')) if data.get('year') else None
            },
            'status': data.get('status', {}).get('name'),
            'runtime': data.get('averageRuntime'),
            'ratings': {
                'tvdb': {
                    'score': data.get('score')
                }
            },
            'genres': [g.get('name') for g in data.get('genres', [])],
            'network': {
                'name': data.get('network', {}).get('name') if data.get('network') else None,
                'id': str(data.get('network', {}).get('id')) if data.get('network') else None
            } if data.get('network') else {},
            'people': self._normalize_characters(data.get('characters', []))
        }
        
        return normalized
    
    def _normalize_characters(self, characters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize characters into cast and crew"""
        cast = []
        crew = []
        
        for char in characters:
            person = {
                'id': str(char.get('peopleId', '')),
                'name': char.get('personName'),
                'character': char.get('name')
            }
            
            # type 3 is actor/cast
            if char.get('type') == 3:
                cast.append(person)
            else:
                crew.append(person)
        
        return {
            'cast': cast,
            'crew': crew
        }
