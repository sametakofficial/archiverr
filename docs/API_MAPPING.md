# API Response Structure & Variable Mapping

Bu dokümant archiverr'ın normalize edilmiş API yanıt yapısını ve kullanılabilir değişkenleri gösterir.

## 📊 Ana Yapı

```python
api_response = {
    'globals': {...},     # Global metadata (parsed, execution)
    'file': {...},        # File metadata (FFProbe)
    'show': {...},        # TV show metadata
    'season': {...},      # Season metadata
    'episode': {...},     # Episode metadata
    'movie': {...},       # Movie metadata
    'tmdb': {...},        # TMDb client namespace
    'ffprobe': {...},     # FFProbe client namespace
}
```

---

## 🌐 Globals Namespace

### `$parsed.*` - Parsed Filename Data

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$parsed.mediaType` | string | `"show"` / `"movie"` | Media type |
| `$parsed.showTitle` | string | `"Friends"` | TV show title |
| `$parsed.movieTitle` | string | `"Inception"` | Movie title |
| `$parsed.movieYear` | int | `2010` | Movie release year |
| `$parsed.seasonNumber` | int | `1` | Season number |
| `$parsed.episodeNumber` | int | `4` | Episode number |
| `$parsed.ignored` | list | `[]` | Ignored tokens |

### `$execution.*` - Execution Metadata

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$execution.status` | string | `"success"` | Execution status |
| `$execution.time` | float | `2.34` | Total execution time |
| `$execution.apiSource` | string | `"tmdb"` | Primary API source |
| `$execution.tmdbTime` | float | `1.23` | TMDb execution time |
| `$execution.ffprobeTime` | float | `0.11` | FFProbe execution time |
| `$execution.clients.tmdb.time` | float | `1.23` | Per-client timing |
| `$execution.clients.tmdb.success` | bool | `true` | Client success status |

---

## 📁 File Namespace

### `$file.*` - File & Media Technical Data (FFProbe)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$file.path` | string | `"/media/file.mkv"` | Full file path |
| `$file.name` | string | `"file.mkv"` | File name |
| `$file.size` | int | `1073741824` | File size (bytes) |
| `$file.container` | string | `"matroska"` | Container format |

### `$file.video.*` - Video Stream

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$file.video.codec` | string | `"h264"` | Video codec |
| `$file.video.width` | int | `1920` | Video width |
| `$file.video.height` | int | `1080` | Video height |
| `$file.video.resolution` | string | `"1080p"` | Resolution label |
| `$file.video.fps` | float | `23.976` | Frame rate |
| `$file.video.bitrate` | int | `5000000` | Video bitrate |
| `$file.video.duration` | float | `1320.5` | Duration (seconds) |
| `$file.videoLength` | float | `1320.5` | Alias for duration |

### `$file.audio.*` - Audio Streams (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$file.audio.0.codec` | string | `"aac"` | Audio codec |
| `$file.audio.0.channels` | int | `6` | Channel count |
| `$file.audio.0.language` | string | `"eng"` | Language code |
| `$file.audio.0.bitrate` | int | `192000` | Audio bitrate |

### `$file.subtitles.*` - Subtitle Streams (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$file.subtitles.0.language` | string | `"eng"` | Subtitle language |
| `$file.subtitles.0.forced` | bool | `false` | Forced subtitle |
| `$file.subtitles:count` | int | `3` | Total subtitle count |

---

## 📺 Show Namespace

### `$show.*` - TV Show Metadata

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.title` | string | `"Friends"` | Show title |
| `$show.originalTitle` | string | `"Friends"` | Original title |
| `$show.overview` | string | `"Six friends..."` | Show description |
| `$show.firstAirDate` | string | `"1994-09-22"` | First air date (ISO) |
| `$show.lastAirDate` | string | `"2004-05-06"` | Last air date |
| `$show.status` | string | `"Ended"` | Show status |
| `$show.type` | string | `"Scripted"` | Show type |
| `$show.inProduction` | bool | `false` | Currently in production |
| `$show.numberOfSeasons` | int | `10` | Total seasons |
| `$show.numberOfEpisodes` | int | `236` | Total episodes |
| `$show.voteAverage` | float | `8.424` | Average rating |
| `$show.voteCount` | int | `8658` | Vote count |
| `$show.popularity` | float | `245.67` | Popularity score |
| `$show.homepage` | string | `"http://..."` | Official homepage |
| `$show.originalLanguage` | string | `"en"` | Original language |

### `$show.ids.*` - External IDs

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.ids.tmdb` | string | `"1668"` | TMDb ID |
| `$show.ids.imdb` | string | `"tt0108778"` | IMDb ID |
| `$show.ids.tvdb` | string | `"79168"` | TVDB ID |

