# Progress

## What Works

### ✅ Core Functionality
- [x] CLI entry point with argparse
- [x] YAML configuration loading
- [x] .env fallback for backward compatibility
- [x] Directory scanning (recursive)
- [x] Filename parsing (movies and TV shows)
- [x] FFprobe integration
  - [x] Video codec/resolution detection
  - [x] Audio track enumeration
  - [x] Subtitle detection
  - [x] NFO caching (optional)
- [x] File operations
  - [x] Move files
  - [x] Hardlink creation
  - [x] unique_path() collision avoidance
  - [x] Dry-run mode
- [x] NFO generation
  - [x] Kodi-compatible movie NFO
  - [x] Kodi-compatible episode NFO

### ✅ Multi-API Integration
- [x] TMDb: Movies + TV shows (comprehensive metadata)
- [x] TVMaze: TV shows only (better regional data)
- [x] TVDb: Movies + TV shows (JWT auth, v4 API)
- [x] OMDb: Movies + TV shows (IMDb-based)
- [x] **NEW** List-based priority system (simpler config)
- [x] Priority-based fallback system
- [x] Content-type awareness (skip incompatible APIs)
- [x] API source tracking (`apiSource` variable)
- [x] Automatic normalization of API responses
- [x] Multi-language support (lang + fallback_lang)
- [x] Sequential processing (match->rename per file)
- [x] **COMPLETE** All API extras working (credits, images, external_ids, content_ratings)
- [x] **FIXED** Episode name bug (variable override conflict resolved)

### ✅ Variable Engine
- [x] Unified `{var:filter}` syntax
- [x] Filter system
  - [x] Text filters (upper, lower, title, slug, trim)
  - [x] Numeric filters (pad:N, max:N)
  - [x] Date filters (year)
  - [x] Advanced filters (replace, snake, camel)
- [x] Nested variable access (`{tmdb.first_air_date:year}`)
- [x] 1-based array indexing (`{audio.1.language}`)
- [x] Context building from TMDb + FFprobe + parsed data
- [x] Query-based configuration (print/save templates)

### ✅ Logging System
- [x] Structured logger with ISO8601 timestamps
- [x] Component-based organization
- [x] Context fields (key=value pairs)
- [x] Debug mode toggle
- [x] Session statistics
- [x] JSON report generation
- [x] Failed files tracking
- [x] Timing statistics (took variable)
- [x] Customizable summary output

### ✅ Documentation
- [x] YAML_ENGINE.md (variable reference)
- [x] README.md with examples
- [x] TODO.md for development tracking
- [x] Memory bank structure (AGENT.MD compliant)

## What's Left to Build

### 🔨 In Progress
- [x] TVMaze integration ✅
- [x] API Manager with priority/fallback ✅
- [x] Parallel processing removal ✅
- [x] TVDb API client ✅
- [x] OMDb API client ✅
- [x] Multi-API testing with real data ✅
- [x] All API extras implementation ✅
- [ ] Force variable feature (cross-API data fetching)
- [ ] Comprehensive testing suite

### 📋 Planned - High Priority

#### Database Integration
- [ ] SQLite schema for operation history
- [ ] Models for jobs, files, operations
- [ ] Migration system
- [ ] Undo/redo with diff storage

#### FastAPI Backend
- [ ] API endpoints
  - [ ] POST /jobs (create rename job)
  - [ ] GET /jobs (list jobs)
  - [ ] GET /jobs/{id} (job details)
  - [ ] POST /jobs/{id}/undo (undo operation)
  - [ ] GET /config (get current config)
  - [ ] PUT /config (update config)
- [ ] WebSocket for real-time progress
- [ ] OpenAPI documentation
- [ ] CORS configuration

#### Query Engine Completion
- [ ] `where` clause evaluation
  - [ ] Comparison operators (==, !=, <, >, <=, >=)
  - [ ] Logical operators (and, or, not)
  - [ ] Variable resolution in conditions
- [ ] `loop` implementation
  - [ ] Iteration over arrays
  - [ ] Variable scoping
  - [ ] Nested loop support
- [ ] `save` action with query context
- [ ] Integration with main rename engine

### 📋 Planned - Medium Priority

