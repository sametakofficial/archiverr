# Quick Start

## Test Run

```bash
archiverr --path "/downloads/breaking.bad.s01e01.mkv" --type tv --dry-run
```

Expected output:
```
Matched: Breaking Bad (2008)
  S01E01 - Pilot
  New: Breaking Bad/Season 1/Breaking Bad - S01E01.mkv
```

## Execute

```bash
archiverr --path "/downloads/breaking.bad.s01e01.mkv" --type tv
```

## Batch Processing

```bash
archiverr --path "/downloads/tv-shows/" --type tv
```

## Common Options

```
--type tv|movie      Media type
--dry-run           Test mode
--debug             Verbose logs
--hardlink          Hardlink vs move
```
