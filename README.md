# LogLog

A hierarchical note-taking format where **everything is a list**. LogLog eliminates structural decision-making so you can focus entirely on capturing your thoughts. No headers, no sections, no paragraphs -- just indentation.

## What Is LogLog?

LogLog is a plain-text format built on a single rule: **nesting through indentation**. Every item is a list item, and every list item can contain other list items. That is the entire specification.

```
- Project planning
    - Timeline
        - Q1: Research phase
        - Q2: Development phase
            - Build prototype
            - User testing
    - Budget
        - Engineering: $50k
        - Design: $20k
    - Team
        [x] Hire lead developer
        [-] Recruit designers
        [] Set up CI/CD pipeline
```

This repository provides:

- **`loglog.py`** -- A Python library that parses loglog files into tree structures and converts them to Markdown, HTML, LaTeX, and PDF
- **`loglog_cli.py`** -- A full-featured command-line interface for batch processing, filtering, searching, and analyzing loglog files
- **`loglog-mobile/`** -- A React Native mobile application for editing loglog files on Android/iOS
- **`loglog-knowledge/`** -- An experimental knowledge graph service that extracts structured knowledge from loglog documents using Claude API

## Why LogLog?

### Zero Structural Overhead

Traditional formats force you to make structural decisions while writing:

```markdown
# Is this a title?
## Or a subtitle?
### Or a section header?

- Should this be a bullet point?
  1. Or a numbered list?

This paragraph needs to be separate...
Or does it belong in the list above?
```

LogLog removes all of that friction:

```
- Just start writing your thought
    - Add details by indenting
    - Keep adding whatever comes to mind
        - No decisions about format types
        - No wondering if this should be a header
    - Everything flows naturally
```

Your brain can focus 100% on **what** you are thinking, not **how** to structure it.

### The Magic of Select-and-Indent

LogLog supports a powerful "write first, organize later" workflow:

1. **Start anywhere** -- begin with any idea at any depth level
2. **Nest naturally** -- go deeper as details emerge
3. **Retroactive organization** -- select a group of related items, press Tab, and they all indent one level. Now you have room above them to add a parent concept

**Before organizing:**
```
- meeting with Sarah about project timeline
- need to order more office supplies
- review quarterly budget numbers
- call vendor about delivery delay
- prepare presentation for board meeting
```

**After grouping (select related items, indent, add parents):**
```
- Administrative Tasks
    - meeting with Sarah about project timeline
    - need to order more office supplies
    - call vendor about delivery delay
- Financial Review
    - review quarterly budget numbers
    - prepare presentation for board meeting
```

Structure emerges from content, not the other way around.

### Comparison to Traditional Formats

| Feature | Markdown | Word Processors | Org Mode | LogLog |
|---------|----------|-----------------|----------|--------|
| Structural decisions upfront | Yes (header levels) | Yes (styles) | Yes (`*` levels) | No |
| Editor dependency | No | Yes | Yes (Emacs) | No |
| Learning curve | Moderate | Low | High | Minimal |
| Restructuring ease | Difficult | Difficult | Moderate | Trivial (select + Tab) |
| Plain text | Yes | No | Yes | Yes |

