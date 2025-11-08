"""Template rendering with $ syntax and filters"""
import re
from typing import Any, Dict, List
from .filters import apply_filter


# Pattern: $path.to.value or $path.to.value:filter or $path.to.value:filter:arg
# Enhanced to support complex modifiers like :loop:field|sep, :filter:key=val
# Supports alphanumeric, underscores, and dots in variable names
# Lookahead accepts: space, pipe, parenthesis, bracket, end of string, or any punctuation
VARIABLE_REGEX = re.compile(r'\$([a-zA-Z0-9_\.]+)(?::([\s\S]+?))?(?=\s|\||$|\)|\]|,|/)')


def resolve_variable_path(path: str, api_response: Dict[str, Any]) -> Any:
    """
    Resolve $ prefixed path to actual value from api_response.
    
    $ character = apiResponse. (direct replacement)
    
    Special handling for globals shortcuts:
    - $parsed.x → api_response['globals']['parsed']['x']
    - $execution.x → api_response['globals']['execution']['x']
    - $summary.x → api_response['globals']['summary']['x']
    
    Otherwise:
    - $show.x → api_response['show']['x']
    - $file.path → api_response['file']['path']
    - $movie.ids.tmdb → api_response['movie']['ids']['tmdb']
    - $extras.credits.cast.0.name → api_response['extras']['credits']['cast'][0]['name']
    
    Args:
        path: $-prefixed path (e.g., "$show.showTitle")
        api_response: Complete API response dictionary
        
    Returns:
        Resolved value or None if not found
    """
    if not path.startswith('$'):
        return None
    
    # Remove $, split by dots
    parts = path[1:].split('.')
    if not parts:
        return None
    
    first_key = parts[0]
    
    # Globals shortcuts: parsed, execution, summary
    GLOBALS_SHORTCUTS = ['parsed', 'execution', 'summary']
    
    if first_key in GLOBALS_SHORTCUTS:
        # $parsed.x → api_response['globals']['parsed']['x']
        current = api_response.get('globals', {}).get(first_key, {})
        remaining_parts = parts[1:]
    else:
        # $show.x → api_response['show']['x']
        current = api_response.get(first_key)
        remaining_parts = parts[1:]
    
    if current is None:
        return None
    
    # Traverse remaining path
    for part in remaining_parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if 0 <= idx < len(current) else None
        else:
            return None
        
        if current is None:
            return None
    
    return current


def render_template(template: str, api_response: Dict[str, Any]) -> str:
    """
    Render template string with $ variable substitution.
    
    Supports:
    - Basic: $show.title
    - Nested: $show.networks.0.name
    - Array access: $extras.credits.cast.0.name
    - Filters: $show.title:upper, $parsed.seasonNumber:02d
    - Count: $show.genres:count
    - Loop: $show.genres:loop:name|, :max:5
    - Filter: $crew:filter:job=Director:loop:name|, 
    - Prefix functions: all:, avg:, total:, max:, min:
    
    Args:
        template: Template string with $ variables
        api_response: Complete API response
        
    Returns:
        Rendered string
    """
    def replacer(match):
        var_path = match.group(1)  # path.to.value
        modifiers = match.group(2)  # everything after first :
        
        # Check for prefix functions (all:, avg:, total:, max:, min:)
        prefix_func = None
        if ':' in var_path:
            first_part = var_path.split(':')[0]
            if first_part in ['all', 'avg', 'total', 'max', 'min']:
                prefix_func = first_part
                var_path = var_path.split(':', 1)[1]
        
        # Resolve value
        value = resolve_variable_path(f'${var_path}', api_response)
        
        if value is None:
            return ''
        
        # Apply prefix function if specified
        if prefix_func:
            value = apply_prefix_function(value, prefix_func)
        
        # Apply modifiers if specified
        if modifiers:
            value = apply_modifiers(value, modifiers)
        
        return str(value) if value is not None else ''
    
    return VARIABLE_REGEX.sub(replacer, template)