#### Caching System
- [ ] TMDb response caching
  - [ ] In-memory LRU cache
  - [ ] Persistent cache (SQLite)
  - [ ] TTL configuration
  - [ ] Cache invalidation
- [ ] Matcher result caching
- [ ] FFprobe result sharing across runs

#### Testing
- [ ] Unit tests
  - [ ] Variable engine filters
  - [ ] Config loading
  - [ ] Filename parsing
- [ ] Integration tests
  - [ ] TMDb matching
  - [ ] FFprobe analysis
  - [ ] Path building
- [ ] End-to-end tests
  - [ ] Full pipeline with mock data
  - [ ] Error scenarios
  - [ ] Edge cases

#### Web UI
- [ ] React/Vue frontend
- [ ] Job creation wizard
- [ ] Config editor with validation
- [ ] Operation history browser
- [ ] Diff viewer for undo/redo
- [ ] Real-time progress display

### 📋 Planned - Low Priority

#### Enhanced Features
- [ ] Multiple metadata sources
  - [ ] IMDB integration
  - [ ] Trakt integration
  - [ ] Custom source plugins
- [ ] Advanced filtering
  - [ ] Quality profiles
  - [ ] Language preferences
  - [ ] Custom tags
- [ ] Batch operations
  - [ ] Multi-type processing (movies + TV in one run)
  - [ ] Conditional processing
  - [ ] Scheduled jobs

#### DevOps
- [ ] Docker containerization
- [ ] Docker Compose setup
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Release automation
- [ ] Package distribution (PyPI)

## Current Status

### Version: 0.6.0
**Status**: Production-ready CLI with 4 fully-functional APIs (TMDb, TVMaze, TVDb, OMDb)

**Recent Milestones**:
- 2025-10-30: Variable engine unification complete
- 2025-10-30: Structured logging system implemented
- 2025-10-31 AM: Performance optimizations (ffprobe options)
- 2025-10-31 AM: Memory bank initialization
- 2025-10-31 PM: Timing statistics and customizable summary
- 2025-10-31 Late: TVMaze integration, multi-API priority system, parallel removal
- 2025-11-01 AM: List-based priority, OMDb integration, sequential processing, TVDb fixes
- 2025-11-03 PM: **Episode name bug fixed**, **All API extras complete** (TVDb, TVMaze, OMDb)

**Active Development**:
- All APIs fully operational with complete extras support
- Variable system stabilized (no more override conflicts)
- Production testing with real-world data

**Blockers**:
- None currently

## Known Issues

### Critical
- None

### Major
- [ ] No TMDb response caching (duplicate API calls for same content)
- [ ] No operation history (can't undo)
- [ ] Query engine incomplete (where/loop not functional)

### Minor
- [ ] Season padding not configurable (always 2 digits)
- [ ] No progress bar for batch operations
- [ ] JSON report doesn't include operation diff
- [ ] No validation for template syntax errors

### Documentation
- [ ] YAML_ENGINE.md missing query examples
- [ ] README missing installation instructions
- [ ] No migration guide from older versions

## Evolution of Decisions

### Configuration Format
- **v0.1**: .env only → Limited flexibility
- **v0.2**: YAML with pattern strings → Better organization
- **v0.3**: YAML with query objects (print/save) → Full flexibility
- **Impact**: Breaking change, but migration path clear

### Variable Syntax
- **v0.1**: `$var` (shell-style) → Confusion with env vars
- **v0.3**: `{var}` (Jinja-style) → Clearer, filter support
- **Impact**: Breaking change, regex-based migration possible

### Logging Strategy
- **v0.1**: Colored console output → Hard to parse
- **v0.2**: JSON mode option → Good for automation, bad for humans
- **v0.3**: Structured logs with debug toggle → Best of both
- **Impact**: Additive, no breaking changes

### Parallel Processing
- **v0.1**: Sequential → Slow for large batches
- **v0.2**: Hardcoded 6 workers → Not configurable
- **v0.3**: Config-driven parallel count → User control
- **Impact**: Performance improvement, backward compatible

## Next Session Priorities

1. Test performance improvements with new config options
2. Validate FFprobe behavior matrix
3. Document new configuration options
4. Plan database schema for undo/redo
5. Begin FastAPI backend skeleton