### `$show.networks.*` - Networks (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.networks.0.name` | string | `"NBC"` | Network name |
| `$show.networks.0.id` | string | `"6"` | Network ID |
| `$show.networks:count` | int | `2` | Total networks |

### `$show.genres.*` - Genres (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.genres.0` | string | `"Comedy"` | Genre name |
| `$show.genres:count` | int | `2` | Total genres |

### `$show.seasons.*` - Season List (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.seasons.0.number` | int | `1` | Season number |
| `$show.seasons.0.episodeCount` | int | `24` | Episodes in season |
| `$show.seasons:count` | int | `10` | Total seasons |

### `$show.extras.*` - Show Extras

#### `$show.extras.credits.*` - Cast & Crew

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.extras.credits.cast.0.name` | string | `"Jennifer Aniston"` | Actor name |
| `$show.extras.credits.cast.0.character` | string | `"Rachel Green"` | Character name |
| `$show.extras.credits.cast.0.order` | int | `0` | Billing order |
| `$show.extras.credits.cast:count` | int | `6` | Total cast |
| `$show.extras.credits.crew.0.name` | string | `"David Crane"` | Crew name |
| `$show.extras.credits.crew.0.job` | string | `"Director"` | Job title |
| `$show.extras.credits.crew:count` | int | `45` | Total crew |

#### `$show.extras.images.*` - Images

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.extras.images.posters.0.url` | string | `"https://..."` | Poster URL |
| `$show.extras.images.posters.0.width` | int | `2000` | Image width |
| `$show.extras.images.posters:count` | int | `12` | Total posters |
| `$show.extras.images.backdrops:count` | int | `8` | Total backdrops |

#### `$show.extras.videos.*` - Videos

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.extras.videos.trailers.0.name` | string | `"Official Trailer"` | Video name |
| `$show.extras.videos.trailers.0.key` | string | `"dQw4w9WgXcQ"` | YouTube key |
| `$show.extras.videos.trailers:count` | int | `3` | Total trailers |

#### `$show.extras.keywords.*` - Keywords (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$show.extras.keywords.0.name` | string | `"friendship"` | Keyword |
| `$show.extras.keywords:count` | int | `15` | Total keywords |

---

## 📅 Season Namespace

### `$season.*` - Season Metadata

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$season.number` | int | `1` | Season number |
| `$season.name` | string | `"Season 1"` | Season name |
| `$season.overview` | string | `"The first..."` | Season description |
| `$season.airDate` | string | `"1994-09-22"` | Air date |
| `$season.episodeCount` | int | `24` | Episodes in season |
| `$season.voteAverage` | float | `8.2` | Season rating |
| `$season.poster` | string | `"https://..."` | Poster URL |

### `$season.episodes.*` - Episodes List

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$season.episodes.0.number` | int | `1` | Episode number |
| `$season.episodes.0.title` | string | `"Pilot"` | Episode title |
| `$season.episodes:count` | int | `24` | Total episodes |

---

## 🎬 Episode Namespace

### `$episode.*` - Episode Metadata

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$episode.number` | int | `4` | Episode number |
| `$episode.title` | string | `"The One With..."` | Episode title |
| `$episode.overview` | string | `"While the men..."` | Episode description |
| `$episode.airDate` | string | `"1994-10-13"` | Air date (ISO) |
| `$episode.runtime` | int | `23` | Runtime (minutes) |
| `$episode.voteAverage` | float | `7.739` | Episode rating |
| `$episode.voteCount` | int | `69` | Vote count |
| `$episode.productionCode` | string | `"456654"` | Production code |
| `$episode.still` | string | `"https://..."` | Still image URL |
| `$episode.stillPath` | string | `"/path.jpg"` | Still image path |

### `$episode.extras.*` - Episode Extras

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$episode.extras.credits.cast:count` | int | `6` | Guest stars |
| `$episode.extras.images:count` | int | `3` | Episode images |

---

## 🎥 Movie Namespace

