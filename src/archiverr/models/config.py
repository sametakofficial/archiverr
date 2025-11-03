# config.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os

try:
    import yaml  # type: ignore
except Exception:
    yaml = None
import json

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

@dataclass
class ScannerConfig:
    recursive: bool = True
    exclude_unparsed: bool = False
    delete_keywords: List[str] = field(default_factory=list)

@dataclass
class PathsConfig:
    movies_src: str = ""
    movies_dst: str = ""
    series_src: str = ""
    series_dst: str = ""

@dataclass
class PatternsConfig:
    movie: str = ""
    series: str = ""

@dataclass
class TMDbConfig:
    api_key: Optional[str] = None
    lang: str = "tr-TR"
    fallback_lang: str = "en-US"
    region: str = "TR"
    movie_primary: bool = False
    tv_primary: bool = False
    movie_priority: int = 1
    tv_priority: int = 1

@dataclass
class TVDbConfig:
    api_key: Optional[str] = None
    lang: str = "en"
    fallback_lang: str = "en"
    region: str = "US"
    movie_primary: bool = False
    tv_primary: bool = False
    movie_priority: int = 2
    tv_priority: int = 2

@dataclass
class TVMazeConfig:
    api_key: Optional[str] = None  # Not used but kept for consistency
    lang: str = "en"
    fallback_lang: str = "en"
    region: str = "US"
    movie_primary: bool = False
    tv_primary: bool = False
    movie_priority: int = 3
    tv_priority: int = 1

@dataclass
class OMDbConfig:
    api_key: Optional[str] = None
    lang: str = "en"
    fallback_lang: str = "en"
    region: str = "US"
    movie_primary: bool = False
    tv_primary: bool = False
    movie_priority: int = 3
    tv_priority: int = 3

@dataclass
class NFOCacheConfig:
    # ffprobe JSON cache: <stem>-ffmpeg.nfo
    enable: bool = True

@dataclass
class OptionsConfig:
    dry_run: bool = True
    debug: bool = False
    hardlink: bool = False
    nfo_enable: bool = True
    nfo_force: bool = False
    dry_run_save_nfo: bool = False
    ffprobe_enable: bool = True  # FFprobe master switch
    ffprobe_nfo_enable: bool = True  # FFprobe cache (.nfo) yazma/okuma
    ffprobe_force: bool = False  # Cache'i görmezden gelip zorla ffprobe çalıştır
    dry_run_save_ffprobe: bool = False
    allow_virtual_paths: bool = False  # Virtual path mode (dosya yoksa bile çalışır)

@dataclass
class RenameQueryConfig:
    """Query-based rename configuration"""
    print: str = ""  # Log formatı (örn: "{name} ({movieYear})")
    save: str = ""   # Dosya yolu pattern'i (örn: "$name ($movieYear)/...")
    where: str = ""  # Opsiyonel filtre
    loop: Optional[Dict[str, Any]] = None  # Opsiyonel loop

@dataclass
class RenameConfig:
    # Legacy support için src/dst paths
    movies_src: str = ""
    movies_dst: str = ""
    series_src: str = ""
    series_dst: str = ""
    
    # Query-based config (yeni sistem)
    movies: Optional[Dict[str, Any]] = None  # Query config dict
    series: Optional[Dict[str, Any]] = None  # Query config dict
    
    # Legacy patterns (backward compatibility)
    movie_pattern: str = ""
    series_pattern: str = ""

@dataclass
class QueryGlobals:
    allVideoQualities: Any = "auto"  # "auto" ya da [2160,1080,...]

@dataclass
class QueryConfig:
    globals: Dict[str, Any] = field(default_factory=dict)
    queries: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class SummaryConfig:
    print: str = ""  # Summary print template

@dataclass
class AppConfig:
    """Ana config modeli."""
    scanner: ScannerConfig
    tmdb: TMDbConfig
    tvdb: TVDbConfig
    tvmaze: TVMazeConfig
    omdb: OMDbConfig
    options: OptionsConfig
    rename: RenameConfig
    summary: SummaryConfig
    query_engine: QueryConfig
    tv_priority: List[str] = field(default_factory=list)  # Yeni liste-tabanlı priority
    movie_priority: List[str] = field(default_factory=list)  # ["tmdb", "tvdb", ...]
    extras: Dict[str, bool] = field(default_factory=dict)  # Global extras config

