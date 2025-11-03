# Future Feature Notes

## Force Variable (Cross-API Data Fetching)

### Concept
When a variable is used in a template but the current API doesn't support it, automatically fetch that specific data from another API that does support it.

### Example Scenario
```yaml
tvmaze:
  tv_primary: true  # Primary for TV shows

tmdb:
  tv_priority: 2    # Fallback

# Template uses a TVMaze-unsupported variable
series:
  print: "{showName} - {tmdb.vote_average} stars"  # vote_average only in TMDb
```

**Current Behavior**: `{tmdb.vote_average}` would be empty when using TVMaze

**With force_variable**: 
1. Detect that `tmdb.vote_average` is needed
2. Check if current API (TVMaze) supports it → No
3. Find which API supports `vote_average` → TMDb
4. Make additional request to TMDb for just that show
5. Merge the data into context
6. Render template with complete data

### Implementation Notes

**Variable Support Matrix** (to be built):
```python
VARIABLE_SUPPORT = {
    "vote_average": ["tmdb"],
    "imdb_id": ["tmdb", "tvdb", "omdb"],
    "guest_stars": ["tvdb"],
    "premiered": ["tvmaze", "tmdb", "tvdb"],
    # ... etc
}
```

**Config Option**:
```yaml
options:
  force_variable: true  # Enable cross-API fetching (default: true)
  max_api_calls_per_file: 3  # Limit to prevent excessive requests
```

### Performance Considerations
- Cache cross-API fetches to avoid duplicate requests
- Only fetch when variable is actually used in template
- Add timeout limits per file
- Consider batch requests where possible

### Priority
- **Low priority** for now
- Implement after TVDb and OMDb are added
- Most users won't need variables from multiple APIs simultaneously
- Current approach (single API per file) covers 95% of use cases

### Related Files
- `src/archiverr/core/matching/api_manager.py` - Would need `fetch_variable()` method
- `src/archiverr/engines/yaml/variable_engine.py` - Detect missing variables
- Config models - Add `force_variable` option

---

*Note: User specifically mentioned this feature but agreed to postpone implementation until core multi-API system is stable and tested.*
