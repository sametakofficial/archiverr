"""TVMaze Response Normalizer"""
from typing import Dict, Any, List


class TVMazeNormalizer:
    """Normalize TVMaze API responses to community standard format"""
    
    def normalize_show(self, show_data: Dict[str, Any], extras: Dict[str, Any] = None) -> Dict[str, Any]:
        """Normalize show response"""
        if not show_data:
            return {}
        
        normalized = {
            'media_type': 'show',
            'identifiers': {
                'tvmaze_id': str(show_data.get('id', ''))
            },
            'title': {
                'primary': show_data.get('name'),
                'original': show_data.get('name')
            },
            'air_dates': {
                'first': show_data.get('premiered'),
                'last': show_data.get('ended'),
                'year': int(show_data.get('premiered', '0000')[:4]) if show_data.get('premiered') else None
            },
            'status': show_data.get('status'),
            'runtime': show_data.get('runtime'),
            'ratings': {
                'tvmaze': {
                    'score': show_data.get('rating', {}).get('average')
                }
            },
            'genres': show_data.get('genres', []),
            'network': {
                'name': show_data.get('network', {}).get('name') if show_data.get('network') else None,
                'id': str(show_data.get('network', {}).get('id')) if show_data.get('network') else None,
                'country': show_data.get('network', {}).get('country', {}).get('code') if show_data.get('network') else None
            } if show_data.get('network') else {}
        }
        
        # Add extras if provided
        if extras:
            if extras.get('shows_cast'):
                normalized['people'] = self._normalize_people(extras['shows_cast'], extras.get('shows_crew', []))
        
        return normalized
    
    def _normalize_people(self, cast_data: List[Dict[str, Any]], crew_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize cast and crew"""
        cast = []
        for item in cast_data:
            person = item.get('person', {})
            character = item.get('character', {})
            cast.append({
                'id': str(person.get('id', '')),
                'name': person.get('name'),
                'character': character.get('name')
            })
        
        crew = []
        for item in crew_data:
            person = item.get('person', {})
            crew.append({
                'id': str(person.get('id', '')),
                'name': person.get('name'),
                'job': item.get('type')
            })
        
        return {
            'cast': cast,
            'crew': crew
        }
