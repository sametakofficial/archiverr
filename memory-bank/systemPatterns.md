# System Patterns

## Core Architecture

### Plugin-Agnostic Principle (STRICTLY ENFORCED)

**Rule:** Core system MUST NEVER know plugin names or implementations.

**Fixed November 8, 2025:**
- ✅ No hardcoded plugin names in core
- ✅ All patterns are generic
- ✅ Dynamic imports only
- ✅ Config opaque to core

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

## Design Principles

1. **Plugin-Agnostic**: Core never knows plugin names
2. **Expects-Based**: Runtime data validation
3. **Generic Patterns**: Work with any plugin
4. **Professional Debug**: Consistent logging
5. **Clean Separation**: Core vs plugins vs tasks

---

For complete patterns, see AI_AGENT_CONTEXT.md
