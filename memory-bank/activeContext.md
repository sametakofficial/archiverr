# Active Context

## Current Focus (2025-11-06)
**PLUGIN ARCHITECTURE COMPLETE** - Full refactoring from integrations-based to plugin-based system with Jinja2 templates, task execution, and extras modules.

## Recent Major Changes

### 1. Complete Plugin Architecture Refactoring (2025-11-04 to 2025-11-06)

**MASSIVE SYSTEM REDESIGN** - Removed entire legacy architecture and rebuilt from scratch:

#### Removed Components
- ❌ `integrations/` directory (TMDb, TVDb, TVMaze, OMDb)
- ❌ `core/matcher/` (TMDbMatcher, api_normalizer)
- ❌ `core/renamer/` (engine, query_logger, variable mapping)
- ❌ `core/plugin_manager/` (old plugin system)
- ❌ `models/config.py` (TMDbConfig, TVDbConfig with priority system)
- ❌ `utils/parser.py` (movie/show parsing)
- ❌ Variable engine with `{var:filter}` syntax
- ❌ Priority lists (`tv_priority`, `movie_priority`)

#### New Plugin System

**Directory Structure**:
```
src/archiverr/
├── core/
│   ├── plugin_system/       # Plugin discovery, loading, execution
│   │   ├── discovery.py     # Scan plugins/*/plugin.json
│   │   ├── loader.py        # Load enabled plugins from config
│   │   ├── resolver.py      # Dependency resolution (topological sort)
│   │   └── executor.py      # Execute plugins per match
│   └── task_system/         # Template rendering, task execution
│       ├── jinja_engine.py  # Jinja2 template rendering
│       └── task_executor.py # Execute tasks (print, save, summary)
├── models/
│   └── response_builder.py # Merge plugin outputs
├── plugins/                 # ALL domain logic
│   ├── scanner/             # Input plugin (scan directories/files)
│   ├── file_reader/         # Input plugin (read targets.txt)
│   ├── ffprobe/             # Output plugin (video analysis)
│   ├── renamer/             # Output plugin (filename parsing)
│   ├── tmdb/                # Output plugin (metadata)
│   │   ├── plugin.json
│   │   ├── client.py
│   │   └── extras.py        # Movie/show extras (credits, images, videos)
│   ├── tvdb/                # Output plugin
│   │   ├── plugin.json
│   │   ├── client.py
│   │   └── extras.py        # TV/movie extras (cast, images)
│   ├── tvmaze/              # Output plugin
│   │   ├── plugin.json
│   │   ├── client.py
│   │   └── extras.py        # TV extras (cast, crew, guest cast)
│   └── omdb/                # Output plugin
│       ├── plugin.json
│       └── client.py
└── cli/
    └── main.py              # Entry point
```

**Plugin.json Format**:
```json
{
  "name": "tmdb",
  "version": "1.0.0",
  "category": "output",
  "depends_on": ["renamer"],
  "expects": {
    "renamer": ["parsed"]
  }
}
```

**Plugin Class Interface**:
```python
class PluginClass:
    def __init__(self, config: Dict[str, Any]):
        self.name = "plugin_name"
        self.category = "input" | "output"
        self.config = config
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        # Returns: {status: {...}, ...plugin-specific data}
        pass
```

#### Execution Flow

1. **PluginDiscovery**: Scan `plugins/*/plugin.json`, load manifests
2. **PluginLoader**: Load enabled plugins from `config.yml`
3. **DependencyResolver**: Build execution groups via topological sort
   - Group plugins with no dependencies → parallel execution
   - Dependent plugins in later groups
4. **PluginExecutor**: 
   - Run input plugins → collect matches
   - For each match: run output plugins in execution groups
   - Merge results into unified response structure
5. **TaskExecutor**: For each match, execute tasks (print, save)
   - Summary tasks run only on last match

**Response Structure**:
```json
{
  "global_status": {
    "success": true,
    "matches": 5,
    "tasks": 10,
    "errors": 0
  },
  "items": [
    {
      "index": 0,
      "matchGlobals": {
        "success_plugins": ["ffprobe", "renamer", "tmdb"],
        "failed_plugins": [],
        "not_supported_plugins": ["tvmaze"]
      },
      "scanner": {"status": {...}, "input": "/path/file.mkv"},
      "ffprobe": {"status": {...}, "video": {...}, "audio": [...]}},
      "renamer": {"status": {...}, "parsed": {"movie": {...}, "show": null}},
      "tmdb": {"status": {...}, "movie": {...}, "extras": {...}}
    }
  ]
}
```

#### Jinja2 Template System

**Variable Access** ($ prefix removed, now standard Jinja2):
```jinja2
{{ tmdb.movie.name }}                    # Movie name
{{ renamer.parsed.show.season }}         # Show season
{{ ffprobe.video.codec }}                # Video codec
{{ status.success_plugins | length }}    # Plugin count
{{ global_status.matches }}              # Global match count
```

**Task Configuration**:
```yaml
tasks:
  - name: "print_movie"
    type: "print"
    condition: "{% if renamer.parsed.movie and renamer.parsed.movie.year %}"
    template: |
      MOVIE: {{ renamer.parsed.movie.name }} ({{ renamer.parsed.movie.year }})
      {% if tmdb and tmdb.movie %}TMDb Rating: {{ tmdb.movie.vote_average }}/10{% endif %}
  
  - name: "summary"
    type: "summary"
    template: |
      Processed {{ global_status.matches }} files
      Success: {{ global_status.success }}
```

#### Config.yml Structure

