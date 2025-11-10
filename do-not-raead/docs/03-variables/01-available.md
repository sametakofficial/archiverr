# Available Variables

Complete variable reference for all supported metadata.

## TV Series Variables

```
{showName}                  Show title
{originalShowName}          Original title (non-English)
{firstAirYear}              First air year (YYYY)
{firstAirDate}              First air date (YYYY-MM-DD)
{lastAirDate}               Last air date (YYYY-MM-DD)
{seasonNumber}              Season number
{episodeNumber}             Episode number
{episodeName}               Episode title
{episodeOverview}           Episode description
{episodeAirDate}            Episode air date (YYYY-MM-DD)
{episodeRuntime}            Episode runtime (minutes)
{episodeVoteAverage}        Episode rating (0-10)
{episodeVoteCount}          Episode vote count
{networkName}               Network name (e.g., AMC, HBO)
{genreName}                 Primary genre
{numberOfSeasons}           Total seasons
{numberOfEpisodes}          Total episodes in series
{voteAverage}               Series rating (0-10)
{voteCount}                 Series vote count
{overview}                  Series description
{showType}                  Type (Scripted, Documentary, etc.)
{inProduction}              Production status (true/false)
{status}                    Status (Returning Series, Ended, etc.)
```

## Movie Variables

```
{name}                      Movie title
{originalName}              Original title (non-English)
{movieYear}                 Release year (YYYY)
{releaseDate}               Release date (YYYY-MM-DD)
{runtime}                   Duration (minutes)
{voteAverage}               Rating (0-10)
{voteCount}                 Vote count
{overview}                  Description
{budget}                    Budget (USD)
{revenue}                   Revenue (USD)
{tagline}                   Movie tagline
{status}                    Status (Released, Post Production, etc.)
```

## Common Variables

```
{apiSource}                 API used (tmdb, tvdb, tvmaze, omdb)
{extension}                 File extension (mkv, mp4, avi)
{took}                      Processing time (seconds, float)
```

## Extras Variables (if enabled)

### Credits (tv_credits / movie_credits)

```
{cast.1.name}               First cast member name
{cast.2.name}               Second cast member name
{cast.N.name}               Nth cast member name (1-based)
{cast.1.character}          Character name
{cast.1.order}              Cast order
{cast.1.profile_path}       Actor profile image path
{castCount}                 Total cast members

{crew.1.name}               First crew member name
{crew.2.name}               Second crew member name
{crew.N.name}               Nth crew member name (1-based)
{crew.1.job}                Job title (Director, Writer, etc.)
{crew.1.department}         Department (Directing, Writing, etc.)

{director}                  Primary director name
```

**API Support:**
- TMDb: Full cast/crew
- TVDb: Cast only (no crew)
- TVMaze: Full cast/crew
- OMDb: Basic (actors as comma-separated string)

### Images (tv_images / movie_images)

```
{posters.1.file_path}       First poster image path
{posters.2.file_path}       Second poster image path
{posters.N.file_path}       Nth poster image path (1-based)
{posters.1.width}           Poster width (pixels)
{posters.1.height}          Poster height (pixels)
{postersCount}              Total posters

{backdrops.1.file_path}     First backdrop image path
{backdrops.2.file_path}     Second backdrop image path
{backdrops.N.file_path}     Nth backdrop image path (1-based)
{backdrops.1.width}         Backdrop width (pixels)
{backdrops.1.height}        Backdrop height (pixels)
{backdropsCount}            Total backdrops
```

**API Support:**
- TMDb: Full collection
- TVDb: Full collection
- TVMaze: Available
- OMDb: Single poster only

### Videos (tv_videos / movie_videos)

```
{videos.1.name}             First video title
{videos.1.key}              YouTube video key
{videos.1.site}             Site (YouTube)
{videos.1.type}             Type (Trailer, Teaser, Clip, etc.)
{videos.1.size}             Resolution (1080, 720, etc.)

{trailers.1.name}           First trailer title (filtered to trailers only)
{trailers.1.key}            Trailer YouTube key
```

**API Support:**
- TMDb: Full support
- Others: Not supported

### Keywords (tv_keywords / movie_keywords)

```
{keywords.1.name}           First keyword
{keywords.2.name}           Second keyword
{keywords.N.name}           Nth keyword (1-based)
{keywords.1.id}             Keyword ID
```

**API Support:**
- TMDb: Full support
- Others: Not supported

### External IDs (tv_external_ids / movie_external_ids)

```
{imdb_id}                   IMDB identifier (tt0000000)
{tvdb_id}                   TVDB identifier
{tmdb_id}                   TMDb identifier
{tvmaze_id}                 TVMaze identifier
{tvrage_id}                 TVRage identifier (deprecated)
{facebook_id}               Facebook page ID
{instagram_id}              Instagram username
{twitter_id}                Twitter username
```

**API Support:**
- TMDb: imdb_id, tvdb_id, facebook_id, instagram_id, twitter_id
- TVDb: imdb_id, tvdb_id
- TVMaze: imdb_id, tvdb_id, tvmaze_id, tvrage_id
- OMDb: imdb_id only

### Content Ratings (tv_content_ratings)

