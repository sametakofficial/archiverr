# MongoDB Collections - API Response v4 Final

**Son Güncelleme**: 2025-11-11 00:46  
**Durum**: API Response v4 - Simplified & Plugin-Agnostic  
**Backend**: Python Motor + Beanie ODM (FastAPI ready)

---

## 🎯 Core Principles

### 1. Plugin-Agnostic Architecture
- Core NEVER knows plugin-specific concepts
- Validation is plugin responsibility, not global concern
- Input/output paths are plugin-managed

### 2. No Redundancy
- Config stored once: `globals.config`
- Task definitions: `globals.config.tasks`
- Task execution results: `match.globals.output.tasks`
- NO separate paths object (use tasks[].destination)

### 3. Simplified Structure
- `match.globals.input_path` - Just the path string
- `match.globals.output.tasks` - Only task execution results
- Plugins manage their own validation data

---

## 📊 Collection: branches

```javascript
{
  _id: ObjectId("673abc"),
  name: "main",                    // Unique
  description: "Main production branch",
  status: "active",                // active, archived
  last_commit_id: ObjectId("674def"),
  created_at: ISODate("2025-11-10T17:10:00Z"),
  updated_at: ISODate("2025-11-10T17:14:34Z")
}
```

**Indexes**:
- `{name: 1}` unique
- `{status: 1, updated_at: -1}`

---

## 📊 Collection: commits

```javascript
{
  _id: ObjectId("674def"),
  branch_id: ObjectId("673abc"),
  
  // SNAPSHOT: globals from api_response (immutable)
  globals: {
    status: {
      success: true,
      matches: 2,
      tasks: 4,
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
      total_duration_seconds: 7199.58
    },
    config: {                      // ✅ Single source of truth
      options: {
        debug: true,
        dry_run: true,
        hardlink: true
      },
      plugins: {
        scanner: {enabled: true, targets: [...], recursive: true, ...},
        ffprobe: {enabled: true, timeout: 15},
        tmdb: {enabled: true, api_key: "***", lang: "tr"},
        omdb: {enabled: true, api_key: "***"},
        tvdb: {enabled: true, api_key: "***"},
        renamer: {enabled: true}
      },
      tasks: [
        {name: "print_match_header", type: "print", template: "..."},
        {name: "save_nfo", type: "save", external: true, path: "tasks/save_nfo.yml"},
        {name: "print_summary", type: "print", condition: "...", template: "..."}
      ]
    }
  },
  
  // Reference to full data
  api_response_id: ObjectId("675ghi"),
  
  // Commit metadata
  created_at: ISODate("2025-11-10T17:14:34.984764")
}
```

**Indexes**:
- `{branch_id: 1, created_at: -1}`
- `{api_response_id: 1}`

---

## 📊 Collection: api_responses

