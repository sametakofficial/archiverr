# Variable Syntax

Complete syntax reference for variable resolution and manipulation.

## Basic Syntax

```
{variable}                  Simple variable access
{variable.field}            Nested field access
{variable.array.1}          Array element (1-based indexing)
{variable:filter}           Apply single filter
{variable:f1:f2:f3}         Chain multiple filters
{variable:02d}              Python format specifier
{variable.field:filter}     Combined nested + filter
```

## Variable Access

### Simple Variables

```yaml
{showName}                  # Breaking Bad
{movieYear}                 # 2008
{episodeNumber}             # 4
{voteAverage}               # 9.5
```

### Nested Field Access

```yaml
{tmdb.first_air_date}       # 2008-01-20
{tmdb.vote_average}         # 9.5
{tmdb.genres.1.name}        # Drama
{ffprobe.streams.0.codec}   # h264
```

### Array Access (1-based)

```yaml
{cast.1.name}               # First cast member
{cast.2.name}               # Second cast member
{audio.1.codec}             # First audio codec
{audio.2.language}          # Second audio language
{keywords.1.name}           # First keyword
```

**Important:** Arrays use 1-based indexing (not 0-based).

## Filters

### Text Filters

```
:upper              UPPERCASE CONVERSION
:lower              lowercase conversion
:title              Title Case Conversion
:slug               url-safe-slug-conversion
:trim               Remove leading/trailing whitespace
:snake              convert_to_snake_case
:camel              convertToCamelCase
```

Examples:
```yaml
{showName:upper}                # BREAKING BAD
{showName:lower}                # breaking bad
{showName:slug}                 # breaking-bad
{showName:snake}                # breaking_bad
{showName:camel}                # breakingBad
```

### Numeric Filters

```
:pad:N              Zero-pad to N digits
:max:N              Maximum N digits
```

Examples:
```yaml
{seasonNumber:pad:2}            # 01, 02, 03
{episodeNumber:pad:3}           # 001, 002, 003
{seasonNumber:max:2}            # 12 → 12, 123 → 99
```

### Date Filters

```
:year               Extract year from date
```

Examples:
```yaml
{firstAirDate:year}             # 2008-01-20 → 2008
{releaseDate:year}              # 1999-03-31 → 1999
{episodeAirDate:year}           # 2024-05-15 → 2024
```

### Format Specifiers

Python format syntax supported:

```
:02d                Zero-pad integer to 2 digits
:03d                Zero-pad integer to 3 digits
:04d                Zero-pad integer to 4 digits
:.1f                Float with 1 decimal place
:.2f                Float with 2 decimal places
```

Examples:
```yaml
{seasonNumber:02d}              # 1 → 01
{episodeNumber:03d}             # 5 → 005
{voteAverage:.1f}               # 9.543 → 9.5
{took:.2f}                      # 1.23456 → 1.23
```

## Filter Chaining

Filters applied left-to-right:

```yaml
{showName:lower:slug}           # Breaking Bad → breaking-bad
{showName:upper:trim}           # " Breaking Bad " → "BREAKING BAD"
{genreName:lower:snake}         # "Science Fiction" → science_fiction
```

## Conditionals

### Basic Conditions

```yaml
where: "voteAverage > 8.0"
where: "seasonNumber == 1"
where: "videoHeight >= 1080"
where: "genreName == 'Drama'"
where: "cast.1.name == 'Bryan Cranston'"
```

### Operators

```
==      Equal
!=      Not equal
>       Greater than
<       Less than
>=      Greater than or equal
<=      Less than or equal
```

### Logical Operators

```
and     Logical AND
or      Logical OR
not     Logical NOT
```

Examples:
```yaml
where: "voteAverage > 8.0 and videoHeight >= 2160"
where: "genreName == 'Drama' or genreName == 'Thriller'"
where: "not (seasonNumber == 1 and episodeNumber == 1)"
```

### Membership Test

```
in      Check if value in list
```

Examples:
```yaml
where: "genreName in ['Drama', 'Comedy', 'Action']"
where: "video.codec in ['hevc', 'av1']"
where: "'space' in keywords.1.name"
```

### Field Existence Check

