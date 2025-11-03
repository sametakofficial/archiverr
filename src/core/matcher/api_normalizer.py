# api_normalizer.py
from __future__ import annotations
from typing import Any, Dict, Mapping, Literal

Entity = Literal["tv","season","episode","movie","media"]

ALLOWED_KEYS: Dict[Entity, set] = {
    "tv": {
        "entity","ids","name","original_name","overview",
        "first_air_date","last_air_date","status","in_production",
        "episode_run_time","genres","spoken_languages","original_language",
        "networks","production_companies","homepage",
        "poster","backdrop","images","ratings","seasons",
        "external_urls","credits","extras"
    },
    "season": {
        "entity","ids","season_number","overview","air_date","poster",
        "episodes","images","credits","external_urls","extras"
    },
    "episode": {
        "entity","ids","season_number","episode_number","name","overview",
        "air_date","runtime","still","images","credits","ratings",
        "external_urls","extras"
    },
    "movie": {
        "entity","ids","title","original_title","overview",
        "release_date","status","runtime","genres",
        "spoken_languages","original_language","production_companies",
        "homepage","poster","backdrop","images","ratings",
        "external_urls","credits","extras"
    },
    "media": {
        "entity","ids","container","video","audio","subtitles","extras"
    }
}

def _is_empty(x: Any) -> bool:
    return (isinstance(x, (list,dict,set,tuple)) and len(x)==0)

def _clean(value: Any):
    if isinstance(value, dict):
        out = {k:_clean(v) for k,v in value.items() if v is not None}
        return {k:v for k,v in out.items() if not _is_empty(v)}
    if isinstance(value, list):
        out = [_clean(v) for v in value if v is not None]
        return [v for v in out if not _is_empty(v)]
    return value

def normalize(entity: Entity, payload: Mapping[str, Any]) -> Dict[str, Any]:
    if entity not in ALLOWED_KEYS:
        raise ValueError(f"Unknown entity {entity}")
    allowed = ALLOWED_KEYS[entity]
    base: Dict[str, Any] = {"entity": entity}
    for k, v in dict(payload).items():
        if k in allowed:
            base[k] = v
    if "ids" in base and not isinstance(base["ids"], dict):
        raise ValueError("ids must be an object")
    return _clean(base)

def make_tv(**kwargs) -> Dict[str, Any]: return normalize("tv", kwargs)
def make_season(**kwargs) -> Dict[str, Any]: return normalize("season", kwargs)
def make_episode(**kwargs) -> Dict[str, Any]: return normalize("episode", kwargs)
def make_movie(**kwargs) -> Dict[str, Any]: return normalize("movie", kwargs)
def make_media(**kwargs) -> Dict[str, Any]: return normalize("media", kwargs)
