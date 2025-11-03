# Technical Context

## Technology Stack

### Core Runtime
- **Python**: 3.10+ (required for modern type hints, dataclasses)
- **Package Manager**: pip + venv
- **Dependency Management**: requirements.txt

### Key Dependencies
```
requests>=2.31.0          # HTTP client for TMDb API
python-dateutil>=2.8.2    # Date parsing from filenames
pyyaml>=6.0              # Config file parsing
```

### External Tools
- **FFprobe**: Part of ffmpeg package, video file analysis
- **TMDb API**: v3, requires API key (free tier sufficient)

### Development Tools
- Standard library only for core functionality
- No heavy frameworks (Django/Flask) in CLI
- FastAPI planned for future web API

## Project Structure

```
archiverr/
├── config/
│   └── config.yml                    # User configuration
├── docs/
│   ├── YAML_ENGINE.md               # Variable reference
│   └── TODO.md                      # Development tracking
├── memory-bank/                     # Cline memory system
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   └── progress.md
├── logs/                            # Structured log outputs
│   └── report_YYYYMMDD-HHMMSS.json
├── src/archiverr/
│   ├── main.py                      # CLI entry point
│   ├── models/
│   │   └── config.py                # Config dataclasses + loaders
│   ├── core/
│   │   ├── matching/
│   │   │   └── matcher.py           # Filename parsing + TMDb matching
│   │   ├── renamer/
│   │   │   ├── engine.py            # Main orchestrator
│   │   │   ├── path_builder.py      # Path generation logic
│   │   │   ├── query_logger.py      # User-facing print logs
│   │   │   ├── logger.py            # Legacy colored output
│   │   │   └── operations.py        # File move/hardlink
│   │   └── scanner/
│   │       └── scanner.py           # Directory traversal
│   ├── engines/
│   │   └── yaml/
│   │       ├── variable_engine.py   # Template rendering + filters
│   │       └── engine.py            # Query execution
│   ├── integrations/
│   │   ├── tmdb/
│   │   │   └── client.py            # TMDb API wrapper
│   │   └── ffprobe/
│   │       └── analyzer.py          # FFprobe subprocess wrapper
│   └── utils/
│       ├── structured_logger.py     # Production logging system
│       └── nfo_writer.py            # Kodi NFO generation
└── tests/
    └── targets.txt                  # Test file list
```

## Development Setup

### Initial Setup
```bash
cd /home/samet/Workspace/archiverr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
```bash
cp config/config.yml.example config/config.yml
# Edit config.yml: Add TMDb API key
vim config/config.yml
```

### Running
```bash
source .venv/bin/activate
archiverr --help
archiverr --paths-from tests/targets.txt --type tv --dry-run
```

## Technical Constraints

### Performance
- **Target**: <1s per file with cache
- **Bottleneck**: TMDb API latency (~200-500ms per request)
- **Mitigation**: Parallel workers (default: 8)

### API Limits
- **TMDb**: 40 requests/10 seconds (free tier)
- **Strategy**: Parallel processing stays under limit with 8 workers
- **Future**: Response caching to reduce API calls

### File System
- **Hardlink Requirement**: Source and destination on same filesystem
- **Permission**: Write access to destination directories
- **Safety**: Dry-run mode enabled by default

### Memory
- **Footprint**: Minimal (<100MB for typical batches)
- **Scaling**: Linear with batch size (all results in memory)
- **Future**: Database persistence for large operations

## Code Standards

### Style
- PEP 8 compliance
- Type hints on all public functions
- Dataclasses for configuration structures
- No emojis in production code/logs

### Logging
```python
# Format: TIMESTAMP LEVEL COMPONENT [context] message
2025-10-31T16:24:11.004+03:00  INFO   parse.start          [file=Friends.S01E01.mkv] Starting filename parse
```

### Error Handling
- Exception isolation at file level
- Clear error messages with context
- Failed files logged separately
- No silent failures

### Configuration
- YAML primary, .env fallback for compatibility
- Dataclass validation on load
- Explicit defaults in code
- No magic values

## Testing Strategy

### Current
- Manual testing with `tests/targets.txt`
- Dry-run validation before real operations
- Visual inspection of structured logs

### Planned
- Unit tests for variable engine filters
- Integration tests for TMDb matching
- End-to-end tests for full pipeline
- Regression tests for edge cases

## Deployment

### Current
- Local installation via pip install -e .
- Virtual environment required
- Configuration in user space

### Future
- Docker container
- Systemd service for background processing
- Web UI with FastAPI backend
- Database migrations
