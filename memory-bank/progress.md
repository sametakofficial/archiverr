# Progress

## What Works (v2.0 - Plugin Architecture)

### ✅ Plugin System
- [x] Plugin discovery via plugin.json manifests
- [x] Flat plugins/ directory structure
- [x] Auto-loading of enabled plugins from config.yml
- [x] Dependency resolution (topological sort)
- [x] Execution groups (parallel-safe grouping)
- [x] Plugin categories (input/output)
- [x] Status tracking (success/failed/not_supported)

### ✅ Core Plugins

**Input Plugins**:
- [x] Scanner - Directory/file scanning with recursive option
- [x] File Reader - Read targets from targets.txt

**Output Plugins**:
- [x] FFprobe - Video/audio analysis
- [x] Renamer - Filename parsing (movies/shows)
- [x] TMDb - Movie/TV metadata with extras
- [x] TVDb - Movie/TV metadata with extras (JWT auth)
- [x] TVMaze - TV-only metadata with extras
- [x] OMDb - Movie/TV metadata (IMDb-based)

### ✅ Extras System
- [x] Separate extras.py modules per plugin
- [x] TMDb extras: movie_credits, movie_images, movie_videos, movie_keywords, episode_credits, episode_images, show_images, show_videos
- [x] TVDb extras: show_cast, show_images, movie_credits, movie_images, episode_images
- [x] TVMaze extras: show_cast, show_crew, show_images, episode_guest_cast, episode_guest_crew
- [x] Config-driven extras (enable/disable per extra type)

### ✅ Template System
- [x] Jinja2 template engine
- [x] Full Jinja2 syntax support (no custom $ prefix)
- [x] Conditional templates ({% if %} statements)
- [x] Variable access ({{ plugin.field.subfield }})
- [x] Filters (| upper, | lower, | length, etc.)
- [x] Per-match task execution
- [x] Summary tasks (run on last match only)

### ✅ Task System
- [x] Print tasks (console output)
- [x] Save tasks (file writing - planned)
- [x] Conditional execution
- [x] Summary tasks
- [x] Task configuration via config.yml

### ✅ Response Structure
- [x] Unified API response format
- [x] Per-match data (`items` array)
- [x] Global status tracking
- [x] Plugin status per match (`matchGlobals`)
- [x] Error counting (failed plugins only)
- [x] Not supported tracking (doesn't count as error)

### ✅ Configuration
- [x] YAML-based config.yml
- [x] Per-plugin configuration
- [x] Plugin enable/disable
- [x] Extras configuration
- [x] Task definitions
- [x] Global options (debug, dry_run, hardlink)

### ✅ Architecture
- [x] Plugin-agnostic core
- [x] No core dependencies on plugins
- [x] Clean separation of concerns
- [x] Manifest-based plugin metadata
- [x] Dependency injection via config

## What's Left to Build

### 🔨 High Priority

#### Save Task Implementation
- [ ] File writing from templates
- [ ] Directory creation
- [ ] Destination path validation
- [ ] Collision handling

#### Config Validation
- [ ] Plugin.json schema validation
- [ ] Config.yml validation
- [ ] Dependency cycle detection
- [ ] Required field validation

#### Error Handling
- [ ] Better error messages
- [ ] Error recovery strategies
- [ ] Partial failure handling
- [ ] Rollback mechanism

### 📋 Medium Priority

#### Testing
- [ ] Unit tests for core system
- [ ] Plugin integration tests
- [ ] Template rendering tests
- [ ] Dependency resolution tests

#### Documentation
- [ ] Plugin development guide
- [ ] Template syntax reference
- [ ] Config.yml reference
- [ ] API response format docs

#### Performance
- [ ] Response caching
- [ ] Template compilation caching
- [ ] Parallel plugin execution optimization
- [ ] Memory usage profiling

### 📋 Low Priority

#### MongoDB Integration
- [ ] Response persistence
- [ ] History tracking
- [ ] Query interface
- [ ] Branch/commit model

#### Web UI
- [ ] Task builder interface
- [ ] Config editor
- [ ] Response viewer
- [ ] Plugin manager

#### Advanced Features
- [ ] Plugin hot-reloading
- [ ] Dynamic plugin installation
- [ ] Plugin marketplace
- [ ] Custom filter registration

## Current Status

### Version: 2.0.0-alpha (Plugin Architecture)
**Status**: Core system functional, production testing needed

**Recent Milestones**:
- 2025-11-04: Plugin system design complete
- 2025-11-05: Core plugins migrated
- 2025-11-06: Extras refactoring complete
- 2025-11-06: Error counting fixed
- 2025-11-06: Template system operational

**Active Development**:
- Plugin system refinement
- Extras optimization
- Testing framework setup

**Blockers**:
- None

## Known Issues

### Critical
- None

### Major
- [ ] No save task implementation (only print works)
- [ ] No config validation (manual errors possible)
- [ ] No plugin version compatibility checks

### Minor
- [ ] No progress indicators
- [ ] Limited error messages
- [ ] No dry-run visualization

### Documentation
- [ ] No plugin development guide
- [ ] No template examples
- [ ] No migration guide from v1.x

## Removed Features (From v1.x)

### Removed in v2.0
- ❌ Variable engine with {var:filter} syntax → Jinja2
- ❌ Priority lists (tv_priority, movie_priority) → Plugin enable/disable
- ❌ integrations/ directory → plugins/
- ❌ APIManager with fallback → Plugin execution groups
- ❌ Custom template syntax → Standard Jinja2
- ❌ $ prefix for variables → Direct variable access
- ❌ core/matcher/ → plugins/renamer/
- ❌ core/renamer/engine.py → core/plugin_system/executor.py

### Why Removed
- Simpler architecture
- Industry-standard tools (Jinja2)
- Cleaner plugin isolation
- Easier to extend
- Less custom code to maintain

## Architecture Evolution

### v1.0 → v1.5 (Integrations Era)
- Centralized API clients
- Priority-based fallback
- Custom variable engine
- Template strings in config

### v1.5 → v2.0 (Plugin Refactoring)
- Distributed plugin system
- Dependency-based execution
- Jinja2 templates
- Task-driven output
- Extras separation

### Impact
- **Breaking**: Config format changed completely
- **Breaking**: Variable syntax changed ($ removed)
- **Breaking**: Response structure changed
- **Benefit**: Much more flexible and maintainable

## Next Session Priorities

1. Implement save task functionality
2. Add config validation
3. Write plugin development guide
4. Create testing framework
5. Performance profiling
