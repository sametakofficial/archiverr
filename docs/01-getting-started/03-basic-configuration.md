# Configuration

## Basic Config

```yaml
tmdb:
  api_key: "your_key"
  lang: "en-US"

options:
  dry_run: true

rename:
  series:
    save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
```

## API Priority

```yaml
tv_priority:
  - tmdb
  - tvdb
  - tvmaze
```

First API tried first, then next if no match.

## Language

```yaml
tmdb:
  lang: "tr-TR"
  fallback_lang: "en-US"
```

## Options

```yaml
options:
  dry_run: true      # Test mode
  debug: false       # Verbose logs
  hardlink: false    # Hardlink vs move
```

## Extras

```yaml
extras:
  tv_credits: true
  tv_images: true
  tv_external_ids: true
```

Each extra = 1 API call. Disable unused for speed.

## Patterns

```yaml
rename:
  series:
    save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
  movies:
    save: "{name} ({movieYear})/{name} ({movieYear})"
```

