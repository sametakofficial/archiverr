"""Filters for variable manipulation"""
from typing import Any
import re
import unicodedata


def apply_filter(value: Any, filter_name: str) -> Any:
    """
    Apply a filter to a value.
    
    COMPLETE FILTER LIST:
    
    Case Filters:
    - uppercase, upper, u: UPPERCASE
    - lowercase, lower, l: lowercase
    - title, t: Title Case
    - capitalize, cap: Capitalize first letter
    - swapcase: sWAP cASE
    
    String Manipulation:
    - strip, trim: Remove leading/trailing whitespace
    - lstrip: Remove leading whitespace
    - rstrip: Remove trailing whitespace
    - normalize: Remove special characters
    - slugify: URL-safe slug (lowercase, hyphens)
    - clean: Remove extra whitespace
    - reverse: Reverse string
    
    Extraction:
    - year: Extract year (YYYY)
    - first: First character/word
    - last: Last character/word
    - length, len: String/list length
    
    Numeric:
    - int: Convert to integer
    - float: Convert to float
    - abs: Absolute value
    - round: Round to integer
    - round2, round3: Round to N decimals
    - 02d, 03d, 04d: Zero-padded format
    
    Boolean:
    - bool: Convert to boolean
    - not: Logical NOT
    
    Encoding:
    - ascii: ASCII representation
    - base64: Base64 encode
    - urlencode: URL encode
    - quote: URL quote
    
    Args:
        value: Value to filter
        filter_name: Filter name
        
    Returns:
        Filtered value
    """
    if value is None:
        return ''
    
    filter_lower = filter_name.lower().strip()
    
    # ===== CASE FILTERS =====
    if filter_lower in ['uppercase', 'upper', 'u']:
        return str(value).upper()
    
    elif filter_lower in ['lowercase', 'lower', 'l']:
        return str(value).lower()
    
    elif filter_lower in ['title', 't']:
        return str(value).title()
    
    elif filter_lower in ['capitalize', 'cap']:
        text = str(value)
        return text[0].upper() + text[1:] if text else ''
    
    elif filter_lower == 'swapcase':
        return str(value).swapcase()
    
    # ===== STRING MANIPULATION =====
    elif filter_lower in ['strip', 'trim']:
        return str(value).strip()
    
    elif filter_lower == 'lstrip':
        return str(value).lstrip()
    
    elif filter_lower == 'rstrip':
        return str(value).rstrip()
    
    elif filter_lower == 'normalize':
        text = str(value)
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
        # Remove special chars, keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    elif filter_lower == 'slugify':
        text = str(value).lower()
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)
        # Remove non-alphanumeric except hyphens
        text = re.sub(r'[^a-z0-9-]', '', text)
        # Remove multiple hyphens
        text = re.sub(r'-+', '-', text)
        return text.strip('-')
    
    elif filter_lower == 'clean':
        text = str(value)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    elif filter_lower == 'reverse':
        return str(value)[::-1]
    
    # ===== EXTRACTION =====
    elif filter_lower == 'year':
        text = str(value)
        match = re.search(r'(\d{4})', text)
        return match.group(1) if match else ''
    
    elif filter_lower == 'first':
        if isinstance(value, (list, tuple)):
            return value[0] if value else ''
        text = str(value)
        return text.split()[0] if text.split() else text[:1]
    
    elif filter_lower == 'last':
        if isinstance(value, (list, tuple)):
            return value[-1] if value else ''
        text = str(value)
        return text.split()[-1] if text.split() else text[-1:]
    
    elif filter_lower in ['length', 'len']:
        if isinstance(value, (list, tuple, dict, str)):
            return len(value)
        return 0
    
    # ===== NUMERIC =====
    elif filter_lower == 'int':
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    elif filter_lower == 'float':
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    elif filter_lower == 'abs':
        try:
            return abs(float(value))
        except (ValueError, TypeError):
            return 0
    
    elif filter_lower == 'round':
        try:
            return round(float(value))
        except (ValueError, TypeError):
            return 0
    
    elif filter_lower.startswith('round') and filter_lower[5:].isdigit():
        try:
            decimals = int(filter_lower[5:])
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return 0
    
    # Zero-padded number formats (02d, 03d, 04d, etc.)
    elif re.match(r'0\dd', filter_lower):
        try:
            width = int(filter_lower[1])
            return str(int(value)).zfill(width)
        except (ValueError, TypeError):
            return str(value)
    
    # ===== BOOLEAN =====
    elif filter_lower == 'bool':
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value)
    
    elif filter_lower == 'not':
        return not bool(value)
    
    # ===== ENCODING =====
    elif filter_lower == 'ascii':
        return ascii(str(value))
    
    elif filter_lower == 'base64':
        try:
            import base64
            return base64.b64encode(str(value).encode()).decode()
        except Exception:
            return str(value)
    
    elif filter_lower in ['urlencode', 'quote']:
        try:
            from urllib.parse import quote
            return quote(str(value))
        except Exception:
            return str(value)
    
    # Default: return as-is
    else:
        return value
