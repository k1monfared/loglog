# loglog

A simple way of taking notes with absolute minimum structure. Everything is a list, even the list items are lists.

## What is LogLog?

LogLog is a hierarchical note-taking format that eliminates structural decision-making from the writing process. You can start writing at any depth level and reorganize later through simple indentation.

**Example:**
```
- Project Ideas
    - Mobile App
        - User authentication
        - Data synchronization  
        [] Implement offline mode
        [x] Design wireframes
    - Desktop Tool
        - CLI interface
        - GUI application
```

## Core Philosophy

**Zero Structural Overhead**: No need to decide between headers, sections, lists, or paragraphs. Everything is a list item that can be nested indefinitely.

**Mind-First Structure**: Start writing wherever your thoughts flow, then organize retroactively by selecting and indenting.

## Key Benefits

- **Reduces cognitive load** - focus on content, not formatting
- **Highly flexible** - restructure by simple indentation  
- **Cross-platform** - plain text files work everywhere
- **Foldable in most editors** - collapse/expand sections
- **Algorithmically parseable** - enables powerful tooling

## Quick Start

1. **Create a `.log` file** and start writing with dashes:
   ```
   - Your first thought
       - Supporting detail
       - Another detail
   - Second main thought
   ```

2. **Use TODO syntax** for tasks:
   ```
   [] Pending task
   [x] Completed task
   [?] Unknown status
   ```

3. **Convert to other formats**:
   ```python
   from loglog import build_tree_from_file, to_html_file, to_md_file
   
   # Convert to interactive HTML
   to_html_file('notes.log')
   
   # Convert to Markdown
   to_md_file('notes.log')
   ```

## Features

### Desktop Python Library ✅
- **Tree parsing and manipulation**
- **Format conversion**: Markdown ↔ LogLog, HTML (interactive), LaTeX, PDF
- **TODO management** with status tracking
- **Hashtag filtering** - extract sections by tags (`#decision`, `#important`)
- **Branch preservation** - maintain structure when filtering

### Mobile Application ✅
- **React Native app** with gesture-based editing
- **Real-time parsing** and visual feedback  
- **File management** with persistent storage
- **Multi-format export** and native sharing
- **Advanced touch controls** (swipe to indent, double-tap to fold)

**Status**: Production ready, pending device testing

### Planned Features 📋
- **Linux desktop GUI** with file browser and editor
- **Command-line interface** for batch operations
- **Search functionality** across document collections
- **Knowledge graph generation** from related topics

## Documentation

- **[Features](docs/FEATURES.md)** - Detailed feature explanations and philosophy
- **[Format Conversions](docs/FORMAT_CONVERSIONS.md)** - Conversion algorithms and examples
- **[Mobile Development](docs/mobile/DEVELOPMENT_SUMMARY.md)** - Mobile app technical details
- **[Technical Architecture](docs/mobile/TECHNICAL_ARCHITECTURE.md)** - System design and patterns
- **[Roadmap](docs/planning/ROADMAP.md)** - Complete project roadmap with decisions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/loglog.git
cd loglog

# Use the Python library
python3 -c "from loglog import build_tree_from_file; print('LogLog ready!')"

# Run mobile app (requires Node.js and Expo)
cd loglog-mobile && npm install && npm start
```

## Contributing

LogLog is designed to be simple and maintainable. When contributing:

1. **Follow the core philosophy** - avoid feature bloat
2. **Maintain cross-platform compatibility** 
3. **Preserve the plain-text nature** of the format
4. **Test with real-world use cases**

## License

[MIT License](LICENSE) - Feel free to use LogLog for personal and commercial projects.