# API Normalizer Format

Expected data structure from API clients.

## TV Series Response

```python
{
    'ids': {
        'tmdb': int,                    # TMDb ID
        'imdb': str,                    # tt0000000
        'tvdb': int,                    # TVDB ID
        'tvmaze': int,                  # TVMaze ID (optional)
        'tvrage': int                   # TVRage ID (optional, deprecated)
    },
    'name': str,                        # Show title
    'original_name': str,               # Original title (non-English)
    'first_air_date': str,              # YYYY-MM-DD
    'last_air_date': str,               # YYYY-MM-DD (optional)
    'overview': str,                    # Description
    'status': str,                      # "Returning Series", "Ended", etc.
    'type': str,                        # "Scripted", "Documentary", etc.
    'in_production': bool,              # Production status
    'vote_average': float,              # 0-10 rating
    'vote_count': int,                  # Number of votes
    'number_of_seasons': int,           # Total seasons
    'number_of_episodes': int,          # Total episodes
    'genres': [
        {
            'id': int,
            'name': str                 # "Drama", "Comedy", etc.
        }
    ],
    'networks': [
        {
            'id': int,
            'name': str                 # "AMC", "HBO", etc.
        }
    ],
    'seasons': [
        {
            'season_number': int,
            'episode_count': int,
            'air_date': str             # YYYY-MM-DD (optional)
        }
    ],
    'extras': {}                        # See Extras Format below
}
```

## Episode Response

```python
{
    'ids': {
        'tmdb': int,
        'imdb': str,
        'tvdb': int
    },
    'season_number': int,
    'episode_number': int,
    'name': str,                        # Episode title
    'overview': str,                    # Episode description
    'air_date': str,                    # YYYY-MM-DD
    'runtime': int,                     # Minutes
    'vote_average': float,              # 0-10 rating
    'vote_count': int,                  # Number of votes
    'still_path': str                   # Episode thumbnail URL (optional)
}
```

## Movie Response

```python
{
    'ids': {
        'tmdb': int,
        'imdb': str,
        'facebook': str,                # Facebook page ID (optional)
        'instagram': str,               # Instagram username (optional)
        'twitter': str                  # Twitter username (optional)
    },
    'name': str,                        # Movie title
    'original_name': str,               # Original title (non-English)
    'release_date': str,                # YYYY-MM-DD
    'overview': str,                    # Description
    'tagline': str,                     # Movie tagline (optional)
    'status': str,                      # "Released", "Post Production", etc.
    'runtime': int,                     # Minutes
    'budget': int,                      # USD (optional)
    'revenue': int,                     # USD (optional)
    'vote_average': float,              # 0-10 rating
    'vote_count': int,                  # Number of votes
    'genres': [
        {
            'id': int,
            'name': str
        }
    ],
    'poster_path': str,                 # Poster URL (optional)
    'backdrop_path': str,               # Backdrop URL (optional)
    'extras': {}                        # See Extras Format below
}
```

## Extras Format

### Credits

```python
{
    'credits': {
        'cast': [
            {
                'id': int,
                'name': str,            # Actor name
                'character': str,       # Character name
                'order': int,           # Cast order
                'profile_path': str     # Actor profile image URL (optional)
            }
        ],
        'crew': [
            {
                'id': int,
                'name': str,            # Crew member name
                'job': str,             # "Director", "Writer", etc.
                'department': str       # "Directing", "Writing", etc.
            }
        ]
    }
}
```

### Aggregate Credits (TV only)

```python
{
    'aggregate_credits': {
        'cast': [
            {
                'id': int,
                'name': str,
                'roles': [
                    {
                        'character': str,
                        'episode_count': int
                    }
                ],
                'total_episode_count': int
            }
        ],
        'crew': [
            {
                'id': int,
                'name': str,
                'jobs': [
                    {
                        'job': str,
                        'episode_count': int
                    }
                ],
                'department': str,
                'total_episode_count': int
            }
        ]
    }
}
```

### Images

```python
{
    'images': {
        'posters': [
            {
                'file_path': str,       # Image URL
                'width': int,           # Pixels
                'height': int,          # Pixels
                'iso_639_1': str,       # Language code (optional)
                'vote_average': float,  # Rating (optional)
                'vote_count': int       # Votes (optional)
            }
        ],
        'backdrops': [
            {
                'file_path': str,
                'width': int,
                'height': int,
                'iso_639_1': str,
                'vote_average': float,
                'vote_count': int
            }
        ]
    }
}
```

### Videos

```python
{
    'videos': {
        'results': [
            {
                'id': str,
                'name': str,            # Video title
                'key': str,             # YouTube video key
                'site': str,            # "YouTube"
                'size': int,            # Resolution (1080, 720, etc.)
                'type': str,            # "Trailer", "Teaser", "Clip", etc.
                'official': bool,       # Official video
                'published_at': str     # ISO 8601 date
            }
        ]
    }
}
```

