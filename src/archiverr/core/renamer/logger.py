# core/renamer/logger.py
"""Rename işlemleri için logging utilities."""
import json
import time
from typing import Dict, Any, Optional


def colored(s: str, code: str) -> str:
    """Terminal color code wrapper."""
    return f"\033[{code}m{s}\033[0m"


def log_json(payload: Dict[str, Any]) -> None:
    """JSON formatında log yaz."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(json.dumps(dict(ts=ts, **payload), ensure_ascii=False))


def log_line(src_name: str, dst_name: Optional[str], tmdb_link: Optional[str], 
             took: float, found: bool) -> None:
    """Human-readable log line yaz."""
    head = colored(src_name, "36")
    print(head)
    if found and dst_name:
        print("  " + colored("→ " + dst_name, "32"))
    else:
        print("  " + colored("× no match", "31"))
    if tmdb_link:
        print("  " + colored(tmdb_link, "90"))
    print("  " + colored(f"(search {took:.2f}s)", "90"))


def log_info(message: str) -> None:
    """Info mesajı yaz."""
    print(colored(message, "35"))


def log_error(message: str) -> None:
    """Error mesajı yaz."""
    print(colored(message, "31"))
