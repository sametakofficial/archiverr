# 🗄️ MongoDB Collections Structure - Final

## Overview

**4 Collections:**
1. `branches` - Git-like branch management
2. `commits` - Immutable execution records
3. `api_responses` - Full API response storage
4. `diagnostics` - Debug logs

---

## 1️⃣ Collection: branches

**Purpose:** Git-like branch management for different workflows

```javascript
{
  _id: ObjectId("673..."),
  name: "main",                    // Unique branch name
  description: "Main production branch",
  created_at: ISODate("2025-11-10T14:00:00Z"),
  updated_at: ISODate("2025-11-10T17:14:42Z"),
  metadata: {
    total_commits: 15,
    last_commit_id: ObjectId("674...")
  },
  status: "active"                 // "active", "archived", "deleted"
}
```

**Indexes:**
```javascript
db.branches.createIndex({ name: 1 }, { unique: true })
db.branches.createIndex({ status: 1, updated_at: -1 })
```

**Example Queries:**
```javascript
// Get main branch
db.branches.findOne({ name: "main" })

// List active branches
db.branches.find({ status: "active" }).sort({ updated_at: -1 })
```

---

## 2️⃣ Collection: commits

**Purpose:** Immutable execution records (like git commits)

```javascript
{
  _id: ObjectId("674..."),
  branch_id: ObjectId("673..."),
  parent_commit_id: ObjectId("672..."),  // null for first commit
  
  // API Response globals (DIREKT COPY)
  globals: {
    status: {
      success: true,
      matches: 2,
      tasks: 12,
      errors: 0,
      started_at: "2025-11-10T17:14:34.984764",
      finished_at: "2025-11-10T17:14:42.344800",
      duration_ms: 7360
    },
    summary: {
      input_plugin_used: "scanner",
      output_plugins_used: ["ffprobe", "renamer", "tmdb", "omdb"],
      categories: ["movie", "show"],
      total_size_bytes: 6181584889,
      total_duration_seconds: 7199.584
    },
    options: {
      debug: true,
      dry_run: true,
      hardlink: true
    },
    plugins: {
      scanner: { enabled: true, targets: [...], ... },
      ffprobe: { enabled: true, timeout: 15 },
      tmdb: { enabled: true, api_key: "...", lang: "tr" },
      // ... tüm plugin configs
    },
    tasks: [
      { name: "print_match_header", type: "print", template: "..." },
      { name: "save_nfo", type: "save", destination: "..." },
      // ... tüm tasks
    ]
  },
  
  // Reference to full API response
  api_response_id: ObjectId("675..."),
  
  // Commit metadata
  title: "Processed 2 movies from torrents folder",
  message: "Optional detailed commit message",
  created_at: ISODate("2025-11-10T17:14:34.984764")  // SAME as globals.status.started_at
}
```

**Indexes:**
```javascript
db.commits.createIndex({ branch_id: 1, created_at: -1 })
db.commits.createIndex({ api_response_id: 1 })
db.commits.createIndex({ "globals.status.success": 1 })
db.commits.createIndex({ "globals.summary.categories": 1 })
```

**Example Queries:**
```javascript
// Recent commits in main branch
db.commits.find({ 
  branch_id: ObjectId("673..."),
  "globals.status.success": true 
})
.sort({ created_at: -1 })
.limit(50)

// Failed commits
db.commits.find({ "globals.status.success": false })

// Commits with movies
db.commits.find({ "globals.summary.categories": "movie" })
```

---

## 3️⃣ Collection: api_responses

**Purpose:** Full API response storage (cold data)

