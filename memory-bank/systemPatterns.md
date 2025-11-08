# System Patterns

## Core Architecture

### Plugin-Agnostic Principle
**Rule**: Core system must never import plugin-specific types or know plugin implementations.

**Enforcement**:
- Core imports only from `core/`, `models/`, `utils/`
- Plugin data structures defined in plugin modules
- Config.yml is opaque dictionary to core
- Plugin.json provides only category and dependencies

**Example Violation** (NOT ALLOWED):
```python
# core/some_module.py
from plugins.tmdb.client import TMDbPlugin  # ❌ FORBIDDEN
```

**Correct Pattern**:
```python
# core/plugin_system/executor.py
plugin_class = import_module(f"plugins.{name}.client")
plugin = getattr(plugin_class, class_name)(config)  # ✅ Dynamic loading
```

### Separation of Concerns

**Layer Structure**:
```
CLI Layer (cli/main.py)
    ↓
Core System (core/)
    ↓ 
Plugin Layer (plugins/)
```

**Responsibilities**:
- **CLI**: Argument parsing, config loading, system initialization
- **Core**: Plugin orchestration, template rendering, response building
- **Plugins**: Domain logic, API calls, data transformation

## Plugin System

### Plugin Discovery

**Pattern**: Filesystem-based manifest discovery
```python
# core/plugin_system/discovery.py
def discover_plugins(plugins_dir: Path) -> Dict[str, PluginInfo]:
    plugins = {}
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
        
        manifest_path = plugin_dir / "plugin.json"
        if not manifest_path.exists():
            continue
        
        manifest = json.loads(manifest_path.read_text())
        plugins[manifest['name']] = {
            'manifest': manifest,
            'path': plugin_dir,
            'class_name': f"{manifest['name'].title()}Plugin"
        }
    
    return plugins
```

**Key Decisions**:
- Single `plugin.json` per plugin directory
- Flat structure (no nested plugins)
- Name from manifest, not directory name
- Auto-discovery (no manual registration)

### Dependency Resolution

**Pattern**: Topological sort with Kahn's algorithm
```python
# core/plugin_system/resolver.py
def resolve_dependencies(plugins: List[PluginInfo]) -> List[List[str]]:
    # Build graph
    graph = {}
    in_degree = {}
    
    for plugin in plugins:
        name = plugin['name']
        deps = plugin['manifest'].get('depends_on', [])
        graph[name] = deps
        in_degree[name] = 0
    
    for deps in graph.values():
        for dep in deps:
            in_degree[dep] = in_degree.get(dep, 0) + 1
    
    # Topological sort
    groups = []
    while in_degree:
        # Find nodes with no dependencies
        ready = [name for name, count in in_degree.items() if count == 0]
        if not ready:
            raise CyclicDependencyError()
        
        groups.append(ready)
        
        # Remove processed nodes
        for name in ready:
            del in_degree[name]
            for dep in graph[name]:
                in_degree[dep] -= 1
    
    return groups
```

**Benefits**:
- Parallel execution within groups
- Automatic dependency ordering
- Cycle detection
- Clear execution flow

### Plugin Loading

**Pattern**: Dynamic import with class instantiation
```python
# core/plugin_system/loader.py
def load_plugin(plugin_info: PluginInfo, config: Dict) -> Any:
    module_path = f"archiverr.plugins.{plugin_info['name']}.client"
    module = import_module(module_path)
    
    class_name = plugin_info['class_name']
    plugin_class = getattr(module, class_name)
    
    # Plugin-specific config from config.yml
    plugin_config = config.get('plugins', {}).get(plugin_info['name'], {})
    
    return plugin_class(plugin_config)
```

**Key Points**:
- No type hints on return (plugin-agnostic)
- Config passed to __init__
- Class name derived from plugin name
- Module path follows convention

### Plugin Execution

**Pattern**: Per-match execution with status tracking
```python
# core/plugin_system/executor.py
def execute_match(plugins: Dict, match_data: Dict) -> Dict:
    result = {'status': {'success_plugins': [], 'failed_plugins': []}}
    
    for group in execution_groups:
        for plugin_name in group:
            plugin = plugins[plugin_name]
            
            try:
                plugin_result = plugin.execute(match_data)
                
                if plugin_result['status'].get('success', False):
                    result['status']['success_plugins'].append(plugin_name)
                elif plugin_result['status'].get('not_supported', False):
                    result['status']['not_supported_plugins'].append(plugin_name)
                else:
                    result['status']['failed_plugins'].append(plugin_name)
                
                result[plugin_name] = plugin_result
                
            except Exception as e:
                result['status']['failed_plugins'].append(plugin_name)
                result[plugin_name] = error_result(e)
    
    return result
```

