"""OMDb Response Normalizer"""
from typing import Dict, Any


class OMDbNormalizer:
    """Normalize OMDb API responses to community standard format"""
    
    def normalize_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize movie response with ALL OMDb fields"""
        if not movie_data:
            return {}
        
        normalized = {
            'media_type': 'movie',
            'identifiers': {
                'imdb_id': movie_data.get('imdbID')
            },
            'title': {
                'primary': movie_data.get('Title'),
                'original': movie_data.get('Title')
            },
            'release': {
                'date': movie_data.get('Released'),
                'year': int(movie_data.get('Year', '0')) if movie_data.get('Year', '').isdigit() else None,
                'dvd': movie_data.get('DVD') if movie_data.get('DVD') != 'N/A' else None
            },
            'runtime': self._parse_runtime(movie_data.get('Runtime')),
            'ratings': self._parse_ratings(movie_data),
            'overview': movie_data.get('Plot') if movie_data.get('Plot') != 'N/A' else None,
            'genres': [g.strip() for g in movie_data.get('Genre', '').split(',') if g.strip()],
            'content_rating': movie_data.get('Rated') if movie_data.get('Rated') != 'N/A' else None,
            'people': {
                'director': [d.strip() for d in movie_data.get('Director', '').split(',') if d.strip() and d.strip() != 'N/A'],
                'writer': [w.strip() for w in movie_data.get('Writer', '').split(',') if w.strip() and w.strip() != 'N/A'],
                'actors': [a.strip() for a in movie_data.get('Actors', '').split(',') if a.strip() and a.strip() != 'N/A']
            },
            'production': {
                'company': movie_data.get('Production') if movie_data.get('Production') != 'N/A' else None,
                'country': [c.strip() for c in movie_data.get('Country', '').split(',') if c.strip()],
                'language': [l.strip() for l in movie_data.get('Language', '').split(',') if l.strip()]
            },
            'financial': {
                'box_office': movie_data.get('BoxOffice') if movie_data.get('BoxOffice') != 'N/A' else None
            },
            'awards': movie_data.get('Awards') if movie_data.get('Awards') != 'N/A' else None,
            'website': movie_data.get('Website') if movie_data.get('Website') != 'N/A' else None
        }
        
        return normalized
    
    def normalize_show(self, show_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TV show response with ALL OMDb fields"""
        if not show_data:
            return {}
        
        normalized = {
            'media_type': 'show',
            'identifiers': {
                'imdb_id': show_data.get('imdbID')
            },
            'title': {
                'primary': show_data.get('Title'),
                'original': show_data.get('Title')
            },
            'air_dates': {
                'first': show_data.get('Released'),
                'year': int(show_data.get('Year', '0-')[:4]) if show_data.get('Year') else None
            },
            'seasons': {
                'total': int(show_data.get('totalSeasons', 0)) if show_data.get('totalSeasons', 'N/A') != 'N/A' else None
            },
            'runtime': self._parse_runtime(show_data.get('Runtime')),
            'ratings': self._parse_ratings(show_data),
            'overview': show_data.get('Plot') if show_data.get('Plot') != 'N/A' else None,
            'genres': [g.strip() for g in show_data.get('Genre', '').split(',') if g.strip()],
            'content_rating': show_data.get('Rated') if show_data.get('Rated') != 'N/A' else None,
            'people': {
                'director': [d.strip() for d in show_data.get('Director', '').split(',') if d.strip() and d.strip() != 'N/A'],
                'writer': [w.strip() for w in show_data.get('Writer', '').split(',') if w.strip() and w.strip() != 'N/A'],
                'actors': [a.strip() for a in show_data.get('Actors', '').split(',') if a.strip() and a.strip() != 'N/A']
            },
            'production': {
                'country': [c.strip() for c in show_data.get('Country', '').split(',') if c.strip()],
                'language': [l.strip() for l in show_data.get('Language', '').split(',') if l.strip()]
            },
            'awards': show_data.get('Awards') if show_data.get('Awards') != 'N/A' else None,
            'website': show_data.get('Website') if show_data.get('Website') != 'N/A' else None
        }
        
        return normalized
    
    def _parse_runtime(self, runtime_str: str) -> int:
        """Parse runtime string like '120 min' to integer"""
        if not runtime_str or runtime_str == 'N/A':
            return None
        try:
            return int(runtime_str.split()[0])
        except (ValueError, IndexError):
            return None
    
    def _parse_ratings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse all ratings sources (IMDb, Rotten Tomatoes, Metacritic)"""
        ratings = {}
        
        # IMDb rating
        imdb_rating = data.get('imdbRating')
        imdb_votes = data.get('imdbVotes', '').replace(',', '')
        if imdb_rating and imdb_rating != 'N/A':
            ratings['imdb'] = {
                'score': float(imdb_rating),
                'votes': imdb_votes
            }
        
        # Metacritic score
        metascore = data.get('Metascore')
        if metascore and metascore != 'N/A':
            ratings['metacritic'] = {
                'score': int(metascore)
            }
        
        # Ratings array (Rotten Tomatoes, etc.)
        ratings_array = data.get('Ratings', [])
        for rating in ratings_array:
            source = rating.get('Source', '')
            value = rating.get('Value', '')
            
            if source == 'Rotten Tomatoes':
                # Parse percentage like "87%"
                try:
                    score = int(value.replace('%', ''))
                    ratings['rotten_tomatoes'] = {'score': score}
                except ValueError:
                    pass
            elif source == 'Metacritic':
                # Parse score like "72/100"
                try:
                    score = int(value.split('/')[0])
                    ratings['metacritic'] = {'score': score}
                except (ValueError, IndexError):
                    pass
        
        return ratings