```javascript
{
  _id: ObjectId("675ghi"),
  commit_id: ObjectId("674def"),
  
  // FULL API RESPONSE (exact structure from Archiverr)
  globals: {
    status: {...},        // Same as commit.globals.status
    summary: {...},       // Same as commit.globals.summary
    config: {...}         // Same as commit.globals.config
  },
  
  matches: [
    {
      globals: {
        index: 0,
        input_path: "/home/samet/torrents/Mr. & Mrs. Smith (2005).mkv",
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
          tasks: [                        // ✅ Task execution results
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
              destination: "/path/to/Mr. & Mrs. Smith (2005).nfo"
            }
          ]
        }
      },
      plugins: {
        scanner: {
          globals: {
            status: {success: true, started_at: "...", finished_at: "...", duration_ms: 12}
          },
          input: "/home/samet/torrents/Mr. & Mrs. Smith (2005).mkv",
          virtual: false,
          category: "movie"
        },
        ffprobe: {
          globals: {
            status: {success: true, ...}
          },
          video: {
            codec: "hevc",
            width: 1920,
            height: 1080,
            fps: 23.976,
            bitrate: 6845123
          },
          audio: [
            {codec: "eac3", channels: 6, sample_rate: 48000, bitrate: 640000}
          ],
          container: {
            format: "matroska",
            size: 6181584889,
            duration: 7199.584
          }
        },
        renamer: {
          globals: {
            status: {success: true, ...}
          },
          parsed: {
            show: null,
            movie: {
              title: "Mr. & Mrs. Smith",
              year: 2005,
              quality: "BluRay 1080p",
              audio: "DDP5.1",
              codec: "H.265",
              group: "TSRG"
            }
          },
          category: "movie"
        },
        tmdb: {
          globals: {
            status: {success: true, ...},
            validation: {              // ✅ Plugin-managed validation
              tests_passed: 1,
              tests_total: 1,
              details: {
                duration_match: {
                  passed: true,
                  ffprobe_duration: 7199.584,
                  api_runtime: 120,
                  diff_seconds: 0.416,
                  tolerance: 600
                }
              }
            }
          },
          movie: {
            id: 1234,
            title: "Mr. & Mrs. Smith",
            original_title: "Mr. & Mrs. Smith",
            release_date: "2005-06-10",
            runtime: 120,
            vote_average: 6.7,
            genres: ["Action", "Comedy", "Thriller"],
            overview: "...",
            tagline: "...",
            people: {
              directors: ["Doug Liman"],
              cast: [
                {name: "Brad Pitt", character: "John Smith", order: 0},
                {name: "Angelina Jolie", character: "Jane Smith", order: 1}
              ]
            },
            images: {
              poster: "/poster.jpg",
              backdrop: "/backdrop.jpg"
            }
          },
          episode: null,
          season: null,
          show: null
        },
        omdb: {
          globals: {
            status: {success: true, ...},
            validation: {              // ✅ Plugin-managed validation
              tests_passed: 1,
              tests_total: 1,
              details: {duration_match: {...}}
            }
          },
          movie: {
            title: "Mr. & Mrs. Smith",
            year: "2005",
            rated: "PG-13",
            runtime: "120 min",
            genre: "Action, Comedy, Crime",
            director: "Doug Liman",
            actors: "Brad Pitt, Angelina Jolie, Vince Vaughn",
            plot: "...",
            imdb_rating: "6.5",
            imdb_votes: "487,394",
            imdb_id: "tt0356910",
            ratings: [
              {source: "Internet Movie Database", value: "6.5/10"},
              {source: "Rotten Tomatoes", value: "60%"}
            ]
          },
          episode: null,
          season: null,
          show: null
        }
      }
    }
    // ... more matches
  ],
  
  // Storage metadata
  created_at: ISODate("2025-11-10T17:14:34.984764"),
  size_bytes: 458932,
  compressed: false
}
```

**Indexes**:
- `{commit_id: 1}` unique
- TTL: `{created_at: 1}` expireAfterSeconds: 7776000 (90 days)

---

## 📊 Collection: diagnostics

```javascript
{
  _id: ObjectId("676jkl"),
  commit_id: ObjectId("674def"),
  
  logs: [
    {
      level: "info",
      category: "system",
      message: "Starting Archiverr execution",
      timestamp: "2025-11-10T17:14:34.984764",
      metadata: {}
    },
    {
      level: "debug",
      category: "plugins",
      message: "Loading plugin: scanner",
      timestamp: "2025-11-10T17:14:35.123456",
      metadata: {plugin: "scanner", version: "1.0.0"}
    }
    // ... more logs
  ],
  
  created_at: ISODate("2025-11-10T17:14:34Z")
}
```

**Indexes**:
- `{commit_id: 1}`
- TTL: `{created_at: 1}` expireAfterSeconds: 604800 (7 days)

---

## 🔄 Data Flow (Async)

