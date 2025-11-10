# Project Brief: archiverr

## Core Purpose
Plugin-based media metadata enrichment and organization system with multi-API support (TMDb, TVDb, TVMaze, OMDb, FFprobe), Jinja2 templating, and task-driven execution model.

## Primary Goals
1. **Plugin Architecture**: Flat, discoverable plugin system with manifest-based configuration
2. **Multi-API Support**: Comprehensive metadata from 4+ APIs with automatic fallback
3. **Template-Driven**: Jinja2 templates for all output (print, save, conditional execution)
4. **Flexibility**: YAML-driven tasks, per-match execution, dependency resolution
5. **Production Ready**: Clean separation of concerns, no core dependencies on plugins

## Target Users
- Media archivists managing large collections
- Home server administrators (Plex/Jellyfin/Emby)
- Developers building media automation tools
- Advanced users needing extensible metadata pipelines

## Key Features
- **Plugin System**: Flat plugins/ directory, plugin.json manifests, auto-discovery
- **Multi-API**: TMDb, TVDb, TVMaze, OMDb with unified response structure
- **Jinja2 Engine**: Full template power with filters, conditions, variables
- **Task System**: Per-match execution, conditional tasks, summary tasks
- **Extras Support**: Dedicated extras.py modules for extended metadata (credits, images, videos)
- **Clean Architecture**: Core system knows nothing about plugins, fully plugin-agnostic
- **Dependency Resolution**: Topological sort, parallel execution groups
- **Expects System**: Runtime data validation before plugin execution
- **Compact Reports**: Structural simplification (94% size reduction) for AI analysis
- **Dual Reports**: Full data + compact structure view

## Architecture Philosophy
**Plugin-Agnostic Core**:
- Core cannot import plugin-specific types
- Plugins define their own data structures
- Config.yml is opaque dict to core
- Plugin.json declares: category, depends_on, expects

## Non-Goals
- Video transcoding/conversion
- Torrent client integration
- Media playback
- Duplicate detection
- Plugin package management (manual installation)

## Success Criteria
- ✅ Process 100+ files without errors
- ✅ Clean plugin isolation (no cross-plugin imports)
- ✅ Template rendering <10ms per match
- ✅ API response structure fully normalized
- ✅ Error handling without silent failures
- ✅ Zero hardcoded plugin names in core
- ✅ Expects-based execution (runtime validation)
- ✅ Compact system operational (AI-readable structure)
- ✅ 3,500 lines removed (schema system)
- ✅ Professional folder structure (no _system suffixes)
