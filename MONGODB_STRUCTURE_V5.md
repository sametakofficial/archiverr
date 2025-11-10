# MongoDB Structure v5 - Professional Time-Series Design

**Last Updated**: 2025-11-11 01:40  
**Philosophy**: Time-series database for execution tracking  
**Approach**: Denormalized, read-optimized, minimal joins

---

## 🎯 Design Philosophy

### 1. Time-Series First
- Each Archiverr run = One execution document
- Timestamped, immutable records
- Optimized for time-range queries
- TTL for automatic cleanup

### 2. Denormalized Storage
- Full data in single document
- No joins needed for common queries
- Config embedded (small overhead, big win)
- Matches embedded (complete picture)

### 3. Query-Optimized Structure
- Flat fields for indexing
- Aggregatable statistics at root
- Plugin data directly accessible
- No nested complexity

### 4. Professional Standards
- Industry-standard field naming
- ISO8601 timestamps
- Hash-based deduplication
- Proper indexes for performance

---

## 📊 Collection: executions

**Purpose**: Main collection - one document per Archiverr run

```javascript
{
  _id: ObjectId("673abc"),
  
  // === EXECUTION METADATA (Indexed) ===
  started_at: ISODate("2025-11-11T01:32:49.360Z"),
  finished_at: ISODate("2025-11-11T01:32:59.478Z"),
  duration_ms: 10117,
  success: true,
  
  // === AGGREGATED STATISTICS (Quick Access) ===
  total_matches: 2,
  successful_matches: 2,
  failed_matches: 0,
  total_tasks_executed: 12,
  total_size_bytes: 6181584889,
  total_duration_seconds: 7199.58,
  enabled_plugins: ["file-reader", "ffprobe"],
  
  // === CONFIG REFERENCE (Deduplication) ===
  config_hash: "a3f5d8e2b1c4",  // SHA256 hash (first 16 chars)
  config: {
    options: {
      dry_run: true,
      debug: true
    },
    plugins: {
      "file-reader": {enabled: true, version: "1.0.0"},
      "ffprobe": {enabled: true, version: "1.0.0"}
    }
  },
  
  // === MATCH RESULTS (Denormalized) ===
  matches: [
    {
      // Top-level metadata (flat)
      index: 0,
      input_path: "/home/samet/torrents/Mr. & Mrs. Smith (2005).mkv",
      success: true,
      executed_plugins: ["file-reader", "ffprobe"],
      failed_plugins: [],
      not_supported_plugins: [],
      duration_ms: 2535,
      
      // Tasks (flat)
      tasks: [
        {
          name: "print_match_header",
          type: "print",
          success: true,
          rendered: "========== MATCH 0 =========="
        }
      ],
      
      // Plugin data (direct access, flat)
      "file-reader": {
        status: {
          success: true,
          started_at: "2025-11-11T01:32:49.360Z",
          finished_at: "2025-11-11T01:32:50.120Z",
          duration_ms: 760
        },
        input: "/home/samet/torrents/Mr. & Mrs. Smith (2005).mkv",
        virtual: false,
        category: "movie"
      },
      
      ffprobe: {
        status: {
          success: true,
          started_at: "2025-11-11T01:32:50.121Z",
          finished_at: "2025-11-11T01:32:52.655Z",
          duration_ms: 2534
        },
        video: {
          codec: "hevc",
          width: 1920,
          height: 1080,
          resolution: "1080p",
          fps: 23.976,
          bitrate: 6845123,
          duration: 7199.584
        },
        audio: [
          {
            codec: "eac3",
            channels: 6,
            channel_layout: "5.1",
            sample_rate: "48000",
            bitrate: 640000,
            language: "eng"
          }
        ],
        container: {
          format: "matroska,webm",
          duration: 7199.584,
          size: 6181584889,
          bitrate: 6873456
        }
      }
    }
    // ... more matches
  ],
  
  // === DEBUG LOGS (Optional, embedded) ===
  debug_logs: [
    {
      timestamp: "2025-11-11T01:32:49.360Z",
      level: "INFO",
      component: "system",
      message: "Archiverr starting",
      fields: {debug: true, dry_run: true}
    }
    // ... more logs (limited to last 100)
  ]
}
```

