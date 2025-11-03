# System Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer                              │
│  src/archiverr/main.py (argparse → engine.rename_files)     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Core Engine                               │
│  src/archiverr/core/renamer/engine.py                       │
│  - Parallel matching (ThreadPoolExecutor)                   │
│  - Structured logging integration                           │
│  - Error aggregation                                        │
└──┬──────────┬───────────┬──────────────┬───────────────────┘
   │          │           │              │
   │          │           │              │
┌──▼──┐  ┌───▼────┐  ┌───▼────┐   ┌────▼─────┐
│Match│  │Variable│  │FFprobe │   │Operations│
│er   │  │Engine  │  │Analyzer│   │move/link │
└──┬──┘  └───┬────┘  └───┬────┘   └────┬─────┘
   │          │           │              │
┌──▼──────────▼───────────▼──────────────▼─────┐
│         Integration Layer                     │
│  - TMDb Client (requests + caching)           │
│  - FFprobe (subprocess wrapper)               │
│  - File System (pathlib + os)                 │
└───────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Matcher (`core/matching/matcher.py`)
**Input**: File path string
**Output**: `{path, parsed, best, took}` dict
**Responsibility**:
- Parse filename with regex patterns
- Extract: show/title, season, episode, year
- Query TMDb for best match
- Return parsed metadata + TMDb result

