# YML Engine - Gelişmiş Değişken Sistemi

## 🎯 Özet

**YML Engine** archiverr'a yüzlerce değişken ile pattern rendering ve query execution gücü kazandırır.

### Yenilikler

✅ **Yüzlerce Değişken** - TMDb + FFprobe + Global + Derived  
✅ **Gelişmiş Filtreler** - `:lower`, `:upper`, `:slug`, `:year`, `:pad:N`, `:trim`, vb.  
✅ **Query Engine** - `where`/`print`/`save` ile gelişmiş filtreleme  
✅ **Loop Support** - Kalite/codec bazlı toplu işlem  
✅ **FFprobe Cache** - `*-ffmpeg.nfo` dosya cache sistemi  
✅ **config.yml** - .env artık kullanılmıyor, tüm yapılandırma YAML'da  

---

## 📂 Dosya Yapısı

```
archiverr/
├── engine/                      # YML Engine modülleri
│   ├── __init__.py
│   ├── engine.py               # Ana orchestrator
│   ├── variables.py            # TMDb + FFprobe + Global değişkenler
│   ├── pattern.py              # Pattern rendering ($var syntax)
│   ├── query.py                # Query execution (where/print/save)
│   └── filters.py              # Değişken filtreleri
│
├── query_templates/             # Örnek query YAML'ları
│   ├── 2010_sonrasi_filmler.yml
│   ├── 8bit_10bit_ayir.yml
│   ├── turkce_filmler.yml
│   ├── kalite_bazli_organize.yml
│   └── sadece_rapor.yml
│
├── config.yml                   # Ana yapılandırma (.env yerine)
└── README_YML_ENGINE.md        # Bu dosya
```

---

## 🔧 Kullanım

### 1. config.yml Yapılandırması

```yaml
tmdb:
  api_key: "YOUR_API_KEY"
  lang: "tr-TR"

options:
  dry_run: true              # false -> gerçek taşıma
  hardlink: false            # true -> hardlink oluştur
  nfo_enable: true           # ffprobe cache yaz

rename:
  movies_dst: "/media/Movies"
  series_dst: "/media/Series"
  
  # Pattern'lerde yüzlerce değişken kullanılabilir
  movie_pattern: >
    $name ($movieYear)/$name ($movieYear) [$video.resolution][$video.codec][$audio.1.language:upper]
  
  series_pattern: >
    $showName ($tmdb.first_air_date:year)/Season $seasonNumber/$showName - S$seasonNumberE$episodeNumber

query_engine:
  globals:
    allVideoQualities: [2160, 1080, 720]
    cutYear: 2010
  
  queries:
    - name: "8-bit Videolar"
      where: "videoBitDepth == 8"
      print: "8-bit: {count} dosya | {sizeH}"
      save: "/archive/8bit/{q}p/"
```

### 2. Değişken Kullanımı

#### Pattern'lerde ($var syntax)

```yaml
# Basit
movie_pattern: "$name ($movieYear)"

# Nested + Filter
movie_pattern: "$tmdb.title:upper - [$video.codec]"

# 1-based index
movie_pattern: "$name [$audio.1.language] [$audio.2.language]"

# Çoklu filtre
movie_pattern: "$showName:slug-$tmdb.first_air_date:year"
```

#### Query'lerde (degiskenAdi - dolar yok)

```yaml
queries:
  - name: "4K HDR Filmler"
    where: "videoHeight >= 2160 and videoHdrFormat"
    print: "4K HDR: {count} dosya"
```

---

## 📊 Değişken Kategorileri

### 🎬 TMDb Değişkenleri

```yaml
# Film
$name                          # title / original_title
$movieYear                     # release_date:year
$tmdb.title                    # Orijinal başlık
$tmdb.genres.1.name            # İlk genre
$tmdb.production_companies.1.name
$tmdb.vote_average             # IMDb puanı
$tmdb.runtime                  # Dakika

# Dizi
$showName                      # name / original_name
$seasonNumber                  # 01, 02, ...
$episodeNumber                 # 01, 02, ...
$episodeName                   # Bölüm adı
$tmdb.first_air_date:year      # İlk yayın yılı
$tmdb.networks.1.name          # Netflix, HBO, vb.
$tmdb.episode.name             # Bölüm detayı
```

