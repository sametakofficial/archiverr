# Configuration Reference

Complete config.yml reference.

## Structure

```yaml
tmdb:
  api_key: "..."
  lang: "..."
  fallback_lang: "..."
  region: "..."

tvdb:
  api_key: "..."

tvmaze: {}

omdb:
  api_key: "..."

tv_priority: [...]
movie_priority: [...]

options:
  dry_run: true|false
  debug: true|false
  hardlink: true|false
  ffprobe_enable: true|false
  ffprobe_nfo_enable: true|false
  ffprobe_force: true|false

extras:
  tv_credits: true|false
  tv_aggregate_credits: true|false
  tv_images: true|false
  tv_videos: true|false
  tv_keywords: true|false
  tv_external_ids: true|false
  tv_content_ratings: true|false
  tv_watch_providers: true|false
  movie_credits: true|false
  movie_images: true|false
  movie_videos: true|false
  movie_keywords: true|false
  movie_external_ids: true|false
  movie_watch_providers: true|false

rename:
  series:
    save: "..."
    print: "..."
  movies:
    save: "..."
    print: "..."

summary:
  print: "..."

query_engine:
  queries: [...]
```

## TMDb Configuration

```yaml
tmdb:
  api_key: "your_tmdb_api_key"           # Required
  lang: "en-US"                          # Default: en-US
  fallback_lang: "en-US"                 # Default: en-US
  region: "US"                           # Default: US
```

**api_key**
- TMDb API v3 key
- Get from: themoviedb.org/settings/api

**lang**
- ISO 639-1 + ISO 3166-1 format (e.g., tr-TR, de-DE)
- Used for metadata language

**fallback_lang**
- Language used when primary unavailable
- Ensures metadata always returned

**region**
- ISO 3166-1 country code
- Affects content ratings, release dates

## TVDb Configuration

```yaml
tvdb:
  api_key: "your_tvdb_api_key"           # Optional
```

**api_key**
- TVDb v4 API key
- Get from: thetvdb.com/dashboard/account/apikeys
- JWT authentication automatic

## TVMaze Configuration

```yaml
tvmaze: {}
```

No configuration needed. Free API.

## OMDb Configuration

```yaml
omdb:
  api_key: "your_omdb_api_key"           # Optional
```

**api_key**
- OMDb API key
- Get from: omdbapi.com/apikey.aspx
- Free tier: 1000 req/day

## API Priority

```yaml
tv_priority:
  - tmdb
  - tvdb
  - tvmaze
  - omdb

movie_priority:
  - tmdb
  - tvdb
  - omdb
```

**tv_priority**
- API order for TV shows
- First match wins
- TVMaze skips movies automatically

**movie_priority**
- API order for movies
- First match wins

## Options

```yaml
options:
  dry_run: true                          # Default: true
  debug: false                           # Default: false
  hardlink: false                        # Default: false
  ffprobe_enable: true                   # Default: true
  ffprobe_nfo_enable: true               # Default: true
  ffprobe_force: false                   # Default: false
```

**dry_run**
- `true`: Test mode, no file modifications
- `false`: Execute operations

**debug**
- `true`: Verbose logging with timestamps
- `false`: Minimal output

**hardlink**
- `true`: Create hardlinks (keeps original location)
- `false`: Move files to new location
- Requires same filesystem

**ffprobe_enable**
- `true`: Analyze media files (codec, resolution, audio)
- `false`: Skip FFprobe (faster, no video variables)

**ffprobe_nfo_enable**
- `true`: Cache FFprobe results in .nfo files
- `false`: No caching
- Requires ffprobe_enable: true

**ffprobe_force**
- `true`: Force fresh FFprobe analysis, ignore cache
- `false`: Use cached data if available
- Requires ffprobe_enable: true and ffprobe_nfo_enable: true

## Extras Configuration

```yaml
extras:
  # TV Series
  tv_credits: true                       # Default: false
  tv_aggregate_credits: false            # Default: false
  tv_images: true                        # Default: false
  tv_videos: false                       # Default: false
  tv_keywords: false                     # Default: false
  tv_external_ids: true                  # Default: false
  tv_content_ratings: true               # Default: false
  tv_watch_providers: false              # Default: false
  
  # Movies
  movie_credits: false                   # Default: false
  movie_images: false                    # Default: false
  movie_videos: false                    # Default: false
  movie_keywords: false                  # Default: false
  movie_external_ids: false              # Default: false
  movie_watch_providers: false           # Default: false
```