---

## 📊 Collection: config_snapshots (Optional)

**Purpose**: Deduplication - store unique configs once

```javascript
{
  _id: ObjectId("674def"),
  config_hash: "a3f5d8e2b1c4",  // Unique index
  
  config: {
    options: {...},
    plugins: {...}
  },
  
  // Usage tracking
  first_used: ISODate("2025-11-10T10:00:00Z"),
  last_used: ISODate("2025-11-11T01:32:49Z"),
  execution_count: 42,  // How many times used
  
  created_at: ISODate("2025-11-10T10:00:00Z")
}
```

**Note**: This collection is **OPTIONAL**. For small to medium usage, embedding config in executions is fine. Only use this if you have thousands of executions with repeated configs.

---

## 🔍 Indexes

### executions
```javascript
// Time-series queries (most common)
{started_at: -1}  // DESC for latest first

// Status filtering
{success: 1, started_at: -1}

// Plugin-based queries
{enabled_plugins: 1, started_at: -1}

// Match count queries
{total_matches: 1, started_at: -1}

// Compound for advanced queries
{success: 1, enabled_plugins: 1, started_at: -1}

// TTL index (automatic cleanup)
{started_at: 1} expireAfterSeconds: 7776000  // 90 days
```

### config_snapshots (if used)
```javascript
{config_hash: 1} unique  // Deduplication
{last_used: -1}           // Cleanup old configs
```

---

## 🔄 Data Flow (Simplified)

```python
# 1. Archiverr execution
api_response = builder.build(matches, config, start_time, loaded_plugins)

# 2. Save to MongoDB (if enabled)
if config.get('mongodb', {}).get('enabled'):
    await save_execution(api_response)

# save_execution implementation:
async def save_execution(api_response: dict):
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Connect
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    
    # Insert execution (single operation)
    await db.executions.insert_one(api_response)
    
    # Optional: Update config_snapshots
    config_hash = api_response['config_hash']
    await db.config_snapshots.update_one(
        {'config_hash': config_hash},
        {
            '$setOnInsert': {
                'config': api_response['config'],
                'first_used': api_response['started_at'],
                'created_at': datetime.now()
            },
            '$set': {'last_used': api_response['started_at']},
            '$inc': {'execution_count': 1}
        },
        upsert=True
    )
    
    # Close
    client.close()
```

---

## 🔍 Common Queries (Professional)

### 1. Latest Executions
```python
# Get last 50 runs
executions = await db.executions.find().sort('started_at', -1).limit(50).to_list()
```

### 2. Failed Executions
```python
# Get all failed runs in last 7 days
from datetime import datetime, timedelta

week_ago = datetime.now() - timedelta(days=7)
failed = await db.executions.find({
    'success': False,
    'started_at': {'$gte': week_ago}
}).to_list()
```

### 3. Plugin Usage Statistics
```python
# Count executions by enabled plugins
pipeline = [
    {'$group': {
        '_id': '$enabled_plugins',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}}
]
stats = await db.executions.aggregate(pipeline).to_list()
```

### 4. Time-Series Analytics
```python
# Daily execution count for last 30 days
pipeline = [
    {'$match': {
        'started_at': {'$gte': datetime.now() - timedelta(days=30)}
    }},
    {'$group': {
        '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$started_at'}},
        'count': {'$sum': 1},
        'avg_duration': {'$avg': '$duration_ms'},
        'total_matches': {'$sum': '$total_matches'}
    }},
    {'$sort': {'_id': 1}}
]
daily_stats = await db.executions.aggregate(pipeline).to_list()
```

### 5. Full Execution Details
```python
# Get complete execution with all matches
execution = await db.executions.find_one(
    {'_id': ObjectId(execution_id)}
)
# Everything is in one document - no joins!
```

### 6. Search by File Path
```python
# Find executions that processed specific file
executions = await db.executions.find({
    'matches.input_path': {'$regex': 'Mr. & Mrs. Smith'}
}).to_list()
```

---

