# Query System

Complete query engine reference for rename patterns and conditionals.

## Pattern Syntax

```yaml
rename:
  series:
    save: "{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
    print: "✓ {showName} S{seasonNumber:02d}E{episodeNumber:02d}"
```

### Variable Resolution

```
{variable}              Simple variable access
{variable.field}        Nested field access
{variable.array.1}      Array access (1-based indexing)
{variable:filter}       Single filter application
{variable:f1:f2}        Chained filters
{variable:02d}          Python format specifier
```

### Operators

```
==      Equal
!=      Not equal
>       Greater than
<       Less than
>=      Greater than or equal
<=      Less than or equal
and     Logical AND
or      Logical OR
not     Logical NOT
in      Membership test
```

## Conditionals (where)

```yaml
queries:
  - where: "videoHeight >= 2160"
    save: "/4K/{name}"
  
  - where: "seasonNumber == 1 and episodeNumber == 1"
    save: "/Pilots/{showName}"
  
  - where: "cast.1.name == 'Bryan Cranston'"
    save: "/Bryan/{showName}"
```

### Field Access in Conditions

```yaml
where: "tmdb.vote_average > 8.0"
where: "audio.1.language == 'eng'"
where: "video.codec in ['hevc', 'av1']"
where: "numberOfSeasons > 5 and voteAverage > 7"
```

## Loops (loop)

```yaml
queries:
  - loop:
      var: quality
      in: [2160, 1080, 720, 480]
    where: "videoHeight == quality"
    save: "/Movies-{quality}p/{name}"
```

### Loop Variables

```yaml
# Quality-based organization
- loop:
    var: q
    in: [2160, 1080, 720]
  where: "videoHeight == q"
  save: "/TV-{q}p/{showName}"

# Year-based organization
- loop:
    var: year
    in: [2023, 2022, 2021, 2020]
  where: "firstAirYear == year"
  save: "/{year}/{showName}"

# Genre-based organization
- loop:
    var: genre
    in: ["Drama", "Comedy", "Action"]
  where: "genreName == genre"
  save: "/{genre}/{showName}"
```

### Nested Loops

```yaml
- loop:
    var: year
    in: [2023, 2022]
  loop:
    var: quality
    in: [2160, 1080]
  where: "movieYear == year and videoHeight == quality"
  save: "/{year}/{quality}p/{name}"
```

## Filters

### Text Filters

```
:upper          Convert to UPPERCASE
:lower          Convert to lowercase
:title          Convert To Title Case
:slug           convert-to-url-safe-slug
:trim           Remove leading/trailing whitespace
:snake          convert_to_snake_case
:camel          convertToCamelCase
```

### Numeric Filters

```
:pad:N          Zero-pad to N digits (e.g., :pad:2 → 01)
:max:N          Maximum N digits
```

### Date Filters

```
:year           Extract year from date (2024-01-15 → 2024)
```

### Format Specifiers

```
:02d            Zero-pad 2 digits
:03d            Zero-pad 3 digits
:.1f            One decimal place (8.5)
:.2f            Two decimal places (8.52)
```

## Print Templates

```yaml
rename:
  series:
    print: |
      ✓ SHOW: {showName} ({firstAirYear})
        S{seasonNumber:02d}E{episodeNumber:02d} - {episodeName}
        Rating: {voteAverage}/10 | API: {apiSource}
```

### Multi-line Prints

```yaml
print: |
  ✓ {showName}
    Cast: {cast.1.name}, {cast.2.name}, {cast.3.name}
    Director: {director}
    Posters: {postersCount} | Rating: {voteAverage}/10
```

## Summary Templates

```yaml
summary:
  print: |
    Total: {total_time:.2f}s
    Average: {avg_time:.2f}s
    Min: {min_time:.2f}s | Max: {max_time:.2f}s
    Success: {success} | Failed: {failed}
```

### Summary Variables

```
{total_time}        Total processing time
{avg_time}          Average per file
{min_time}          Fastest file
{max_time}          Slowest file
{success}           Successful operations
{failed}            Failed operations
{total}             Total files
```

## Advanced Patterns

### Conditional Formatting

```yaml
save: "{showName}/{seasonNumber and 'Season ' + seasonNumber or 'Specials'}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"
```

### Multiple Filters

```yaml
save: "{showName:lower:slug}/season-{seasonNumber}"
```

### Nested Field Access

```yaml
print: "Director: {crew.1.name} | Cinematographer: {crew.2.name}"
print: "Audio: {audio.1.codec} {audio.1.language}"
print: "Genres: {tmdb.genres.1.name}, {tmdb.genres.2.name}"
```

### Array Iteration

```yaml
print: "Cast: {cast.1.name}, {cast.2.name}, {cast.3.name}"
print: "Keywords: {keywords.1.name}, {keywords.2.name}, {keywords.3.name}"
```

## Query Execution Order

1. Load file metadata
2. Apply API matching
3. Evaluate `where` conditions
4. Execute `loop` iterations
5. Render `save` pattern
6. Render `print` template
7. Execute file operation

## Context Variables

Variables available in all templates:

```
File Context:
  {path}            Original file path
  {filename}        Original filename
  {extension}       File extension
  {took}            Processing time (seconds)

Metadata Context:
  {apiSource}       API used (tmdb, tvdb, tvmaze, omdb)
  All TV/Movie variables
  All Extras variables (if enabled)
  All FFprobe variables (if enabled)
```

## Error Handling

```yaml
# Missing variables resolve to empty string
save: "{showName}/Season {seasonNumber}/{episodeName}"  # episodeName missing → ignored

# Failed conditions skip query
where: "nonexistent.field == 1"  # Skips this query

# Invalid operators log warning
where: "seasonNumber === 1"  # Logs warning, skips query
```

## Performance Notes

- Conditions evaluated before file operations
- Loops multiply operations (use sparingly)
- Print templates only evaluated if defined
- Empty results skip file operations