```
{contentRating}             Primary content rating
{contentRating.US}          US rating (TV-MA, TV-14, etc.)
{contentRating.GB}          UK rating
{contentRating.TR}          Turkish rating
{contentRating.DE}          German rating
{contentRating.FR}          French rating
```

**API Support:**
- TMDb: Full (all countries)
- TVDb: Available
- TVMaze: Limited
- OMDb: Single rating (Rated field)

### Watch Providers (tv_watch_providers / movie_watch_providers)

```
{watchProviders.US.flatrate.1.name}         First US streaming service
{watchProviders.US.flatrate.2.name}         Second US streaming service
{watchProviders.US.buy.1.name}              First US buy option
{watchProviders.US.rent.1.name}             First US rent option
{watchProviders.TR.flatrate.1.name}         First TR streaming service
{watchProviders.{region}.{type}.N.name}     General pattern
```

**API Support:**
- TMDb: Full support
- Others: Not supported

### Aggregate Credits (tv_aggregate_credits)

```
{aggregate_cast.1.name}     First cast member (all seasons)
{aggregate_cast.1.roles}    All roles played
{aggregate_cast.1.total_episodes}  Episode count
{aggregate_crew.1.name}     First crew member (all seasons)
{aggregate_crew.1.jobs}     All jobs held
```

**API Support:**
- TMDb: Full support (TV only)
- Others: Not supported

## FFprobe Variables (if ffprobe_enable: true)

### Video Stream

```
{video.codec}               Video codec (h264, hevc, av1, vp9, mpeg4)
{video.codec_long}          Full codec name (H.264 / AVC)
{video.profile}             Codec profile (High, Main, Baseline)
{video.level}               Codec level
{video.resolution}          Resolution height (1080, 720, 480)
{video.width}               Width (pixels)
{video.height}              Height (pixels)
{video.aspect}              Aspect ratio (16:9, 4:3)
{video.fps}                 Frame rate (23.976, 24, 25, 29.97, 30, 60)
{video.bitrate}             Bitrate (Mbps)
{video.pix_fmt}             Pixel format (yuv420p, yuv420p10le)
{video.color_space}         Color space (bt709, bt2020)
{video.color_transfer}      Color transfer (smpte2084, bt709)
{video.color_primaries}     Color primaries (bt709, bt2020)
```

**Resolution Detection:**
- 3840x2160 → 2160
- 1920x1080 → 1080
- 1280x720 → 720
- 720x480 → 480

**Codec Normalization:**
- h264, avc → h264
- hevc, h265 → hevc
- av1 → av1
- vp9 → vp9

### Audio Streams (1-based indexing)

```
{audio.1.codec}             First audio codec (aac, ac3, dts, flac, opus, mp3)
{audio.1.codec_long}        Full codec name (AAC, Dolby Digital)
{audio.1.language}          Language code (eng, tur, jpn, etc.)
{audio.1.channels}          Channel count (2, 6, 8)
{audio.1.channel_layout}    Layout (stereo, 5.1, 7.1)
{audio.1.bitrate}           Bitrate (Kbps)
{audio.1.sample_rate}       Sample rate (48000, 44100)
{audio.1.title}             Track title
{audio.1.default}           Default track (true/false)

{audio.2.codec}             Second audio stream
{audio.N.codec}             Nth audio stream
{audioCount}                Total audio streams
```

**Codec Normalization:**
- aac → aac
- ac3, eac3 → ac3
- dts, dts-hd → dts
- truehd → truehd
- flac → flac
- opus → opus

### Subtitle Streams (1-based indexing)

```
{subtitle.1.codec}          First subtitle codec (srt, ass, pgs, vobsub)
{subtitle.1.language}       Language code (eng, tur, etc.)
{subtitle.1.title}          Track title
{subtitle.1.forced}         Forced subtitle (true/false)
{subtitle.1.default}        Default track (true/false)

{subtitle.2.codec}          Second subtitle stream
{subtitle.N.codec}          Nth subtitle stream
{subtitleCount}             Total subtitle streams
```

### Container Info

```
{container.format}          Container format (matroska, mp4, avi)
{container.duration}        Duration (seconds)
{container.size}            File size (bytes)
{container.bitrate}         Total bitrate (Kbps)
```

## Nested Access

All nested fields accessible with dot notation:

```
{tmdb.first_air_date}       Direct TMDb field access
{tmdb.genres.1.name}        First genre from TMDb
{tmdb.networks.1.name}      First network from TMDb
{tmdb.vote_average}         Rating from TMDb
{ffprobe.streams.0.codec}   Direct FFprobe stream access
```

## Summary Variables

Available in summary template only:

```
{total_time}                Total processing time (seconds)
{avg_time}                  Average time per file (seconds)
{min_time}                  Fastest file time (seconds)
{max_time}                  Slowest file time (seconds)
{success}                   Successful operations count
{failed}                    Failed operations count
{total}                     Total files processed
```

## Variable Resolution Rules

1. Variables resolved from query context first
2. Nested fields accessed with dot notation
3. Array indexing is 1-based (not 0-based)
4. Missing variables resolve to empty string
5. Type conversion automatic (int, float, string, bool)
6. Filters applied left-to-right

## Performance Notes

- Extras variables require API calls
- FFprobe variables require media analysis
- Disable unused extras for speed
- Use caching (ffprobe_nfo_enable: true)
