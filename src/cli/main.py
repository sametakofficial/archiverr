# cli.py
import argparse
import os
import sys
from pathlib import Path

from models.config import load_config_with_fallback
from integrations.tmdb.client import TMDbClient
from integrations.tvmaze.client import TVMazeClient
from integrations.tvdb.client import TVDbClient
from integrations.omdb.client import OMDbClient
from core.scanner.scanner import collect_inputs
from core.renamer.engine import rename_files
from core.matcher.api_manager import APIManager

def log(msg: str):
    """Simple logging helper."""
    print(msg)

def strip_outer_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def parse_args():
    p = argparse.ArgumentParser(description='Archiverr (Python).')
    # Kullanıcı çoğu zaman 1 veya daha fazla path geçecek; bazen tırnakları unugittabilir.
    p.add_argument('paths', nargs='*', help='File/dir paths. You can also pass a single .txt manifest.')
    p.add_argument('--path', dest='single_path', help='Single file/dir path (alternative to positional)')
    p.add_argument('--paths-from', help='Read newline-separated paths from a text file (manifest).')
    p.add_argument('--type', choices=['movie', 'tv'], default='movie', help='Media type to treat inputs as')
    p.add_argument('--recursive', action='store_true', help='Scan subdirectories (when inputs are directories)')
    p.add_argument('--dry-run', action='store_true', help='Force dry-run (do not rename)')
    
    # Config overrides
    p.add_argument('--debug', action='store_true', help='Enable debug mode')
    p.add_argument('--allow-virtual-paths', action='store_true', help='Allow non-existent paths (virtual mode)')
    p.add_argument('--hardlink', action='store_true', help='Use hardlinks instead of move')
    p.add_argument('--nfo-enable', action='store_true', help='Enable NFO writing')
    p.add_argument('--nfo-force', action='store_true', help='Force overwrite existing NFO')
    
    # External config files
    p.add_argument('--movie-print', help='External YAML file for movie print template')
    p.add_argument('--series-print', help='External YAML file for series print template')
    p.add_argument('--summary-print', help='External YAML file for summary template')
    p.add_argument('--queries', help='External YAML file with queries')
    
    return p.parse_args()