## 🏆 Benefits Over Previous Design

### Before (v4 - Git-like)
- ❌ 4 collections (branches, commits, api_responses, diagnostics)
- ❌ 3 queries needed for full data
- ❌ Complex branching (unnecessary for Archiverr)
- ❌ Normalized (good for writes, bad for reads)

### After (v5 - Time-Series)
- ✅ 1 main collection (executions)
- ✅ 1 query for full data
- ✅ Simple timestamped records
- ✅ Denormalized (read-optimized)

### Performance Comparison
| Operation | v4 (Git-like) | v5 (Time-Series) |
|-----------|---------------|------------------|
| Get latest execution | 3 queries | 1 query |
| Get execution details | 2 queries + 1 join | 1 query |
| Time-series stats | Complex aggregation | Simple aggregation |
| Storage overhead | ~30% (normalization) | ~5% (config embedding) |

---

## 📊 Storage Estimates

### Single Execution
- Metadata: ~500 bytes
- Config snapshot: ~1 KB
- Match (with plugins): ~5-20 KB per match
- Debug logs (optional): ~2-5 KB

**Total per execution**: ~10-50 KB (typical)

### 90-Day Retention
- 10 executions/day = ~5-25 MB
- 100 executions/day = ~50-250 MB
- 1000 executions/day = ~500 MB - 2.5 GB

**Conclusion**: MongoDB 16MB document limit is safe. Even with 100 matches and full plugin data, typical execution < 1 MB.

---

## 🚀 Migration from v4 (If Needed)

```python
async def migrate_v4_to_v5():
    """Migrate from git-like structure to time-series"""
    
    # Get all commits
    commits = await db.commits.find().to_list()
    
    for commit in commits:
        # Get full api_response
        api_response = await db.api_responses.find_one({
            'commit_id': commit['_id']
        })
        
        # Get diagnostics (optional)
        diag = await db.diagnostics.find_one({
            'commit_id': commit['_id']
        })
        
        # Build v5 execution document
        execution = {
            # From commit.globals.status
            'started_at': commit['globals']['status']['started_at'],
            'finished_at': commit['globals']['status']['finished_at'],
            'duration_ms': commit['globals']['status']['duration_ms'],
            'success': commit['globals']['status']['success'],
            
            # From commit.globals.summary
            'total_matches': commit['globals']['summary']['total_matches'],
            # ... other summary fields
            
            # From api_response
            'matches': api_response['matches'],
            
            # From diagnostics (optional)
            'debug_logs': diag['logs'] if diag else []
        }
        
        # Insert into executions
        await db.executions.insert_one(execution)
    
    print(f"Migrated {len(commits)} executions")
```

---

## 🎯 Future Enhancements

### Phase 1: Basic MongoDB Integration ✅
- executions collection
- Simple save after each run
- Basic time-series queries

### Phase 2: Analytics (Optional)
- Aggregation pipelines
- Performance tracking
- Plugin usage statistics

### Phase 3: Web UI (Future)
- FastAPI backend
- Real-time execution monitoring
- Historical data visualization
- File search interface

---

## 📝 Implementation Checklist

- [ ] Update `models/response_builder.py` ✅ DONE
- [ ] Update `__main__.py` for flat structure ✅ DONE
- [ ] Update `task_manager.py` for flat access ✅ DONE
- [ ] Update `template_manager.py` for flat routing ✅ DONE
- [ ] Create `backend/database.py` (Motor client)
- [ ] Create `backend/repositories/execution_repository.py`
- [ ] Add MongoDB settings to `config.yml`
- [ ] Add MongoDB save in `__main__.py`
- [ ] Update `config.schema.json`
- [ ] Test with real execution
- [ ] Verify MongoDB queries
- [ ] Update documentation

---

## 🏁 Conclusion

**v5 Design**: Professional, simple, performant

- **One collection to rule them all**: executions
- **One query for everything**: Complete data
- **Industry-standard**: Time-series approach
- **Plugin-agnostic**: No domain logic in structure
- **Production-ready**: Indexed, TTL'd, optimized

**This is how professionals build time-series databases.**
