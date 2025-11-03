# API Extras Support Matrix

This document tracks which extras are available from each API integration.

**Last Updated**: 2025-11-03

## TV Series Extras

| Extra Type | TMDb | TVDb | TVMaze | OMDb | Notes |
|------------|------|------|--------|------|-------|
| **Credits (Cast)** | ✅ Full | ✅ Full | ✅ Full | ✅ Limited | All working |
| **Credits (Crew)** | ✅ Full | ❌ N/A | ✅ Full | ✅ Limited | TVDb API doesn't provide |
| **Images (Posters)** | ✅ Full | ✅ Full | ✅ Full | ✅ Single | TVDb: 74 posters for Friends |
| **Images (Backdrops)** | ✅ Full | ✅ Full | ✅ Full | ❌ N/A | TVDb: 349 backdrops for Friends |
| **Videos (Trailers)** | ✅ Full | ❌ N/A | ❌ N/A | ❌ N/A | Only TMDb has video data |
| **Keywords** | ✅ Full | ❌ N/A | ❌ N/A | ❌ N/A | Only TMDb has keywords |
| **External IDs** | ✅ Full | ✅ Full | ✅ Full | ✅ Limited | All working |
| **Content Ratings** | ✅ Full | ✅ Full | ❌ N/A | ✅ Single | TVMaze has single rating field |
| **Watch Providers** | ✅ Full | ❌ N/A | ❌ N/A | ❌ N/A | Only TMDb has streaming data |
| **Aggregate Credits** | ✅ Full | ❌ N/A | ❌ N/A | ❌ N/A | TMDb-specific feature |

## Episode Details

| Detail | TMDb | TVDb | TVMaze | OMDb | Notes |
|--------|------|------|--------|------|-------|
| **Episode Name** | ✅ | ✅ | ✅ | ✅ | Fixed Nov 3 - variable override bug |
| **Episode Overview** | ✅ | ✅ | ✅ | ✅ | All working |
| **Air Date** | ✅ | ✅ | ✅ | ✅ | All working |
| **Runtime** | ✅ | ✅ | ✅ | ✅ | All working |
| **Episode Rating** | ✅ | ✅ | ✅ | ✅ | All working |
| **Episode Image** | ✅ | ✅ | ✅ | ❌ | Still/thumbnail |

## Implementation Details

### TMDb (Most Complete)
- **Endpoint**: `/tv/{id}` for series, `/tv/{id}/season/{s}/episode/{e}` for episodes
- **Extras Endpoints**: `/credits`, `/aggregate_credits`, `/images`, `/videos`, `/keywords`, `/external_ids`, `/content_ratings`, `/watch/providers`
- **Status**: ✅ All extras working
- **Coverage**: Comprehensive metadata, best for international content

### TVDb (Good Coverage)
- **Endpoint**: `/series/{id}/extended` for series (includes characters, content ratings)
- **Extras Endpoints**: `/artworks` for images, `/extended` for credits/ratings
- **Status**: ✅ Credits, images, external IDs, content ratings working
- **Missing**: Videos, keywords, watch providers (not in API)
- **Coverage**: Strong for TV series, JWT auth required

### TVMaze (Moderate Coverage)
- **Endpoint**: `/shows/{id}` for series, `/shows/{id}/episodebynumber` for episodes
- **Extras Endpoints**: `/cast`, `/crew`, `/images`, main response for external IDs
- **Status**: ✅ Credits, images, external IDs working
- **Missing**: Videos, keywords, watch providers, content ratings array (not in API)
- **Coverage**: Good for US TV shows, free API

### OMDb (Basic Coverage)
- **Endpoint**: Single endpoint with `apikey` and `i/t` params
- **Extras**: All in main response (Actors, Director, Writer, Poster, Rated, imdbID)
- **Status**: ✅ Basic extras working
- **Missing**: Videos, keywords, watch providers, multiple images (not in API)
- **Coverage**: IMDb-based, simple REST API, limited data

## API Priority Recommendations

### For TV Series (config.yml)
```yaml
tv_priority:
  - tmdb      # Best overall coverage, all extras
  - tvdb      # Good for TV, strong image collection
  - tvmaze    # US shows, free API
  - omdb      # Fallback, IMDb-based
```

### For Movies (config.yml)
```yaml
movie_priority:
  - tmdb      # Best overall coverage
  - tvdb      # Alternative source
  - omdb      # IMDb fallback
```

## Known Limitations

### By API
- **TMDb**: Rate limiting (40 req/10sec), requires API key
- **TVDb**: JWT auth complexity, no videos/keywords/watch providers
- **TVMaze**: No content ratings array, no keywords, US-centric
- **OMDb**: Limited data, single image, no videos/keywords

### By Feature
- **Videos/Trailers**: Only TMDb provides
- **Keywords**: Only TMDb provides
- **Watch Providers**: Only TMDb provides
- **Aggregate Credits**: Only TMDb provides (all cast across seasons)

## Testing Results (2025-11-03)

### Friends S01E04 Test
```
TMDb:
  - Episode Name: ✅ "The One with George Stephanopoulos"
  - Cast: ✅ 6 cast members
  - Images: ✅ 157 posters, 98 backdrops
  - Videos: ✅ 2 trailers
  - Keywords: ✅ 13 keywords
  - External IDs: ✅ IMDB tt0108778, TVDB 79168
  - Content Rating: ✅ TV-14

TVDb:
  - Episode Name: ✅ "The One with George Stephanopoulos"
  - Cast: ✅ 7 cast members (Jennifer Aniston, Lisa Kudrow, Matthew Perry, etc.)
  - Images: ✅ 74 posters, 349 backdrops
  - External IDs: ✅ IMDB tt0108778, TVDB 79168
  - Content Rating: ✅ Available

TVMaze:
  - Episode Name: ✅ "The One with George Stephanopoulos"
  - Cast: ✅ Full cast
  - Crew: ✅ Full crew
  - Images: ✅ Available
  - External IDs: ✅ IMDB tt0108778, TVDB 79168, TVMaze ID

OMDb:
  - Episode Name: ✅ "The One with George Stephanopoulos"
  - Cast: ✅ Main actors (comma-separated string)
  - Director: ✅ Available
  - Image: ✅ Single poster
  - External IDs: ✅ IMDB tt0108778
  - Content Rating: ✅ "TV-PG"
```

## Architecture Notes

### Variable System Integration
- All extras normalized to common format before variable system
- Direct 1:1 mapping: API normalizer output → variables
- No intermediate transformation layers (caused bugs)
- Override conflicts avoided (e.g., episodeName bug fixed)

### Best Practices
1. Always normalize at API client level
2. Use consistent key names (`imdb_id`, `file_path`, etc.)
3. Avoid multiple functions setting same variables
4. Log all exceptions (no silent `except: pass`)
5. Debug with temporary logs, remove after fix