**tv_credits / movie_credits**
- Cast and crew information
- Enables: {cast.N.name}, {crew.N.name}, {director}, {castCount}
- API support: TMDb (full), TVDb (cast only), TVMaze (full), OMDb (basic)
- Cost: +1 API call per file (TMDb, TVMaze)

**tv_aggregate_credits**
- All cast across all seasons (TMDb only)
- Enables: Complete series cast list
- API support: TMDb only
- Cost: +1 API call per series

**tv_images / movie_images**
- Posters, backdrops, promotional images
- Enables: {posters.N.file_path}, {backdrops.N.file_path}, {postersCount}
- API support: TMDb (full), TVDb (full), TVMaze (full), OMDb (single)
- Cost: +1 API call per file (TMDb, TVDb, TVMaze)

**tv_videos / movie_videos**
- Trailers and promotional videos
- Enables: {trailers.N.name}, {trailers.N.key}, {videos.N.type}
- API support: TMDb only
- Cost: +1 API call per file

**tv_keywords / movie_keywords**
- Tags and keywords
- Enables: {keywords.N.name}
- API support: TMDb only
- Cost: +1 API call per file

**tv_external_ids / movie_external_ids**
- External database identifiers
- Enables: {imdb_id}, {tvdb_id}, {tmdb_id}, {tvmaze_id}
- API support: All APIs (varying coverage)
- Cost: +0 (included in main response for most APIs)

**tv_content_ratings**
- Age ratings by country
- Enables: {contentRating}, {contentRating.US}, {contentRating.TR}
- API support: TMDb (full), TVDb (yes), OMDb (single)
- Cost: +0 (TVDb), +1 (TMDb)

**tv_watch_providers / movie_watch_providers**
- Streaming service availability
- Enables: {watchProviders.US.flatrate.N.name}
- API support: TMDb only
- Cost: +1 API call per file

## Rename Configuration

```yaml
rename:
  series:
    save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
    print: "✓ {showName} S{seasonNumber:02d}E{episodeNumber:02d}"
  
  movies:
    save: "{name} ({movieYear})/{name} ({movieYear})"
    print: "✓ {name} ({movieYear})"
```

**series.save**
- Path pattern for TV episodes
- Supports all TV variables and filters
- Required field

**series.print**
- Console output template for TV episodes
- Optional (no output if not defined)

**movies.save**
- Path pattern for movies
- Supports all movie variables and filters
- Required field

**movies.print**
- Console output template for movies
- Optional

## Summary Configuration

```yaml
summary:
  print: |
    Total: {total_time:.2f}s
    Average: {avg_time:.2f}s
    Success: {success} | Failed: {failed}
```

**summary.print**
- Template for final summary
- Optional
- Variables: {total_time}, {avg_time}, {min_time}, {max_time}, {success}, {failed}, {total}

## Query Engine

```yaml
query_engine:
  queries:
    - name: "Query Name"
      where: "condition"
      save: "/path/pattern"
      print: "template"
    
    - loop:
        var: varname
        in: [values]
      where: "condition"
      save: "/path/pattern"
```

**queries**
- Array of query objects
- Evaluated in order
- First matching query wins

**name** (optional)
- Query identifier for logging

**where** (optional)
- Conditional expression
- Supports: ==, !=, >, <, >=, <=, and, or, not, in

**loop** (optional)
- Iterator configuration
- var: Loop variable name
- in: Array of values to iterate

**save** (required)
- Path pattern for matched files
- Supports all variables

**print** (optional)
- Console output for matched files

## Environment Variable Overrides

```bash
export ARCHIVERR_DRY_RUN=true
export ARCHIVERR_DEBUG=true
export ARCHIVERR_HARDLINK=false
export ARCHIVERR_FFPROBE_ENABLE=true
```

Priority: CLI args > ENV vars > config.yml

## Command Line Overrides

```bash
archiverr --dry-run --debug --hardlink
```

Priority: CLI args > ENV vars > config.yml

## Performance Notes

- Each extra adds API calls
- FFprobe analysis adds 50-200ms per file
- Caching reduces repeat overhead
- Disable unused extras for speed

## Rate Limits

- TMDb: 40 requests/10 seconds (managed automatically)
- TVDb: JWT rotation automatic
- TVMaze: No limit
- OMDb: 1000 requests/day (free tier)
