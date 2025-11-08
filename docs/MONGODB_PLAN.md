# MongoDB Integration Plan

## Database Schema

### Collections

#### 1. `system_info`
Application metadata (singleton)
```json
{
  "_id": "archiverr",
  "name": "Archiverr",
  "version": "2.0.0",
  "author": "samet",
  "description": "Config-driven media archiving system with plugin architecture",
  "created_at": "2025-11-06T00:00:00Z",
  "last_updated": "2025-11-06T19:00:00Z"
}
```

#### 2. `branches`
Git-like branches
```json
{
  "_id": "main",
  "name": "main",
  "head_commit_id": "c_2025-11-06T19:00:01Z",
  "created_at": "2025-11-06T19:00:01Z",
  "updated_at": "2025-11-06T19:05:16Z"
}
```

#### 3. `commits`
Each run creates a commit
```json
{
  "_id": "c_2025-11-06T19:00:01Z",
  "branch": "main",
  "parent_ids": ["c_2025-11-05T10:00:00Z"],
  "options": {
    "debug": false,
    "dry_run": true,
    "hardlink": true
  },
  "global_status": {
    "success": true,
    "matches": 12,
    "tasks": 25,
    "errors": 6,
    "started_at": "2025-11-06T19:00:01Z",
    "finished_at": "2025-11-06T19:05:16Z",
    "duration_ms": 315000
  },
  "api_responses_id": "ar_c_2025-11-06T19:00:01Z",
  "created_at": "2025-11-06T19:00:01Z"
}
```

#### 4. `api_responses`
Aggregate API response for a commit
```json
{
  "_id": "ar_c_2025-11-06T19:00:01Z",
  "commit_id": "c_2025-11-06T19:00:01Z",
  "global_status": {
    "success": true,
    "matches": 12,
    "tasks": 25,
    "errors": 6,
    "started_at": "2025-11-06T19:00:01Z",
    "finished_at": "2025-11-06T19:05:16Z",
    "duration_ms": 315000
  }
}
```

#### 5. `responses`
Individual match responses (plugin outputs)
```json
{
  "_id": "r_ar_c_2025-11-06T19:00:01Z_00000",
  "api_responses_id": "ar_c_2025-11-06T19:00:01Z",
  "commit_id": "c_2025-11-06T19:00:01Z",
  "index": 0,
  "status": {
    "success": true,
    "started_at": "2025-11-06T19:00:02Z",
    "finished_at": "2025-11-06T19:00:10Z",
    "duration_ms": 8000
  },
  "scanner": {
    "status": {...},
    "input": "/data/file.mkv"
  },
  "ffprobe": {
    "status": {...},
    "video": {...},
    "audio": [...],
    "container": {...}
  },
  "renamer": {
    "status": {...},
    "parsed": {
      "show": {...},
      "movie": {...}
    }
  },
  "tmdb": {
    "status": {...},
    "episode": {...},
    "season": {...},
    "show": {...},
    "movie": {...}
  }
}
```

#### 6. `matches`
Match-level metadata
```json
{
  "_id": "m_c_2025-11-06T19:00:01Z_00000",
  "commit_id": "c_2025-11-06T19:00:01Z",
  "index": 0,
  "status": {
    "success_plugins": ["scanner", "ffprobe", "renamer", "tmdb"],
    "failed_plugins": ["tvmaze"],
    "success": true,
    "started_at": "2025-11-06T19:00:02Z",
    "finished_at": "2025-11-06T19:00:10Z",
    "duration_ms": 8000
  }
}
```

#### 7. `tasks`
Task execution results
```json
{
  "_id": "t_m_c_2025-11-06T19:00:01Z_00000_print_movie",
  "commit_id": "c_2025-11-06T19:00:01Z",
  "match_id": "m_c_2025-11-06T19:00:01Z_00000",
  "index": 0,
  "task_name": "print_movie",
  "task_type": "print",
  "print_output": "MOVIE: Friends...",
  "save_output": null,
  "started_at": "2025-11-06T19:00:11Z",
  "finished_at": "2025-11-06T19:00:11Z",
  "duration_ms": 5
}
```

#### 8. `diagnostics`
Debug logs and diagnostics
```json
{
  "_id": "dg_2025-11-06T19:09:39.247Z_00001",
  "commit_id": "c_2025-11-06T19:00:01Z",
  "match_id": "m_c_2025-11-06T19:00:01Z_00000",
  "timestamp": "2025-11-06T19:09:39.247+03:00",
  "level": "DEBUG",
  "component": "tmdb.api",
  "message": "API request to TMDb search/tv",
  "metadata": {
    "query": "Friends",
    "year": 1994
  }
}
```

## Implementation Steps

### Phase 1: MongoDB Client Setup
1. Add pymongo dependency
2. Create `core/database/client.py`
3. Connection management with config
4. Create indexes for performance

### Phase 2: Repository Layer
1. Create `core/database/repositories/`
2. SystemInfoRepository
3. BranchRepository
4. CommitRepository
5. ResponseRepository
6. MatchRepository
7. TaskRepository
8. DiagnosticRepository

### Phase 3: Integration
1. Modify `__main__.py` to create commit on start
2. Save responses after each match
3. Save tasks after execution
4. Update commit on completion

### Phase 4: Query API
1. Get commit by ID
2. Get all commits for branch
3. Get responses for commit
4. Get tasks for match
5. Get diagnostics with filtering

### Phase 5: Web UI Data Provider
1. REST API endpoints
2. Pagination support
3. Filtering and search
4. Performance optimization

## Configuration

Add to `config.yml`:
```yaml
database:
  enabled: true
  type: "mongodb"
  host: "localhost"
  port: 27017
  name: "archiverr"
  username: ""
  password: ""
```

## Notes

- Each run creates new commit
- Commits are immutable (no updates after creation)
- Branch head pointer updates on each run
- Diagnostics optional (debug mode only)
- Indexes: commit_id, match_id, timestamp
- TTL index on diagnostics (optional cleanup)
