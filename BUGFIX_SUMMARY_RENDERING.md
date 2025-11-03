# Bug Fix: Summary Rendering Error

## Problem
Summary template rendering failed with `KeyError` when variables were missing from context:
```
Summary render error: 'showName'
```

## Root Cause
The summary template in `config.yml` uses Python format strings with TV show variables like `{showName}`, `{seasonNumber:02d}`, etc. 

When these variables weren't in the context (e.g., no files processed, or last file was a movie instead of TV show), Python's standard `.format()` method threw a `KeyError`.

## Error Flow
1. User runs: `archiverr --paths-from tests/targets.txt --type tv --dry-run`
2. Engine processes files successfully
3. At summary time, tries to render template with last file's context
4. Template expects TV variables: `{showName}`, `{seasonNumber:02d}`, etc.
5. Standard Python `.format()` throws `KeyError` for missing variables
6. Error message: `Summary render error: 'showName'`

## Solution

### Two-Pronged Approach

#### 1. Default Values (engine.py)
Added comprehensive default values for all possible variables in summary context:

```python
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
    # ... and many more
}
```

#### 2. SafeFormatter (engine.py & query_logger.py)
Created `SafeFormatter` class that returns empty string for missing keys instead of raising `KeyError`:

```python
from string import Formatter

class SafeFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, '')
        return super().get_value(key, args, kwargs)

formatter = SafeFormatter()
summary_text = formatter.format(config.summary.print, **summary_ctx)
```

## Files Modified

### 1. `/src/archiverr/core/renamer/engine.py`
- Added default values for all TV/movie/extras variables in summary context
- Implemented `SafeFormatter` for safe template rendering
- Summary now renders successfully even with missing variables

### 2. `/src/archiverr/core/renamer/query_logger.py`
- Updated `render_query_print()` to use `SafeFormatter` instead of raw `.format()`
- Ensures consistent behavior across all template rendering
- Better handling of format specs like `{took:.2f}s`

## Benefits

1. **No More Crashes**: Summary always renders successfully
2. **Graceful Degradation**: Missing variables show as empty strings
3. **Consistency**: Same SafeFormatter used in both summary and print templates
4. **Format Spec Support**: Works with Python format specs like `{var:02d}`, `{var:.2f}`
5. **Backward Compatible**: Existing templates continue to work

## Testing

Created verification script: `verify_summary_fix.py`

Tests:
- ✅ Standard `.format()` fails with KeyError (expected)
- ✅ `SafeFormatter` handles missing variables gracefully
- ✅ `SafeFormatter` works with complete context
- ✅ `SafeFormatter` works with default empty values

## Before vs After

### Before (Broken)
```bash
$ archiverr --paths-from tests/targets.txt --type tv --dry-run
# ... processing output ...
Summary render error: 'showName'
```

### After (Fixed)
```bash
$ archiverr --paths-from tests/targets.txt --type tv --dry-run
# ... processing output ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 İşlem Özeti
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Toplam Dosya    : 1
Başarılı        : 1
# ... complete summary renders successfully ...
```

## Related Patterns

### Variable Engine (variable_engine.py)
Already handles missing variables gracefully by returning `None` → converted to empty string:
```python
def replacer(match):
    token = match.group(1)
    value = resolve_variable(token, context)
    return str(value) if value is not None else ""  # Safe
```

### Query Logger (query_logger.py)
Two-pass rendering:
1. First pass: `variable_engine.render_template()` - handles `{var:filter}` syntax
2. Second pass: `SafeFormatter.format()` - handles Python format specs like `{var:.2f}`

## Prevention

To prevent similar issues in the future:
1. Always use `SafeFormatter` instead of raw `.format()` for user templates
2. Provide comprehensive default values when building contexts
3. Test templates with minimal/empty contexts
4. Use exception handling as last resort, not primary strategy

## Date
2025-11-03

## Author
Cascade (AI Assistant)