### 🎞️ FFprobe Değişkenleri

```yaml
# Video
$video.codec                   # h264, hevc, av1
$video.resolution              # 2160p, 1080p, 720p
$video.width                   # 1920
$video.height                  # 1080
$video.bitRate                 # bps
$video.fps                     # "24000/1001"
$video.fpsFloat                # 23.976
$video.hdrFormat               # HDR10, DolbyVision, HLG
$video.bitDepth                # 8, 10, 12
$videoBitDepth                 # Alias (query'lerde kullan)

# Audio
$audioCount                    # Toplam ses tracki
$audio.1.codec                 # aac, dts, truehd
$audio.1.language              # tur, eng
$audio.1.channels              # 6
$audio.1.layout                # 5.1, stereo
$audioDefaultIndex             # Varsayılan track (1-based)

# Subtitle
$subtitleCount                 # Toplam altyazı
$subtitle.1.language           # tur, eng
$subtitle.1.forced             # true/false

# Konteyner
$container.format              # matroska,webm
$sizeInt                       # Bayt
$sizeH                         # "1.5 GiB"
$sizeGiB                       # 1.5 (float)
$durationSec                   # 7200.5
$durationH                     # "02:00:00"
$totalBitrateBps               # Toplam bitrate
```

### 🌍 Global & Derived Değişkenler

```yaml
# Path/File
$path                          # Tam dosya yolu
$dir                           # Klasör
$fileName                      # dosya.mkv
$stem                          # dosya (uzantısız)
$ext                           # .mkv

# Date/Time
$nowIso                        # 2025-10-30T16:30:00
$nowDate                       # 30-10-2025
$todayYear                     # 2025
$epochSec                      # Unix timestamp

# User-defined (config.yml → query_engine.globals)
$globals.cutYear               # 2010
$globals.allVideoQualities.1   # 2160

# Derived Buckets
$sizeBucket                    # "0-1 GiB", "1-5 GiB", ">10 GiB"
$bitrateBucket                 # "<2", "2-5", "5-10", ">10"
$yearBucket                    # "<=2000", "2001-2010", ">=2021"
$video.fpsBucket               # "<=24", "25-30", ">30"
```

---

## 🎨 Filtreler

```yaml
:lower       # küçük harf
:upper       # BÜYÜK HARF
:slug        # url-safe-slug
:year        # YYYY-MM-DD → YYYY
:trim        # Boşlukları temizle
:title       # Title Case
:snake       # snake_case
:camel       # camelCase
:pad:3       # 001, 002, ...
:max:10      # İlk 10 karakter
:replace:old:new   # String replace
```

### Örnekler

```yaml
$tmdb.title:upper                    # THE MATRIX
$showName:slug                       # breaking-bad
$seasonNumber:pad:2                  # 01, 02
$tmdb.overview:max:100               # İlk 100 karakter
$name:replace: :-                    # Boşlukları tire yap
```

---

## 🔍 Query Engine

### Basit Query

```yaml
queries:
  - name: "2010+ Filmler"
    where: "movieYear >= 2010"
    print: "Toplam: {count} dosya | {sizeH}"
```

### Loop Query (Kalite Bazlı)

```yaml
queries:
  - name: "Kalite Bazlı Organizasyon"
    loop:
      var: q
      in: [2160, 1080, 720, 480]
    where: "videoHeight == q"
    print: "{q}p: {count} dosya | {sizeH}"
    save: "/media/Movies-{q}p/$name ($movieYear)"
```

### Çoklu Koşul

```yaml
queries:
  - name: "8-bit + Tek Ses"
    where: "videoBitDepth == 8 and audioCount == 1"
    print: "8-bit Tek Ses: {count}"
```

### Print Değişkenleri ({var})

```yaml
{count}              # Eşleşen dosya sayısı
{sizeBytes}          # Toplam bayt
{sizeH}              # Toplam okunur boyut
{durationSec}        # Toplam süre (saniye)
{durationH}          # Toplam süre (HH:MM:SS)

# İstatistik
{minSizeBytes}       # En küçük dosya
{maxSizeBytes}       # En büyük dosya
{avgSizeBytes}       # Ortalama dosya boyutu
{minYear}            # En eski yıl
{maxYear}            # En yeni yıl

# Loop
{q}                  # Loop değişkeni
{yearBucket}         # Loop değişkeni

# Diğer
{samplePath}         # İlk eşleşen dosya
```

