# Query Examples

Real-world query scenarios for media organization.

## Quality-Based Organization

```yaml
query_engine:
  queries:
    - name: "4K Movies"
      where: "videoHeight >= 2160"
      save: "/media/Movies-4K/{name} ({movieYear})"
    
    - name: "1080p Movies"
      where: "videoHeight >= 1080 and videoHeight < 2160"
      save: "/media/Movies-1080p/{name} ({movieYear})"
    
    - name: "720p Movies"
      where: "videoHeight >= 720 and videoHeight < 1080"
      save: "/media/Movies-720p/{name} ({movieYear})"
```

## Year-Based Organization

```yaml
query_engine:
  queries:
    - loop:
        var: year
        in: [2024, 2023, 2022, 2021, 2020]
      where: "movieYear == year"
      save: "/media/Movies/{year}/{name} ({movieYear})"
    
    - where: "movieYear < 2020"
      save: "/media/Movies/Archive/{name} ({movieYear})"
```

## Actor-Based Organization

```yaml
query_engine:
  queries:
    - name: "Bryan Cranston"
      where: "cast.1.name == 'Bryan Cranston' or cast.2.name == 'Bryan Cranston'"
      save: "/media/Actors/Bryan Cranston/{showName}"
    
    - name: "Leonardo DiCaprio"
      where: "'Leonardo DiCaprio' in cast.1.name or 'Leonardo DiCaprio' in cast.2.name"
      save: "/media/Actors/Leonardo DiCaprio/{name}"
```

## Genre-Based Organization

```yaml
query_engine:
  queries:
    - loop:
        var: genre
        in: ["Drama", "Comedy", "Action", "Sci-Fi", "Horror"]
      where: "genreName == genre"
      save: "/media/TV/{genre}/{showName}"
    
    - where: "genreName not in ['Drama', 'Comedy', 'Action', 'Sci-Fi', 'Horror']"
      save: "/media/TV/Other/{showName}"
```

## Rating-Based Organization

```yaml
query_engine:
  queries:
    - name: "Highly Rated (9+)"
      where: "voteAverage >= 9.0"
      save: "/media/Top-Rated/{showName}"
      print: "⭐ {showName} - {voteAverage}/10"
    
    - name: "Good (7-9)"
      where: "voteAverage >= 7.0 and voteAverage < 9.0"
      save: "/media/Good/{showName}"
    
    - name: "Average (<7)"
      where: "voteAverage < 7.0"
      save: "/media/Average/{showName}"
```

## Codec-Based Organization

```yaml
query_engine:
  queries:
    - name: "HEVC/H.265"
      where: "video.codec == 'hevc'"
      save: "/media/HEVC/{name}"
    
    - name: "AV1"
      where: "video.codec == 'av1'"
      save: "/media/AV1/{name}"
    
    - name: "H.264"
      where: "video.codec == 'h264'"
      save: "/media/H264/{name}"
```

## Language-Based Organization

```yaml
query_engine:
  queries:
    - name: "English Audio"
      where: "audio.1.language == 'eng'"
      save: "/media/English/{showName}"
    
    - name: "Turkish Audio"
      where: "audio.1.language == 'tur'"
      save: "/media/Turkish/{showName}"
    
    - name: "Multi-Audio"
      where: "audioCount > 1"
      save: "/media/Multi-Audio/{showName}"
      print: "🔊 {showName} - {audioCount} audio tracks"
```

## Network-Based Organization

```yaml
query_engine:
  queries:
    - name: "Netflix Originals"
      where: "networkName == 'Netflix'"
      save: "/media/Netflix/{showName}"
    
    - name: "HBO"
      where: "networkName == 'HBO'"
      save: "/media/HBO/{showName}"
    
    - name: "AMC"
      where: "networkName == 'AMC'"
      save: "/media/AMC/{showName}"
```

## Season-Based Organization

```yaml
query_engine:
  queries:
    - name: "Pilots"
      where: "seasonNumber == 1 and episodeNumber == 1"
      save: "/media/Pilots/{showName} - Pilot"
      print: "🎬 Pilot: {showName}"
    
    - name: "Series Finales"
      where: "seasonNumber == numberOfSeasons and episodeNumber == numberOfEpisodes"
      save: "/media/Finales/{showName} - Finale"
      print: "🏁 Finale: {showName}"
    
    - name: "Long-Running Shows (5+ seasons)"
      where: "numberOfSeasons >= 5"
      save: "/media/Long-Running/{showName}"
```

## Multi-Criteria Organization

```yaml
query_engine:
  queries:
    - name: "4K Drama High-Rated"
      where: "videoHeight >= 2160 and genreName == 'Drama' and voteAverage >= 8.0"
      save: "/media/Premium/Drama/{showName}"
      print: "💎 {showName} - {voteAverage}/10 - 4K"
    
    - name: "HD Comedy Recent"
      where: "videoHeight >= 1080 and genreName == 'Comedy' and firstAirYear >= 2020"
      save: "/media/Recent/Comedy/{showName}"
```