### `$movie.*` - Movie Metadata

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$movie.title` | string | `"Inception"` | Movie title |
| `$movie.originalTitle` | string | `"Inception"` | Original title |
| `$movie.overview` | string | `"A thief who..."` | Movie description |
| `$movie.releaseDate` | string | `"2010-07-16"` | Release date (ISO) |
| `$movie.status` | string | `"Released"` | Release status |
| `$movie.runtime` | int | `148` | Runtime (minutes) |
| `$movie.budget` | int | `160000000` | Production budget |
| `$movie.revenue` | int | `825532764` | Box office revenue |
| `$movie.voteAverage` | float | `8.367` | Average rating |
| `$movie.voteCount` | int | `35481` | Vote count |
| `$movie.popularity` | float | `98.765` | Popularity score |
| `$movie.homepage` | string | `"http://..."` | Official homepage |
| `$movie.originalLanguage` | string | `"en"` | Original language |

### `$movie.ids.*` - External IDs

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$movie.ids.tmdb` | string | `"27205"` | TMDb ID |
| `$movie.ids.imdb` | string | `"tt1375666"` | IMDb ID |

### `$movie.genres.*` - Genres (Array)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `$movie.genres.0` | string | `"Action"` | Genre name |
| `$movie.genres:count` | int | `3` | Total genres |

### `$movie.extras.*` - Movie Extras

Similar structure to `$show.extras.*` with credits, images, videos, keywords.

---

## 🔧 Variable Modifiers

### Format Modifiers

| Modifier | Usage | Example | Result |
|----------|-------|---------|--------|
| `:year` | Extract year | `$show.firstAirDate:year` | `1994` |
| `:max:N` | Truncate string | `$episode.overview:max:50` | First 50 chars |
| `:02d` | Zero-pad integer | `$parsed.seasonNumber:02d` | `01` |
| `:upper` | Uppercase | `$show.title:upper` | `FRIENDS` |
| `:lower` | Lowercase | `$show.title:lower` | `friends` |
| `:.2f` | Float format | `$execution.time:.2f` | `2.34` |

### Array Modifiers

| Modifier | Usage | Example | Result |
|----------|-------|---------|--------|
| `:count` | Array length | `$show.genres:count` | `2` |
| `.N` | Array index | `$show.genres.0` | `"Comedy"` |
| `:loop:field\|sep` | Loop & join | `$show.genres:loop:name\|, ` | `Comedy, Romance` |
| `:filter:key=val` | Filter array | `$show.extras.credits.crew:filter:job=Director` | Directors only |

### Loop Syntax

```yaml
# Basic loop
$show.extras.credits.cast:loop:name|, :max:5
# Output: Jennifer Aniston, Courteney Cox, Lisa Kudrow, Matt LeBlanc, Matthew Perry

# Loop with multiple fields
$show.extras.credits.cast:loop:name → character|
# Output:
# Jennifer Aniston → Rachel Green
# Courteney Cox → Monica Geller

# Filter + Loop
$show.extras.credits.crew:filter:job=Director:loop:name|, :max:3
# Output: James Burrows, David Crane, Marta Kauffman
```

---

## 📝 Config.yml Examples

### Rename Template with Loops

```yaml
shows:
  print: |
    ✓ SHOW: $show.title ($show.firstAirDate:year)
    
    [Cast] $show.extras.credits.cast:loop:name|, :max:5
    [Directors] $show.extras.credits.crew:filter:job=Director:loop:name|, :max:2
    [Keywords] $show.extras.keywords:loop:name|, :max:10
    
  save: "$show.title ($show.firstAirDate:year)/Season $parsed.seasonNumber/$show.title - S$parsed.seasonNumber:02dE$parsed.episodeNumber:02d - $episode.title"
```

### Priority with Dependencies

```yaml
priority:
  - ffprobe,tmdb  # Run FFProbe and TMDb in parallel
  - tvdb          # Fallback to TVDB if TMDb fails
  - omdb          # Fallback to OMDb

tmdb:
  expects:
    - "$file.videoLength"  # Requires FFProbe data
  dependsOn: "ffprobe"     # Wait for FFProbe
```

---

## 🎯 Best Practices

1. **Always check :count before looping**
   ```yaml
   Cast ($show.extras.credits.cast:count): $show.extras.credits.cast:loop:name|, :max:5
   ```

2. **Use fallback values**
   ```yaml
   Rating: $show.voteAverage/10 ($show.voteCount votes) | N/A if missing
   ```

3. **Format dates properly**
   ```yaml
   Year: $show.firstAirDate:year
   Full Date: $show.firstAirDate
   ```

4. **Combine modifiers**
   ```yaml
   $show.title:upper:max:20  # UPPERCASE and truncate
   ```

5. **Filter before looping**
   ```yaml
   $show.extras.credits.crew:filter:job=Director:loop:name|, :max:3
   ```
