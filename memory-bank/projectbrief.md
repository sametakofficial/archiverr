# Project Brief: archiverr

## Core Purpose
Enterprise-grade media file organization system for archiving movies and TV series with automated TMDb metadata retrieval, FFprobe video analysis, and flexible YAML-driven renaming rules.

## Primary Goals
1. **Automated Organization**: Parse filenames → Match TMDb → Rename/move with rich metadata
2. **Flexibility**: YAML configuration with powerful variable engine and query system
3. **Safety**: Dry-run mode, hardlink support, undo/redo capability
4. **Performance**: Parallel processing for TMDb/FFprobe operations
5. **Production Ready**: Structured logging, error handling, database persistence

## Target Users
- Media archivists managing large collections (TBs of content)
- Home server administrators (Plex/Jellyfin/Emby)
- Content curators requiring consistent naming
- Advanced users needing custom organization rules

## Key Features
- **TMDb Integration**: Automatic metadata retrieval (movies/TV shows/episodes)
- **FFprobe Analysis**: Video codec, resolution, audio tracks, subtitles
- **Variable Engine**: Unified `{var:filter}` syntax for patterns
- **Query Engine**: Conditional processing with `where`/`loop`/`save`
- **NFO Support**: Kodi-compatible metadata + FFprobe cache
- **Parallel Processing**: Configurable worker count for batch operations
- **Structured Logging**: ISO8601 timestamps, component-based organization
- **FastAPI Backend**: REST API for job management, history, undo/redo (planned)

## Non-Goals
- Video transcoding/conversion
- Torrent client integration
- Media playback
- Duplicate detection (separate tool domain)

## Success Criteria
- Process 1000+ files without errors
- Sub-second per-file processing (with cache)
- Zero data loss (dry-run + hardlink safety)
- Clear error reporting with actionable messages
- API-driven architecture for UI integration
