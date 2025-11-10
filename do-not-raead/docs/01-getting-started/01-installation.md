# Installation

## API Keys

### TMDb (Required)
1. Register at [themoviedb.org](https://www.themoviedb.org/)
2. Get API key: Settings > API
3. Add to `config.yml`:

```yaml
tmdb:
  api_key: "your_key_here"
```

### TVDb (Optional)
```yaml
tvdb:
  api_key: "your_key_here"
```

### OMDb (Optional)
```yaml
omdb:
  api_key: "your_key_here"
```

## Configuration

Edit `config.yml`:

```yaml
tmdb:
  api_key: "..."
  lang: "en-US"

options:
  dry_run: true

rename:
  series:
    save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
```

## Verify

```bash
archiverr --path "/test/file.mkv" --type tv --dry-run
```