```javascript
{
  _id: ObjectId("675..."),
  commit_id: ObjectId("674..."),
  
  // FULL API RESPONSE (EXACT STRUCTURE)
  globals: {
    status: { ... },      // Same as commit.globals.status
    summary: { ... },     // Same as commit.globals.summary
    options: { ... },     // Same as commit.globals.options
    plugins: { ... },     // Same as commit.globals.plugins
    tasks: [ ... ]        // Same as commit.globals.tasks
  },
  
  matches: [
    {
      globals: {
        index: 0,
        input: {
          path: "/home/samet/torrents/Mr. & Mrs. Smith (2005) BluRay 1080p DDP5.1 H.265 TSRG.mkv",
          virtual: false,
          category: "movie"
        },
        status: {
          success: true,
          success_plugins: ["scanner", "ffprobe", "renamer", "tmdb", "omdb"],
          failed_plugins: [],
          not_supported_plugins: [],
          started_at: "2025-11-10T17:14:34.984764",
          finished_at: "2025-11-10T17:14:37.520108",
          duration_ms: 2535
        },
        output: {
          tasks: [
            {
              name: "print_match_header",
              type: "print",
              success: true,
              rendered: "========== MATCH 0 =========="
            },
            {
              name: "save_nfo",
              type: "save",
              success: true,
              destination: "/path/to/file.nfo"
            }
          ],
          validations: {
            tmdb: {
              tests_passed: 1,
              tests_total: 1,
              details: {
                duration_match: {
                  passed: true,
                  ffprobe_duration: 7199.584,
                  api_runtime: 120,
                  diff_seconds: 79.584,
                  tolerance: 600
                }
              }
            },
            omdb: {
              tests_passed: 1,
              tests_total: 1,
              details: { ... }
            },
            summary: {
              total_tests: 2,
              passed_tests: 2,
              failed_tests: 0,
              accuracy: 1.0
            }
          },
          paths: {
            nfo_path: "/path/to/file.nfo",
            renamed_path: null
          }
        }
      },
      plugins: {
        scanner: {
          status: { ... },
          input: { ... }
        },
        ffprobe: {
          status: { ... },
          video: { ... },
          audio: [ ... ],
          container: { ... }
        },
        renamer: {
          status: { ... },
          parsed: { ... },
          category: "movie"
        },
        tmdb: {
          status: { ... },
          movie: { ... },
          validation: {
            tests_passed: 1,
            tests_total: 1,
            details: { ... }
          }
        },
        omdb: {
          status: { ... },
          movie: { ... },
          validation: { ... }
        }
      }
    },
    // ... more matches
  ],
  
  // Storage metadata
  created_at: ISODate("2025-11-10T17:14:34.984764"),
  size_bytes: 458932,
  compressed: false
}
```

**Indexes:**
```javascript
db.api_responses.createIndex({ commit_id: 1 }, { unique: true })
db.api_responses.createIndex({ created_at: 1 }, { expireAfterSeconds: 7776000 }) // 90 days TTL
```

**Example Queries:**
```javascript
// Get full API response for a commit
db.api_responses.findOne({ commit_id: ObjectId("674...") })

// Search matches by file path (requires text index)
db.api_responses.find({
  "matches.globals.input.path": { $regex: "Mr. & Mrs. Smith" }
})
```

---

## 4️⃣ Collection: diagnostics

**Purpose:** Debug logs and system diagnostics

```javascript
{
  _id: ObjectId("676..."),
  commit_id: ObjectId("674..."),  // null for system-level logs
  
  // Debug log entries (from DebugSystem.log_buffer)
  logs: [
    {
      timestamp: "2025-11-10T17:14:34.984+03:00",
      level: "INFO",
      component: "system",
      message: "Archiverr started",
      fields: {
        debug: true,
        dry_run: true
      }
    },
    {
      timestamp: "2025-11-10T17:14:35.102+03:00",
      level: "DEBUG",
      component: "ffprobe",
      message: "Video stream found",
      fields: {
        codec: "hevc",
        resolution: "1920x816"
      }
    },
    // ... all debug logs
  ],
  
  // Metadata
  created_at: ISODate("2025-11-10T17:14:34.984764"),
  total_entries: 156,
  debug_mode_was_enabled: true
}
```

**Indexes:**
```javascript
db.diagnostics.createIndex({ commit_id: 1 })
db.diagnostics.createIndex({ created_at: 1 }, { expireAfterSeconds: 604800 }) // 7 days TTL
db.diagnostics.createIndex({ "logs.level": 1 })
```

**Example Queries:**
```javascript
// Get logs for a commit
db.diagnostics.findOne({ commit_id: ObjectId("674...") })

// Find ERROR logs across all commits
db.diagnostics.find({ "logs.level": "ERROR" })
```

---

## 🔄 Data Flow

