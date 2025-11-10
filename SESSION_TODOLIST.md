# 🎯 Session TODO List - API Response Enhancement & MongoDB Integration

## ✅ TAMAMLANAN FAZLAR: 1-6.6

**Son Güncelleme**: 2025-11-11 00:46  
**Durum**: API Response v4 (Simplified & Plugin-Agnostic) tamamlandı, MongoDB entegrasyonu bekliyor

### 📊 İlerleme Özeti
- **Tamamlanan**: Phase 1-6.6 (API Response v4 Final, Simplified)
- **Bekleyen**: Phase 7-10 (MongoDB Backend, Testing, Documentation)
- **Değiştirilen Dosyalar**: 11 dosya (~900 LOC)
- **Syntax Validation**: ✅ PASS (v4)

### 🎯 Final API Response Yapısı (v4 - Simplified)
```javascript
{
  globals: {
    status: {...},
    summary: {                   // ✅ NO validations (plugin-agnostic)
      input_plugin_used: "scanner",
      output_plugins_used: [...],
      categories: [...],
      total_size_bytes, total_duration_seconds
    },
    config: {                    // ✅ Single source of truth
      options: {...},
      plugins: {...},
      tasks: [...]               // Task DEFINITIONS
    }
  },
  matches: [
    {
      globals: {
        index: 0,
        input_path: "/path/file.mkv",  // ✅ Just string (simplified)
        status: {...},
        output: {
          tasks: [...]           // ✅ ONLY task RESULTS
        }
      },
      plugins: {
        tmdb: {
          globals: {
            status: {...},
            validation: {...}    // ✅ Plugin-managed
          },
          movie: {...}           // Plugin data
        }
      }
    }
  ]
}
```

### 🔧 v3 → v4 Değişiklikleri (Plugin-Agnostic)
1. ❌ **globals.summary.validations KALDIRILDI** - Core validation aggregate etmemeli (plugin concern)
2. ❌ **match.globals.output.validations KALDIRILDI** - Plugin kendi yönetsin
3. ❌ **match.globals.output.paths KALDIRILDI** - Redundant (tasks[].destination kullan)
4. ✅ **match.globals.input → input_path** - Basitleştirildi (sadece string)
5. ✅ **External task name fix** - Artık unnamed değil, config'deki ismi kullanıyor
6. ✅ **Plugin validation preserved** - Her plugin `plugin.globals.validation` ile kendi manage eder

---

## 📌 PHASE 1: API Response Structure Changes ✅ COMPLETE