**No more priority lists** - Plugins are auto-discovered:
```yaml
options:
  debug: false
  dry_run: false
  hardlink: true

plugins:
  scanner:
    enabled: true
    targets:
      - "/media/movies"
      - "/media/shows"
    recursive: true
  
  tmdb:
    enabled: true
    api_key: "xxx"
    lang: "tr-TR"
    extras:
      movie_credits: true
      movie_images: true
      episode_credits: true
  
  tvdb:
    enabled: true
    api_key: "xxx"
    extras:
      show_cast: true
      movie_credits: true

tasks:
  - name: "print_movie"
    type: "print"
    condition: "{% if renamer.parsed.movie %}"
    template: "MOVIE: {{ renamer.parsed.movie.name }}"
```

### 2. Extras System Refactoring (2025-11-06)

**Problem**: Extras were inline in client.py files, making them hard to maintain.

**Solution**: Separate `extras.py` modules per plugin:

**TMDb Extras** (`plugins/tmdb/extras.py`):
- Movie: credits, images, videos, keywords
- TV: episode_credits, episode_images, show_images, show_videos
- Normalize functions for consistent data structure

**TVDb Extras** (`plugins/tvdb/extras.py`):
- TV: show_cast, show_images
- Episode: episode_images (from extended endpoint)
- Movie: movie_credits, movie_images (from extended endpoint)
- Uses JWT token from main client

**TVMaze Extras** (`plugins/tvmaze/extras.py`):
- TV: show_cast, show_crew, show_images
- Episode: episode_guest_cast, episode_guest_crew
- No authentication required

**Integration**:
```python
# In client.py
from .extras import TMDbExtras

class TMDbPlugin:
    def __init__(self, config):
        self.extras_client = TMDbExtras(self.api_key)
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data):
        # ... fetch movie
        if self.extras_config.get('movie_credits'):
            credits = self.extras_client.movie_credits(movie_id)
            result['extras']['cast'] = credits['cast'][:10]
```

### 3. Error Counting Fix (2025-11-06)

**Problem**: `not_supported_plugins` were counted as errors.

**Solution**: Modified `response_builder.py`:
```python
# Old
if not item['matchGlobals'].get('success', False):
    total_errors += 1

# New - only count failed plugins
failed_count = len(item['matchGlobals'].get('failed_plugins', []))
if failed_count > 0:
    total_errors += 1
```

**Result**: TVMaze returning "not supported" for movies no longer increases error count.

## Active Decisions

### Plugin-Agnostic Architecture
**Decision**: Core system knows nothing about plugins
**Rationale**: 
- Clean separation of concerns
- Easy to add new plugins
- No core changes for plugin updates
**Status**: ENFORCED - core cannot import plugin types

### Jinja2 Over Custom Template Engine
**Decision**: Use Jinja2 for all template rendering
**Rationale**:
- Industry standard, well-tested
- Rich filter ecosystem
- Conditional logic built-in
- No need to maintain custom syntax
**Status**: COMPLETE

### Flat Plugin Directory
**Decision**: Single plugins/ directory, no nesting
**Rationale**:
- Simple discovery (glob plugins/*/plugin.json)
- No namespace conflicts
- Clear structure
**Status**: ENFORCED

### Task-Based Execution
**Decision**: Tasks run per-match, not batch operations
**Rationale**:
- Immediate feedback per file
- Easier error handling
- Natural flow for template rendering
**Status**: COMPLETE

## Important Patterns

### Plugin Discovery
```python
# core/plugin_system/discovery.py
for plugin_dir in plugins_path.iterdir():
    manifest_path = plugin_dir / "plugin.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        plugins[manifest['name']] = {
            'manifest': manifest,
            'path': plugin_dir
        }
```

### Dependency Resolution
```python
# core/plugin_system/resolver.py
def resolve_dependencies(plugins):
    # Topological sort using Kahn's algorithm
    # Returns list of execution groups (parallel-safe)
    groups = []
    while unprocessed:
        independent = [p for p in unprocessed if no_dependencies(p)]
        groups.append(independent)
        unprocessed.remove_all(independent)
    return groups
```

### Template Rendering
```python
# core/task_system/jinja_engine.py
def render(template, context):
    env = jinja2.Environment()
    # NO $ prefix needed - standard Jinja2
    compiled = env.from_string(template)
    return compiled.render(**context)
```

## Next Steps

### Immediate
- [x] Plugin system complete
- [x] Extras refactoring complete
- [x] Error counting fixed
- [ ] Update README with new architecture
- [ ] Add plugin development guide

### Short Term
- [ ] MongoDB integration for response persistence
- [ ] Plugin hot-reloading
- [ ] Config validation
- [ ] Better error messages

### Medium Term
- [ ] Web UI for task configuration
- [ ] Plugin marketplace/registry
- [ ] Automated testing framework
- [ ] Performance profiling

## Technical Debt
- No unit tests for plugin system
- No config validation
- Plugin.json schema not enforced
- No plugin versioning/compatibility checks
- Response builder could be more efficient

## Learnings

### Architecture Wins
1. **Plugin isolation**: No cross-plugin dependencies
2. **Config simplicity**: No priority lists, just enable/disable
3. **Template power**: Jinja2 handles all logic needs
4. **Clean APIs**: execute() is the only plugin requirement

### Challenges Overcome
1. **Extras separation**: Required token/api_key passing from client to extras
2. **Error counting**: Not supported vs failed distinction
3. **Template variable access**: $ prefix removal for standard Jinja2

### Design Principles Validated
1. **Plugin-agnostic core**: Never violated, enforced strictly
2. **Manifest-based config**: Works well, easy to discover
3. **Task execution model**: Natural flow, easy to understand
4. **Response normalization**: Consistent data structure across plugins
