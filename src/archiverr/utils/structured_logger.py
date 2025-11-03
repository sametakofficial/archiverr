# utils/structured_logger.py
"""
Structured logging system - production-grade timestamped logs.
Logs are emitted immediately at each stage when debug=true.
"""
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from pathlib import Path


class StructuredLogger:
    """Production-grade structured logger with immediate output."""
    
    def __init__(self, enabled: bool = False, service: str = "archiverr"):
        self.enabled = enabled
        self.service = service
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.stats = {"success": 0, "failed": 0, "total": 0}
        self.failed_files: List[Dict[str, str]] = []
        self.operations: List[Dict[str, Any]] = []  # Detaylı operasyon kayıtları
        self.log_buffer: List[str] = []  # Debug logları buffer
    
    def _timestamp(self) -> str:
        """ISO8601 timestamp with timezone."""
        return datetime.now(timezone.utc).astimezone().isoformat(timespec='milliseconds')
    
    def _log(self, level: str, component: str, message: str, **fields):
        """Emit structured log line immediately."""
        ts = self._timestamp()
        context = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
        
        if context:
            line = f"{ts}  {level:5s}  {component:20s} [{context}] {message}"
        else:
            line = f"{ts}  {level:5s}  {component:20s} {message}"
        
        # Always buffer logs for report (regardless of debug mode)
        self.log_buffer.append({
            "timestamp": ts,
            "level": level,
            "component": component,
            "message": message,
            **fields
        })
        
        # Only print to console if debug enabled
        if self.enabled:
            print(line, file=sys.stderr)
            sys.stderr.flush()  # Force immediate flush
    
    def info(self, component: str, message: str, **fields):
        """INFO level log."""
        self._log("INFO", component, message, **fields)
    
    def debug(self, component: str, message: str, **fields):
        """DEBUG level log."""
        self._log("DEBUG", component, message, **fields)
    
    def error(self, component: str, message: str, **fields):
        """ERROR level log."""
        self._log("ERROR", component, message, **fields)
    
    def warn(self, component: str, message: str, **fields):
        """WARN level log."""
        self._log("WARN", component, message, **fields)
    
    # Stage-specific helpers
    def log_parse_start(self, filename: str):
        self.info("parse.start", "Starting filename parse", file=filename)
    
    def log_parse_result(self, filename: str, show: str = None, season: int = None, episode: int = None, title: str = None):
        if show:
            self.info("parse.result", "Parsed TV show", 
                     file=filename, show=show, season=season, episode=episode)
        elif title:
            self.info("parse.result", "Parsed movie", 
                     file=filename, title=title)
    
    def log_api_search(self, query: str, media_type: str, api: str):
        self.info("api.search", f"Searching {api} ({media_type})", query=query, api=api)
    
    def log_api_match(self, name: str, year: str = None, score: float = None, api: str = None):
        self.info("api.match", "Best match found", 
                 name=name, year=year, score=f"{score:.2f}" if score else None, api=api)
    
    def log_api_details(self, item_id: int, api: str):
        self.debug("api.details", f"Fetching full details from {api}", id=item_id, api=api)
    
    def log_ffprobe_start(self, filepath: str):
        self.debug("ffprobe.start", "Analyzing media", file=Path(filepath).name)
    
    def log_ffprobe_result(self, codec: str = None, resolution: str = None, 
                          audio_count: int = None, duration: float = None):
        self.debug("ffprobe.result", "Media analysis complete",
                  codec=codec, res=resolution, audio=audio_count, 
                  duration=f"{duration:.1f}s" if duration else None)
    
    def log_pattern_render(self, pattern: str):
        self.debug("pattern.render", "Rendering path pattern", pattern=pattern)
    
    def log_pattern_result(self, rendered: str):
        self.info("pattern.result", "Path rendered", path=rendered)
    
    def log_file_operation(self, action: str, src: str, dst: str):
        """Log file operation."""
        self.info("file." + action, f"File {action}", src=src, dst=dst)
        
        # Undo/redo için detaylı kayıt
        self.operations.append({
            "timestamp": self._timestamp(),
            "action": action,
            "source": src,
            "destination": dst,
            "reversible": action in ["move", "hardlink", "dryrun"]
        })
    
    def log_file_success(self, filepath: str):
        self.stats["success"] += 1
        self.stats["total"] += 1
        self.info("file.success", "Processing complete", file=Path(filepath).name)
    
    def log_file_error(self, filepath: str, error: str):
        self.stats["failed"] += 1
        self.stats["total"] += 1
        self.failed_files.append({"file": filepath, "error": error})
        self.error("file.error", "Processing failed", file=Path(filepath).name, error=error)
    
    def log_summary(self):
        """Print final summary."""
        if self.stats["total"] == 0:
            return
        
        ts = self._timestamp()
        print(f"\n{ts}  INFO   summary              Processing complete", file=sys.stderr)
        print(f"{ts}  INFO   summary              success={self.stats['success']} "
              f"failed={self.stats['failed']} total={self.stats['total']}", file=sys.stderr)
        
        if self.failed_files:
            for item in self.failed_files:
                print(f"{ts}  WARN   summary.failed       {item['file']}: {item['error']}", 
                      file=sys.stderr)
        
        # Always save report (detaylı log undo/redo için gerekli)
        if self.stats["total"] > 0:
            self._save_report()
    
    def _save_report(self):
        """Save JSON report to logs directory."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        report_file = log_dir / f"report_{self.session_id}.json"
        
        report = {
            "session_id": self.session_id,
            "timestamp": self._timestamp(),
            "stats": self.stats,
            "failed_files": self.failed_files,
            "operations": self.operations,  # Undo/redo için detaylı işlem listesi
            "debug_logs": self.log_buffer   # Tüm debug logları (debug açık olmasına gerek yok)
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        ts = self._timestamp()
        print(f"{ts}  INFO   report.saved         Report written to {report_file} ({len(self.operations)} ops, {len(self.log_buffer)} logs)", 
              file=sys.stderr)


# Global instance
_logger: Optional[StructuredLogger] = None


def init_logger(enabled: bool = False) -> StructuredLogger:
    """Initialize global structured logger."""
    global _logger
    _logger = StructuredLogger(enabled=enabled)
    return _logger


def get_logger() -> StructuredLogger:
    """Get global structured logger instance."""
    global _logger
    if _logger is None:
        _logger = StructuredLogger(enabled=False)
    return _logger
