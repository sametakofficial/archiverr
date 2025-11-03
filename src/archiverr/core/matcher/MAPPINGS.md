# Normalized API Mapping — TV & Movies (TMDb, OMDb, TVDb, TVmaze)

Aşağıdaki tablolar **normalized şema** (sağdaki sütun) ile sağlayıcıların döndürdüğü alanların kapsamlı bir eşlemesini içerir.  
TV ve **Movie** için ayrı tablolar verilmiştir. TVmaze film desteklemediği için Movie tablosunda yer almaz.

---

## TV (Series / Season / Episode)

| Normalized Key | Açıklama | TMDb (v3) | OMDb | TVDb v4 | TVmaze |
|---|---|---|---|---|---|
| `ids.tmdb` | TMDb dizi ID | `id` (GET /tv/{id}) | — | — | — |
| `ids.imdb` | IMDb ID | `external_ids.imdb_id` (append) | `imdbID` | `remoteIds`/`aliases` içinden imdb | `externals.imdb` |
| `ids.tvdb` | TVDb ID | `external_ids.tvdb_id` (append) | — | `id` | `externals.thetvdb` |
| `ids.tvmaze` | TVmaze ID | — | — | — | `id` |
| `name` | Yerelleşmiş ad | `name` | `Title` | `name` | `name` |
| `original_name` | Orijinal ad | `original_name` | `Title` | `nativeName` \| `name` | `name` |
| `overview` | Özet | `overview` | `Plot` | `overview` | `summary` (HTML → text) |
| `first_air_date` | İlk yayın | `first_air_date` | `Released` (yaklaşık) | `firstAired` | `premiered` |
| `last_air_date` | Son yayın | `last_air_date` | — | `lastAired` | `ended` |
| `status` | Yayın durumu | `status` | — | `status` | `status` |
| `in_production` | Üretimde mi | `in_production` | — | — | `status == "Running"` |
| `episode_run_time[]` | Tipik bölüm süresi | `episode_run_time[]` | `Runtime` (dakika tekil) | `averageRuntime` | `runtime` |
| `genres[]` | Türler | `genres[].name` | `Genre` (CSV) | `genres[].name` \| `genre` | `genres[]` |
| `spoken_languages[]` | Diller | `spoken_languages[].iso_639_1` | `Language` (CSV) | — | — |
| `original_language` | Orijinal dil | `original_language` | `Language` | `originalLanguage` | — |
| `networks[]` | Yayıncılar | `networks[].name` | — | `networks[].name` | `network.name` / `webChannel.name` |
| `production_companies[]` | Yapımcılar | `production_companies[].name` | `Production` (CSV) | — | — |
| `homepage` | Resmi site | `homepage` | `Website` | `officialWebsite` | `officialSite` \| `url` |
| `poster` | Poster URL | `poster_path` → `https://image.tmdb.org/t/p/w500` | `Poster` | `image` \| `poster` | `image.original` \| `image.medium` |
| `backdrop` | Arka plan | `backdrop_path` → TMDb | — | — | — |
| `images.*` | Görseller | `images.posters/backdrops` (append) | — | `artwork` | show/episode `image` alanları |
| `ratings.tmdb` | TMDb oylama | `vote_average` / `vote_count` | — | — | — |
| `ratings.imdb` | IMDb puanı | — | `imdbRating` | — | — |
| `seasons[]` | Sezon listesi | `seasons[]` | `totalSeasons` (sayı → sentetik) | `seasons[]` | — |
| `credits.cast[]` | Oyuncular | `credits`/`aggregate_credits.cast[]` | `Actors` (CSV) | `/series/{id}/actors` | `/shows/{id}/cast` |
| `credits.crew[]` | Ekip | `credits.crew[]` | `Director`/`Writer` CSV | — | — |
| `external_urls.tmdb` | Detay linki | `https://www.themoviedb.org/tv/{id}` | — | — | `url` |
| `external_urls.imdb` | IMDb linki | `external_ids.imdb_id` | `imdbID` | — | — |

