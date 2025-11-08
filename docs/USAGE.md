# Archiverr Usage Guide

## Overview

Archiverr is a config-driven media archiving system with a plugin architecture. Process and organize your media files using configurable plugins and tasks.

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

Required dependencies:
- pyyaml
- jinja2
- requests
- pymongo (for database features)

### 2. Configuration

Edit `config.yml` to configure your setup:

```yaml
options:
  debug: false        # Enable debug output
  dry_run: true       # Don't actually move files
  hardlink: true      # Use hardlinks instead of copy

plugins:
  scanner:
    enabled: true
    targets:
      - "/path/to/media"
    recursive: true
    allow_virtual_paths: false
  
  tmdb:
    enabled: true
    api_key: "your_api_key"
    lang: "en-US"
```

### 3. Run

```bash
# From project root
PYTHONPATH=src python -m archiverr

# Or if installed
archiverr
```

## Input Plugins

### Scanner
Scans directories for media files.

```yaml
scanner:
  enabled: true
  targets:
    - "/home/user/downloads"
    - "/mnt/media/unsorted"
  recursive: true
  allow_virtual_paths: false
  movies_dst: "/media/Movies"
  shows_dst: "/media/Shows"
```

### File Reader
Reads file paths from text files.

```yaml
file_reader:
  enabled: true
  allow_virtual_paths: true
  targets:
    - "/path/to/targets.txt"
```

**targets.txt format:**
```
# Lines starting with # are comments
/path/to/movie1.mkv
/path/to/movie2.mkv
```

## Output Plugins

### FFProbe
Extracts media file metadata.

```yaml
ffprobe:
  enabled: true
  timeout: 15
```

### Renamer
Parses filenames to extract metadata.

```yaml
renamer:
  enabled: true
```

Supported formats:
- Movies: `Name (Year).mkv` or `Turkish Title - English Title (Year).mkv`
- TV Shows: `Show.S01E01.mkv` or `Show.1x01.mkv`

### TMDb
Fetches metadata from The Movie Database.

```yaml
tmdb:
  enabled: true
  api_key: "your_api_key"
  lang: "tr-TR"
  fallback_lang: "en-US"
```

## Tasks

Tasks execute after each match completes. Define custom output templates and save operations.

### Print Task

```yaml
tasks:
  - name: "print_movie"
    type: "print"
    condition: "{% if tmdb.movie %}"
    template: |
      MOVIE: {{ tmdb.movie.name }} ({{ renamer.parsed.movie.year }})
      Rating: {{ tmdb.movie.vote_average }}/10
      Resolution: {{ ffprobe.video.width }}x{{ ffprobe.video.height }}
```

### Save Task

```yaml
tasks:
  - name: "save_movie"
    type: "save"
    condition: "{% if tmdb.movie %}"
    destination: "{{ scanner.movies_dst }}/{{ tmdb.movie.name }} ({{ renamer.parsed.movie.year }})/{{ tmdb.movie.name }}.mkv"
```

### Summary Task

Runs only after the last match:

```yaml
tasks:
  - name: "summary"
    type: "print"
    template: |
      ============================================================
      Pipeline Summary
      ============================================================
      Total Targets: {{ global_status.matches }}
      Tasks Executed: {{ global_status.tasks }}
      Errors: {{ global_status.errors }}
      ============================================================
```

## Template Variables

Access plugin data in tasks using Jinja2 syntax:

### Current Match
```jinja2
{{ scanner.input }}                    # Input file path
{{ ffprobe.video.codec }}              # Video codec
{{ renamer.parsed.movie.name }}        # Parsed movie name
{{ tmdb.movie.vote_average }}          # TMDb rating
```

### Indexed Access
```jinja2
{{ items[0].tmdb.movie.name }}         # First match movie name
{{ items[100].scanner.input }}         # 100th match input path
```

### Global Data
```jinja2
{{ global_status.matches }}            # Total matches
{{ global_status.tasks }}              # Total tasks executed
{{ global_status.errors }}             # Total errors
{{ status.success }}                   # Current match success
```

## Plugin Development

### Create New Plugin

1. Create plugin directory:
```bash
mkdir src/archiverr/plugins/myplugin
```

2. Create `plugin.json`:
```json
{
  "name": "myplugin",
  "version": "1.0.0",
  "category": "output",
  "depends_on": ["renamer"],
  "expects": ["renamer.parsed"]
}
```

3. Create `client.py`:
```python
class MypluginPlugin:
    def __init__(self, config):
        self.config = config
        self.name = "myplugin"
        self.category = "output"
    
    def execute(self, match_data):
        # Access dependencies
        parsed = match_data['renamer']['parsed']
        
        # Your logic here
        
        return {
            'status': {
                'success': True,
                'started_at': None,
                'finished_at': None,
                'duration_ms': 0
            },
            'my_data': {...}
        }
```

4. Add to `config.yml`:
```yaml
plugins:
  myplugin:
    enabled: true
    option1: value1
```

## Examples

### Example 1: Movie Processing
```yaml
plugins:
  scanner:
    targets: ["/downloads/movies"]
  ffprobe:
    enabled: true
  renamer:
    enabled: true
  tmdb:
    enabled: true

tasks:
  - name: "print_movie"
    type: "print"
    condition: "{% if tmdb.movie %}"
    template: "{{ tmdb.movie.name }} - {{ ffprobe.video.resolution }}"
  
  - name: "save_movie"
    type: "save"
    condition: "{% if tmdb.movie %}"
    destination: "/media/Movies/{{ tmdb.movie.name }}.mkv"
```

### Example 2: TV Show Processing
```yaml
plugins:
  file_reader:
    targets: ["/tmp/episodes.txt"]
  tmdb:
    enabled: true

tasks:
  - name: "print_episode"
    type: "print"
    condition: "{% if tmdb.episode %}"
    template: "S{{ tmdb.episode.season }}E{{ tmdb.episode.number }} - {{ tmdb.episode.name }}"
```

## Troubleshooting

### Enable Debug Mode
```yaml
options:
  debug: true
```

### Check Plugin Loading
Debug output shows:
- Discovered plugins
- Loaded plugins
- Execution groups

### Dry Run Mode
Test configuration without actually moving files:
```yaml
options:
  dry_run: true
```

## Advanced Features

### Virtual Paths
Allow processing of non-existent paths (useful for planning):
```yaml
plugins:
  file_reader:
    allow_virtual_paths: true
```

### Plugin Dependencies
Plugins execute in dependency order automatically:
```json
{
  "depends_on": ["ffprobe", "renamer"]
}
```

### Parallel Execution
Plugins without dependencies run in parallel automatically.

## Support

For issues and feature requests, check the project repository.
