# core/renamer/engine.py
"""Ana renamer engine - tüm parçaları orchestrate eder."""
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from .logger import log_json, log_info, log_error, colored
from .query_logger import build_print_context, render_query_print, print_query_log
from .operations import unique_path, move_file, hardlink_file
from utils.structured_logger import init_logger, get_logger
from .path_builder import (
    build_movie_path, build_tv_path, tmdb_link,
    pattern_needs_ffprobe, pattern_needs_episode_details
)


def rename_files(paths: List[str], media_type: str, config, client):
    """
    Dosyaları rename et - ana orchestrator.
    
    Args:
        paths: Dosya yolları listesi
        media_type: "movie" | "tv"
        config: AppConfig instance
        client: TMDbClient instance
    """
    # Import geçici - circular dependency önlemek için
    from core.matcher.matcher import match_movie, match_tv
    from integrations.ffprobe.client import FFProbeClient
    from core.query_engine.variable_engine import render_template, execute_query
    from utils.nfo_writer import make_movie_nfo, make_episode_nfo, maybe_write
    
    # Config shortcuts
    HARDLINK = config.options.hardlink
    DRY_RUN = config.options.dry_run
    NFO_ENABLE = config.options.nfo_enable
    NFO_FORCE = config.options.nfo_force
    FFPROBE_ENABLE = config.options.ffprobe_enable
    FFPROBE_NFO_ENABLE = config.options.ffprobe_nfo_enable
    FFPROBE_FORCE = config.options.ffprobe_force
    
    start_ts = time.time()
    total = len(paths)
    ok = miss = err = 0
    file_times = []  # Her dosyanın işlem süresi
    
    # Structured logger başlat
    logger = init_logger(enabled=config.options.debug)
    
    # FFProbe client başlat
    ffprobe_client = FFProbeClient() if FFPROBE_ENABLE else None
    
    # Last print context (for summary enrichment)
    last_print_ctx: dict = {}
    
    # Sequential processing: match -> rename için her dosya
    for p in paths:
        try:
            # Match
            if media_type == 'movie':
                item = match_movie(p, client, config)
            else:
                item = match_tv(p, client, config)
        except Exception as e:
            err += 1
            log_error(f"ERROR {Path(p).name}: {e}")
            continue
        
        # Rename işlemi hemen ardından
        src = item["path"]
        took = item["took"]
        best = item["best"]
        parsed = item["parsed"]
        api_source = item.get("api_source", "unknown")
        ep_full = item.get("ep_full")  # Episode details (matcher'dan)
        
        # Took değerini kaydet
        file_times.append(took)
        
        # Structured logs
        logger.debug(
            "file.processing",
            src=src,
            api=api_source,
            message=f"Processing file via {api_source}"
        )
        logger.log_parse_start(Path(src).name)
        
        if media_type == "movie":
            logger.log_parse_result(Path(src).name, title=parsed.get("parsed_title"))
        else:
            logger.log_parse_result(
                Path(src).name,
                show=parsed.get("parsed_show"),
                season=parsed.get("parsed_season"),
                episode=parsed.get("parsed_episode")
            )
        
        # Match bulunamadı
        if not best:
            miss += 1
            logger.log_file_error(src, f"{api_source} match not found")
            continue
        
        # Match already done by matcher, no need to log again
        
        link = tmdb_link(best, media_type)
        
        # FFprobe + Path building
        try:
            # Query config al (yeni sistem) veya fallback legacy pattern
            if media_type == "movie":
                query_cfg = config.rename.movies or {}
                pattern = query_cfg.get('save', config.rename.movie_pattern)
                print_template = query_cfg.get('print', '')
                
                # FFprobe gerekiyorsa çalıştır
                ffenv = {}
                if ffprobe_client and pattern_needs_ffprobe(pattern):
                    logger.log_ffprobe_start(src)
                    # Cache kontrolü: FFPROBE_NFO_ENABLE && !FFPROBE_FORCE
                    use_cache = FFPROBE_NFO_ENABLE and not FFPROBE_FORCE
                    ffenv = ffprobe_client.probe_file(src, use_cache=use_cache)
                
                if ffenv:
                    logger.log_ffprobe_result(
                        codec=(ffenv.get("video") or {}).get("codec"),
                        resolution=(ffenv.get("video") or {}).get("resolution"),
                        audio_count=len(ffenv.get("audio") or [])
                    )
                
                # Full movie details al (if not already fetched)
                movie_id = None
                if best and best.get('ids'):
                    ids = best['ids']
                    if api_source == 'tmdb' and 'tmdb' in ids:
                        movie_id = int(ids['tmdb'])
                    elif api_source == 'tvdb' and 'tvdb' in ids:
                        movie_id = int(ids['tvdb'])
                    elif api_source == 'omdb' and 'imdb' in ids:
                        movie_id = ids['imdb']
                
                movie_full = best
                if movie_id:
                    try:
                        movie_full = client.get_movie_details(movie_id, api_source) or best
                    except Exception:
                        movie_full = best
                
                # Path oluştur
                parent_rel, fname = build_movie_path(
                    config, movie_full or best, ffenv, render_template
                )
            
            else:  # TV
                query_cfg = config.rename.series or {}
                pattern = query_cfg.get('save', config.rename.series_pattern)
                print_template = query_cfg.get('print', '')
                # Need episode details if NFO enabled, pattern needs it, OR print template exists
                need_ep = NFO_ENABLE or pattern_needs_episode_details(pattern) or bool(print_template)
                
                # Full show details al (APIManager üzerinden)
                series_id = None
                if best and best.get('ids'):
                    ids = best['ids']
                    if api_source == 'tmdb' and 'tmdb' in ids:
                        series_id = int(ids['tmdb'])
                    elif api_source == 'tvdb' and 'tvdb' in ids:
                        series_id = int(ids['tvdb'])
                    elif api_source == 'tvmaze' and 'tvmaze' in ids:
                        series_id = int(ids['tvmaze'])
                    elif api_source == 'omdb' and 'imdb' in ids:
                        series_id = ids['imdb']
                
                show_full = best
                # Preserve extras from matcher (get_tv_details doesn't include extras)
                extras_from_matcher = best.get('extras', {})
                
                if series_id:
                    try:
                        show_full = client.get_tv_details(series_id, api_source) or best
                        # Restore extras from matcher
                        if extras_from_matcher:
                            show_full['extras'] = extras_from_matcher
                    except Exception:
                        show_full = best
                
                season_num = parsed["parsed_season"]
                episode_num = parsed["parsed_episode"]
                
                # Episode details: matcher'dan geldi, fallback APIManager if needed
                if not ep_full and need_ep and series_id:
                    # Fallback: APIManager ile episode detayları
                    try:
                        ep_raw = client.get_episode_details(series_id, season_num, episode_num, api_source)
                    except Exception:
                        ep_raw = None
                    # ep_raw already normalized by client
                    if ep_raw:
                        ep_full = ep_raw
                
                # FFprobe
                ffenv = {}
                if ffprobe_client and pattern_needs_ffprobe(pattern):
                    logger.log_ffprobe_start(src)
                    # Cache kontrolü: FFPROBE_NFO_ENABLE && !FFPROBE_FORCE
                    use_cache = FFPROBE_NFO_ENABLE and not FFPROBE_FORCE
                    ffenv = ffprobe_client.probe_file(src, use_cache=use_cache)
                
                if ffenv:
                    logger.log_ffprobe_result(
                        codec=(ffenv.get("video") or {}).get("codec"),
                        resolution=(ffenv.get("video") or {}).get("resolution"),
                        audio_count=len(ffenv.get("audio") or [])
                    )
                
                # Path oluştur
                parent_rel, fname = build_tv_path(
                    config, show_full or best, ep_full,
                    dict(parsed, parsed_season=season_num, parsed_episode=episode_num),
                    ffenv, render_template
                )
            
            # Extension ekle
            ext = Path(src).suffix
            if not fname.endswith(ext):
                fname = f"{fname}{ext}"
            
            # Final path
            dst = os.path.join(parent_rel if parent_rel else os.path.dirname(src), fname)
            dst = unique_path(dst)
            
            # Pattern rendering
            logger.log_pattern_render(pattern)
            logger.log_pattern_result(dst)
            
            # Print query log (config'den)
            if print_template:
                # For TV, merge show_full (series details) with extras from best
                # but keep using best as base since it has episode info from matcher
                best_for_print = best
                if media_type == "tv" and show_full and show_full != best:
                    # Merge show_full details into best (preserve episode info and extras)
                    best_for_print = {**show_full, **best}
                    # Ensure extras are preserved
                    if 'extras' in best:
                        best_for_print['extras'] = best['extras']
                
                try:
                    print_ctx = build_print_context(
                        best_for_print, media_type, parsed,
                        ep_full=ep_full if media_type == "tv" else None,
                        took=took,
                        api_source=api_source
                    )
                    log_msg = render_query_print(print_template, print_ctx)
                    print_query_log(log_msg, config)
                    # Keep last print context to expose variables in summary
                    last_print_ctx = print_ctx
                except Exception as e:
                    logger.warn(
                        "print.template_error",
                        error=str(e),
                        message=f"Print template rendering failed: {e}"
                    )
                    import traceback
                    traceback.print_exc()
            
            # Dry run
            if DRY_RUN:
                ok += 1
                logger.log_file_success(src)
                continue
            
            # Gerçek rename (print zaten yukarıda yapıldı)
            try:
                if HARDLINK:
                    dst = hardlink_file(src, dst)
                else:
                    move_file(src, dst)
                
                # NFO yazma
                if NFO_ENABLE:
                    nfo_base = dst[:-len(ext)]
                    
                    if media_type == "movie":
                        txt = make_movie_nfo(movie_full or best)
                        if not (Path(nfo_base + ".nfo").is_file() and not NFO_FORCE):
                            maybe_write(nfo_base, txt)
                    else:
                        if ep_full and show_full:
                            txt = make_episode_nfo(show_full, ep_full)
                            if not (Path(nfo_base + ".nfo").is_file() and not NFO_FORCE):
                                maybe_write(nfo_base, txt)
                
                ok += 1
                logger.log_file_success(src)
            
            except Exception as e:
                err += 1
                logger.log_file_error(src, str(e))
                log_error(f"RENAME ERROR {Path(src).name} -> {Path(dst).name}: {e}")
        
        except Exception as e:
            err += 1
            logger.log_file_error(src, str(e))
            log_error(f"PROCESSING ERROR {Path(src).name}: {e}")
    
    # Query engine print'leri (eğer varsa)
    if config.query_engine.queries:
        print()  # Boş satır
        for query_cfg in config.query_engine.queries:
            # Query execute et - sadece print için (save yapma)
            # TODO: File contexts oluştur ve execute et
            # Şimdilik sadece query name göster
            query_name = query_cfg.get('name', 'Unnamed Query')
            if query_cfg.get('print'):
                print(f"\033[90m[Query: {query_name}]\033[0m")
    
    # Summary
    logger.log_summary()
    
    # Custom summary from config
    if config.summary.print:
        end_ts = time.time()
        total_time = end_ts - start_ts
        
        # Timing statistics
        avg_time = total_time / total if total > 0 else 0
        min_time = min(file_times) if file_times else 0
        max_time = max(file_times) if file_times else 0
        
        # Summary context with safe defaults for all possible variables
        summary_ctx = {
            # Timing stats
            "total": total,
            "success": ok,
            "failed": err,
            "skipped": miss,
            "total_time": total_time,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            
            # TV show defaults
            "showName": "",
            "originalShowName": "",
            "seasonNumber": 0,
            "episodeNumber": 0,
            "episodeName": "",
            "episodeAirDate": "",
            "episodeRuntime": 0,
            "episodeVoteAverage": 0.0,
            "episodeVoteCount": 0,
            "episodeOverview": "",
            "firstAirDate": "",
            "firstAirYear": 0,
            "lastAirDate": "",
            "numberOfSeasons": 0,
            "numberOfEpisodes": 0,
            "networkName": "",
            "showType": "",
            "inProduction": False,
            
            # Movie defaults
            "title": "",
            "originalTitle": "",
            "year": 0,
            "releaseDate": "",
            "runtime": 0,
            
            # Common defaults
            "overview": "",
            "voteAverage": 0.0,
            "voteCount": 0,
            "popularity": 0.0,
            "genreName": "",
            "apiSource": "",
            "took": 0.0,
            
            # Extras defaults
            "castCount": 0,
            "crewCount": 0,
            "director": "",
            "postersCount": 0,
            "backdropsCount": 0,
            "trailersCount": 0,
            "teasersCount": 0,
            "keywordsCount": 0,
            "imdbId": "",
            "tvdbId": "",
            "contentRatingUS": "",
        }
        
        # Enrich with last file's context (TV/Movie variables override defaults)
        if isinstance(last_print_ctx, dict):
            for k, v in last_print_ctx.items():
                # Skip dict values (cast, keywords, etc) - they don't work in Python format strings
                if not isinstance(v, dict):
                    summary_ctx[k] = v
        
        # Render template - Use safe format with defaults
        try:
            # Use string.Formatter for safe formatting (returns empty string for missing keys)
            from string import Formatter
            
            class SafeFormatter(Formatter):
                def get_value(self, key, args, kwargs):
                    if isinstance(key, str):
                        return kwargs.get(key, '')
                    return super().get_value(key, args, kwargs)
            
            formatter = SafeFormatter()
            summary_text = formatter.format(config.summary.print, **summary_ctx)
            print(summary_text)
        except Exception as e:
            print(f"Summary render error: {e}")
