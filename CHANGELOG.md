# Changelog

## [0.3.0] - 2025-10-30

### 🎯 Birleşik Variable Engine

#### ✅ Önemli Değişiklikler
- **Pattern + Query birleştirme**: `pattern.py` ve `query.py` → `variable_engine.py`
- **Birleşik {var} syntax**: Artık her yerde `{var}` kullanılıyor ($ kaldırıldı)
- **Query-based rename**: `config.yml` rename bölümü artık query formatında
- **Sessiz loglama**: Sadece config'deki `print` template'leri gösteriliyor
- **Temiz çıktı**: Standart loglar kaldırıldı (Start/Summary/→ vb.)

#### 🔧 Config Değişiklikleri
```yaml
# ESKİ (v0.2.0)
rename:
  movie_pattern: "$name ($movieYear)"
  series_pattern: "$showName/..."

# YENİ (v0.3.0)
rename:
  movies:
    print: "✓ {name} ({movieYear})"
    save: "{name} ({movieYear})/..."
  series:
    print: "✓ {showName} - S{seasonNumber:pad:2}E{episodeNumber:pad:2}"
    save: "{showName}/..."
```

#### 📦 Dosya Değişiklikleri
- ✅ Yeni: `src/archiverr/engines/yaml/variable_engine.py`
- ✅ Yeni: `src/archiverr/core/renamer/query_logger.py`
- 🗑️ Kaldırıldı: `src/archiverr/engines/yaml/pattern.py` (artık gerekli değil)
- 🗑️ Kaldırıldı: `src/archiverr/engines/yaml/query.py` (artık gerekli değil)

#### 🔄 Breaking Changes
- **Tüm pattern syntax değişti**: `$var` → `{var}`
- **Config yapısı değişti**: `movie_pattern` → `movies.save`
- **Print zorunlu**: Log görmek için config'de `print` tanımlanmalı

---

## [0.2.0] - 2025-10-30

### 🏗️ Majör Yeniden Yapılandırma (Restructure)

#### ✅ Eklenenler
- **Modüler mimari**: Profesyonel `src/` layout
- **YAML Engine**: 100+ değişken, 10+ filtre
- **Query Engine**: `where`/`print`/`save` ile gelişmiş filtreleme
- **FFprobe cache**: `*-ffmpeg.nfo` dosya sistemi
- **Matcher modülü**: TMDb matching ayrı modül
- **Logger sistemi**: JSON ve debug log desteği
- **Setup.py**: PyPI uyumlu paket yapısı
- **Query templates**: 5 hazır query örneği
- **Dokümantasyon**: README.md, README_YML_ENGINE.md, memory/

#### 🔄 Değişenler
- `engine/` → `src/archiverr/engines/yaml/`
- `renamer.py` → `src/archiverr/core/renamer/` (4 modüle bölündü)
- `config.py` → `src/archiverr/models/config.py`
- `tmdb_client.py` → `src/archiverr/integrations/tmdb/client.py`
- `mediainfo.py` → `src/archiverr/integrations/ffprobe/analyzer.py`
- `sanitiser.py` → `src/archiverr/utils/parser.py`
- `filescanner.py` → `src/archiverr/core/scanner/scanner.py`
- `nfo.py` → `src/archiverr/utils/nfo_writer.py`
- `cli.py` → `src/archiverr/cli/main.py`
- `config.yml` → `config/config.yml`
- `memory/` → `docs/memory/`

#### 🗑️ Silinenler
- `.env` - Artık config.yml kullanılıyor
- `pattern_engine.py` - → `yaml/pattern.py`
- `engine.py` - Eski query engine
- `test_phase1.py` - Eski test dosyası
- `README_PHASE1.md` - Eski doküman
- `main.py` - Gereksiz wrapper

#### 📦 Taşınanlar (drafts/)
- `api.py` → `docs/drafts/` (gelecek özellik)
- `database.py` → `docs/drafts/` (gelecek özellik)

### 🎯 Yeni Klasör Yapısı

```
archiverr/
├── src/archiverr/              # Ana kaynak
│   ├── core/                   # Çekirdek (renamer, matching, scanner)
│   ├── engines/yaml/           # YAML engine
│   ├── integrations/           # TMDb, FFprobe
│   ├── models/                 # Config models
│   ├── utils/                  # Parser, NFO
│   └── cli/                    # CLI
├── config/                     # Yapılandırma
│   ├── config.yml
│   └── query_templates/
├── docs/                       # Dokümantasyon
│   ├── memory/
│   └── drafts/
├── tests/                      # Testler
├── README.md                   # Ana doküman
├── README_YML_ENGINE.md        # Engine rehberi
└── setup.py                    # Paket kurulumu
```

### 📚 Yeni Dokümantasyon
- `README.md` - Ana kullanım kılavuzu
- `README_YML_ENGINE.md` - Detaylı değişken referansı
- `docs/memory/00_PROJE_GENEL_BAKIS.md` - Türkçe proje özeti
- `config/query_templates/` - 5 örnek query

### 🔧 Breaking Changes
- Import path'leri değişti: `from archiverr.core.renamer import rename_files`
- CLI entry point: `archiverr` command (setup.py install sonrası)
- Config dosyası: `config/config.yml` (root yerine)

---

## [0.1.0] - Önceki Versiyon

### Özellikler
- Basit CLI renamer
- TMDb entegrasyonu
- Pattern engine (basit)
- NFO yazma
- .env yapılandırma
