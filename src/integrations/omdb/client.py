# integrations/omdb/client.py
"""
OMDb API Client - Movies + TV Shows support.
API: https://www.omdbapi.com/
"""
from __future__ import annotations
import requests
from typing import List, Dict, Any, Optional
from core.matcher.api_normalizer import make_tv, make_season, make_episode, make_movie

OMDB_BASE = 'https://www.omdbapi.com/'

class OMDbClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError('OMDb API key required')
        self.api_key = api_key
    
    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params['apikey'] = self.api_key
        resp = requests.get(OMDB_BASE, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get('Response') == 'False':
            raise RuntimeError(f"OMDb API error: {data.get('Error','Unknown error')}")
        return data

    # -------- MOVIE --------
    def search_movie(self, title: str, year: Optional[int] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {'s': title, 'type': 'movie'}
        if year: params['y'] = year
        results = self._request(params).get('Search', [])[:max_results]
        out = []
        for it in results:
            out.append(make_movie(
                ids={"imdb": it.get("imdbID")},
                title=it.get("Title"),
                original_title=it.get("Title"),
                release_date=f"{it['Year']}-01-01" if it.get("Year") and it.get("Year").isdigit() else None,
                poster=it.get("Poster") if it.get("Poster") and it.get("Poster")!="N/A" else None
            ))
        return out

    def movie_details(self, imdb_id: str) -> Dict[str, Any]:
        raw = self._request({'i': imdb_id, 'plot': 'full', 'type': 'movie'})
        ratings_map = { (r.get("Source") or ""): r.get("Value") for r in (raw.get("Ratings") or []) }
        
        # Extract extras from OMDb response
        extras = _extract_extras_from_raw_omdb(raw)
        
        return make_movie(
            ids={"imdb": raw.get("imdbID")},
            title=raw.get("Title"),
            original_title=raw.get("Title"),
            overview=raw.get("Plot"),
            release_date=raw.get("Released"),
            runtime=_to_int(raw.get("Runtime")),
            genres=_split_csv(raw.get("Genre")),
            spoken_languages=_split_csv(raw.get("Language")),
            production_companies=_split_csv(raw.get("Production")),
            poster=raw.get("Poster") if raw.get("Poster")!="N/A" else None,
            ratings={"imdb": raw.get("imdbRating"), "metascore": raw.get("Metascore"), "source_ratings": ratings_map},
            external_urls={"imdb": f"https://www.imdb.com/title/{raw.get('imdbID')}/"} if raw.get("imdbID") else None,
            extras=extras if extras else None
        )

    # -------- TV --------
    def search_tv(self, title: str, first_air_year: Optional[int] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {'s': title, 'type': 'series'}
        if first_air_year: params['y'] = first_air_year
        results = self._request(params).get('Search', [])[:max_results]
        out = []
        for it in results:
            year_str = (it.get('Year') or '')
            first_year = year_str.split('-')[0] if '-' in year_str else year_str
            out.append(make_tv(
                ids={"imdb": it.get("imdbID")},
                name=it.get("Title"),
                original_name=it.get("Title"),
                first_air_date=f"{first_year}-01-01" if first_year else None,
                poster=it.get("Poster") if it.get("Poster") and it.get("Poster")!="N/A" else None
            ))
        return out
    
    def get_details(self, imdb_id: str) -> Dict[str, Any]:
        raw = self._request({'i': imdb_id, 'plot': 'full'})
        # decide entity by Type
        typ = (raw.get("Type") or "").lower()
        if typ == "movie":
            return self.movie_details(imdb_id)
        
        # Extract extras from OMDb response
        extras = _extract_extras_from_raw_omdb(raw)
        
        # TV fallback
        return make_tv(
            ids={"imdb": raw.get("imdbID")},
            name=raw.get("Title"),
            original_name=raw.get("Title"),
            overview=raw.get("Plot"),
            first_air_date=raw.get("Released"),
            original_language=raw.get("Language"),
            genres=_split_csv(raw.get("Genre")),
            poster=raw.get("Poster") if raw.get("Poster")!="N/A" else None,
            ratings={
                "imdb": raw.get("imdbRating"),
                "metascore": raw.get("Metascore"),
                "source_ratings": {r.get("Source"): r.get("Value") for r in (raw.get("Ratings") or [])}
            },
            seasons=[{"season_number": i+1} for i in range(int(raw.get("totalSeasons") or 0))] if raw.get("totalSeasons") else None,
            external_urls={"imdb": f"https://www.imdb.com/title/{raw.get('imdbID')}/"} if raw.get("imdbID") else None,
            extras=extras if extras else None
        )

    def get_season(self, imdb_series_id: str, season: int) -> Dict[str, Any]:
        raw = self._request({'i': imdb_series_id, 'Season': season, 'type': 'series'})
        episodes = []
        for e in (raw.get("Episodes") or []):
            episodes.append(make_episode(
                ids={"imdb": e.get("imdbID")},
                season_number=season,
                episode_number=int(e.get("Episode") or 0),
                name=e.get("Title"),
                air_date=e.get("Released"),
                ratings={"imdb": e.get("imdbRating")},
            ))
        return make_season(
            ids={"imdb": raw.get("imdbID")},
            season_number=season,
            poster=raw.get("Poster") if raw.get("Poster")!="N/A" else None,
            episodes=episodes or None
        )

    def get_episode(self, imdb_series_id: str, season: int, episode: int) -> Dict[str, Any]:
        raw = self._request({'i': imdb_series_id, 'Season': season, 'Episode': episode})
        return make_episode(
            ids={"imdb": raw.get("imdbID")},
            season_number=int(raw.get("Season") or season),
            episode_number=int(raw.get("Episode") or episode),
            name=raw.get("Title"),
            overview=raw.get("Plot"),
            air_date=raw.get("Released"),
            runtime=_to_int(raw.get("Runtime")),
            ratings={"imdb": raw.get("imdbRating")},
            external_urls={"imdb": f"https://www.imdb.com/title/{raw.get('imdbID')}/"} if raw.get("imdbID") else None,
        )

def _split_csv(text: Optional[str]) -> Optional[list]:
    if not text or text=="N/A":
        return None
    return [s.strip() for s in str(text).split(",") if s.strip()]

def _to_int(v: Optional[str]) -> Optional[int]:
    if not v or v=="N/A": return None
    import re
    m = re.search(r"(\d+)", str(v))
    return int(m.group(1)) if m else None


def _extract_extras_from_raw_omdb(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Extract extras information from OMDb raw response."""
    extras = {}
    
    # Credits - OMDb provides Actors, Director, Writer as CSV strings
    actors_csv = raw.get("Actors")
    director_csv = raw.get("Director")
    writer_csv = raw.get("Writer")
    
    if actors_csv and actors_csv != "N/A":
        cast_list = []
        for i, name in enumerate(actors_csv.split(",")):
            name = name.strip()
            if name:
                cast_list.append({
                    'name': name,
                    'character': '',  # OMDb doesn't provide character names
                    'order': i
                })
        
        crew_list = []
        if director_csv and director_csv != "N/A":
            for name in director_csv.split(","):
                name = name.strip()
                if name:
                    crew_list.append({
                        'name': name,
                        'job': 'Director',
                        'department': 'Directing'
                    })
        
        if writer_csv and writer_csv != "N/A":
            for name in writer_csv.split(","):
                name = name.strip()
                if name and name not in [c['name'] for c in crew_list]:
                    crew_list.append({
                        'name': name,
                        'job': 'Writer',
                        'department': 'Writing'
                    })
        
        if cast_list or crew_list:
            extras['credits'] = {
                'cast': cast_list,
                'crew': crew_list
            }
    
    # Images - OMDb provides single Poster
    poster_url = raw.get("Poster")
    if poster_url and poster_url != "N/A":
        extras['images'] = {
            'posters': [{'file_path': poster_url}],
            'backdrops': [],
            'stills': []
        }
    
    # External IDs
    imdb_id = raw.get("imdbID")
    if imdb_id:
        extras['external_ids'] = {
            'imdb_id': imdb_id,
            'tvdb_id': '',
            'facebook_id': '',
            'instagram_id': '',
            'twitter_id': ''
        }
    
    # Content Rating
    rated = raw.get("Rated")
    if rated and rated != "N/A":
        extras['content_ratings'] = [{
            'iso_3166_1': 'US',
            'rating': rated
        }]
    
    return extras if extras else None