def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def load_config(path: str) -> AppConfig:
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"HATA: config.yml bulunamadı: {p}")
    text = _load_text(p)
    data: Dict[str, Any]
    if yaml:
        data = yaml.safe_load(text) or {}
    else:
        try:
            data = json.loads(text)
        except Exception as e:
            raise SystemExit(f"Konfig YAML/JSON parse hatası: {e}")

    # Build all config objects first
    # TMDb
    tm = data.get("tmdb") or {}
    tmdb_config = TMDbConfig(
        api_key=tm.get("api_key"),
        lang=str(tm.get("lang", "tr-TR")),
        fallback_lang=str(tm.get("fallback_lang", "en-US")),
        region=str(tm.get("region", "TR")),
        movie_primary=bool(tm.get("movie_primary", False)),
        tv_primary=bool(tm.get("tv_primary", False)),
        movie_priority=int(tm.get("movie_priority", 1)),
        tv_priority=int(tm.get("tv_priority", 1)),
    )
    
    # TVDb
    tvdb = data.get("tvdb") or {}
    tvdb_config = TVDbConfig(
        api_key=tvdb.get("api_key"),
        lang=str(tvdb.get("lang", "en")),
        fallback_lang=str(tvdb.get("fallback_lang", "en")),
        region=str(tvdb.get("region", "US")),
        movie_primary=bool(tvdb.get("movie_primary", False)),
        tv_primary=bool(tvdb.get("tv_primary", False)),
        movie_priority=int(tvdb.get("movie_priority", 2)),
        tv_priority=int(tvdb.get("tv_priority", 2)),
    )
    
    # TVMaze
    tvmaze = data.get("tvmaze") or {}
    # movie_priority false means don't use for movies at all
    movie_pri = tvmaze.get("movie_priority", 999)
    if movie_pri is False or movie_pri == "false":
        movie_pri = 999  # Very high = never used
    tvmaze_config = TVMazeConfig(
        api_key=tvmaze.get("api_key"),
        lang=str(tvmaze.get("lang", "en")),
        fallback_lang=str(tvmaze.get("fallback_lang", "en")),
        region=str(tvmaze.get("region", "US")),
        movie_primary=bool(tvmaze.get("movie_primary", False)),
        tv_primary=bool(tvmaze.get("tv_primary", False)),
        movie_priority=int(movie_pri),
        tv_priority=int(tvmaze.get("tv_priority", 1)),
    )
    
    # OMDb
    omdb = data.get("omdb") or {}
    omdb_config = OMDbConfig(
        api_key=omdb.get("api_key"),
        lang=str(omdb.get("lang", "en")),
        fallback_lang=str(omdb.get("fallback_lang", "en")),
        region=str(omdb.get("region", "US")),
        movie_primary=bool(omdb.get("movie_primary", False)),
        tv_primary=bool(omdb.get("tv_primary", False)),
        movie_priority=int(omdb.get("movie_priority", 3)),
        tv_priority=int(omdb.get("tv_priority", 3)),
    )
    
    # Options
    opt = data.get("options") or {}
    options_config = OptionsConfig(
        dry_run=bool(opt.get("dry_run", True)),
        debug=bool(opt.get("debug", False)),
        hardlink=bool(opt.get("hardlink", False)),
        nfo_enable=bool(opt.get("nfo_enable", True)),
        nfo_force=bool(opt.get("nfo_force", False)),
        dry_run_save_nfo=bool(opt.get("dry_run_save_nfo", False)),
        ffprobe_enable=bool(opt.get("ffprobe_enable", True)),
        ffprobe_nfo_enable=bool(opt.get("ffprobe_nfo_enable", True)),
        ffprobe_force=bool(opt.get("ffprobe_force", False)),
        dry_run_save_ffprobe=bool(opt.get("dry_run_save_ffprobe", False)),
        allow_virtual_paths=bool(opt.get("allow_virtual_paths", False)),
    )
    
    # Scanner
    s = data.get("scanner") or {}
    scanner_config = ScannerConfig(
        recursive=bool(s.get("recursive", True)),
        exclude_unparsed=bool(s.get("exclude_unparsed", False)),
        delete_keywords=list(s.get("delete_keywords", [])),
    )
    
    # Rename
    rn = data.get("rename") or {}
    rename_config = RenameConfig(
        movies_src=str(rn.get("movies_src", "")),
        movies_dst=str(rn.get("movies_dst", "")),
        series_src=str(rn.get("series_src", "")),
        series_dst=str(rn.get("series_dst", "")),
        
        # Query-based config (yeni)
        movies=rn.get("movies"),
        series=rn.get("series"),
        
        # Legacy patterns
        movie_pattern=str(rn.get("movie_pattern", "")),
        series_pattern=str(rn.get("series_pattern", "")),
    )
    
    # Summary
    summary = data.get("summary") or {}
    summary_config = SummaryConfig(
        print=str(summary.get("print", ""))
    )
    
    # Query Engine
    qe = data.get("query_engine") or {}
    query_engine_config = QueryConfig(
        globals=qe.get("globals", {}) or {},
        queries=qe.get("queries", []) or {},
    )
    
    # Priority lists (yeni format)
    tv_priority_list = data.get("tv_priority", [])
    movie_priority_list = data.get("movie_priority", [])
    
    # Liste formatından priority değerlerine çevir
    if tv_priority_list and isinstance(tv_priority_list, list):
        tv_priority = tv_priority_list
    else:
        tv_priority = []
    
    if movie_priority_list and isinstance(movie_priority_list, list):
        movie_priority = movie_priority_list
    else:
        movie_priority = []
    
    # Extras (global config)
    extras_dict = data.get("extras", {}) or {}
    
    # Create AppConfig with all components
    cfg = AppConfig(
        scanner=scanner_config,
        tmdb=tmdb_config,
        tvdb=tvdb_config,
        tvmaze=tvmaze_config,
        omdb=omdb_config,
        options=options_config,
        rename=rename_config,
        summary=summary_config,
        query_engine=query_engine_config,
        tv_priority=tv_priority,
        movie_priority=movie_priority,
        extras=extras_dict
    )
    
    return cfg