### Write Path (Execution)
```
1. Config.yml read
2. Plugins execute
3. API Response build (with globals.summary, match.globals, match.plugins)
4. MongoDB save (if enabled):
   ├─ Get/Create branch
   ├─ Save api_response → api_responses collection
   ├─ Create commit (globals = api_response.globals)
   └─ Save debug logs → diagnostics
5. File export (reports/)
```

### Read Path (UI/Query)
```
# Timeline view
GET /branches/{name}/commits → commits (globals embedded)

# Commit detail
GET /commits/{id} → commits + api_responses (join)

# Match detail
GET /commits/{id}/matches/{index} → api_responses.matches[index]

# Search
GET /search?q=inception → api_responses (text search on matches)

# Logs
GET /commits/{id}/logs → diagnostics
```

---

## 📊 Example: Complete Data Set

### Branch
```javascript
{
  _id: ObjectId("673abc"),
  name: "main",
  last_commit_id: ObjectId("674def")
}
```

### Commit
```javascript
{
  _id: ObjectId("674def"),
  branch_id: ObjectId("673abc"),
  globals: {
    status: { success: true, matches: 2, ... },
    summary: { categories: ["movie"], ... },
    options: { ... },
    plugins: { ... },
    tasks: [ ... ]
  },
  api_response_id: ObjectId("675ghi"),
  created_at: ISODate("2025-11-10T17:14:34Z")
}
```

### API Response
```javascript
{
  _id: ObjectId("675ghi"),
  commit_id: ObjectId("674def"),
  globals: { ... },  // SAME as commit.globals
  matches: [
    {
      globals: {
        index: 0,
        input: {path, virtual, category},
        status: {success, plugins, timestamps}
      },
      options: {...},  // Config snapshot
      tasks: [...],    // Task results
      plugins: {       // Plugin results
        tmdb: {
          globals: {status, options, validation},
          movie: {...},
          episode: null,
          ...
        }
      }
    }
  ]
}
```

### Diagnostics
```javascript
{
  _id: ObjectId("676jkl"),
  commit_id: ObjectId("674def"),
  logs: [ {timestamp, level, component, message, fields}, ... ]
}
```

---

## 🎯 Key Design Decisions

### 1. API Response = Source of Truth
- MongoDB is index/query layer
- File export always works (reports/)
- MongoDB optional

### 2. Globals Consistency
- `commit.globals = api_response.globals` (direkt copy)
- No foreach, no transformation
- Single timestamp across all

### 3. Plugin-Agnostic Storage
- `match.plugins` is storage wrapper (not logic)
- Plugin results stored as-is (opaque)
- No plugin-specific schema validation

### 4. Hot vs Cold Data
- **Hot**: commits (globals embedded) → Fast queries
- **Cold**: api_responses (full payload) → Rare access
- **Cold**: diagnostics (logs) → Debug only

### 5. TTL for Cleanup
- diagnostics: 7 days
- api_responses: 90 days (configurable)
- commits: Never expire (metadata small)

---

## 📈 Performance Characteristics

### Document Sizes
- `branches`: ~500 bytes
- `commits`: ~5-10 KB (with globals)
- `api_responses`: ~50-500 KB (full payload)
- `diagnostics`: ~10-50 KB (logs)

### Query Performance
- Commit list: <10ms (indexed)
- Commit detail: <20ms (globals embedded)
- Full API response: <50ms (cold data)
- Search: <100ms (text index)

### Storage Estimates
- 1000 commits/month × 10 KB = 10 MB
- 1000 api_responses/month × 200 KB = 200 MB
- With 90-day TTL: ~600 MB total

---

## 🔐 Security Considerations

### API Keys
- **Never store in MongoDB**: Use references only
- Config snapshot includes plugin names, not secrets
- API keys from environment variables

### Access Control
- MongoDB authentication required
- Read-only users for UI
- Write access only for system

---

## 🚀 Future Enhancements

### Potential Additions
1. **Text search index** on matches (file paths, titles)
2. **Aggregation pipelines** for statistics
3. **Sharding** by branch_id (horizontal scaling)
4. **Compression** for large api_responses
5. **Change streams** for real-time updates

### Not Needed Now
- ❌ matches collection (api_responses.matches sufficient)
- ❌ tasks collection (match.globals.output.tasks sufficient)
- ❌ extracted fields (globals provides all)
