# OMDb Client

## Features

- Movies: Basic support
- TV Series: Basic support
- Episodes: Basic support

## Configuration

```yaml
omdb:
  api_key: "your_key"
```

## Extras

All data in single response (no extra requests):
- Credits (basic - actors, director)
- Images (single poster)
- External IDs (IMDB only)
- Content ratings (single rating)

Not supported:
- Videos
- Keywords
- Watch providers

## Rate Limit

1,000 requests per day (free tier)
