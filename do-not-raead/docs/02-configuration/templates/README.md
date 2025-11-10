# External YAML Templates

This folder contains example external YAML template files that can be used with CLI parameters.

## Usage

### Series Print Template
```bash
archiverr --series-print templates/series_print.yml --type tv --path "Show S01E01.mkv"
```

### Summary Template
```bash
archiverr --summary-print templates/summary_print.yml --paths-from files.txt
```

### Queries
```bash
archiverr --queries templates/queries_example.yml --paths-from files.txt
```

## CLI Parameters

- `--movie-print <file.yml>` - Override movie print template
- `--series-print <file.yml>` - Override series print template
- `--summary-print <file.yml>` - Override summary template
- `--queries <file.yml>` - Load queries from external file

## Template Format

### Print Templates (series_print.yml, summary_print.yml)
```yaml
print: |
  Your template here
  {variable1}
  {variable2}
```

### Queries Template (queries_example.yml)
```yaml
- name: "Query Name"
  where: "condition"
  print: "Output format"
  save: "/path/{variable}/"
  loop:
    var: q
    in: [value1, value2]
```

## Config Overrides

All config options can also be overridden via CLI:

```bash
# Enable debug mode
archiverr --debug --path "file.mkv"

# Allow virtual paths
archiverr --allow-virtual-paths --path "NonExistent.mkv"

# Use hardlinks
archiverr --hardlink --path "file.mkv"

# Force NFO overwrite
archiverr --nfo-enable --nfo-force --path "file.mkv"
```

## Benefits

1. **Modularity**: Keep templates in separate files
2. **Reusability**: Share templates between projects
3. **Version Control**: Track template changes separately
4. **Testing**: Test different templates without editing main config
5. **CI/CD**: Use different templates for different environments
