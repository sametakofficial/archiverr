# TV & Movie API Normalizer (per-client mapping)

- Ortak modül: `api_normalizer.py` → `make_tv`, `make_season`, `make_episode`, `make_movie`
- Client'lar **kendi içinde** mapping yapar; normalize edilmiş dict döner.
- Film desteği: **TMDb**, **OMDb**, **TVDb** (TVmaze hariç).

Dizin:
```
integrations/
  omdb/client.py
  tmdb/client.py
  tvdb/client.py
  tvmaze/client.py  # TV only
api_normalizer.py
MAPPINGS.md
requirements.txt
```