def _load_env_fallback() -> Dict[str, Any]:
    """Load configuration from .env file as fallback."""
    if load_dotenv:
        load_dotenv()
    
    # Map .env variables to config structure
    env_data: Dict[str, Any] = {}
    
    # TMDb config from .env
    env_data["tmdb"] = {
        "api_key": os.getenv("TMDB_API_KEY"),
        "lang": os.getenv("TMDB_LANG", "tr-TR"),
        "fallback_lang": os.getenv("TMDB_FALLBACK_LANG", "en-US"),
        "region": os.getenv("TMDB_REGION", "TR"),
    }
    
    # Options from .env
    dry_run_str = os.getenv("DRY_RUN", "true").lower()
    dry_run = dry_run_str in ("1", "true", "yes")
    
    hardlink_str = os.getenv("HARDLINK", "false").lower()
    hardlink = hardlink_str in ("1", "true", "yes")
    
    nfo_enable_str = os.getenv("NFO_ENABLE", "true").lower()
    nfo_enable = nfo_enable_str in ("1", "true", "yes")
    
    nfo_force_str = os.getenv("NFO_FORCE", "false").lower()
    nfo_force = nfo_force_str in ("1", "true", "yes")
    
    env_data["options"] = {
        "dry_run": dry_run,
        "hardlink": hardlink,
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "parallel": int(os.getenv("PARALLEL", "8")),
        "nfo_enable": nfo_enable,
        "nfo_force": nfo_force,
        "ffprobe_enable": os.getenv("FFPROBE_ENABLE", "true").lower() in ("1", "true", "yes"),
        "ffprobe_nfo_enable": os.getenv("FFPROBE_NFO_ENABLE", "true").lower() in ("1", "true", "yes"),
        "ffprobe_force": os.getenv("FFPROBE_FORCE", "false").lower() in ("1", "true", "yes"),
    }
    
    # Rename from .env
    env_data["rename"] = {
        "movie_pattern": os.getenv("MOVIE_PATTERN", ""),
        "series_pattern": os.getenv("SERIES_PATTERN", ""),
    }
    
    return env_data

def _merge_configs(yaml_data: Dict[str, Any], env_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge YAML and .env data, with YAML taking precedence."""
    merged = env_data.copy()
    
    for key, value in yaml_data.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(value, dict) and isinstance(merged[key], dict):
            # Deep merge for nested dicts
            merged[key] = {**merged[key], **value}
        else:
            # YAML overrides .env
            merged[key] = value
    
    return merged

def load_config_with_fallback(config_path: str = "config.yml") -> AppConfig:
    """
    Load configuration from YAML with .env fallback for backward compatibility.
    
    Priority order:
    1. config.yml (if exists)
    2. .env (fallback)
    3. Defaults from dataclass fields
    
    Args:
        config_path: Path to YAML config file (default: config.yml)
    
    Returns:
        AppConfig instance
    """
    p = Path(config_path)
    yaml_data: Dict[str, Any] = {}
    
    # Try to load YAML first
    if p.is_file():
        try:
            text = _load_text(p)
            if yaml:
                yaml_data = yaml.safe_load(text) or {}
            else:
                try:
                    yaml_data = json.loads(text)
                except Exception:
                    pass
        except Exception as e:
            print(f"[warn] Failed to load {config_path}: {e}")
    
    # Load .env fallback
    env_data = _load_env_fallback()
    
    # Merge: YAML takes precedence over .env
    data = _merge_configs(yaml_data, env_data)
    
    # Build AppConfig using load_config logic
    # Just call load_config since we already have merged data
    return load_config(config_path)