**Key Patterns**:
- Parallel execution via `match_movie()` / `match_tv()` functions
- Exception isolation (per-file failures don't crash batch)
- TMDb result caching in future iterations

### 2. Variable Engine (`engines/yaml/variable_engine.py`)
**Input**: Template string + context dict
**Output**: Rendered string
**Responsibility**:
- Parse `{var:filter1:filter2}` syntax
- Resolve variables from context (TMDb, FFprobe, parsed)
- Apply filters (`:upper`, `:pad:2`, `:year`, etc.)
- Support nested access (`{tmdb.first_air_date:year}`)

**Key Patterns**:
- Jinja2-like template rendering
- Filter chaining
- 1-based indexing for arrays
- Graceful handling of missing variables (empty string)

### 3. Path Builder (`core/renamer/path_builder.py`)
**Input**: Config, TMDb data, FFprobe data, render function
**Output**: `(parent_path, filename)` tuple
**Responsibility**:
- Determine if FFprobe/episode details needed
- Build context for variable engine
- Render save pattern → final path

**Key Patterns**:
- Lazy evaluation (only fetch data if pattern needs it)
- Context building from multiple sources
- Pattern introspection (`pattern_needs_ffprobe()`)

### 4. Renamer Engine (`core/renamer/engine.py`)
**Input**: File paths, media type, config, client
**Output**: Stats (ok, miss, err counts)
**Responsibility**:
- Orchestrate entire pipeline
- Parallel matching
- Sequential path building & operations
- Structured logging
- Error aggregation

**Key Patterns**:
- ThreadPoolExecutor for parallel TMDb queries
- Sequential file operations (avoid race conditions)
- Config-driven behavior (dry_run, hardlink, parallel count)
- Immediate logging at each stage (when debug=true)

### 5. Structured Logger (`utils/structured_logger.py`)
**Input**: Component, level, message, context
**Output**: Formatted log line to stderr
**Responsibility**:
- ISO8601 timestamps with timezone
- Component-based organization
- Context fields as key=value
- Session statistics
- JSON report generation

**Key Patterns**:
- Immediate output (flush=True)
- stderr for logs, stdout for user output
- Component naming convention (module.function)
- Stats accumulation in memory

## Data Flow

### Movie Processing
```
File Path → Matcher → TMDb Query → TMDb Details → FFprobe (if needed) 
  → Variable Engine → Path Builder → unique_path() → move_file/hardlink_file
  → NFO Writer → Success Log
```

### TV Show Processing
```
File Path → Matcher → TMDb Query → Show Details → Episode Details (if needed)
  → FFprobe (if needed) → Variable Engine → Path Builder → unique_path()
  → move_file/hardlink_file → NFO Writer → Success Log
```

## Configuration Schema

### Core Structure
```yaml
tmdb:
  api_key: string
  lang: string (default: tr-TR)

options:
  dry_run: bool (default: true)
  debug: bool (default: false)
  hardlink: bool (default: false)
  parallel: int (default: 8)
  ffprobe_enable: bool (default: true)
  ffprobe_nfo_enable: bool (default: true)
  ffprobe_force: bool (default: false)

rename:
  movies:
    print: template_string
    save: template_string
  series:
    print: template_string
    save: template_string
```

### Variable Resolution Order
1. **Parsed data**: `{parsed_title}`, `{parsed_season}`, etc.
2. **TMDb aliases**: `{name}`, `{movieYear}`, `{showName}`, etc.
3. **TMDb nested**: `{tmdb.first_air_date}`, `{tmdb.vote_average}`, etc.
4. **FFprobe**: `{video.codec}`, `{audio.1.language}`, etc.
5. **Custom mappings**: Legacy compatibility

## Error Handling Strategy

### Levels
1. **File-level errors**: Log + continue (don't crash batch)
2. **TMDb errors**: Retry with exponential backoff (not implemented)
3. **FFprobe errors**: Fallback to empty dict, continue
4. **File operation errors**: Log to stderr + failed list

### Recovery
- Dry-run mode for validation
- Structured logs for debugging
- Failed files list in summary
- JSON report for post-mortem analysis

## Performance Optimizations

### Current
- Sequential processing (simpler, more reliable than parallel)
- Multi-API fallback system (list-based priority)
- FFprobe NFO caching (optional)
- Early pattern introspection (avoid unnecessary API calls)

### Planned
- TMDb response caching (in-memory LRU)
- Database for operation history
- Batch API requests where possible
- Worker pool reuse across runs

## Architecture Lessons Learned (2025-11-03)

### 1. Direct Mapping Principle
**Problem**: Variable override conflicts (e.g., `episodeName` bug)
**Root Cause**: Multiple layers transforming same data
- `query_logger.py` sets `episodeName` from `ep_full`
- `_build_api_vars()` overrides it with empty string from wrong data source

**Solution**: API normalizer → variable system should be 1:1
- No intermediate transformation layers
- Single source of truth for each variable
- Explicit documentation of which function owns which variables

**Pattern**:
```python
# ❌ BAD: Multiple functions setting same variable
def query_logger():
    ctx['episodeName'] = ep_full.get('name', '')  # First set
    
def _build_api_vars():
    ctx['episodeName'] = api_data['episode']['name']  # Override!

# ✅ GOOD: Single owner per variable
def query_logger():
    ctx['episodeName'] = ep_full.get('name', '')  # Only place
    
def _build_api_vars():
    # episodeName is owned by query_logger, skip it
    pass
```

### 2. Silent Failure Anti-Pattern
**Problem**: Bugs hidden by `except: pass`
**Impact**: Episode name bug took hours to debug

**Solution**: Always log exceptions
```python
# ❌ BAD: Silent failure
try:
    process_template()
except Exception:
    pass  # Bug is invisible!

# ✅ GOOD: Logged failure
try:
    process_template()
except Exception as e:
    logger.warn("template_error", error=str(e))
    traceback.print_exc()  # During debug
```

### 3. Debug Logging Strategy
**Pattern**: Temporary stderr prints for fast debugging
```python
# Add temporary debug during investigation
import sys
print(f"[DEBUG] variable value: {value}", file=sys.stderr)

# Remove after fix is confirmed
# Don't leave debug prints in production
```

**When to use**:
- Variable not appearing in output (like episodeName)
- Data transformation bugs
- Override conflicts
- Quick validation of hypothesis

### 4. API Normalization Consistency
**Problem**: Each API returns different field names
**Solution**: Normalize at client level, not variable level

**Pattern**:
```python
# At API client level (tvdb/client.py, tvmaze/client.py)
def normalize_response(raw):
    return {
        'name': raw.get('title') or raw.get('name'),  # Consistent key
        'imdb_id': raw['externals']['imdb'],          # Consistent format
        'file_path': raw.get('image'),                # Not 'path' or 'url'
    }
```

**Key Names Standardized**:
- `imdb_id`, `tvdb_id`, `tvmaze_id` (not `imdbID`, `thetvdb`, etc.)
- `file_path` for images (not `path`, `url`, `image`)
- `cast` and `crew` as lists of dicts (not strings or objects)
- `name` for titles (not `title`, `showName`, etc.)

### 5. Multi-API Architecture
**Pattern**: Priority-based fallback with content-type awareness

```python
# List-based priority (simpler than numeric priority)
tv_priority:
  - tmdb      # Primary for TV
  - tvdb      # Fallback 1
  - tvmaze    # Fallback 2
  - omdb      # Fallback 3

# API Manager tries in order, skips incompatible
for api_name in priority_list:
    if api.supports_content_type(media_type):
        result = api.search(query)
        if result:
            return result, api_name
```

**Benefits**:
- Resilient to API outages
- Best data wins (TMDb usually most complete)
- User can customize per content type
- Automatic skip of incompatible APIs (TVMaze for movies)

### 6. Sequential vs Parallel Processing
**Decision**: Removed parallel processing (2025-11-01)

**Rationale**:
- Simpler code, easier debugging
- No race conditions on file operations
- Multi-API fallback logic clearer
- Log order is correct (match→rename per file)
- Performance impact minimal for typical batches

**Pattern**:
```python
# Sequential: match → rename → match → rename
for file_path in files:
    match_result = matcher.match(file_path)
    rename(match_result)
    # Logs flow correctly!
```

### 7. Configuration Evolution
**Progression**:
1. `.env` only → Limited, no nesting
2. YAML + .env fallback → Better structure
3. List-based priority → Simpler than numeric
4. Query objects (print/save) → Full flexibility

**Current Best Practice**:
```yaml
# Clean, declarative, self-documenting
tv_priority:
  - tmdb
  - tvdb
  - tvmaze

series:
  print: "✓ {showName} S{seasonNumber:02d}E{episodeNumber:02d} - {episodeName}"
  save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
```
