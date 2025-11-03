# engines/yaml/variable_engine.py
"""
Birleşik değişken ve query engine - {var} syntax ile template rendering ve query execution.
Pattern ve Query sistemleri artık tek bir engine altında.
"""
import re
from typing import Any, Dict, List, Optional
from .filters import apply_filter


# ============================================================================
# VARIABLE RESOLUTION & RENDERING
# ============================================================================

VARIABLE_REGEX = re.compile(r'\{([\w\.]+(?::\w+)*)\}')


def render_template(template: str, context: Dict[str, Any]) -> str:
    """
    Template string'i context ile render et.
    
    Artık sadece {var} syntax kullanılıyor, $ yok.
    
    Args:
        template: Template string (örn: "{name} ({movieYear})")
        context: Değişken context
    
    Returns:
        Rendered string
    
    Examples:
        >>> render_template("{name} ({movieYear})", {"name": "Matrix", "movieYear": "1999"})
        "Matrix (1999)"
        
        >>> render_template("{showName:slug}", {"showName": "Breaking Bad"})
        "breaking-bad"
    """
    def replacer(match):
        token = match.group(1)
        value = resolve_variable(token, context)
        return str(value) if value is not None else ""
    
    return VARIABLE_REGEX.sub(replacer, template)


def resolve_variable(token: str, context: Dict[str, Any]) -> Any:
    """
    Token'ı çöz ve değer döndür.
    
    Token format: değişkenAdi.alan.1.nested:filtre:filtre2
    
    Args:
        token: Değişken token (örn: "audio.1.language:upper")
        context: Değişken ortamı
    
    Returns:
        Resolved ve filtrelenmiş değer
    """
    # Filtreleri ayır
    if ':' in token:
        parts = token.split(':')
        var_path = parts[0]
        filters = parts[1:]
    else:
        var_path = token
        filters = []
    
    # Değişkeni resolve et
    value = _resolve_path(var_path, context)
    
    # Filtreleri uygula
    for flt in filters:
        value = apply_filter(value, flt)
    
    return value


def _resolve_path(path: str, context: Dict[str, Any]) -> Any:
    """
    Dot-notation path'i resolve et.
    
    Örnekler:
        "name" → context["name"]
        "video.codec" → context["video"]["codec"]
        "audio.1.language" → context["audio"][1]["language"]  # 1-based index
        "apiResponse.genres.1.name" → context["apiResponse"]["genres"][0]["name"]  # 1-based → 0-based
    
    Args:
        path: Dot-separated path
        context: Değişken ortamı
    
    Returns:
        Resolved değer veya None
    """
    parts = path.split('.')
    current = context
    
    for part in parts:
        if current is None:
            return None
        
        # Numeric index check (1-based → 0-based conversion)
        if part.isdigit():
            idx = int(part)
            if idx < 1:  # 1-based, 0 geçersiz
                return None
            
            # List/dict check
            if isinstance(current, list):
                idx_0 = idx - 1  # 1-based → 0-based
                if 0 <= idx_0 < len(current):
                    current = current[idx_0]
                else:
                    return None
            elif isinstance(current, dict):
                current = current.get(idx)
            else:
                return None
        
        # String key
        else:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
    
    return current


# ============================================================================
# QUERY ENGINE
# ============================================================================