**Status Model**:
- `success_plugins`: Completed successfully
- `failed_plugins`: Errored out
- `not_supported_plugins`: Intentionally skipped (e.g., TVMaze for movies)

## Template System

### Jinja2 Integration

**Pattern**: Standard Jinja2 with no modifications
```python
# core/task_system/jinja_engine.py
def render_template(template: str, context: Dict) -> str:
    env = jinja2.Environment(
        autoescape=False,  # We control all inputs
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    compiled = env.from_string(template)
    return compiled.render(**context)
```

**No Custom Syntax**:
- ❌ `$variable` syntax removed
- ❌ `{var:filter}` syntax removed
- ✅ Standard Jinja2: `{{ variable }}`
- ✅ Standard filters: `{{ text | upper }}`
- ✅ Standard conditionals: `{% if condition %}`

### Variable Access Pattern

**Direct Dictionary Access**:
```jinja2
{# Plugin output access #}
{{ tmdb.movie.name }}
{{ renamer.parsed.show.season }}
{{ ffprobe.video.codec }}

{# Status access #}
{{ status.success_plugins | length }}
{{ global_status.matches }}

{# Array access (1-indexed maintained for compatibility) #}
{{ ffprobe.audio.0.language }}
```

**Context Building**:
```python
context = {
    'global_status': global_status,
    'status': match_status,
    **match_data  # All plugin outputs
}
```

### Task Execution Pattern

**Per-Match Task Execution**:
```python
# core/task_system/task_executor.py
def execute_tasks(tasks: List[Dict], match_data: Dict, is_last: bool):
    for task in tasks:
        # Skip summary tasks unless last match
        if task.get('type') == 'summary' and not is_last:
            continue
        
        # Evaluate condition
        condition = task.get('condition', '')
        if condition and not evaluate_condition(condition, match_data):
            continue
        
        # Execute task
        if task['type'] == 'print':
            template = task['template']
            output = render_template(template, match_data)
            print(output)
        
        elif task['type'] == 'save':
            # Future implementation
            pass
```

**Task Types**:
1. **Print**: Console output (implemented)
2. **Save**: File writing (planned)
3. **Summary**: Run only on last match (implemented)

## Response Building

### Unified Response Structure

**Pattern**: Consistent structure regardless of plugin outputs
```python
# models/response_builder.py
def build_response(matches: List[Dict]) -> Dict:
    items = []
    total_errors = 0
    
    for index, match in enumerate(matches):
        item = dict(match)
        item['index'] = index
        
        # Rename status to matchGlobals
        if 'status' in item:
            item['matchGlobals'] = item.pop('status')
            
            # Count only failed plugins (not "not supported")
            failed_count = len(item['matchGlobals'].get('failed_plugins', []))
            if failed_count > 0:
                total_errors += 1
        
        items.append(item)
    
    return {
        'global_status': {
            'success': total_errors == 0,
            'matches': len(matches),
            'errors': total_errors
        },
        'items': items
    }
```

**Key Decisions**:
- `status` → `matchGlobals` (avoid keyword conflict)
- Error count = failed plugins only
- Not supported ≠ error
- Index added for reference

## Extras Pattern

### Separate Extras Modules

**Structure**:
```
plugins/
└── tmdb/
    ├── plugin.json
    ├── client.py      # Main API client
    └── extras.py      # Extended metadata
```

**Client Integration**:
```python
# plugins/tmdb/client.py
from .extras import TMDbExtras

class TMDbPlugin:
    def __init__(self, config):
        self.api_key = config.get('api_key')
        self.extras_client = TMDbExtras(self.api_key)
        self.extras_config = config.get('extras', {})
    
    def execute(self, match_data):
        # Fetch main data
        movie_id = self._search_movie(...)
        
        # Fetch extras if enabled
        extras = {}
        if self.extras_config.get('movie_credits'):
            credits = self.extras_client.movie_credits(movie_id)
            extras['cast'] = credits['cast'][:10]
        
        return {'movie': movie_data, 'extras': extras}
```

