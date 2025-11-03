# Active Context

## Current Focus
**ALL 4 APIs FULLY OPERATIONAL** - Episode names and extras working across TMDb, TVMaze, TVDb, OMDb. Variable system conflicts resolved.

## Recent Changes (Session: 2025-11-03 Afternoon)

### 7. Episode Name Bug Fix + API Extras Completion
**Date**: 2025-11-03 PM

**Critical Bug Fixed**: Episode names were missing in print templates despite being fetched correctly from all APIs.

**Root Cause**: 
- `_build_api_vars()` in `src/archiverr/core/query_engine/variables.py` was overriding `episodeName` with empty string
- This happened AFTER `query_logger.py` correctly set it from `ep_full`
- Classic variable override conflict - multiple functions setting same variable

**Files Modified**:
- `src/archiverr/core/query_engine/variables.py` - Removed episodeName override
- `src/archiverr/core/renamer/engine.py` - Added print_template check to need_ep calculation
- `src/archiverr/integrations/tvdb/extras.py` - Added tv_credits(), tv_content_ratings(), fixed tv_images()
- `src/archiverr/integrations/tvdb/client.py` - Enabled credits and content_ratings fetching
- `src/archiverr/integrations/tvmaze/client.py` - Added external_ids extraction
- `src/archiverr/integrations/omdb/client.py` - Already had extras extraction (completed earlier)

**TVDb Extras Implementation**:
- ✅ **Credits (Cast)**: Extracts from `/series/{id}/extended` endpoint's `characters` array
- ✅ **Content Ratings**: Extracts from `/series/{id}/extended` endpoint's `contentRatings` array  
- ✅ **Images**: Fixed `/series/{id}/artworks` parsing - handles array/dict responses, proper type mapping
- ✅ **External IDs**: Already working (IMDB, TVDB)
- ❌ Videos, Keywords, Watch Providers: Not available in TVDb API v4

**TVMaze Extras Implementation**:
- ✅ **External IDs**: IMDB ID, TVDB ID, TVMaze ID, TVRage ID from `externals` field
- ✅ **Credits**: Cast and crew already working
- ✅ **Images**: Already working
- ❌ Videos, Keywords, Watch Providers: Not available in TVMaze API

**OMDb Extras** (Already Completed):
- ✅ **Credits**: Actors, Director, Writer from raw response
- ✅ **Images**: Poster URL
- ✅ **External IDs**: IMDB ID
- ✅ **Content Ratings**: Rated field (PG, PG-13, R, etc.)
- ❌ Videos, Keywords, Watch Providers: Not available in OMDb API

**Architecture Lessons Learned**:
1. **Direct mapping principle**: API normalizer → variable system should be 1:1, no intermediate transformers
2. **Override conflicts**: Multiple functions setting same variables causes bugs (episodeName case)
3. **Silent failures**: `except: pass` hides critical bugs - always log exceptions
4. **Debug best practice**: Temporary debug logs helped trace the exact override point

**Testing Results**:
```
✅ TMDb: Episode names + all extras (credits, images, videos, keywords, external_ids, content_ratings, watch_providers)
✅ TVDb: Episode names + credits (7 cast) + images (74 posters, 349 backdrops) + external_ids + content_ratings
✅ TVMaze: Episode names + credits + images + external_ids (IMDB, TVDB)
✅ OMDb: Episode names + credits + images + external_ids + content_ratings
```

**Status**: ALL APIS PRODUCTION READY ✅

## Previous Changes (Session: 2025-11-01 Early Morning)

### 1. Configuration Enhancements
**Files Modified**:
- `src/archiverr/models/config.py`
- `config/config.yml`

**Changes**:
- Added `parallel` option (default: 8) for worker count control
- Added `ffprobe_enable` master switch to disable FFprobe entirely
- Added `ffprobe_nfo_enable` for cache file control
- Added `ffprobe_force` to bypass cache and force fresh analysis
- Updated both `load_config()` and `load_config_with_fallback()` functions
- Added .env fallback support for new options

**Rationale**: User needed fine-grained control over FFprobe behavior and parallel processing performance.

### 2. Engine Optimization
**File Modified**: `src/archiverr/core/renamer/engine.py`

**Changes**:
- Worker count now uses `config.options.parallel` if not explicitly provided
- FFprobe calls now respect `FFPROBE_ENABLE` flag
- Cache behavior controlled by `FFPROBE_NFO_ENABLE && !FFPROBE_FORCE`
- Removed hardcoded `USE_CACHE = True`

**Performance Impact**:
- Users can disable FFprobe to skip video analysis entirely
- Cache can be bypassed for fresh analysis when needed
- Parallel count adjustable based on system resources

