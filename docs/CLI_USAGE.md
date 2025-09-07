# LogLog CLI Usage Guide

The LogLog Command Line Interface (CLI) provides powerful batch processing and automation capabilities for the LogLog hierarchical note-taking format.

## Installation

1. **Setup the CLI tool:**
   ```bash
   cd loglog
   python3 setup_cli.py
   ```

2. **Verify installation:**
   ```bash
   loglog --help
   ```

## Commands Overview

| Command | Description |
|---------|-------------|
| `convert` | Convert LogLog files to other formats (HTML, Markdown, LaTeX, PDF) |
| `filter` | Filter files by hashtags |
| `todos` | Extract and manage TODO items |
| `show` | Display file structure |
| `search` | Search content in files |
| `batch-convert` | Batch convert multiple files |
| `stats` | Show file statistics |

## Detailed Command Usage

### Convert Files

Convert LogLog files to other formats:

```bash
# Convert single file to HTML
loglog convert notes.log --to html

# Convert with custom title
loglog convert notes.log --to html --title "My Notes"

# Convert multiple files 
loglog convert *.log --to md

# Convert to specific directory
loglog convert notes.log --to pdf --output-dir exports/

# Convert with different header levels
loglog convert notes.log --to md --header-levels 6
```

**Available formats:**
- `html` - Interactive HTML with keyboard navigation
- `md` - Standard Markdown
- `latex` - LaTeX document
- `pdf` - PDF document (requires pdflatex)

### Filter by Hashtags

Extract content containing specific hashtags:

```bash
# Filter by single hashtag
loglog filter project.log --hashtags important --output important.log

# Filter by multiple hashtags
loglog filter project.log --hashtags decision,important --output filtered.log

# Preserve parent structure (default)
loglog filter project.log --hashtags meeting --preserve-structure --output meetings.log
```

### TODO Management

Extract and manage TODO items:

```bash
# Show all TODOs
loglog todos project.log

# Filter by status
loglog todos project.log --status pending
loglog todos project.log --status completed
loglog todos project.log --status in_progress

# Export to file
loglog todos project.log --status pending --output pending_tasks.log

# Export as JSON
loglog todos project.log --format json --output tasks.json

# Export as CSV
loglog todos project.log --format csv --output tasks.csv
```

**TODO Status Values:**
- `pending` - Incomplete tasks `[ ]`
- `completed` - Finished tasks `[x]`
- `in_progress` - Active tasks `[-]`
- `all` - All TODO items (default)

### Display Structure

View the hierarchical structure of LogLog files:

```bash
# Show full structure
loglog show notes.log

# Show with node numbers
loglog show notes.log --numbered

# Compact display (no decorations)
loglog show notes.log --compact

# Limit depth
loglog show notes.log --depth 3
```

### Search Content

Search for text patterns across files:

```bash
# Simple text search
loglog search "project status" *.log

# Regular expression search
loglog search "project.*status" notes.log --regex

# Case-sensitive search
loglog search "TODO" notes.log --case-sensitive

# Show context lines
loglog search "important" notes.log --context 2
```

### Batch Operations

Process multiple files efficiently:

```bash
# Convert all .log files to HTML
loglog batch-convert . --to html

# Recursive processing
loglog batch-convert . --to md --recursive

# Custom file pattern
loglog batch-convert docs/ --pattern "*.txt" --to html

# Convert from markdown to log
loglog batch-convert . --from md --to log
```

### File Statistics

Analyze LogLog files:

```bash
# Show statistics for single file
loglog stats project.log

# Analyze multiple files
loglog stats *.log

# JSON output for scripting
loglog stats project.log --format json
```

**Statistics include:**
- Total nodes count
- Maximum depth level
- TODO counts by status
- Hashtag frequency

## Advanced Usage Examples

### Workflow Integration

**1. Daily TODO Review:**
```bash
# Extract pending TODOs from all project files
loglog todos projects/*.log --status pending --output daily_todos.log

# Convert to HTML for browser viewing
loglog convert daily_todos.log --to html --title "Daily TODOs"
```

**2. Project Decision Tracking:**
```bash
# Filter all decision-related content
loglog filter project.log --hashtags decision --output decisions.log

# Generate decision summary report
loglog convert decisions.log --to pdf --title "Project Decisions"
```

**3. Meeting Notes Processing:**
```bash
# Extract meeting-related content
loglog filter *.log --hashtags meeting,action --output meeting_summary.log

# Create HTML dashboard
loglog convert meeting_summary.log --to html --title "Meeting Dashboard"
```

**4. Batch Export for Sharing:**
```bash
# Convert all documentation to markdown
loglog batch-convert docs/ --to md --recursive

# Create interactive HTML exports
loglog batch-convert . --pattern "*.log" --to html
```

### Scripting and Automation

**Get TODO counts in JSON for scripting:**
```bash
loglog stats *.log --format json | jq '.[] | {file: .file, todos: .todo_count}'
```

**Find files with high TODO counts:**
```bash
loglog stats *.log --format json | jq '.[] | select(.todo_count.total > 10) | .file'
```

**Batch process with error handling:**
```bash
#!/bin/bash
for file in *.log; do
    if loglog convert "$file" --to html --overwrite; then
        echo "✓ Converted $file"
    else
        echo "✗ Failed to convert $file"
    fi
done
```

## Configuration and Options

### Global Options

- `-v, --verbose` - Enable verbose output
- `--version` - Show version information

### File Patterns

The CLI supports standard shell glob patterns:
- `*.log` - All .log files
- `project_*.log` - Files starting with "project_"
- `**/*.log` - All .log files recursively (in batch-convert)

### Error Handling

- Files that don't exist are skipped with warnings
- Invalid LogLog format files show parsing errors
- Missing dependencies (like pdflatex) show helpful error messages
- Use `--verbose` for detailed error information

## Integration with Other Tools

### Pandoc Integration

LogLog CLI works well with pandoc for additional format conversions:

```bash
# Convert to more formats via markdown
loglog convert notes.log --to md
pandoc notes.md -o notes.docx
pandoc notes.md -o notes.epub
```

### Git Integration

```bash
# Track changes in exported formats
git add *.html
git commit -m "Update exported documentation"

# Pre-commit hook example
loglog batch-convert . --to html --overwrite
```

### Text Processing

```bash
# Count words in all LogLog files
loglog batch-convert . --to md
wc -w *.md

# Search across converted files
loglog batch-convert . --to md
grep -r "important" *.md
```

## Performance Tips

1. **Batch Operations:** Use `batch-convert` for multiple files instead of individual `convert` commands
2. **File Patterns:** Be specific with patterns to avoid processing unnecessary files
3. **Output Directory:** Use `--output-dir` to organize generated files
4. **Overwrite Flag:** Use `--overwrite` in scripts to avoid interactive prompts

## Troubleshooting

### Common Issues

**Command not found:**
- Run `python3 setup_cli.py` to install
- Check that `~/.local/bin` is in your PATH

**Permission denied:**
- Ensure scripts are executable: `chmod +x loglog_cli.py setup_cli.py`

**PDF conversion fails:**
- Install pdflatex: `sudo apt install texlive-latex-base` (Ubuntu/Debian)
- Or use HTML/Markdown formats instead

**Module import errors:**
- Ensure `loglog.py` is in the same directory as `loglog_cli.py`
- Check Python path with `python3 -c "import sys; print(sys.path)"`

**Large file processing:**
- Use `--verbose` to monitor progress
- Consider filtering or splitting large files first

### Getting Help

For command-specific help:
```bash
loglog convert --help
loglog filter --help
loglog todos --help
```

For bug reports or feature requests, please use the project's issue tracker.