# filescanner.py
from pathlib import Path
from typing import List
import os

ALLOWED_EXT = {
    '.mkv', '.mp4', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp', '.3g2'
}

def scan_directory(path: str, recursive: bool = True) -> List[str]:
    """
    Return list of media file paths under `path`.
    If `path` is a single file, return that file (if it has allowed ext).
    """
    p = Path(path)
    files: List[str] = []

    if p.is_file():
        if p.suffix.lower() in ALLOWED_EXT:
            return [str(p.resolve())]
        return []

    if not p.exists():
        return []

    if recursive:
        for f in p.rglob('*'):
            if f.is_file() and f.suffix.lower() in ALLOWED_EXT:
                files.append(str(f.resolve()))
    else:
        for f in p.iterdir():
            if f.is_file() and f.suffix.lower() in ALLOWED_EXT:
                files.append(str(f.resolve()))

    return files

def collect_inputs(inputs: List[str], recursive: bool = True, skip_existence_check: bool = False) -> List[str]:
    """
    Birden fazla kök girdi (dosya/klasör) alır, hepsini tarayıp tek bir medya dosyası listesine çevirir.
    Kök girdi bir dosyaysa ve uzantısı uygunsa direkt eklenir.
    Klasörse scan_directory uygulanır.
    
    Args:
        inputs: Dosya/klasör yolları listesi
        recursive: Alt klasörleri de tara
        skip_existence_check: True ise dosya varlığı kontrol edilmez (test için)
    """
    out: List[str] = []
    for raw in inputs:
        # Kullanıcı shell’de tırnakları unutmuşsa, burada tekrar şans yok;
        # cli içinde birleştirme zaten yapılıyor.
        path = os.path.expanduser(raw)
        p = Path(path)
        
        # Virtual path mode: dosya varlığı kontrol edilmez
        if skip_existence_check:
            out.append(path)
            continue
            
        # Normal akış: dosya var mı kontrol et
        if not p.exists():
            continue
        if p.is_file():
            if p.suffix.lower() in ALLOWED_EXT:
                out.append(str(p.resolve()))
        else:
            out.extend(scan_directory(path, recursive=recursive))
    # Tekrarları at
    out = list(dict.fromkeys(out))
    return out

