# engine/filters.py
"""
Değişken filtreleri - :lower, :upper, :slug, :year vb.
"""
import re
import unicodedata
from typing import Any


def apply_filter(value: Any, filter_name: str) -> str:
    """
    Değişkene filtre uygula.
    
    Args:
        value: Değişken değeri
        filter_name: Filtre adı (lower, upper, slug, year, vb)
    
    Returns:
        Filtrelenmiş string
    """
    if value is None:
        return ""
    
    s = str(value)
    
    if filter_name == "lower":
        return s.lower()
    
    elif filter_name == "upper":
        return s.upper()
    
    elif filter_name == "slug":
        return _slugify(s)
    
    elif filter_name == "year":
        return _extract_year(s)
    
    elif filter_name == "trim":
        return s.strip()
    
    elif filter_name == "title":
        return s.title()
    
    elif filter_name == "snake":
        return _to_snake_case(s)
    
    elif filter_name == "camel":
        return _to_camel_case(s)
    
    elif filter_name.startswith("pad:"):
        # :pad:N → zero-pad to N digits
        try:
            n = int(filter_name.split(':')[1])
            return s.zfill(n)
        except:
            return s
    
    elif filter_name.startswith("max:"):
        # :max:N → truncate to N chars
        try:
            n = int(filter_name.split(':')[1])
            return s[:n]
        except:
            return s
    
    elif filter_name.startswith("replace:"):
        # :replace:old:new
        parts = filter_name.split(':', 2)
        if len(parts) == 3:
            _, old, new = parts
            return s.replace(old, new)
        return s
    
    else:
        # Unknown filter → warn and return original
        # TODO: Log warning
        return s


def _slugify(s: str) -> str:
    """String → URL-safe slug (kebab-case)."""
    # Normalize unicode
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    
    # Lowercase
    s = s.lower()
    
    # Replace non-alphanumeric with dash
    s = re.sub(r'[^a-z0-9]+', '-', s)
    
    # Remove leading/trailing dashes
    s = s.strip('-')
    
    return s


def _extract_year(s: str) -> str:
    """Extract YYYY from string (örn: "1999-03-31" → "1999")."""
    match = re.search(r'\b(\d{4})\b', s)
    return match.group(1) if match else s


def _to_snake_case(s: str) -> str:
    """camelCase → snake_case."""
    # Insert underscore before uppercase letters
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
    return s.lower()


def _to_camel_case(s: str) -> str:
    """snake_case → camelCase."""
    parts = s.split('_')
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