### 1.1 globals.summary Ekleme ✅
- [x] `api_response.globals.summary` object oluştur
  - [x] `input_plugin_used`: "scanner" veya "file_reader"
  - [x] `output_plugins_used`: ["ffprobe", "renamer", "tmdb", "omdb"]
  - [x] `categories`: ["movie", "show"] (plugin.json'dan toplanan)
  - [x] `total_size_bytes`: Tüm matchlerin toplam boyutu
  - [x] `total_duration_seconds`: Tüm matchlerin toplam süresi
  - [x] `validations`: Global validation summary (yeni eklendi)

### 1.2 globals.options/plugins/tasks Snapshot ✅
- [x] Config.yml okunduğunda snapshot al
- [x] `api_response.globals.options` = config['options']
- [x] `api_response.globals.plugins` = config['plugins']
- [x] `api_response.globals.tasks` = config['tasks']
- [x] Reproducibility: API response self-contained

### 1.3 match.globals Yapısı Oluştur ✅
- [x] Her match için `match.globals` object oluştur
- [x] `match.globals.index`: Match sırası (0, 1, 2...)
- [x] `match.globals.input`:
  - [x] `path`: Dosya yolu
  - [x] `virtual`: Boolean
  - [x] `category`: "movie" veya "show"
- [x] `match.globals.status`:
  - [x] `success`: Boolean
  - [x] `success_plugins`: ["ffprobe", "renamer", "tmdb"]
  - [x] `failed_plugins`: []
  - [x] `not_supported_plugins`: []
  - [x] `started_at`: ISO timestamp
  - [x] `finished_at`: ISO timestamp
  - [x] `duration_ms`: Milisaniye
- [x] **DEĞİŞİKLİK**: `match.globals.output` KALDIRILDI
  - Tasks artık `match.tasks` (root level)
  - Validations artık `plugin.globals.validation`

### 1.4 match.plugins Wrapper ✅ (YENİ YAPI)
- [x] **Sadece API Response yapısında değişiklik**
- [x] Tüm plugin sonuçlarını `match.plugins` altına al
- [x] **YENİ YAPI**:
  ```javascript
  api_response.matches[0] = {
    globals: {index, input, status},  // output kaldırıldı
    options: {...},     // Yeni: Config snapshot
    tasks: [...],       // Yeni: Root level
    plugins: {
      tmdb: {
        globals: {status, options, validation},  // Yeni wrapper
        movie: {...},    // Plugin kendi yapısı
        episode: null,
        ...
      }
    }
  }
  ```
- [x] **Plugin Isolation**: Sadece `plugin.globals` reserved, geri kalan plugin kontrolünde

### 1.5 match.globals.output (DÜZELTİLDİ v3) ✅
- [x] **YENİ**: `match.globals.output` geri geldi
- [x] `match.globals.output.tasks`: Task execution results
  ```javascript
  tasks: [
    {
      name: "print_match_header",
      type: "print",
      success: true,
      rendered: "..."
    },
    {
      name: "save_nfo",
      type: "save",
      success: true,
      destination: "/path/file.nfo"
    }
  ]
  ```
- [x] `match.globals.output.validations`: Plugin validations summary
  ```javascript
  validations: {
    tmdb: {tests_passed: 1, tests_total: 1, details: {...}},
    omdb: {...},
    summary: {total_tests: 2, accuracy: 1.0}
  }
  ```
- [x] `match.globals.output.paths`: Output file paths
  ```javascript
  paths: {nfo_path: "/path.nfo", renamed_path: null}
  ```

### 1.6 Kaldırılan Alanlar (v3) ✅
- [x] ❌ `match.options` - Duplicate (globals.config.options kullan)
- [x] ❌ `match.tasks` - Yanlış yer (globals.output.tasks kullan)
- [x] ❌ `plugin.globals.options` - Gereksiz (globals.config.plugins kullan)

---

## 📌 PHASE 2: Plugin Validation System ✅ COMPLETE

### 2.1 Base Validation Helper ✅
- [x] `plugins/base.py` → `ValidationResult` dataclass ekle
- [x] `BasePlugin` → `_validate_duration()` method ekle
- [x] OutputPlugin base class kullanımı

### 2.2 TMDb Plugin Validation ✅
- [x] `plugins/tmdb/client.py` güncellemesi
- [x] OutputPlugin inheritance
- [x] Movie duration validation
- [x] Episode duration validation
- [x] Validation result in plugin output

### 2.3 OMDb Plugin Validation ✅
- [x] `plugins/omdb/client.py` güncellemesi
- [x] OutputPlugin inheritance
- [x] Runtime parsing ("120 min" → 120)
- [x] Duration validation
- [x] Validation result return

### 2.4 TVDb Plugin Validation ✅
- [x] Movie runtime validation
- [x] Episode runtime validation
- [x] OutputPlugin inheritance
- [x] Validation result return

### 2.5 TVMaze Plugin Validation ⏭️ SKIP
- [ ] Episode runtime kontrolü (not supported for movies)
- **Not**: TVMaze movie desteği yok, sadece show

### 2.6 Validation Summary ✅
- [x] Response builder içinde global validation summary
- [x] `globals.summary.validations`:
  - [x] total_tests (tüm match'ler)
  - [x] passed_tests
  - [x] accuracy
  - [x] by_plugin breakdown

---

## 📌 PHASE 3: Plugin Categories System ✅ COMPLETE

### 3.1 plugin.json Schema Update ✅
- [x] Her plugin.json'a `categories` field eklendi (9 dosya)
- [x] scanner, file-reader, ffprobe: `[]` (all)
- [x] renamer, tmdb, omdb, tvdb, tvmaze: ilgili kategoriler

### 3.2 Category Collection at Startup ✅
- [x] Response builder içinde categories toplama
- [x] Loaded plugins'den categories çıkarma
- [x] `api_response.globals.summary.categories` oluşturuldu

---

## 📌 PHASE 4: Template Variable Resolution Enhancement ✅ COMPLETE

### 4.1 Smart Variable Routing ✅
- [x] `core/tasks/template_manager.py` güncellemesi
- [x] Jinja2 context yeniden yapılandırıldı
- [x] Routing:
  - `$tmdb.movie` → `match.plugins.tmdb.movie`
  - `$tmdb.globals` → `match.plugins.tmdb.globals`
  - `$globals` → `match.globals`
  - `$options` → `match.options`
  - `$tasks` → `match.tasks`
  - `$apiresponse` → API root

### 4.2 Backward Compatibility ✅
- [x] Template routing güncellendi
- [x] Indexed access: `$100.tmdb.movie` → `matches[100].plugins.tmdb.movie`
- [x] Plugin globals: `$100.globals` → `matches[100].globals`

### 4.3 Test Cases ⏭️ TODO
- [ ] Integration test yazılacak
- [ ] Template rendering verification

---

## 📌 PHASE 5: Response Builder Refactor ✅ COMPLETE

### 5.1 APIResponseBuilder Updates ✅
- [x] `models/response_builder.py` tam refactor
- [x] `_format_match()`: Yeni yapı (plugin.globals wrapper)
- [x] Config, start_time, loaded_plugins parametreleri
- [ ] `build()` method:
  ```python
  def build(self, matches, config, start_time):
      # 1. Globals oluştur
      globals_obj = {
          'status': {...},
          'summary': self._build_summary(matches, config),
          'options': config['options'],
          'plugins': config['plugins'],
          'tasks': config['tasks']
      }
      
      # 2. Matches dönüştür (plugins wrapper ekle)
      formatted_matches = []
      for match in matches:
          formatted_match = {
              'globals': self._build_match_globals(match),
              'plugins': {
                  # Tüm plugin results buraya
                  plugin_name: match[plugin_name]
                  for plugin_name in match
                  if plugin_name not in ['globals']
              }
          }
          formatted_matches.append(formatted_match)
      
      return {
          'globals': globals_obj,
          'matches': formatted_matches
      }
  ```

### 5.2 Summary Builder ✅
- [x] `_build_summary()` method tamamlandı
- [x] Input/output plugins detection
- [x] Categories collection
- [x] Size ve duration aggregation

### 5.3 Match Globals Builder ✅
- [x] Match globals creation (index, input, status)
- [x] **Değişiklik**: output kaldırıldı
- [x] Tasks ve validations yeni yerlerde

### 5.4 Validation Summary ✅
- [x] `_build_global_validations_summary()` eklendi
- [x] Cross-match aggregation
- [x] Per-plugin breakdown
- [x] `globals.summary.validations` oluşturuldu

---

## 📌 PHASE 6: Task Execution Integration ✅ COMPLETE

### 6.1 Task Results → match.tasks ✅
- [x] Task results tracking in `__main__.py`
- [x] Format: name, type, success, rendered/source/destination/dry_run
- [x] `match.tasks[]` (root level) oluşturuldu

### 6.2 Output Paths Tracking ✅ (DEĞİŞTİ)
- [x] Paths ayrı object kaldırıldı
- [x] `match.tasks[].destination` kullan
- [x] Task name'den path tipi anlaşılır

---

---

## 📌 PHASE 6.5: API Response v3 Corrections ✅ COMPLETE
(Superseded by v4)

---

## 📌 PHASE 6.6: API Response v4 - Simplified & Plugin-Agnostic ✅ COMPLETE

### 6.5.1 Structure Fixes ✅
- [x] Remove `match.options` (duplicate)
- [x] Restore `match.globals.output` (tasks, validations, paths)
- [x] Move `match.tasks` → `match.globals.output.tasks`
- [x] Remove `plugin.globals.options` (duplicate)
- [x] Wrap config: `globals.config` = {options, plugins, tasks}

### 6.5.2 Template Manager Update ✅
- [x] Update context for new structure
- [x] `$options` → `api_response.globals.config.options`
- [x] `$output` → `match.globals.output`
- [x] Remove `match.options` and `match.tasks` references

### 6.5.3 Main Entry Point Update ✅
- [x] Task results → `match.globals.output.tasks`
- [x] Paths tracking → `match.globals.output.paths`

---

## 📌 PHASE 6.6: API Response v4 - Simplified & Plugin-Agnostic ✅ COMPLETE

### 6.6.1 Remove Plugin-Agnostic Violations ✅
- [x] ❌ Remove `globals.summary.validations` - Core shouldn't aggregate
- [x] ❌ Remove `match.globals.output.validations` - Plugin concern
- [x] ❌ Remove `match.globals.output.paths` - Redundant
- [x] ✅ Validation stays in `plugin.globals.validation` (plugin-managed)

### 6.6.2 Simplify Input Structure ✅
- [x] `match.globals.input` → `match.globals.input_path` (just string)
- [x] Remove `{path, virtual, category}` object
- [x] Update `task_manager.py` to use `input_path`

### 6.6.3 Fix External Task Naming ✅
- [x] External tasks artık "unnamed" değil
- [x] Config'deki task name preserve ediliyor

### 6.6.4 Documentation ✅
- [x] `MONGODB_STRUCTURE_FINAL.md` created
- [x] Full v4 structure documented
- [x] Query examples (Beanie)
- [x] Data flow (async)

---

## 📌 PHASE 7: MongoDB Backend (FastAPI Ready) ⏳ READY TO START

### 7.1 Dependencies
- [ ] `requirements.txt` güncelle:
  - [ ] `pymongo>=4.6.0` (async support)
  - [ ] `motor>=3.3.0` (async MongoDB driver for FastAPI)
  - [ ] `beanie>=1.23.0` (ODM, opsiyonel ama önerilen)
  - [ ] `pydantic>=2.0.0` (zaten var, validation için)
- [ ] `.env.example` → MongoDB settings ekle:
  ```
  MONGODB_URI=mongodb://localhost:27017
  MONGODB_DATABASE=archiverr
  MONGODB_BRANCH=main
  ```

### 7.2 Backend Structure (Python-Only, FastAPI Ready)
- [ ] `src/archiverr/backend/` klasör oluştur
- [ ] `backend/__init__.py`
- [ ] `backend/database.py` → Motor async connection manager
  ```python
  from motor.motor_asyncio import AsyncIOMotorClient
  from beanie import init_beanie
  
  class Database:
      client: AsyncIOMotorClient = None
      
      async def connect(uri: str, database: str):
          # Connection pooling, retry logic
      
      async def disconnect():
          # Cleanup
  ```
- [ ] `backend/models/` klasör oluştur (Beanie ODM models)
- [ ] `backend/repositories/` klasör oluştur (Repository pattern)

### 7.3 Beanie ODM Models
- [ ] `models/branch.py`
  ```python
  from beanie import Document
  from pydantic import Field
  from datetime import datetime
  
  class Branch(Document):
      name: str = Field(unique=True)
      description: str = ""
      status: str = "active"  # active, archived
      last_commit_id: Optional[ObjectId] = None
      created_at: datetime = Field(default_factory=datetime.utcnow)
      updated_at: datetime = Field(default_factory=datetime.utcnow)
      
      class Settings:
          name = "branches"
          indexes = [
              "name",
              ["status", ("updated_at", -1)]
          ]
  ```
- [ ] `models/commit.py`
- [ ] `models/api_response.py`
- [ ] `models/diagnostics.py`

### 7.4 Repositories (Async)
- [ ] `repositories/branch_repository.py`
  ```python
  from backend.models.branch import Branch
  
  class BranchRepository:
      async def create(self, name: str, description: str) -> Branch:
          branch = Branch(name=name, description=description)
          await branch.insert()
          return branch
      
      async def get(self, name: str) -> Optional[Branch]:
          return await Branch.find_one(Branch.name == name)
      
      async def list_all(self, status: str = "active") -> List[Branch]:
          return await Branch.find(Branch.status == status).to_list()
      
      async def update_last_commit(self, name: str, commit_id: ObjectId):
          branch = await self.get(name)
          branch.last_commit_id = commit_id
          await branch.save()
  ```
- [ ] `repositories/commit_repository.py`
- [ ] `repositories/api_response_repository.py`
- [ ] `repositories/diagnostics_repository.py`

### 7.5 Collections & Indexes (via Beanie)
Beanie models yukarıda index tanımları içeriyor. Ek notlar:
- [ ] `branches`: name unique, status+updated_at compound
- [ ] `commits`: branch_id+created_at, api_response_id
- [ ] `api_responses`: commit_id unique, TTL 90 days
- [ ] `diagnostics`: commit_id, TTL 7 days

### 7.6 Main Integration (Async)
- [ ] `__main__.py` MongoDB entegrasyonu
- [ ] Config'den MongoDB enable flag al
- [ ] API response oluştuktan sonra:
  ```python
  import asyncio
  from backend.database import Database
  from backend.repositories import BranchRepo, CommitRepo, APIResponseRepo
  
  async def save_to_mongodb(api_response, config, debugger):
      if not config.get('mongodb', {}).get('enabled'):
          return
      
      # Initialize connection
      await Database.connect(
          uri=config['mongodb']['uri'],
          database=config['mongodb']['database']
      )
      
      # Repositories
      branch_repo = BranchRepo()
      commit_repo = CommitRepo()
      api_repo = APIResponseRepo()
      
      # 1. Get/Create branch
      branch = await branch_repo.get(config['mongodb']['branch'])
      if not branch:
          branch = await branch_repo.create(
              name=config['mongodb']['branch'],
              description="Main branch"
          )
      
      # 2. Save API response
      api_response_doc = await api_repo.save(api_response)
      
      # 3. Create commit
      commit = await commit_repo.create(
          branch_id=branch.id,
          globals=api_response['globals'],
          api_response_id=api_response_doc.id
      )
      
      # 4. Update branch
      await branch_repo.update_last_commit(branch.name, commit.id)
      
      await Database.disconnect()
  
  # In main:
  if config.get('mongodb', {}).get('enabled'):
      asyncio.run(save_to_mongodb(api_response, config, debugger))
  ```

---

### 7.7 FastAPI Preparation (Future)
- [ ] Backend zaten async, FastAPI entegrasyonu kolay olacak
- [ ] `backend/api/` klasör oluşturulacak
- [ ] Endpoints: `/branches`, `/commits`, `/matches`, `/diagnostics`
- [ ] WebSocket support for live updates

**Not**: Node.js GEREKSIZ. Python stack yeterli:
- **Motor**: Async MongoDB driver
- **Beanie**: ODM (type-safe, Pydantic integration)
- **FastAPI**: Modern async web framework
- **Svelte**: Frontend (ayrı proje)

---

## 📌 PHASE 8: Config Schema Update

### 8.1 config.yml New Fields
- [ ] MongoDB settings:
  ```yaml
  mongodb:
    enabled: false  # Default: disabled
    uri: "${MONGODB_URI}"  # From .env
    database: "${MONGODB_DATABASE}"
    branch: "${MONGODB_BRANCH}"
  ```
- [ ] Validation settings:
  ```yaml
  validation:
    enabled: true
    duration_tolerance_seconds: 600
  ```

### 8.2 config.schema.json Update
- [ ] MongoDB section ekle
- [ ] Validation section ekle

---

## 📌 PHASE 9: Testing

### 9.1 Unit Tests
- [ ] `tests/test_validation.py`
  - Duration validation
  - ValidationResult creation
- [ ] `tests/test_template_resolution.py`
  - Variable routing logic
  - Plugin vs globals resolution
- [ ] `tests/test_response_builder.py`
  - API response structure
  - match.globals creation
  - match.plugins wrapper

### 9.2 Integration Tests
- [ ] Real file test (Mr. & Mrs. Smith)
- [ ] MongoDB save/load cycle
- [ ] Template resolution end-to-end
- [ ] Validation accuracy calculation

### 9.3 Manual Testing
- [ ] `python -m archiverr` run
- [ ] Check `reports/api_response_full_*.json`
- [ ] Check MongoDB commits/api_responses
- [ ] Check validation results
- [ ] Check template rendering

---

## 📌 PHASE 10: Documentation

### 10.1 Create Docs
- [ ] `docs/API_RESPONSE_FORMAT.md` (yeni yapı)
- [ ] `docs/VALIDATION_SYSTEM.md`
- [ ] `docs/TEMPLATE_VARIABLES.md` (routing logic)
- [ ] `docs/MONGODB_INTEGRATION.md`

### 10.2 Update Docs
- [ ] `docs/MONGODB_ARCHITECTURE.md` (güncel yapı)
- [ ] `README.md` (MongoDB setup)

### 10.3 Code Documentation
- [ ] Validation methods docstring
- [ ] Repository methods docstring
- [ ] Type hints (tüm yeni kod)

---

## ✅ COMPLETION CHECKLIST

- [ ] Tüm unit tests geçiyor
- [ ] Integration tests başarılı
- [ ] Backward compatibility korunuyor
- [ ] MongoDB optional (disable edilebilir)
- [ ] Documentation complete
- [ ] Type hints complete
- [ ] Performance acceptable (<10% overhead)
- [ ] Code quality pass (syntax, linting)

---

## 🚨 CRITICAL NOTES

### Plugin-Agnostic Principles
1. **match.plugins wrapper**: Plugin names storage, ama logic yok
2. **Validation optional**: Plugin validation skip edilebilir
3. **Categories from plugin.json**: Plugin self-declaration
4. **Template routing**: Smart but plugin-agnostic (generic patterns)

### Backward Compatibility
1. **Template variables**: Eski format çalışmalı
2. **File-only mode**: MongoDB olmadan çalışmalı
3. **Config.yml**: Eski config'ler geçerli

### Performance
1. **Validation overhead**: <100ms per match
2. **MongoDB overhead**: <500ms per commit
3. **Memory**: API response +20% max (config snapshot)

### Data Consistency
1. **Single timestamp**: Tüm sistem aynı start_time
2. **API response = source**: MongoDB secondary
3. **Globals sync**: `commit.globals = api_response.globals` (direkt copy)

---

## 📊 PRIORITY LEVELS

**🔴 HIGH (Phase 1-5):**
- API Response structure changes
- Plugin validation system
- Template variable resolution
- Response builder refactor

**🟡 MEDIUM (Phase 6-7):**
- Task execution integration
- MongoDB integration

**🟢 LOW (Phase 8-10):**
- Config schema update
- Testing
- Documentation
