# core/renamer/operations.py
"""Dosya operasyonları - move, hardlink, unique path."""
import os
from pathlib import Path


def ensure_parent(path: str) -> None:
    """Hedef path'in parent klasörünü oluştur."""
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)


def unique_path(path: str) -> str:
    """
    Eğer path varsa, (1), (2), ... ekleyerek unique path döndür.
    
    Args:
        path: İstenen dosya yolu
    
    Returns:
        Unique dosya yolu
    """
    p = Path(path)
    if not p.exists():
        return str(p)
    
    stem, suf = p.stem, p.suffix
    parent = p.parent
    i = 1
    
    while True:
        cand = parent / f"{stem} ({i}){suf}"
        if not cand.exists():
            return str(cand)
        i += 1


def move_file(src: str, dst: str) -> None:
    """Dosyayı taşı (rename)."""
    ensure_parent(dst)
    os.replace(src, dst)


def hardlink_file(src: str, dst: str) -> None:
    """Hardlink oluştur."""
    ensure_parent(dst)
    try:
        os.link(src, dst)
    except FileExistsError:
        # Unique path dene
        dst_unique = unique_path(dst)
        os.link(src, dst_unique)
        return dst_unique
    return dst