```python
# 1. Archiverr execution
api_response = builder.build(matches, config, start_time, loaded_plugins)

# 2. Save to MongoDB (if enabled)
if config.get('mongodb', {}).get('enabled'):
    await save_to_mongodb(api_response, config, debugger)

# save_to_mongodb implementation:
async def save_to_mongodb(api_response, config, debugger):
    # Initialize Beanie
    await Database.connect(
        uri=config['mongodb']['uri'],
        database=config['mongodb']['database']
    )
    
    # Repositories
    branch_repo = BranchRepository()
    commit_repo = CommitRepository()
    api_repo = APIResponseRepository()
    diag_repo = DiagnosticsRepository()
    
    # Get/Create branch
    branch = await branch_repo.get(config['mongodb']['branch'])
    if not branch:
        branch = await branch_repo.create(
            name=config['mongodb']['branch'],
            description="Main branch"
        )
    
    # Save API response (full data)
    api_doc = await api_repo.save(
        commit_id=None,  # Will be set after commit creation
        data=api_response
    )
    
    # Create commit (snapshot of globals)
    commit = await commit_repo.create(
        branch_id=branch.id,
        globals=api_response['globals'],  # Snapshot
        api_response_id=api_doc.id
    )
    
    # Update api_response with commit_id
    api_doc.commit_id = commit.id
    await api_doc.save()
    
    # Update branch pointer
    await branch_repo.update_last_commit(branch.name, commit.id)
    
    # Save diagnostics (optional)
    logs = debugger.get_logs()
    if logs:
        await diag_repo.save(commit.id, logs)
    
    await Database.disconnect()
```

---

## 🔍 Query Examples (Beanie)

### List Recent Commits (Lightweight)
```python
from backend.models import Branch, Commit

branch = await Branch.find_one(Branch.name == "main")
commits = await Commit.find(
    Commit.branch_id == branch.id
).sort(-Commit.created_at).limit(50).to_list()

# Returns: List[{globals: {...}, api_response_id, created_at}]
```

### Get Full API Response
```python
from backend.models import Commit, APIResponse

commit = await Commit.get(commit_id)
response = await APIResponse.find_one(
    APIResponse.commit_id == commit.id
)

# Returns: Full matches[] data
```

### Query by Match Count
```python
commits = await Commit.find(
    Commit.globals.status.matches >= 10
).to_list()
```

### Get Diagnostics
```python
from backend.models import Diagnostics

diag = await Diagnostics.find_one(Diagnostics.commit_id == commit_id)
print(f"Total logs: {len(diag.logs)}")
for log in diag.logs:
    print(f"[{log['level']}] {log['category']}: {log['message']}")
```

---

## 🎯 Key Changes (v3 → v4)

### ❌ Removed (Plugin-Agnostic Violations)
1. `globals.summary.validations` - Core shouldn't aggregate validation
2. `match.globals.output.validations` - Validation is plugin concern
3. `match.globals.output.paths` - Redundant (use tasks[].destination)
4. `match.globals.input.{virtual, category}` - Plugin metadata

### ✅ Simplified
1. `match.globals.input_path` - Just path string
2. `match.globals.output.tasks` - Only execution results
3. Plugins manage their own validation in `plugin.globals.validation`

### ✅ Preserved
1. `globals.config` - Single source of truth for config
2. `match.globals.output.tasks` - Core manages task execution
3. Plugin structure flexibility - Plugins control their own data

---

## 🏆 Benefits

1. **Plugin-Agnostic**: Core never references plugin-specific concepts
2. **No Redundancy**: Config once, tasks definitions vs results separated
3. **Type-Safe**: Beanie ODM with Pydantic validation
4. **Async Ready**: Motor driver, FastAPI integration trivial
5. **Clean Queries**: Lightweight commits, full data on demand
6. **TTL Management**: Auto-cleanup (90d response, 7d diagnostics)
7. **Git-Like**: Branch/commit workflow, immutable snapshots
8. **Reproducible**: Config snapshot in every commit

---

## 🚀 Backend Stack

- **Motor**: Async MongoDB driver
- **Beanie**: ODM (Document models, query builder, migrations)
- **Pydantic**: Validation & serialization
- **FastAPI**: REST API (future integration)
- **Svelte**: Frontend UI (separate project)

**No Node.js needed** - Pure Python stack is industry-standard and sufficient.
