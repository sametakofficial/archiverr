# Extras Configuration

Additional metadata beyond basic information.

## Configuration

```yaml
extras:
  # TV Series
  tv_credits: true
  tv_aggregate_credits: false
  tv_images: true
  tv_videos: false
  tv_keywords: false
  tv_external_ids: true
  tv_content_ratings: true
  tv_watch_providers: false
  
  # Movies
  movie_credits: true
  movie_images: true
  movie_videos: false
  movie_keywords: false
  movie_external_ids: true
  movie_watch_providers: false
```

## TV Series Extras

### tv_credits

Cast and crew information.

**Enabled Variables:**
```
{cast.1.name}           First cast member name
{cast.2.name}           Second cast member name
{cast.N.name}           Nth cast member (1-based)
{cast.1.character}      Character name
{cast.1.profile_path}   Actor profile image
{castCount}             Total cast members

{crew.1.name}           First crew member name
{crew.1.job}            Job title (Director, Writer)
{crew.1.department}     Department (Directing, Writing)
{director}              Primary director name
```

**API Support:**
- TMDb: Full cast and crew (+1 API call)
- TVDb: Cast only, from /extended (+0 API calls)
- TVMaze: Full cast and crew (+1 API call)
- OMDb: Basic actors string, from main response (+0 API calls)

**Performance:** +1 API call per file (TMDb, TVMaze)

### tv_aggregate_credits

Complete cast across all seasons (TMDb only).

**Enabled Variables:**
```
{aggregate_cast.1.name}             First cast member (all seasons)
{aggregate_cast.1.roles}            All roles played
{aggregate_cast.1.total_episodes}   Episode count
{aggregate_crew.1.name}             First crew member (all seasons)
{aggregate_crew.1.jobs}             All jobs held
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per series (not per episode)

### tv_images

Posters, backdrops, promotional images.

**Enabled Variables:**
```
{posters.1.file_path}       First poster image URL
{posters.2.file_path}       Second poster image URL
{posters.N.file_path}       Nth poster (1-based)
{posters.1.width}           Poster width (pixels)
{posters.1.height}          Poster height (pixels)
{postersCount}              Total posters

{backdrops.1.file_path}     First backdrop image URL
{backdrops.2.file_path}     Second backdrop image URL
{backdrops.N.file_path}     Nth backdrop (1-based)
{backdrops.1.width}         Backdrop width (pixels)
{backdrops.1.height}        Backdrop height (pixels)
{backdropsCount}            Total backdrops
```

**API Support:**
- TMDb: Full collection (+1 API call)
- TVDb: Full collection (+1 API call via /artworks)
- TVMaze: Available (+1 API call)
- OMDb: Single poster, from main response (+0 API calls)

**Performance:** +1 API call per file (TMDb, TVDb, TVMaze)

### tv_videos

Trailers and promotional videos (TMDb only).

**Enabled Variables:**
```
{videos.1.name}             First video title
{videos.1.key}              YouTube video key
{videos.1.site}             Site (YouTube)
{videos.1.type}             Type (Trailer, Teaser, Clip)
{videos.1.size}             Resolution (1080, 720)

{trailers.1.name}           First trailer title (filtered)
{trailers.1.key}            Trailer YouTube key
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

### tv_keywords

Tags and keywords (TMDb only).

**Enabled Variables:**
```
{keywords.1.name}           First keyword
{keywords.2.name}           Second keyword
{keywords.N.name}           Nth keyword (1-based)
{keywords.1.id}             Keyword ID
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

### tv_external_ids

External database identifiers.

**Enabled Variables:**
```
{imdb_id}                   IMDB identifier (tt0000000)
{tvdb_id}                   TVDB identifier
{tmdb_id}                   TMDb identifier
{tvmaze_id}                 TVMaze identifier
{facebook_id}               Facebook page ID
{instagram_id}              Instagram username
{twitter_id}                Twitter username
```

**API Support:**
- TMDb: imdb, tvdb, facebook, instagram, twitter (+0 main response)
- TVDb: imdb, tvdb (+0 from /extended)
- TVMaze: imdb, tvdb, tvmaze, tvrage (+0 main response)
- OMDb: imdb only (+0 main response)

**Performance:** +0 API calls (included in main response)

### tv_content_ratings

Age ratings by country.

**Enabled Variables:**
```
{contentRating}             Primary content rating
{contentRating.US}          US rating (TV-MA, TV-14, etc.)
{contentRating.GB}          UK rating
{contentRating.TR}          Turkish rating
{contentRating.DE}          German rating
{contentRating.FR}          French rating
```

**API Support:**
- TMDb: Full, all countries (+1 API call)
- TVDb: Yes, from /extended (+0 API calls)
- TVMaze: Limited, single rating (+0 main response)
- OMDb: Single rating, from main response (+0 API calls)

**Performance:** +1 API call (TMDb), +0 others

### tv_watch_providers

Streaming service availability (TMDb only).

**Enabled Variables:**
```
{watchProviders.US.flatrate.1.name}         First US streaming service
{watchProviders.US.flatrate.2.name}         Second US streaming service
{watchProviders.US.buy.1.name}              First US buy option
{watchProviders.US.rent.1.name}             First US rent option
{watchProviders.TR.flatrate.1.name}         First TR streaming service
{watchProviders.{region}.{type}.N.name}     General pattern
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