### Keywords

```python
{
    'keywords': {
        'keywords': [                   # TV shows
            {
                'id': int,
                'name': str
            }
        ],
        'results': [                    # Movies
            {
                'id': int,
                'name': str
            }
        ]
    }
}
```

### External IDs

```python
{
    'external_ids': {
        'imdb_id': str,                 # tt0000000
        'tvdb_id': int,
        'tvrage_id': int,               # Deprecated
        'tvmaze_id': int,
        'facebook_id': str,
        'instagram_id': str,
        'twitter_id': str
    }
}
```

### Content Ratings

```python
{
    'content_ratings': {
        'results': [
            {
                'iso_3166_1': str,      # Country code (US, GB, TR)
                'rating': str           # "TV-MA", "TV-14", "PG-13", etc.
            }
        ]
    }
}
```

### Watch Providers

```python
{
    'watch_providers': {
        'results': {
            'US': {
                'link': str,            # TMDb watch page URL
                'flatrate': [           # Streaming services
                    {
                        'provider_id': int,
                        'provider_name': str,
                        'logo_path': str
                    }
                ],
                'buy': [                # Purchase options
                    {
                        'provider_id': int,
                        'provider_name': str,
                        'logo_path': str
                    }
                ],
                'rent': [               # Rental options
                    {
                        'provider_id': int,
                        'provider_name': str,
                        'logo_path': str
                    }
                ]
            },
            'TR': { ... },
            'GB': { ... }
        }
    }
}
```

## Field Normalization Rules

### Required Fields

Always present (empty string/list if unavailable):
- `name`
- `ids` (at least one ID)
- `overview`

### Optional Fields

May be `None` or missing:
- `tagline`
- `budget`
- `revenue`
- `still_path`
- `poster_path`
- `backdrop_path`
- All extras

### ID Normalization

```python
# TMDb format
'imdb_id': 'tt0133093'

# TVDb format
'imdb_id': 'tt0133093'

# TVMaze format
'imdb': 'tt0133093'          # Raw field
'imdb_id': 'tt0133093'       # Normalized

# OMDb format
'imdbID': 'tt0133093'        # Raw field
'imdb_id': 'tt0133093'       # Normalized
```

### Date Normalization

All dates in `YYYY-MM-DD` format:
```python
'2024-01-15'                  # Correct
'Jan 15, 2024'                # Convert to 2024-01-15
'2024'                        # Convert to 2024-01-01
```

### Image URL Normalization

Full URLs required:
```python
# TMDb
'/abc123.jpg'                 # Convert to https://image.tmdb.org/t/p/original/abc123.jpg

# TVDb
'https://artworks.thetvdb.com/...'  # Keep as-is

# TVMaze
'https://static.tvmaze.com/...'     # Keep as-is

# OMDb
'https://m.media-amazon.com/...'    # Keep as-is
```

### Array Normalization

Empty arrays if unavailable:
```python
'cast': []                    # No cast data
'genres': []                  # No genres
'keywords': []                # No keywords
```

### Numeric Normalization

```python
# Vote average: 0-10 scale
'vote_average': 9.5           # TMDb native
'vote_average': 8.2           # OMDb: 8.2/10 → 8.2

# Runtime: minutes as int
'runtime': 142                # 2h 22m → 142
'runtime': 58                 # 58 minutes

# IDs: int type
'tmdb': 1396                  # int, not string
'tvdb': 79168                 # int, not string
```

## Validation

All normalized responses must:
1. Include at least one ID in `ids` dict
2. Include `name` field (non-empty)
3. Use ISO 8601 dates (YYYY-MM-DD)
4. Use full URLs for images
5. Use 0-10 scale for ratings
6. Use minutes for runtime/duration
7. Return empty arrays (not `None`) for missing lists

## Error Responses

Failed API calls return `None`:
```python
def get_series_details(series_id):
    try:
        # API call
        return normalized_response
    except Exception as e:
        logger.error(f"API error: {e}")
        return None
```

## Implementation Example

```python
def normalize_tmdb_series(raw):
    """Normalize TMDb TV series response."""
    return {
        'ids': {
            'tmdb': raw['id'],
            'imdb': raw.get('external_ids', {}).get('imdb_id'),
            'tvdb': raw.get('external_ids', {}).get('tvdb_id')
        },
        'name': raw['name'],
        'original_name': raw.get('original_name', raw['name']),
        'first_air_date': raw.get('first_air_date', ''),
        'overview': raw.get('overview', ''),
        'vote_average': raw.get('vote_average', 0.0),
        'vote_count': raw.get('vote_count', 0),
        'number_of_seasons': raw.get('number_of_seasons', 0),
        'number_of_episodes': raw.get('number_of_episodes', 0),
        'genres': raw.get('genres', []),
        'networks': raw.get('networks', []),
        'seasons': raw.get('seasons', []),
        'extras': {}
    }
```