## Nested Loop Organization

```yaml
query_engine:
  queries:
    - loop:
        var: year
        in: [2024, 2023, 2022]
      loop:
        var: quality
        in: [2160, 1080]
      where: "movieYear == year and videoHeight == quality"
      save: "/media/{year}/{quality}p/{name}"
      print: "📁 {year}/{quality}p - {name}"
```

## Complex Conditional Organization

```yaml
query_engine:
  queries:
    - name: "Premium Content"
      where: "(videoHeight >= 2160 or video.codec == 'hevc') and voteAverage >= 8.0 and audioCount >= 2"
      save: "/media/Premium/{name}"
      print: |
        💎 PREMIUM: {name}
        Quality: {video.resolution}p {video.codec}
        Rating: {voteAverage}/10
        Audio: {audioCount} tracks
    
    - name: "Standard Content"
      where: "videoHeight >= 720 and videoHeight < 2160 and voteAverage >= 6.0"
      save: "/media/Standard/{name}"
```

## Subtitle-Based Organization

```yaml
query_engine:
  queries:
    - name: "With Subtitles"
      where: "subtitle.1.language"
      save: "/media/Subtitled/{showName}"
      print: "📝 {showName} - Subtitles: {subtitle.1.language}"
    
    - name: "No Subtitles"
      where: "not subtitle.1.language"
      save: "/media/No-Subs/{showName}"
```

## Director-Based Organization

```yaml
query_engine:
  queries:
    - name: "Christopher Nolan"
      where: "director == 'Christopher Nolan'"
      save: "/media/Directors/Christopher Nolan/{name}"
      print: "🎬 Nolan: {name}"
    
    - name: "Quentin Tarantino"
      where: "director == 'Quentin Tarantino'"
      save: "/media/Directors/Quentin Tarantino/{name}"
```

## Keyword-Based Organization

```yaml
query_engine:
  queries:
    - name: "Space Theme"
      where: "'space' in keywords.1.name or 'space' in keywords.2.name"
      save: "/media/Themes/Space/{name}"
    
    - name: "Time Travel"
      where: "'time travel' in keywords.1.name"
      save: "/media/Themes/Time-Travel/{name}"
```

## Watch Provider Organization

```yaml
query_engine:
  queries:
    - name: "Netflix Available"
      where: "'Netflix' in watchProviders.US.flatrate.1.name"
      save: "/media/Streaming/Netflix/{showName}"
    
    - name: "Amazon Prime"
      where: "'Amazon Prime' in watchProviders.US.flatrate.1.name"
      save: "/media/Streaming/Prime/{showName}"
```

## Runtime-Based Organization

```yaml
query_engine:
  queries:
    - name: "Short Films (<60min)"
      where: "runtime < 60"
      save: "/media/Short/{name}"
    
    - name: "Feature Films (60-180min)"
      where: "runtime >= 60 and runtime <= 180"
      save: "/media/Features/{name}"
    
    - name: "Long Films (>180min)"
      where: "runtime > 180"
      save: "/media/Long/{name}"
      print: "⏱️ {name} - {runtime} minutes"
```

## Content Rating Organization

```yaml
query_engine:
  queries:
    - name: "Family Content (G, PG)"
      where: "contentRating in ['G', 'PG', 'TV-G', 'TV-PG']"
      save: "/media/Family/{showName}"
    
    - name: "Teen Content (PG-13, TV-14)"
      where: "contentRating in ['PG-13', 'TV-14']"
      save: "/media/Teen/{showName}"
    
    - name: "Mature Content (R, TV-MA)"
      where: "contentRating in ['R', 'NC-17', 'TV-MA']"
      save: "/media/Mature/{showName}"
```

## Combined Example

```yaml
query_engine:
  queries:
    # Premium 4K content
    - where: "videoHeight >= 2160 and voteAverage >= 8.0"
      save: "/media/4K-Premium/{showName}"
      print: "💎 4K Premium: {showName} - {voteAverage}/10"
    
    # Quality-based with year
    - loop:
        var: q
        in: [1080, 720]
      where: "videoHeight >= q and videoHeight < (q + 360) and firstAirYear >= 2020"
      save: "/media/{q}p-Recent/{showName}"
    
    # Genre and rating combined
    - loop:
        var: genre
        in: ["Drama", "Comedy", "Action"]
      where: "genreName == genre and voteAverage >= 7.5"
      save: "/media/Quality-{genre}/{showName}"
    
    # Archive old content
    - where: "firstAirYear < 2015 and voteAverage < 7.0"
      save: "/media/Archive/{firstAirYear}/{showName}"
```