### 3. Memory Bank Initialization
**New Files Created**:
- `memory-bank/projectbrief.md`
- `memory-bank/productContext.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/techContext.md`
- `memory-bank/activeContext.md` (this file)
- `memory-bank/progress.md`

**Purpose**: Follow AGENT.MD specification for Cline's memory persistence across sessions.

### 4. Timing Statistics Feature
**Files Modified**:
- `src/archiverr/models/config.py` - Added `SummaryConfig` dataclass
- `config/config.yml` - Added `summary` section with customizable template
- `src/archiverr/core/renamer/engine.py` - Track `file_times`, calculate stats, render summary
- `src/archiverr/core/renamer/query_logger.py` - Added `took` parameter, hybrid rendering
- `docs/YAML_ENGINE.md` - Documented `took` variable and summary configuration

**New Features**:
- `{took}` variable in print templates shows per-file processing time
- `summary.print` in config.yml for customizable summary output
- Statistics: `total_time`, `avg_time`, `min_time`, `max_time`
- Hybrid rendering: variable_engine filters + Python format specifiers

**Example Usage**:
```yaml
series:
  print: "✓ {showName} - S{seasonNumber:pad:2}E{episodeNumber:pad:2} ({took:.2f}s)"

summary:
  print: |
    Toplam Süre: {total_time:.2f}s
    Ortalama: {avg_time:.2f}s
```

**Rationale**: User needed to measure parallel processing performance impact.

### 5. TVMaze API Integration & Priority System
**Files Created**:
- `src/archiverr/integrations/tvmaze/client.py` - TVMaze API client (TV shows only)
- `src/archiverr/core/matching/api_manager.py` - Multi-API priority/fallback manager

**Files Modified**:
- `src/archiverr/models/config.py` - Added TVDb, TVMaze, OMDb configs with priority fields
- `src/archiverr/core/matching/matcher.py` - Updated to use API Manager
- `src/archiverr/cli/main.py` - Initialize API Manager instead of single TMDb client
- `src/archiverr/core/renamer/engine.py` - Removed parallel processing
- `config/config.yml` - Removed parallel option
- `docs/YAML_ENGINE.md` - Added api_source variable

**New Features**:
- **Multi-API Support**: TMDb, TVMaze (TVDb & OMDb ready)
- **Priority System**: `*_priority` (smaller = higher priority, 1 > 2 > 3)
- **Primary API**: `*_primary` flag for preferred API
- **Content-Type Aware**: TVMaze only for TV shows, automatically skipped for movies
- **Automatic Fallback**: If primary fails, tries APIs by priority order
- **API Source Tracking**: `api_source` field shows which API provided the result

**Priority Logic**:
1. Primary API tried first (e.g., `tv_primary: true` for TVMaze)
2. If no result, fallback to other APIs sorted by priority (ascending)
3. Example: TMDb primary for movies, TVMaze primary for TV with TMDb/TVDb/OMDb fallback

**Config Example**:
```yaml
tvmaze:
  tv_primary: true
  tv_priority: 1
  movie_priority: 99  # Won't be used (TVMaze doesn't support movies)

tmdb:
  movie_primary: true
  movie_priority: 1
  tv_priority: 2
```

**Removed**:
- Parallel processing option (`parallel: 8` in config)
- ThreadPoolExecutor from matcher
- Sequential matching now (simpler, no race conditions)

**Rationale**: 
- User wanted multiple API support for better data coverage
- TVMaze has better TV show data in some regions
- Fallback ensures resilience if one API is down
- Priority system allows user customization per content type

### 6. NEW Priority System + OMDb + Sequential Processing
**Date**: 2025-11-01 Early Morning

**Files Created**:
- `src/archiverr/integrations/omdb/client.py` - OMDb API client (movies + TV)

**Files Modified**:
- `src/archiverr/models/config.py` - Lista-tabanlı priority config (tv_priority, movie_priority)
- `src/archiverr/core/matching/api_manager.py` - List-based priority logic
- `src/archiverr/core/renamer/engine.py` - Sequential processing (match->rename per file)
- `src/archiverr/integrations/tvdb/client.py` - Better error handling
- `src/archiverr/cli/main.py` - Register OMDb client
- `config/config.yml` - New YAML list format for priorities
- `docs/YAML_ENGINE.md` - OMDb variables + priority config examples

**New Features**:
- **OMDb API**: 4th API support (simple REST, IMDb-based)
- **List-based Priority**: Much simpler config format
  ```yaml
  tv_priority:
    - tvdb      # 1st = primary
    - tvmaze    # 2nd = fallback
    - tmdb      # 3rd
    - omdb      # 4th
  ```
- **Sequential Processing**: match->rename per file (logs now flow correctly)
- **Better TVDb Error Handling**: Response validation + type checking