**Extras Class Pattern**:
```python
# plugins/tmdb/extras.py
class TMDbExtras:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
    
    def movie_credits(self, movie_id: int) -> Dict:
        response = requests.get(
            f"{self.base_url}/movie/{movie_id}/credits",
            params={'api_key': self.api_key}
        )
        return self._normalize_credits(response.json())
    
    def _normalize_credits(self, data: Dict) -> Dict:
        # Consistent data structure
        return {
            'cast': [{'name': p['name'], 'character': p['character']} 
                     for p in data.get('cast', [])],
            'crew': [{'name': p['name'], 'job': p['job']} 
                     for p in data.get('crew', [])]
        }
```

**Benefits**:
- Separation of concerns
- Optional extras (config-driven)
- Reusable normalization
- Easier testing

## Configuration Pattern

### Opaque Plugin Config

**Core View**:
```python
# Core only sees structure, not content
plugins_config = config.get('plugins', {})  # Dict[str, Dict[str, Any]]

# Pass entire plugin config to plugin
plugin_config = plugins_config.get('tmdb', {})
plugin = TMDbPlugin(plugin_config)  # Plugin interprets config
```

**Plugin View**:
```python
# Plugin extracts what it needs
class TMDbPlugin:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key', '')
        self.lang = config.get('lang', 'en-US')
        self.extras = config.get('extras', {})
        # Plugin defines schema, core doesn't care
```

**Config.yml Structure**:
```yaml
plugins:
  tmdb:
    enabled: true
    api_key: "xxx"
    lang: "tr-TR"
    extras:
      movie_credits: true
      movie_images: false
  
  tvdb:
    enabled: true
    api_key: "yyy"
    extras:
      show_cast: true
```

## Error Handling Pattern

### Three-State Status

**States**:
1. **Success**: `success: true, not_supported: false`
2. **Not Supported**: `success: false, not_supported: true`
3. **Failed**: `success: false, not_supported: false`

**Implementation**:
```python
# Plugin returns appropriate status
def execute(self, match_data):
    # Check if content type is supported
    if not self._can_process(match_data):
        return {
            'status': {
                'success': False,
                'not_supported': True,
                'reason': "TVMaze only supports TV shows"
            }
        }
    
    try:
        # Process data
        result = self._fetch_data(...)
        return {
            'status': {'success': True, 'not_supported': False},
            'data': result
        }
    except Exception:
        return {
            'status': {'success': False, 'not_supported': False}
        }
```

## Critical Implementation Paths

### Full Execution Flow

1. **CLI Initialization**
   - Parse arguments
   - Load config.yml
   - Initialize plugin system

2. **Plugin Discovery**
   - Scan plugins/*/plugin.json
   - Build plugin registry

3. **Plugin Loading**
   - Filter enabled plugins
   - Dynamic import
   - Instantiate with config

4. **Dependency Resolution**
   - Build dependency graph
   - Topological sort
   - Create execution groups

5. **Input Plugin Execution**
   - Scanner/FileReader runs
   - Collect matches

6. **Per-Match Processing**
   - For each match:
     - Execute output plugins (by groups)
     - Build match response
     - Execute tasks
   - On last match: execute summary tasks

7. **Response Building**
   - Merge all match data
   - Calculate global status
   - Return unified response

### Plugin Development Flow

1. Create plugin directory: `plugins/myplugin/`
2. Write `plugin.json` manifest
3. Implement `client.py` with `MyPlugin` class
4. Add `execute(match_data)` method
5. Optional: Create `extras.py` for extended metadata
6. Enable in `config.yml`
7. System auto-discovers and loads

## Design Principles

### 1. Convention Over Configuration
- Plugin class name = `{Name}Plugin`
- Module path = `plugins.{name}.client`
- Manifest = `plugin.json` (fixed name)
- Extras = `extras.py` (fixed name)

### 2. Explicit Over Implicit
- Dependencies declared in manifest
- Status always explicit (success/failed/not_supported)
- No silent failures
- Clear error messages

### 3. Separation Over Integration
- Core ≠ Plugins
- Main data ≠ Extras
- Config ≠ Code
- Discovery ≠ Execution

### 4. Standard Over Custom
- Jinja2 templates (not custom syntax)
- JSON manifests (not Python config)
- Dict responses (not custom classes)
- Import hooks (not metaclasses)