## Movie Extras

### movie_credits

Cast and crew information.

**Enabled Variables:**
```
{cast.1.name}           First cast member name
{cast.2.name}           Second cast member name
{cast.N.name}           Nth cast member (1-based)
{cast.1.character}      Character name
{cast.1.profile_path}   Actor profile image
{castCount}             Total cast members

{crew.1.name}           First crew member name
{crew.1.job}            Job title (Director, Writer)
{crew.1.department}     Department (Directing, Writing)
{director}              Primary director name
```

**API Support:**
- TMDb: Full cast and crew (+1 API call)
- TVDb: Limited (+0 API calls)
- OMDb: Basic actors string (+0 API calls)

**Performance:** +1 API call per file (TMDb)

### movie_images

Posters, backdrops, promotional images.

**Enabled Variables:**
```
{posters.1.file_path}       First poster image URL
{posters.N.file_path}       Nth poster (1-based)
{posters.1.width}           Poster width (pixels)
{posters.1.height}          Poster height (pixels)
{postersCount}              Total posters

{backdrops.1.file_path}     First backdrop image URL
{backdrops.N.file_path}     Nth backdrop (1-based)
{backdrops.1.width}         Backdrop width (pixels)
{backdrops.1.height}        Backdrop height (pixels)
{backdropsCount}            Total backdrops
```

**API Support:**
- TMDb: Full collection (+1 API call)
- TVDb: Limited (+1 API call)
- OMDb: Single poster (+0 API calls)

**Performance:** +1 API call per file (TMDb, TVDb)

### movie_videos

Trailers and promotional videos (TMDb only).

**Enabled Variables:**
```
{videos.1.name}             First video title
{videos.1.key}              YouTube video key
{videos.1.type}             Type (Trailer, Teaser)
{trailers.1.name}           First trailer title
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

### movie_keywords

Tags and keywords (TMDb only).

**Enabled Variables:**
```
{keywords.1.name}           First keyword
{keywords.2.name}           Second keyword
{keywords.N.name}           Nth keyword (1-based)
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

### movie_external_ids

External database identifiers.

**Enabled Variables:**
```
{imdb_id}                   IMDB identifier
{tmdb_id}                   TMDb identifier
{facebook_id}               Facebook page ID
```

**API Support:**
- TMDb: imdb, facebook, instagram, twitter (+0 main response)
- TVDb: Limited (+0 API calls)
- OMDb: imdb only (+0 main response)

**Performance:** +0 API calls (included in main response)

### movie_watch_providers

Streaming service availability (TMDb only).

**Enabled Variables:**
```
{watchProviders.US.flatrate.1.name}         First US streaming service
{watchProviders.US.buy.1.name}              First US buy option
{watchProviders.US.rent.1.name}             First US rent option
```

**API Support:**
- TMDb: Yes (+1 API call)
- Others: No

**Performance:** +1 API call per file

## API Support Matrix

| Extra | TMDb | TVDb | TVMaze | OMDb | Cost (TMDb) |
|-------|------|------|--------|------|-------------|
| Credits (Cast/Crew) | Full | Cast | Full | Basic | +1 call |
| Aggregate Credits | TV only | No | No | No | +1 call |
| Images | Full | Full | Yes | Single | +1 call |
| Videos | Yes | No | No | No | +1 call |
| Keywords | Yes | No | No | No | +1 call |
| External IDs | Full | Limited | Limited | IMDB | +0 calls |
| Content Ratings | Full | Yes | Limited | Single | +1 call |
| Watch Providers | Yes | No | No | No | +1 call |

## Performance Impact

### API Calls Per File

**No Extras:**
```
1 search + 1 details = 2 calls
```

**All TV Extras (TMDb):**
```
1 search + 1 details + 6 extras = 8 calls
```

**All Movie Extras (TMDb):**
```
1 search + 1 details + 5 extras = 7 calls
```

### Processing Time

50 files with all extras:
```
50 files × 8 calls = 400 calls ≈ 100 seconds (TMDb rate limit)
```

50 files with no extras:
```
50 files × 2 calls = 100 calls ≈ 25 seconds
```

## Recommendations

### Minimal (Fastest)
```yaml
extras:
  tv_external_ids: true         # +0 calls
  movie_external_ids: true      # +0 calls
```

### Balanced
```yaml
extras:
  tv_credits: true              # +1 call
  tv_images: true               # +1 call
  tv_external_ids: true         # +0 calls
  movie_credits: true           # +1 call
  movie_images: true            # +1 call
  movie_external_ids: true      # +0 calls
```

### Complete
```yaml
extras:
  tv_credits: true
  tv_aggregate_credits: true
  tv_images: true
  tv_videos: true
  tv_keywords: true
  tv_external_ids: true
  tv_content_ratings: true
  tv_watch_providers: true
  movie_credits: true
  movie_images: true
  movie_videos: true
  movie_keywords: true
  movie_external_ids: true
  movie_watch_providers: true
```
