# 🎯 Session TODO List - API Response Enhancement & MongoDB Integration

## ✅ TAMAMLANAN FAZLAR: 1-6

**Son Güncelleme**: 2025-11-10 22:51  
**Durum**: API Response v2 tamamlandı, MongoDB entegrasyonu bekliyor

### 📊 İlerleme Özeti
- **Tamamlanan**: Phase 1-6 (API Response v2, Validation, Template Resolution)
- **Bekleyen**: Phase 7-10 (MongoDB, Testing, Documentation)
- **Değiştirilen Dosyalar**: 11 dosya (~800 LOC)
- **Syntax Validation**: ✅ PASS

### 🎯 Yeni API Response Yapısı
```javascript
{
  globals: {status, summary, options, plugins, tasks},
  matches: [
    {
      globals: {index, input, status},
      options: {...},
      tasks: [...],
      plugins: {
        tmdb: {
          globals: {status, options, validation},
          movie: {...}, episode, season, show
        }
      }
    }
  ]
}
```

### 🔧 Temel Değişiklikler
1. **Plugin Isolation**: `plugin.globals` reserved, diğer tüm alanlar plugin kontrolünde
2. **Tasks Root Level**: `match.tasks[]` (artık globals.output.tasks değil)
3. **Config Snapshot**: Hem global hem match level'da
4. **Validation System**: TMDb, OMDb, TVDb (duration matching ±10min)
5. **Template Routing**: Smart routing (plugin vs globals vs options)

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

### 1.5 match.tasks & plugin.globals (YENİ YAPI) ✅
- [x] `match.tasks`: Task execution results (root level)
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
      source: "/source.mkv",
      destination: "/path/file.nfo",
      dry_run: true
    }
  ]
  ```
- [x] `plugin.globals.validation`: Her plugin kendi validation
  ```javascript
  tmdb: {
    globals: {
      status: {...},
      options: {...},
      validation: {
        tests_passed: 1,
        tests_total: 1,
        details: {duration_match: {...}}
      }
    },
    movie: {...}  // Plugin data
  }
  ```
- [x] `paths` kaldırıldı → `match.tasks[].destination` kullan

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

## 📌 PHASE 7: MongoDB Integration

### 7.1 Dependencies
- [ ] `requirements.txt` → `pymongo>=4.0.0` ekle
- [ ] `.env.example` → MongoDB URI ekle

### 7.2 Backend Structure
- [ ] `src/archiverr/backend/` klasör oluştur
- [ ] `backend/__init__.py`
- [ ] `backend/mongo_client.py` → Connection manager
- [ ] `backend/repositories/` klasör oluştur

### 7.3 Repositories
- [ ] `repositories/branch_repository.py`
  ```python
  class BranchRepository:
      def create(name, description)
      def get(name)
      def list_all(status="active")
      def update_last_commit(name, commit_id)
  ```
- [ ] `repositories/commit_repository.py`
  ```python
  class CommitRepository:
      def create(branch_id, globals, api_response_id)
      def get(commit_id)
      def list_by_branch(branch_id, limit=50)
  ```
- [ ] `repositories/api_response_repository.py`
  ```python
  class APIResponseRepository:
      def save(commit_id, api_response)
      def get(commit_id)
  ```
- [ ] `repositories/diagnostics_repository.py`
  ```python
  class DiagnosticsRepository:
      def save_logs(commit_id, logs)
      def get_logs(commit_id)
  ```

### 7.4 Collections & Indexes
- [ ] Collection: `branches`
  - Index: `{name: 1}` unique
  - Index: `{status: 1, updated_at: -1}`
- [ ] Collection: `commits`
  - Index: `{branch_id: 1, created_at: -1}`
  - Index: `{api_response_id: 1}`
- [ ] Collection: `api_responses`
  - Index: `{commit_id: 1}` unique
  - TTL: `{created_at: 1}` 90 days
- [ ] Collection: `diagnostics`
  - Index: `{commit_id: 1}`
  - TTL: `{created_at: 1}` 7 days

### 7.5 Main Integration
- [ ] `__main__.py` MongoDB entegrasyonu
- [ ] Config'den MongoDB enable flag al
- [ ] API response oluştuktan sonra:
  ```python
  if mongodb_enabled:
      # 1. Get/Create branch
      branch = branch_repo.get_or_create("main")
      
      # 2. Save API response
      api_response_id = api_response_repo.save(api_response)
      
      # 3. Create commit
      commit = commit_repo.create(
          branch_id=branch['_id'],
          globals=api_response['globals'],  # Direkt copy
          api_response_id=api_response_id,
          created_at=api_response['globals']['status']['started_at']
      )
      
      # 4. Save debug logs
      diagnostics_repo.save_logs(commit['_id'], debugger.get_logs())
      
      # 5. Update branch
      branch_repo.update_last_commit(branch['name'], commit['_id'])
  ```

---

## 📌 PHASE 8: Config Schema Update

### 8.1 config.yml New Fields
- [ ] MongoDB settings:
  ```yaml
  mongodb:
    enabled: true
    uri: "mongodb://localhost:27017"
    database: "archiverr"
    branch: "main"
  ```
- [ ] Validation settings:
  ```yaml
  validation:
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