def execute_query(
    query_config: Dict[str, Any],
    file_contexts: List[Dict[str, Any]],
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Query'yi execute et ve sonuçları döndür.
    
    Args:
        query_config: Query YAML config
            {
                "name": "Query Name",
                "loop": {"var": "q", "in": [1080, 720]},  # Optional
                "where": "videoHeight == q and audioCount >= 2",
                "print": "{q}p => {count} files | {sizeH}",  # Optional
                "save": "/output/{q}p/"  # Optional
            }
        file_contexts: Her dosya için variable context listesi
        dry_run: True ise sadece print, save yapma
    
    Returns:
        {
            "matched_files": [...],
            "stats": {...},
            "print_output": "...",
            "save_actions": [...]
        }
    """
    name = query_config.get('name', 'Unnamed Query')
    loop_config = query_config.get('loop')
    where_expr = query_config.get('where', '')
    print_template = query_config.get('print')
    save_pattern = query_config.get('save')
    
    results = {
        'query_name': name,
        'matched_files': [],
        'stats': {},
        'print_output': '',
        'save_actions': [],
    }
    
    # Loop varsa, her değer için çalıştır
    if loop_config:
        loop_var = loop_config['var']
        loop_values = loop_config['in']
        
        for loop_val in loop_values:
            # Loop değişkenini context'e ekle
            matched = _filter_files(where_expr, file_contexts, {loop_var: loop_val})
            
            if matched:
                stats = _calculate_stats(matched, loop_var, loop_val)
                
                # Print
                if print_template:
                    output = render_template(print_template, stats)
                    results['print_output'] += output + '\n'
                
                # Save
                if save_pattern and not dry_run:
                    save_path = render_template(save_pattern, stats)
                    results['save_actions'].append({
                        'loop_val': loop_val,
                        'destination': save_path,
                        'files': [ctx['path'] for ctx in matched]
                    })
                
                results['matched_files'].extend(matched)
    
    else:
        # Loop yok, tek where evaluation
        matched = _filter_files(where_expr, file_contexts, {})
        results['matched_files'] = matched
        
        if matched:
            stats = _calculate_stats(matched)
            results['stats'] = stats
            
            # Print
            if print_template:
                results['print_output'] = render_template(print_template, stats)
            
            # Save
            if save_pattern and not dry_run:
                save_path = render_template(save_pattern, stats)
                results['save_actions'].append({
                    'destination': save_path,
                    'files': [ctx['path'] for ctx in matched]
                })
    
    return results


def _filter_files(
    where_expr: str,
    file_contexts: List[Dict[str, Any]],
    loop_vars: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Where expression ile dosyaları filtrele."""
    matched = []
    
    for ctx in file_contexts:
        # Loop vars'ı context'e merge et
        eval_ctx = {**ctx, **loop_vars}
        
        # Where expression evaluate et
        if _evaluate_where(where_expr, eval_ctx):
            matched.append(ctx)
    
    return matched


def _evaluate_where(expr: str, context: Dict[str, Any]) -> bool:
    """Where expression'ı evaluate et."""
    if not expr:
        return True
    
    try:
        # Context'i eval için hazırla (flatten nested dicts)
        eval_locals = _flatten_context_for_eval(context)
        
        # Evaluate
        result = eval(expr, {"__builtins__": {}}, eval_locals)
        return bool(result)
    
    except Exception:
        return False


def _flatten_context_for_eval(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Context'i eval için düzleştir.
    
    Nested dict'leri flat hale getir:
        {"video": {"height": 1080}} → {"videoHeight": 1080}
    """
    flat = {}
    
    for key, value in context.items():
        if isinstance(value, dict) and key in ['video', 'audio', 'container', 'apiResponse']:
            # Nested dict'leri camelCase ile flatten et
            for nested_key, nested_val in value.items():
                if not isinstance(nested_val, dict):  # Sadece basit değerler
                    flat_key = key + nested_key.capitalize()
                    flat[flat_key] = nested_val
        else:
            flat[key] = value
    
    return flat


def _calculate_stats(
    matched_files: List[Dict[str, Any]],
    loop_var: Optional[str] = None,
    loop_val: Any = None
) -> Dict[str, Any]:
    """Eşleşen dosyalar için istatistikler hesapla."""
    if not matched_files:
        return {}
    
    sizes = [ctx.get('sizeInt', 0) for ctx in matched_files]
    durations = [ctx.get('durationSec', 0) for ctx in matched_files]
    bitrates = [ctx.get('totalBitrateBps', 0) for ctx in matched_files]
    
    # Years (varsa)
    years = []
    for ctx in matched_files:
        year = ctx.get('movieYear') or ctx.get('firstAirDate', '')[:4]
        if year and str(year).isdigit():
            years.append(int(year))
    
    stats = {
        'count': len(matched_files),
        'matched': len(matched_files),
        
        # Size
        'sizeBytes': sum(sizes),
        'sizeH': _human_size(sum(sizes)),
        'minSizeBytes': min(sizes) if sizes else 0,
        'maxSizeBytes': max(sizes) if sizes else 0,
        'avgSizeBytes': sum(sizes) // len(sizes) if sizes else 0,
        
        # Duration
        'durationSec': sum(durations),
        'durationH': _seconds_to_hms(sum(durations)),
        'minDurationSec': min(durations) if durations else 0,
        'maxDurationSec': max(durations) if durations else 0,
        'avgDurationSec': sum(durations) / len(durations) if durations else 0,
        
        # Bitrate
        'minBitrateBps': min(bitrates) if bitrates else 0,
        'maxBitrateBps': max(bitrates) if bitrates else 0,
        'avgBitrateBps': sum(bitrates) // len(bitrates) if bitrates else 0,
        
        # Year
        'minYear': min(years) if years else 0,
        'maxYear': max(years) if years else 0,
        
        # Sample
        'samplePath': matched_files[0].get('path', '') if matched_files else '',
    }
    
    # Loop variable ekle
    if loop_var and loop_val is not None:
        stats[loop_var] = loop_val
    
    return stats


def _human_size(bytes_val: int) -> str:
    """Bayt → okunur boyut."""
    if bytes_val == 0:
        return "0 B"
    
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    i = 0
    val = float(bytes_val)
    
    while val >= 1024 and i < len(units) - 1:
        val /= 1024
        i += 1
    
    return f"{val:.2f} {units[i]}"


def _seconds_to_hms(seconds: float) -> str:
    """Saniye → HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
