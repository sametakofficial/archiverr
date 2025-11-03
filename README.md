# archiverr

**Akıllı medya organizatörü** - TMDb + FFprobe + YAML pattern engine

## 🎯 Özellikler

- ✅ TMDb API ile akıllı eşleştirme
- ✅ Esnek pattern engine (100+ değişken)
- ✅ FFprobe metadata analizi
- ✅ Dry-run + hardlink desteği
- ✅ Kodi NFO dosyaları
- ✅ Paralel işleme

## 📦 Kurulum

```bash
# Repository clone
git clone https://github.com/yourusername/archiverr.git
cd archiverr

# Gerekli paketleri kur
pip install -e .

# Veya geliştirici modu
pip install -r requirements.txt
```

## 🚀 Hızlı Başlangıç

### 1. Config Ayarla

`config/config.yml` dosyasını düzenle:

```yaml
tmdb:
  api_key: "YOUR_TMDB_API_KEY"  # https://www.themoviedb.org/settings/api

rename:
  series_dst: "/media/Series"
  series_pattern: "$showName/Season $seasonNumber/$showName - S$seasonNumberE$episodeNumber"
```

### 2. Çalıştır

```bash
# Test (dry-run)
archiverr --paths-from tests/targets.txt --type tv --dry-run

# Gerçek rename
archiverr /path/to/series --type tv
```

## 📚 Dokümantasyon

- **[TODO](docs/TODO.md)** - Yapılacaklar listesi
- **[PROJECT](docs/PROJECT.md)** - Proje detayları
- **[YML Engine](README_YML_ENGINE.md)** - Pattern değişkenleri

## 🔧 Değişken Sistemi

Birleşik {var} syntax - hem rename hem query'lerde kullanılır:

```yaml
# TMDb Değişkenleri
{name}                          # Film adı
{movieYear}                     # Yıl
{showName}                      # Dizi adı
{tmdb.genres.1.name}            # Genre (1-based index)

# FFprobe Değişkenleri
{video.codec}                   # h264, hevc, av1
{video.resolution}              # 1080p, 720p
{audio.1.language}              # Ses dili (1-based)
{audioCount}                    # Toplam ses

# Filtreler
{name:upper}                    # BÜYÜK HARF
{showName:slug}                 # url-safe-slug
{tmdb.first_air_date:year}      # Yıl çıkar
{seasonNumber:pad:2}            # 01, 02, ... zero-pad
```

Tam liste için [YML Engine Rehberi](README_YML_ENGINE.md)'ne bakın.

## 🎨 Query Engine

Gelişmiş filtreleme ve organizasyon:

```yaml
query_engine:
  queries:
    # 4K filmleri ayır
    - name: "4K Filmler"
      where: "videoHeight >= 2160"
      save: "/media/Movies-4K/{name} ({movieYear})"
    
    # Kalite bazlı organize
    - name: "Kalite Bazlı"
      loop:
        var: q
        in: [2160, 1080, 720]
      where: "videoHeight == q"
      save: "/media/Movies-{q}p/{name}"
```

## 🛠️ Geliştirme

```bash
# Test çalıştır
pytest tests/

# Kod formatı
black src/
isort src/

# Linting
flake8 src/
mypy src/
```

## 🚧 Gelecek

- FastAPI REST API
- SQLite database + undo/redo
- Svelte web UI
- Query engine

Detaylar: [TODO.md](docs/TODO.md)
