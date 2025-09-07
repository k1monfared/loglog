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

3. **Install and use LogLog**:
   ```bash
   # Option 1: Install system package (recommended)
   ./build_simple.sh                    # Build .deb package
   sudo dpkg -i loglog_1.0.0_all.deb   # Install system-wide
   loglog convert notes.log --to html   # Use anywhere
   
   # Option 2: Use CLI directly
   python3 setup_cli.py                 # One-time setup
   loglog convert notes.log --to html
   ```
   
   Or using Python library:
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

### Command-Line Interface ✅
- **Full-featured CLI tool** with argparse-based commands
- **File conversion** - convert to HTML, Markdown, LaTeX, PDF
- **Batch operations** - process multiple files efficiently
- **Content filtering** - extract by hashtags or TODO status
- **Search functionality** - regex and text search across files
- **Statistics and analysis** - file metrics and TODO tracking

### Distribution Package ✅
- **Debian package (.deb)** ready for Ubuntu/Debian installation
- **Zero dependencies** - uses only Python standard library
- **System-wide installation** - `apt install` compatible
- **Professional packaging** - follows Debian Policy standards
- **33KB package size** - lightweight and efficient
- **Ubuntu repository ready** - documented submission process

### Planned Features 📋
- **Linux desktop GUI** with file browser and editor
- **Search functionality** across document collections
- **Knowledge graph generation** from related topics

## Documentation

- **[CLI Usage Guide](docs/CLI_USAGE.md)** - Complete command-line interface documentation
- **[Packaging Guide](docs/PACKAGING.md)** - Building and distributing .deb packages
- **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** - Configure system-specific paths and settings
- **[Features](docs/FEATURES.md)** - Detailed feature explanations and philosophy
- **[Format Conversions](docs/FORMAT_CONVERSIONS.md)** - Conversion algorithms and examples
- **[Mobile Development](docs/mobile/DEVELOPMENT_SUMMARY.md)** - Mobile app technical details
- **[Technical Architecture](docs/mobile/TECHNICAL_ARCHITECTURE.md)** - System design and patterns
- **[Roadmap](docs/planning/ROADMAP.md)** - Complete project roadmap with decisions

## Installation

### System Package (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/loglog.git
cd loglog

# Build and install .deb package
./build_simple.sh                    # Creates loglog_1.0.0_all.deb
sudo dpkg -i loglog_1.0.0_all.deb   # Install system-wide
sudo apt-get install -f             # Fix any dependencies

# Verify installation
loglog --version
man loglog
```

### Development Setup
```bash
# Set up environment (required for hooks and system-specific paths)
cp .env.example .env
# Edit .env file to match your system - see docs/ENVIRONMENT_SETUP.md

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