def deduce_input_list(args) -> list[str]:
    """
    Aşağıdaki kaynaklardan bir birleşik giriş listesi üretir:
      - --path (tek dosya)
      - --paths-from manifest.txt (varsa)
      - tek .txt argümanı (manifest olarak)
      - normal yollar (boşluklarla bölünmüşse birleştirerek dene)
    """
    inputs: list[str] = []

    # 0) --path (single file)
    if hasattr(args, 'single_path') and args.single_path:
        inputs.append(strip_outer_quotes(args.single_path))
        return inputs

    # 1) --paths-from
    if args.paths_from:
        m = Path(strip_outer_quotes(args.paths_from)).expanduser()
        if not m.exists():
            log(f"[warn] --paths-from manifest not found: {m}")
        else:
            with m.open('r', encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    line = strip_outer_quotes(line.strip())
                    if not line or line.startswith('#'):
                        continue
                    inputs.append(os.path.expanduser(line))

    # 2) positional 'paths'
    # Eğer tek bir argüman var ve .txt ile bitiyorsa, manifest olarak oku
    if len(args.paths) == 1 and str(args.paths[0]).lower().endswith('.txt') and not args.paths_from:
        m = Path(strip_outer_quotes(args.paths[0])).expanduser()
        if m.exists():
            with m.open('r', encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    line = strip_outer_quotes(line.strip())
                    if not line or line.startswith('#'):
                        continue
                    inputs.append(os.path.expanduser(line))
        else:
            # yoksa normal path gibi davran
            inputs.append(os.path.expanduser(strip_outer_quotes(args.paths[0])))
    elif len(args.paths) > 0:
        # Boşluk yüzünden parçalanmış olabilir: bütününü birleştirip deneriz.
        tokens_joined = strip_outer_quotes(" ".join(args.paths))
        if os.path.exists(tokens_joined):
            inputs.append(os.path.expanduser(tokens_joined))
        else:
            # Tek tek ekle (kullanıcı birden çok yol vermiş olabilir)
            for t in args.paths:
                inputs.append(os.path.expanduser(strip_outer_quotes(t)))

    # Tekrarlı/boşları temizle
    normed = []
    seen = set()
    for p in inputs:
        p = p.strip()
        if not p:
            continue
        if p not in seen:
            seen.add(p)
            normed.append(p)

    return normed

def run_cli():
    args = parse_args()

    # Load config from config.yml (with .env fallback for backward compatibility)
    cfg = load_config_with_fallback("config.yml")
    
    # CLI args override config file settings
    if args.dry_run:
        cfg.options.dry_run = True
    cfg.scanner.recursive = args.recursive
    
    # Apply CLI overrides
    if args.debug:
        cfg.options.debug = True
    if args.allow_virtual_paths:
        cfg.options.allow_virtual_paths = True
    if args.hardlink:
        cfg.options.hardlink = True
    if args.nfo_enable:
        cfg.options.nfo_enable = True
    if args.nfo_force:
        cfg.options.nfo_force = True
    
    # Load external YAML templates
    if args.movie_print:
        cfg.rename.movies = cfg.rename.movies or {}
        with open(args.movie_print, 'r') as f:
            import yaml
            template = yaml.safe_load(f)
            if template:
                cfg.rename.movies['print'] = template.get('print', '')
    
    if args.series_print:
        cfg.rename.series = cfg.rename.series or {}
        with open(args.series_print, 'r') as f:
            import yaml
            template = yaml.safe_load(f)
            if template:
                cfg.rename.series['print'] = template.get('print', '')
    
    if args.summary_print:
        with open(args.summary_print, 'r') as f:
            import yaml
            template = yaml.safe_load(f)
            if template:
                cfg.summary.print = template.get('print', '')
    
    if args.queries:
        with open(args.queries, 'r') as f:
            import yaml
            queries = yaml.safe_load(f)
            if queries and isinstance(queries, list):
                cfg.query_engine.queries = queries

    raw_inputs = deduce_input_list(args)
    if not raw_inputs:
        log("[error] No input paths given. Provide paths or use --paths-from manifest.txt")
        sys.exit(2)

    # Her girdi için dosya listelerini topla
    # Virtual paths kontrolü:
    # - allow_virtual_paths=true  → Dosya varlık kontrolünü atla (manual extras fetch için)
    # - allow_virtual_paths=false → Sadece var olan dosyaları işle
    allow_virtual = cfg.options.allow_virtual_paths if hasattr(cfg.options, 'allow_virtual_paths') else False
    
    # Debug: show virtual path setting
    if cfg.options.debug:
        print(f"[DEBUG] allow_virtual_paths: {allow_virtual}", file=sys.stderr)
    
    skip_check = allow_virtual
    paths = collect_inputs(raw_inputs, recursive=cfg.scanner.recursive, skip_existence_check=skip_check)
    
    # Debug: show collected paths
    if cfg.options.debug and not paths:
        print(f"[DEBUG] No paths collected. skip_check={skip_check}, raw_inputs={raw_inputs[:3] if raw_inputs else []}", file=sys.stderr)
    if not paths:
        print("No media files found for given inputs.")
        print(f"Checked {len(raw_inputs)} input paths")
        if raw_inputs:
            print(f"First input: {raw_inputs[0]}")
        return

    # Initialize API Manager with all configured APIs
    api_manager = APIManager(cfg)
    
    # Register TMDb (always available)
    if cfg.tmdb.api_key:
        # Pass global extras config to client
        extras_config = cfg.extras if hasattr(cfg, 'extras') else {}
        tmdb_client = TMDbClient(
            api_key=cfg.tmdb.api_key,
            region=cfg.tmdb.region,
            extras_config=extras_config
        )
        api_manager.register_client("tmdb", tmdb_client)
    
    # Register TVMaze (no API key needed, public API)
    extras_config = cfg.extras if hasattr(cfg, 'extras') else {}
    tvmaze_client = TVMazeClient(extras_config=extras_config)
    api_manager.register_client("tvmaze", tvmaze_client)
    
    # Register TVDb (JWT based auth)
    if cfg.tvdb.api_key:
        # Pass global extras config to client
        extras_config = cfg.extras if hasattr(cfg, 'extras') else {}
        tvdb_client = TVDbClient(
            api_key=cfg.tvdb.api_key,
            extras_config=extras_config
        )
        api_manager.register_client("tvdb", tvdb_client)
    
    # Register OMDb (simple REST API)
    if cfg.omdb.api_key:
        omdb_client = OMDbClient(cfg.omdb.api_key)
        api_manager.register_client("omdb", omdb_client)
    
    rename_files(paths, args.type, cfg, api_manager)

if __name__ == "__main__":
    run_cli()