```yaml
where: "subtitle.1.language"          # True if subtitle exists
where: "not cast.10.name"             # True if less than 10 cast
where: "director"                     # True if director exists
```

## Loops

### Basic Loop

```yaml
- loop:
    var: quality
    in: [2160, 1080, 720]
  where: "videoHeight == quality"
  save: "/Movies-{quality}p/{name}"
```

### Loop with Variable Access

```yaml
- loop:
    var: year
    in: [2024, 2023, 2022]
  where: "firstAirYear == year"
  save: "/{year}/{showName}"
  print: "📁 {year}: {showName}"
```

### Nested Loops

```yaml
- loop:
    var: year
    in: [2024, 2023]
  loop:
    var: quality
    in: [2160, 1080]
  where: "movieYear == year and videoHeight == quality"
  save: "/{year}/{quality}p/{name}"
```

### Loop with String Values

```yaml
- loop:
    var: genre
    in: ["Drama", "Comedy", "Action", "Sci-Fi"]
  where: "genreName == genre"
  save: "/Genres/{genre}/{showName}"
```

## Advanced Usage

### Combined Nested + Filter

```yaml
{tmdb.first_air_date:year}          # Nested + filter
{cast.1.name:upper}                 # Array + filter
{audio.1.codec:upper}               # Array + nested + filter
```

### Multiple Array Access

```yaml
{cast.1.name}, {cast.2.name}, {cast.3.name}
{audio.1.language} | {audio.2.language}
{keywords.1.name}, {keywords.2.name}
```

### Complex Conditions

```yaml
where: "(videoHeight >= 2160 or video.codec == 'hevc') and voteAverage >= 8.0"
where: "numberOfSeasons >= 5 and voteAverage > 7.5 and genreName in ['Drama', 'Thriller']"
where: "cast.1.name in ['Bryan Cranston', 'Aaron Paul'] and firstAirYear >= 2008"
```

### Conditional Pattern Selection

```yaml
queries:
  - where: "videoHeight >= 2160"
    save: "/4K/{name}"
  
  - where: "videoHeight >= 1080"
    save: "/HD/{name}"
  
  - where: "videoHeight >= 720"
    save: "/SD/{name}"
  
  - save: "/Other/{name}"              # Default (no condition)
```

## Pattern Examples

### TV Series

```yaml
# Basic
"{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"

# With episode name
"{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d} - {episodeName}"

# With year
"{showName} ({firstAirYear})/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d}"

# With quality
"{showName}/Season {seasonNumber}/{showName} - S{seasonNumber:02d}E{episodeNumber:02d} [{video.resolution}p]"

# Flat structure
"{showName} - S{seasonNumber:02d}E{episodeNumber:02d} - {episodeName}"
```

### Movies

```yaml
# Basic
"{name} ({movieYear})/{name} ({movieYear})"

# With IMDB ID
"{name} ({movieYear})/{name} ({movieYear}) - {imdb_id}"

# With quality
"{name} ({movieYear})/{name} ({movieYear}) [{video.resolution}p]"

# With codec
"{name} ({movieYear})/{name} ({movieYear}) [{video.codec:upper}]"

# Complex
"{name} ({movieYear})/{name} ({movieYear}) [{video.resolution}p] [{video.codec:upper}] [{audio.1.codec:upper}]"
```

## Variable Resolution Order

1. Query loop variables (if in loop context)
2. File metadata (path, filename, extension)
3. API metadata (TV/Movie variables)
4. Extras metadata (if enabled)
5. FFprobe metadata (if enabled)
6. Nested field access
7. Array indexing (1-based)
8. Filter application
9. Format specifier application

## Error Handling

```yaml
# Missing variables → empty string
{nonexistent}                       # ""
{cast.99.name}                      # "" (array out of bounds)
{tmdb.missing.field}                # "" (field doesn't exist)

# Invalid filters → warning logged, filter skipped
{showName:invalidfilter}            # "Breaking Bad" (filter ignored)

# Type mismatch → conversion attempted
{voteAverage:02d}                   # 9.5 → 09 (float to int)
```

## Performance Notes

- Simple variables fastest (direct access)
- Nested access adds minimal overhead
- Array indexing requires bounds check
- Filters add processing time
- Multiple filters compound overhead
- Complex conditions evaluated per file
- Loops multiply operations
