# Product Context

## Problem Statement
Media collections grow chaotic without consistent naming and organization:
- Downloaded files have arbitrary naming schemes
- Manual renaming is time-consuming and error-prone
- Metadata extraction requires multiple tools
- Organization rules change as collection grows
- No way to undo bulk operations

## Solution
Declarative YAML configuration system that:
1. Parses any filename format (regex-based)
2. Queries TMDb for accurate metadata
3. Analyzes video files with FFprobe
4. Applies user-defined templates with variables/filters
5. Executes rename/move operations safely
6. Logs all changes for undo capability

## User Experience Flow

### Basic Workflow
```bash
# 1. Configure once
vim config/config.yml  # Set TMDb API key, define patterns

# 2. Run dry-run
archiverr --paths-from files.txt --type tv --dry-run

# 3. Review output, then execute
archiverr --paths-from files.txt --type tv

# 4. Optional: Undo if needed (future feature)
archiverr undo --session session-id
```

### Configuration Example
```yaml
rename:
  series:
    print: "{showName} - S{seasonNumber:pad:2}E{episodeNumber:pad:2}"
    save: "{showName} ({tmdb.first_air_date:year})/Season {seasonNumber}/{showName} - S{seasonNumber:pad:2}E{episodeNumber:pad:2} - {episodeName}"
```

### Expected Output
```
2025-10-31T16:24:11.004+03:00  INFO   parse.start          file=Friends.S01E01.mkv
2025-10-31T16:24:11.112+03:00  INFO   tmdb.match           id=1668 name=Friends year=1994
2025-10-31T16:24:11.256+03:00  INFO   pattern.result       path=Friends (1994)/Season 1/Friends - S01E01 - Pilot.mkv
2025-10-31T16:24:11.300+03:00  INFO   file.success         file=Friends.S01E01.mkv
```

## Value Proposition
- **Time Savings**: Bulk operations instead of manual work
- **Consistency**: Enforced naming standards across collection
- **Flexibility**: Change rules without code changes
- **Safety**: Dry-run mode prevents mistakes
- **Metadata Rich**: TMDb + FFprobe data in filenames/NFOs
- **Scalability**: Parallel processing for large batches

## Competitive Landscape
- **FileBot**: Java-based, subscription model, less flexible
- **Sonarr/Radarr**: Focused on download automation, not reorganization
- **Manual Scripts**: Brittle, hard to maintain, no metadata integration
- **archiverr Advantage**: YAML flexibility + TMDb + FFprobe + Parallel + API-first

## Future Vision
- Web UI for configuration and monitoring
- Database-backed operation history
- Undo/redo with diff visualization
- Custom metadata sources (IMDB, Trakt, etc.)
- Plugin system for extensibility
- Multi-user support with permissions
