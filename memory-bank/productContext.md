# Product Context

## Problem Statement
Media collections grow chaotic without consistent naming and organization:
- Downloaded files have arbitrary naming schemes
- Manual renaming is time-consuming and error-prone
- Metadata extraction requires multiple tools
- Organization rules change as collection grows
- No way to undo bulk operations

## Solution
Plugin-based metadata enrichment system that:
1. Discovers files via scanner/file-reader plugins
2. Parses filenames with renamer plugin
3. Analyzes video files with FFprobe plugin
4. Queries multiple APIs (TMDb, TVDb, TVMaze, OMDb) for metadata
5. Executes user-defined tasks via Jinja2 templates
6. Generates dual reports (full + compact)
7. Validates plugin execution via expects system
8. Provides AI-readable structure views

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
- **Flexibility**: YAML config + Jinja2 templates
- **Safety**: Dry-run mode prevents mistakes
- **Metadata Rich**: 4 API sources (TMDb, TVDb, TVMaze, OMDb) + FFprobe
- **Scalability**: Parallel plugin execution
- **Extensibility**: Plugin-agnostic architecture
- **AI-Friendly**: Compact reports for normalization analysis
- **Production Ready**: Clean architecture, zero technical debt

## Competitive Landscape
- **FileBot**: Java-based, subscription model, less flexible
- **Sonarr/Radarr**: Focused on download automation, not reorganization
- **Manual Scripts**: Brittle, hard to maintain, no metadata integration
- **archiverr Advantage**: 
  - Multi-API support (4 providers)
  - Plugin-agnostic architecture
  - Expects-based execution
  - Compact reports for AI
  - Clean separation of concerns
  - Production ready

## Future Vision
- MongoDB integration (architecture ready)
- Plugin normalization improvements
- Web UI for configuration and monitoring
- Advanced branching (Git-like versioning)
- Unit tests and validation
- Plugin marketplace