---

## 📋 Query Template Örnekleri

### 1. Sadece Rapor (Save Yok)

```yaml
# query_templates/sadece_rapor.yml

- name: "Koleksiyon İstatistikleri"
  where: "videoCodec"
  print: |
    Toplam: {count} dosya
    Boyut: {sizeH}
    Süre: {durationH}
```

### 2. 8-bit / 10-bit Ayırma

```yaml
# query_templates/8bit_10bit_ayir.yml

- name: "8-bit Videolar"
  where: "videoBitDepth == 8"
  save: "/archive/8bit/$name ($movieYear)"

- name: "10-bit Videolar"
  where: "videoBitDepth == 10"
  save: "/archive/10bit/$name ($movieYear)"
```

### 3. Kalite Bazlı Organizasyon

```yaml
# query_templates/kalite_bazli_organize.yml

name: "Kalite Bazlı"
loop:
  var: q
  in: [2160, 1080, 720]
where: "videoHeight == q"
save: "/media/Movies-{q}p/$name ($movieYear)"
```

### 4. Türkçe Filmler

```yaml
# query_templates/turkce_filmler.yml

- name: "Türkçe Sesli"
  where: "tmdb.original_language == 'tr'"
  save: "/media/Movies-Turkish/$name ($movieYear)"
```

---

## 🚀 CLI Kullanımı

### Basit Rename

```bash
python cli.py /path/to/movies --type movie
```

### Query Engine Çalıştırma

```bash
# TODO: Query CLI entegrasyonu eklenecek
python -m engine.query --config config.yml --nfo-scan /media/Movies
```

### Python API Kullanımı

```python
from engine import YMLEngine
from config import load_config_with_fallback

# Config yükle
cfg = load_config_with_fallback("config.yml")

# Engine oluştur
engine = YMLEngine(cfg)

# Pattern render
filename = engine.render_filename(
    file_path="/input/movie.mkv",
    tmdb_data={...},
    ffprobe_data={...},
    media_type="movie"
)

# NFO cache kaydet
engine.save_context_to_nfo(
    file_path="/input/movie.mkv",
    tmdb_data={...},
    ffprobe_data={...}
)
# → /input/movie-ffmpeg.nfo

# Query çalıştır
results = engine.execute_queries(
    nfo_files=["/media/Movies/**/*-ffmpeg.nfo"],
    dry_run=True
)
```

---

## 📝 FFprobe Cache Sistemi

### Nasıl Çalışır?

1. Dosya işlendiğinde → `dosyaadi-ffmpeg.nfo` oluşturulur
2. NFO içinde: ffprobe JSON + TMDb JSON + parsed bilgiler
3. Query engine bu NFO'ları okur ve filtreler

### NFO Formatı

```json
{
  "file_path": "/media/Movies/Matrix.mkv",
  "media_type": "movie",
  "tmdb": { ... },
  "ffprobe": { ... },
  "parsed": {
    "title": "Matrix",
    "year": 1999
  }
}
```

### Avantajlar

✅ FFprobe tekrar çağrılmaz (hızlı)  
✅ TMDb API quota korunur  
✅ Offline query çalıştırılabilir  
✅ İleride veritabanına migrasyon kolay  

---

## 🎯 Gelecek Özellikler

- [ ] CLI'da query komutları
- [ ] Web UI'da query editor
- [ ] Database migration (SQLite/Postgres)
- [ ] Undo/redo için cache
- [ ] Custom filtre desteği
- [ ] Transcript-based matching

---

## 📚 Daha Fazla Bilgi

- **Memory Bank**: `/memory/11_YAML_SPEC_SEEDS.md` - Tam değişken referansı
- **Query Templates**: `/query_templates/` - Daha fazla örnek
- **Config**: `config.yml` - Yapılandırma örnekleri

---

**YML Engine ile sınırsız organizasyon gücü! 🚀**
