# System Patterns

## Core Architecture

### Plugin-Agnostic Principle (STRICTLY ENFORCED)

**Rule:** Core system MUST NEVER know plugin names or implementations.

**Status (November 10, 2025):**
- ✅ No hardcoded plugin names in core
- ✅ All patterns are generic
- ✅ Dynamic imports only
- ✅ Config opaque to core
- ✅ Clean folder structure (plugins/, tasks/, reports/)
- ✅ Consistent naming (globals everywhere)

---

## Expects System Pattern

Check data availability at runtime before plugin execution.

```python
# Extract available data
available_data = self._extract_available_data(result)

# Filter plugins by expects
ready = [p for p in group if resolver.check_expects(p, available_data)]

# Execute only ready plugins
results = self.execute_group(plugins, ready, result)
```

---

## Compact Response Pattern (NEW - November 10, 2025)

Structural simplification - show API structure, not content.

```python
class ResponseSimplifier:
    def _simplify_list(self, data: List[Any]) -> List[Any]:
        seen_types = set()
        examples = []
        
        for item in data:
            item_type = "object" if isinstance(item, dict) else type(item).__name__
            
            # Keep first example of each type
            if item_type not in seen_types:
                seen_types.add(item_type)
                examples.append(item)
        
        return [self.simplify(item) for item in examples]
```

**Purpose:** AI can analyze structure without processing massive data.

**Results:**
- 101 cast → 1 example
- 16 keywords → 1 example
- 94% file size reduction

---

## Design Principles

1. **Plugin-Agnostic**: Core never knows plugin names
2. **Expects-Based**: Runtime data validation
3. **Generic Patterns**: Work with any plugin
4. **Professional Debug**: Consistent logging
5. **Clean Separation**: Core vs plugins vs tasks
6. **Structural Simplification**: Type-based, not content-based
7. **Dual Reports**: Full data + compact structure

---

## Folder Structure Pattern

**Clean Naming (November 10, 2025):**
```
src/archiverr/core/
├── plugins/     # NOT plugin_system
├── tasks/       # NOT task_system
└── reports/     # NEW: Response simplification
```

**No _system suffixes** - cleaner, more professional.

---

## Response Naming Pattern

**Consistent globals naming:**
```json
{
  "globals": {...},         // API-level
  "matches": [{
    "globals": {...}        // Match-level (NOT match_globals)
  }]
}
```

**Template access:**
- `$globals` → API-level
- `$0.globals` → Match 0 level
- No naming conflicts!

---

For implementation details, see activeContext.md