def apply_prefix_function(value: Any, func: str) -> Any:
    """
    Apply prefix function to a value.
    
    Supported functions:
    - all: Return all items (identity)
    - avg: Average of numeric list
    - total: Sum of numeric list
    - max: Maximum value
    - min: Minimum value
    
    Args:
        value: Value to process
        func: Function name
        
    Returns:
        Processed value
    """
    if not isinstance(value, list):
        return value
    
    if func == 'all':
        return value
    
    elif func == 'avg':
        try:
            numeric_values = [float(v) for v in value if isinstance(v, (int, float))]
            return sum(numeric_values) / len(numeric_values) if numeric_values else 0
        except (ValueError, ZeroDivisionError):
            return 0
    
    elif func == 'total':
        try:
            numeric_values = [float(v) for v in value if isinstance(v, (int, float))]
            return sum(numeric_values)
        except ValueError:
            return 0
    
    elif func == 'max':
        try:
            return max(value)
        except (ValueError, TypeError):
            return None
    
    elif func == 'min':
        try:
            return min(value)
        except (ValueError, TypeError):
            return None
    
    return value


def apply_modifiers(value: Any, modifiers: str) -> Any:
    """
    Apply modifiers to a value.
    
    Supported modifiers:
    - count: Return array length
    - loop:field|sep: Loop over array and join
    - filter:key=val: Filter array by condition
    - max:N: Limit to N items (works with loop)
    - Standard filters: year, upper, lower, 02d, etc.
    
    Args:
        value: Value to modify
        modifiers: Colon-separated modifiers
        
    Returns:
        Modified value
    """
    # Parse modifiers
    parts = modifiers.split(':')
    
    for i, part in enumerate(parts):
        part = part.strip()
        
        if not part:
            continue
        
        # Count modifier
        if part == 'count':
            if isinstance(value, (list, dict)):
                value = len(value)
            else:
                value = 0
        
        # Filter modifier: filter:key=val
        elif part == 'filter' and i + 1 < len(parts):
            filter_expr = parts[i + 1]
            if '=' in filter_expr and isinstance(value, list):
                key, expected = filter_expr.split('=', 1)
                value = [item for item in value if isinstance(item, dict) and item.get(key) == expected]
                parts[i + 1] = ''  # Mark as consumed
        
        # Loop modifier: loop:field|sep
        elif part == 'loop' and i + 1 < len(parts):
            loop_spec = parts[i + 1]
            if '|' in loop_spec:
                field, separator = loop_spec.rsplit('|', 1)
                field = field.strip()
                separator = separator.strip()
                
                if isinstance(value, list):
                    # Extract field from each item
                    items = []
                    for item in value:
                        if isinstance(item, dict):
                            # Support nested fields like "name → character"
                            if '→' in field or '->' in field:
                                field_parts = field.replace('→', '->').split('->')
                                field_values = [item.get(f.strip(), '') for f in field_parts]
                                items.append(' → '.join(str(v) for v in field_values if v))
                            else:
                                field_value = item.get(field, '')
                                if field_value:
                                    items.append(str(field_value))
                        elif isinstance(item, str):
                            items.append(item)
                        # Skip non-dict, non-str items
                    
                    value = separator.join(items)
                elif isinstance(value, str):
                    value = value  # Already a string
                else:
                    value = str(value)
                
                parts[i + 1] = ''  # Mark as consumed
            else:
                # Simple loop without field extraction
                if isinstance(value, list):
                    # Try to extract sensible string repr
                    items = []
                    for item in value:
                        if isinstance(item, str):
                            items.append(item)
                        elif isinstance(item, dict):
                            # Try common name fields
                            name = item.get('name') or item.get('title') or item.get('label') or str(item)
                            items.append(str(name))
                        else:
                            items.append(str(item))
                    value = ', '.join(items)
        
        # Max modifier: max:N (limit array or string length)
        elif part == 'max' and i + 1 < len(parts):
            try:
                limit = int(parts[i + 1])
                if isinstance(value, list):
                    value = value[:limit]
                elif isinstance(value, str):
                    value = value[:limit]
                parts[i + 1] = ''  # Mark as consumed
            except (ValueError, IndexError):
                pass
        
        # Standard filters (year, upper, lower, format, etc.)
        elif part not in ['', 'filter', 'loop', 'max']:
            value = apply_filter(value, part)
    
    return value
