"""
Debug System - Plugin-agnostic live debugging infrastructure

This module provides a professional, plugin-agnostic debug system that:
1. Allows plugins to send debug messages without knowing about system internals
2. Supports live, immediate output when debug mode is enabled
3. Provides standard log levels (DEBUG, INFO, WARN, ERROR)
4. Maintains strict plugin-agnostic principles (no plugin-specific logic)

Usage in plugins:
    debugger = get_debugger()
    debugger.debug("tmdb", "Searching for movie", query="Inception", year=2010)
    debugger.info("tmdb", "Match found", tmdb_id=27205, score=0.95)

Usage in core:
    debugger = get_debugger()
    debugger.info("discovery", "Found plugins", count=7)
    debugger.debug("executor", "Executing group", group=["ffprobe", "renamer"])
"""
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class DebugSystem:
    """
    Professional debug system with live output.
    
    Features:
    - Config-driven (enabled/disabled via options.debug)
    - Live output (immediate stderr flush)
    - Plugin-agnostic (any component can log)
    - Structured context fields
    - ISO8601 timestamps
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
    
    def _timestamp(self) -> str:
        """ISO8601 timestamp with timezone"""
        return datetime.now(timezone.utc).astimezone().isoformat(timespec='milliseconds')
    
    def _log(self, level: str, component: str, message: str, **fields):
        """
        Emit structured debug line immediately to stderr.
        
        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR)
            component: Component name (plugin name or system component)
            message: Log message
            **fields: Additional context fields
        """
        if not self.enabled:
            return
        
        ts = self._timestamp()
        context = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
        
        if context:
            line = f"{ts}  {level:5s}  {component:20s} [{context}] {message}"
        else:
            line = f"{ts}  {level:5s}  {component:20s} {message}"
        
        print(line, file=sys.stderr)
        sys.stderr.flush()  # Force immediate output
    
    def debug(self, component: str, message: str, **fields):
        """DEBUG level - Detailed diagnostic information"""
        self._log("DEBUG", component, message, **fields)
    
    def info(self, component: str, message: str, **fields):
        """INFO level - General informational messages"""
        self._log("INFO", component, message, **fields)
    
    def warn(self, component: str, message: str, **fields):
        """WARN level - Warning messages"""
        self._log("WARN", component, message, **fields)
    
    def error(self, component: str, message: str, **fields):
        """ERROR level - Error messages"""
        self._log("ERROR", component, message, **fields)


# Global instance
_debugger: Optional[DebugSystem] = None


def init_debugger(enabled: bool = False) -> DebugSystem:
    """
    Initialize global debug system.
    
    Args:
        enabled: Whether debug mode is enabled
        
    Returns:
        Initialized debugger instance
    """
    global _debugger
    _debugger = DebugSystem(enabled=enabled)
    return _debugger


def get_debugger() -> DebugSystem:
    """
    Get global debugger instance.
    
    Returns:
        Debugger instance (creates disabled instance if not initialized)
    """
    global _debugger
    if _debugger is None:
        _debugger = DebugSystem(enabled=False)
    return _debugger