**Season:**  
`/tv/{id}/season/{S}` (TMDb), `/series/{id}/episodes/default?season={S}` (TVDb), OMDb `Season={S}`, TVmaze `/shows/{id}/episodes` filtre.

**Episode:**  
`/tv/{id}/season/{S}/episode/{E}` (TMDb), TVDb `seasons/{seasonId}/extended` içinden `number==E`, OMDb `Episode={E}`, TVmaze `/episodebynumber?season=S&number=E`.

---

## Movies

| Normalized Key | Açıklama | TMDb (v3) | OMDb | TVDb v4 |
|---|---|---|---|---|
| `ids.tmdb` | TMDb film ID | `id` (GET /movie/{id}) | — | — |
| `ids.imdb` | IMDb ID | `external_ids.imdb_id` (append) | `imdbID` | `remoteIds` \| `imdb` alias |
| `ids.tvdb` | TVDb ID | — | — | `id` (GET /movies/{id}) |
| `title` | Yerelleşmiş başlık | `title` | `Title` | `name` |
| `original_title` | Orijinal başlık | `original_title` | `Title` | `name` |
| `overview` | Özet | `overview` | `Plot` | `overview` |
| `release_date` | Vizyon tarihi | `release_date` | `Released` | `firstRelease` \| `releaseDate` |
| `status` | Dağıtım durumu | `status` | — | `status` (varsa) |
| `runtime` | Süre (dk) | `runtime` | `Runtime` (sayıya çevrilir) | `runtime` |
| `genres[]` | Türler | `genres[].name` | `Genre` (CSV) | `genres[].name` |
| `spoken_languages[]` | Konuşulan diller | `spoken_languages[].iso_639_1` | `Language` (CSV) | — |
| `original_language` | Orijinal dil | `original_language` | `Language` (ilk öğe) | `originalLanguage` |
| `production_companies[]` | Yapımcılar | `production_companies[].name` | `Production` (CSV) | — |
| `homepage` | Resmi site | `homepage` | `Website` | `officialWebsite` |
| `poster` | Poster | `poster_path` → TMDb | `Poster` | `image` \| `poster` |
| `backdrop` | Arka plan | `backdrop_path` → TMDb | — | — |
| `images.*` | Görseller | `images.posters/backdrops` (append) | — | `artwork` (varsa) |
| `ratings.tmdb` | TMDb puanı | `vote_average` / `vote_count` | — | — |
| `ratings.imdb` | IMDb puanı | — | `imdbRating` | — |
| `credits.cast[]` | Oyuncular | `credits.cast[]` | `Actors` (CSV) | — |
| `credits.crew[]` | Ekip | `credits.crew[]` | `Director`/`Writer` CSV | — |
| `external_urls.tmdb` | TMDb link | `https://www.themoviedb.org/movie/{id}` | — | — |
| `external_urls.imdb` | IMDb link | `external_ids.imdb_id` | `imdbID` | — |

**Arama Parametreleri (özet):**

- **TMDb**  
  - Film: `/search/movie?query={q}&year={y}&page=1`  
  - TV: `/search/tv?query={q}&first_air_date_year={y}&page=1`  
  - Detaylarda `append_to_response=credits,images,external_ids` kullanılabilir.

- **OMDb**  
  - Film: `?s={q}&type=movie&y={y}` veya tekil: `?t={title}&type=movie&y={y}`  
  - TV: `?s={q}&type=series&y={y}`; tekil bölüm: `?i={imdbSeriesId}&Season={S}&Episode={E}`

- **TVDb v4**  
  - Arama: `/search?query={q}&type=movie|series`  
  - Film detay: `/movies/{id}`  
  - Dizi detay: `/series/{id}/extended`; sezon/bölüm için `seasons/{id}/extended`

> Not: TVmaze film desteklemez.