LogLog shares philosophical similarities with [Emacs Org mode](https://orgmode.org/) -- both use plain text with minimal markup for hierarchical thinking. The key difference is that LogLog has exactly one structural concept (indentation) and works in any text editor.

## Installation

### Python Library

Clone the repository and use `loglog.py` directly -- it has no external dependencies for core functionality:

```bash
git clone https://github.com/k1monfared/loglog.git
cd loglog
```

### CLI Tool

Set up the `loglog` command for system-wide access:

```bash
python3 setup_cli.py
```

Or install as a Python package:

```bash
pip install .
```

### Optional Dependencies

- **pandoc** -- Required for LaTeX conversion (`sudo apt install pandoc`)
- **pdflatex** -- Required for PDF generation (`sudo apt install texlive-latex-base`)

## The LogLog Format

### Basic Syntax

Every item is indented with 4 spaces (or 1 tab) per nesting level. Items can optionally start with `- `:

```
- Top-level item
    - Child item
        - Grandchild item
    - Another child
```

### TODO Items

Items starting with brackets are treated as TODO items with tracked status:

| Syntax | Status | Description |
|--------|--------|-------------|
| `[] Task` or `[ ] Task` | Pending | Not yet started |
| `[x] Task` | Completed | Finished |
| `[-] Task` | In Progress | Currently being worked on |
| `[?] Task` | Unknown | Status unclear |

```
- Sprint 3
    [x] Design database schema
    [x] Implement API endpoints
    [-] Write integration tests
    [] Deploy to staging
    [] Performance benchmarking
```

### Hashtags

Items can contain hashtags for filtering and organization:

```
- Meeting notes #meeting #q1
    - Discussed budget allocation #budget #decision
    - Action item: update roadmap #action
```

## Python Library Usage

### Parsing and Tree Operations

```python
from loglog import build_tree_from_file, build_tree_from_text, print_tree

# Parse from file
root = build_tree_from_file("notes.log")

# Parse from text
text_lines = """
- Project Alpha
    - Phase 1
        [x] Design the architecture
        [] Write initial code
    - Phase 2
        [] Plan testing strategy
""".split('\n')
root = build_tree_from_text(text_lines)

# Print the tree
print_tree(root)

# Access specific nodes by address
from loglog import get_node
node = get_node(root, "0.1.")  # Second child of first item
print(node.data)     # "Phase 2"
print(node.type)     # "regular"
```

### Convert to Markdown

The `to_md()` method uses a **shallowest leaf depth algorithm** to intelligently determine which levels become headers and which become list items:

```python
root = build_tree_from_file("notes.log")
markdown = root.to_md(header_levels=4)

# Or write directly to file
from loglog import to_md_file
to_md_file("notes.log")  # Creates notes.md
```

**Example conversion** -- given this loglog input:
```
- Project Overview
    - Goals
        - Increase user engagement by 20%
        - Reduce load time to under 2 seconds
    - Timeline
        - Q1: Research
        - Q2: Implementation
```

The output is:
```markdown
# Project Overview

## Goals

- Increase user engagement by 20%
- Reduce load time to under 2 seconds

## Timeline

- Q1: Research
- Q2: Implementation
```

### Convert from Markdown

```python
from loglog import from_md, from_md_file, from_md_to_file

# Convert markdown string to loglog format
loglog_text = from_md(markdown_string)

# Convert markdown file to loglog string
loglog_text = from_md_file("document.md")

# Convert markdown file to loglog file
from_md_to_file("document.md")  # Creates document.txt
```

### Generate Interactive HTML

The HTML output is a fully self-contained document with embedded CSS and JavaScript -- no external dependencies. It features:

- Foldable/expandable tree sections (click triangles or use keyboard)
- Keyboard navigation (arrow keys, Enter/Space to toggle)
- Level-based folding (Ctrl+1 through Ctrl+9, Ctrl+0 to unfold all)
- Focus mode (Ctrl+Alt+1-9 folds everything except the current branch)
- Dark/light theme toggle with localStorage persistence
- Styled TODO items (red for pending, strikethrough for completed, orange for in-progress)

```python
from loglog import build_tree_from_file, to_html_file

# Generate HTML file
to_html_file("notes.log")  # Creates notes.html

# Or get HTML as string with custom title
root = build_tree_from_file("notes.log")
html = root.to_html("My Project Notes")
```

### Generate LaTeX and PDF

```python
from loglog import to_latex_file, to_pdf_file

to_latex_file("notes.log")  # Creates notes.tex (requires pandoc)
to_pdf_file("notes.log")    # Creates notes.pdf (requires pandoc + pdflatex)
```

### Filter by Hashtags

```python
from loglog import build_tree_from_file, filter_by_hashtags, export_hashtag_filtered

root = build_tree_from_file("project.log")

# Filter in memory
filtered = filter_by_hashtags(root, ["decision", "important"])

# Export filtered content to file
export_hashtag_filtered("project.log", ["meeting"])  # Creates project_meeting.log
```

### Extract TODO Items

```python
from loglog import export_todos_filtered, get_todos_filtered_content

# Export pending TODOs to file
export_todos_filtered("project.log", status_filter=False)  # Creates project_todos_pending.log

# Get filtered TODO content as string
content = get_todos_filtered_content("project.log", status_filter=False)
print(content)
```

## CLI Usage

The `loglog` command provides seven subcommands for working with loglog files from the terminal.

### Convert Files

```bash
# Convert to interactive HTML
loglog convert notes.log --to html

# Convert to Markdown with custom header depth
loglog convert notes.log --to md --header-levels 6

# Convert multiple files
loglog convert *.log --to md

# Batch convert all .log files to HTML
loglog batch-convert . --to html

# Recursive batch conversion
loglog batch-convert docs/ --to md --recursive

# Preview changes in VS Code before writing
loglog convert notes.log --to md --preview

# Show unified diff without writing
loglog convert notes.log --to md --diff
```

### Filter and Search

```bash
# Filter by hashtags
loglog filter project.log --hashtags decision,important -o decisions.log

# Search across files
loglog search "budget" *.log

# Regex search
loglog search "TODO.*phase" *.log --regex

# Case-sensitive search with context
loglog search "Important" notes.log --case-sensitive --context 2
```

### TODO Management

```bash
# List all pending TODOs
loglog todos project.log --status pending

# Export TODOs as JSON
loglog todos project.log --format json -o tasks.json

# Export TODOs as CSV
loglog todos project.log --format csv -o tasks.csv
```

### Display and Analyze

```bash
# Display tree structure
loglog show notes.log

# Show with node numbering
loglog show notes.log --numbered

# File statistics (total nodes, max depth, TODO counts, hashtag frequency)
loglog stats project.log

# JSON statistics for scripting
loglog stats *.log --format json
```

## Project Structure

```
loglog/
|-- loglog.py              # Core library: TreeNode, parsing, conversions
|-- loglog_cli.py          # CLI application with 7 subcommands
|-- setup.py               # Package installation configuration
|-- setup_cli.py           # CLI symlink/wrapper setup script
|-- generate_outputs.py    # Utility to regenerate test outputs
|-- tree.ipynb             # Jupyter notebook with interactive examples
|-- LICENSE                # GNU General Public License v3
|-- demo/
|   +-- lorem_ipsum.*      # Example files (.log, .md, .tex, .pdf)
|-- docs/
|   |-- CLI_USAGE.md       # Detailed CLI documentation
|   |-- FEATURES.md        # Format philosophy and feature descriptions
|   |-- FORMAT_CONVERSIONS.md  # Conversion algorithm documentation
|   |-- PACKAGING.md       # Distribution and packaging guide
|   +-- PROJECT_INDEX.md   # Full project documentation index
|-- tests/
|   |-- test_framework.py  # YAML-driven test framework
|   |-- test_conversions.py  # Pytest-compatible test suite
|   +-- data/              # Test inputs, expected outputs, manifest
|-- benchmark/
|   |-- benchmark_runner.py  # Performance benchmarking
|   +-- *.log              # Test files of various sizes
|-- loglog-mobile/         # React Native mobile app (Expo)
+-- loglog-knowledge/      # Knowledge graph extraction service
```

## Conversion Algorithm

The Markdown conversion uses a **shallowest leaf depth** algorithm:

1. **Scan the tree** to find the leaf node (a node with no children) at the minimum depth
2. **Compute the header cutoff** as `min(shallowest_leaf_depth, header_levels + 1)`
3. **Apply formatting**:
   - Levels above the cutoff become Markdown headers (H1, H2, H3, ...)
   - Levels at or below the cutoff become nested list items

This ensures that the output always has proper Markdown structure regardless of how deep or shallow the original loglog content is. For example, a document where all items are at the top level produces only list items (no headers), while a deeply nested document gets appropriate header hierarchy.

## Running Tests

```bash
# Using the test framework directly
cd tests
python3 test_framework.py

# Or with pytest
pytest test_conversions.py -v
```

The test framework uses a YAML manifest (`tests/data/test_manifest.yaml`) defining test cases across three categories:
- **Markdown to LogLog** -- header hierarchy, TODO items, code blocks, quote blocks, mixed lists, nested structures
- **LogLog to Markdown** -- basic hierarchy, TODO formatting, deep nesting
- **Roundtrip** -- loglog -> markdown -> loglog and markdown -> loglog -> markdown to verify structural preservation

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Author

Created by [Keivan Monfared](https://github.com/k1monfared).