**Resolved Issues**:
- ✅ Log sıralama sorunu (önce tüm matchler, sonra tüm rename'ler → şimdi sequential)
- ✅ Priority config karmaşası (sayılar + primary flag → basit liste)
- ✅ TVDb API hatası (`str has no attribute get` → proper validation)
- ✅ OMDb eksikliği → Full integration complete

**Rationale**:
- User wanted simpler priority configuration (list format much clearer)
- Sequential processing ensures logs flow in correct order (match-rename-match-rename)
- OMDb adds IMDb-based metadata source for better coverage
- 4 APIs now fully operational with automatic fallback

## Active Decisions

### Variable Engine Architecture
**Decision**: Single unified `{var:filter}` syntax
**Status**: COMPLETE
**Impact**: All patterns use same syntax, no `$` legacy format
**Files**: `src/archiverr/engines/yaml/variable_engine.py`

### Logging System
**Decision**: Structured ISO8601 logs with component-based organization
**Status**: COMPLETE
**Impact**: Production-grade debugging, immediate output to stderr
**Files**: `src/archiverr/utils/structured_logger.py`

### Configuration Migration
**Decision**: YAML primary, .env fallback
**Status**: COMPLETE
**Impact**: Flexible configuration, backward compatible
**Files**: `src/archiverr/models/config.py`

### Parallel Processing
**Decision**: Sequential processing for simplicity and reliability
**Status**: REMOVED (was parallel, now sequential)
**Rationale**: 
- Simpler code, easier to debug
- No race conditions or thread safety issues
- Multi-API fallback logic easier to implement sequentially
- Performance impact minimal for typical use cases (10-50 files)

## Next Steps

### Immediate (This Session)
1. ✅ Add ffprobe config options
2. ✅ Update engine to respect new options
3. ✅ Create memory bank structure
4. ✅ Complete progress.md
5. ✅ Add timing statistics feature
6. ✅ TVMaze API integration
7. ✅ Multi-API priority/fallback system
8. ✅ Remove parallel processing
9. ✅ Update memory bank
10. ✅ Fix episode name bug
11. ✅ Complete all API extras (TVDb, TVMaze, OMDb)
12. ✅ Resolve variable override conflicts

### Short Term
1. ✅ Test TVMaze integration with real TV shows
2. ✅ Implement TVDb API client
3. ✅ Implement OMDb API client
4. ✅ Test multi-API fallback scenarios
5. [ ] Add force_variable feature (cross-API data fetching)
6. [ ] Update README with multi-API examples
7. [ ] Comprehensive testing suite
8. [ ] Performance benchmarks with all 4 APIs

### Medium Term
1. Implement TMDb response caching (reduce API calls)
2. Add database persistence for operation history
3. Build FastAPI backend for web UI
4. Implement undo/redo with diff visualization
5. Query engine full implementation (where/loop/save)

## Important Patterns

### Configuration Loading Priority
1. YAML config file (`config/config.yml`)
2. Environment variables (`.env` fallback)
3. Dataclass defaults

### FFprobe Behavior Matrix
| ffprobe_enable | ffprobe_nfo_enable | ffprobe_force | Behavior |
|----------------|--------------------|--------------|---------------------------------|
| false          | *                  | *            | Skip FFprobe entirely          |
| true           | false              | false        | Run FFprobe, no cache          |
| true           | true               | false        | Use cache if exists            |
| true           | true               | true         | Ignore cache, force fresh run  |

### Parallel Processing Guidelines
- **TMDb queries**: Safe to parallelize (read-only, independent)
- **File operations**: Sequential (avoid race conditions)
- **FFprobe**: Safe to parallelize (read-only)
- **Worker count**: 8 default, adjustable based on API limits and system resources

## Learnings

### Performance Bottlenecks
1. **TMDb API latency**: 200-500ms per request (largest bottleneck)
2. **FFprobe execution**: 50-200ms per file (moderate impact)
3. **File operations**: Minimal impact with hardlinks
4. **Variable rendering**: Negligible (<1ms per pattern)

### Configuration Complexity
- Too many options confuses users
- Group related options (ffprobe_*)
- Provide sensible defaults
- Document decision matrix

### Logging Trade-offs
- Debug mode essential for troubleshooting
- Production mode should be silent
- Structured logs enable post-mortem analysis
- JSON reports for automation integration

## Project Insights

### Architecture Strengths
- Clean separation of concerns (matcher, engine, operations)
- Config-driven behavior (no code changes for rules)
- Parallel processing foundation
- Structured logging for production

### Technical Debt
- No TMDb response caching (duplicate API calls)
- No database persistence (operation history lost)
- No undo mechanism (destructive operations)
- Query engine incomplete (where/loop not fully functional)

### User Feedback Patterns
- Users want more control (hence ffprobe options)
- Performance is critical (parallel processing)
- Debugging needs clear visibility (structured logs)
- Configuration should be declarative (YAML success)
