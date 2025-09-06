# LogLog Linux Tools: Focused Implementation Plan

## Project Vision

Create a lightweight ecosystem for LogLog format that respects the Unix philosophy: users edit with their preferred text editor, while specialized tools handle viewing, conversion, and light editing tasks.

## Architecture Overview

```
LogLog Linux Ecosystem
├── Command-Line Tools
│   ├── loglog --to_html file.log        # Convert to interactive HTML
│   ├── loglog --to_md file.log          # Convert to Markdown
│   ├── loglog --to_pdf file.log         # Convert to PDF
│   ├── loglog --validate file.log       # Validate format
│   └── loglog --stats file.log          # Document statistics
├── GUI Viewer/Light Editor
│   ├── Interactive HTML-like view       # Folding, navigation, themes
│   ├── Light editing capabilities       # Add lines, indent/outdent, todo toggles
│   ├── Find/replace functionality       # Search within document
│   └── File watcher                     # Auto-reload when file changes
└── Integration
    ├── File association (.log files)    # Double-click opens in GUI viewer
    ├── Desktop integration              # Context menu "View in LogLog"
    └── Text editor plugins (future)     # Vim, VS Code, Emacs plugins
```

## Phase 1: Command-Line Tools (Week 1-2)

### Enhanced loglog.py CLI

**Goal**: Robust command-line interface for all conversion operations

#### Enhanced CLI Features Needed

**Core Conversion Commands:**
```bash
# Basic conversions
loglog file.log --to_html                    # Interactive HTML with folding
loglog file.log --to_md                      # Markdown conversion
loglog file.log --to_pdf                     # PDF via pandoc/weasyprint
loglog file.log --to_txt                     # Clean text formatting

# Advanced options
loglog file.log --to_html --theme dark       # Dark theme HTML
loglog file.log --to_html --no-interactive   # Static HTML without JavaScript
loglog file.log --to_pdf --style academic   # Academic paper formatting
loglog file.log --to_md --depth 3           # Only export to depth 3
```

**Utility Commands:**
```bash
# Document analysis
loglog file.log --stats                      # Show document statistics
loglog file.log --validate                   # Validate format correctness
loglog file.log --outline                    # Show document outline
loglog file.log --todos                      # List all TODO items

# Batch operations
loglog *.log --to_html --batch              # Convert multiple files
loglog directory/ --to_html --recursive     # Process directory recursively
```

**Integration Commands:**
```bash
# File watching for live preview
loglog file.log --watch --to_html            # Auto-regenerate HTML on file changes
loglog file.log --serve                      # Start local HTTP server for preview
```

#### Implementation Tasks
- [ ] Create robust argument parsing with argparse or click
- [ ] Add PDF generation using weasyprint or pandoc
- [ ] Implement batch processing capabilities
- [ ] Add file watching for live preview
- [ ] Create comprehensive error handling and validation
- [ ] Add progress bars for batch operations
- [ ] Implement configuration file support (~/.loglogrc)

## Phase 2: GUI Viewer (Week 3-4)

### Technology Choice: GTK4 + Python
**Rationale**: 
- Reuse existing loglog.py code directly
- Native Linux look and feel
- Lightweight compared to Electron
- Good file integration capabilities

### Core GUI Features

#### 1. Document Viewer
**Framework**: GTK4 with custom HTML-like rendering
**Features**:
- **Interactive folding** - Click triangles to fold/unfold sections
- **Keyboard navigation** - Arrow keys, vim-style hjkl navigation
- **Theme switching** - Dark/light themes matching HTML output
- **Zoom controls** - Text scaling for readability
- **Document outline** - Sidebar showing structure

#### 2. File Integration
**Features**:
- **File association** - Double-click .log files opens in viewer
- **Auto-reload** - Detect file changes and refresh automatically
- **Recent files** - Quick access to recently viewed documents
- **Drag-and-drop** - Drop .log files into viewer
- **Command-line launch** - `loglog-view file.log`

#### 3. Navigation and Search
**Features**:
- **Go to line** - Ctrl+G to jump to specific line numbers
- **Find functionality** - Ctrl+F for text search with highlighting
- **Outline navigation** - Click outline items to jump to sections
- **Breadcrumb navigation** - Show current location in hierarchy
- **Back/forward** - Navigate through view history

#### Implementation Tasks
- [ ] Create GTK4 application window with menu bar
- [ ] Implement custom text view widget for loglog rendering
- [ ] Add folding/unfolding with visual triangle indicators
- [ ] Create outline sidebar using TreeView
- [ ] Implement find dialog with highlighting
- [ ] Add file watching with inotify
- [ ] Create desktop integration (.desktop file, mime type)

## Phase 3: Light Editing (Week 5-6)

### Editing Philosophy
**Not a full text editor** - Focus on structural operations that benefit from visual hierarchy understanding.

### Editing Capabilities

#### 1. Line Operations
**Features**:
- **Add new line** - Enter key adds new line at appropriate indent level
- **Delete line** - Delete key removes current line
- **Move lines** - Alt+Up/Down moves lines while preserving structure
- **Duplicate line** - Ctrl+D duplicates current line

#### 2. Indentation Management  
**Features**:
- **Smart indentation** - Enter key auto-indents based on context
- **Tab/Shift+Tab** - Indent/outdent selected lines (4 spaces per level)
- **Visual indent guides** - Show indentation levels with subtle lines
- **Bulk operations** - Select multiple lines and indent/outdent together

#### 3. TODO Item Management
**Features**:
- **Toggle TODO status** - Space bar toggles [ ]/[x] for current line
- **Convert to/from TODO** - Ctrl+T toggles between regular item and TODO
- **TODO overview** - Sidebar showing all TODO items with checkboxes
- **Completion statistics** - Show completion percentage in status bar

#### 4. Structure Operations
**Features**:
- **Promote/demote sections** - Move entire sections up/down hierarchy levels
- **Fold during editing** - Collapse sections to focus on specific areas
- **Cut/copy/paste** - Preserve indentation when moving content
- **Undo/redo** - Standard editing history

#### Implementation Tasks
- [ ] Implement editable text view with loglog-aware editing
- [ ] Add smart auto-indentation logic
- [ ] Create TODO toggle functionality
- [ ] Implement bulk indentation operations
- [ ] Add undo/redo system
- [ ] Create structure-aware cut/copy/paste
- [ ] Add visual feedback for all editing operations

## Phase 4: Find/Replace + Polish (Week 7-8)

### Advanced Search Features

#### 1. Find Functionality
**Features**:
- **Text search** - Find text with case sensitivity options
- **Regex support** - Regular expression search patterns
- **Scope options** - Search in current section, document, or all open files
- **Result highlighting** - Highlight all matches with navigation
- **Search history** - Remember previous search terms

#### 2. Replace Functionality  
**Features**:
- **Simple replace** - Replace text with confirmation
- **Regex replace** - Pattern-based replacements with capture groups
- **Bulk replace** - Replace all occurrences with confirmation
- **Preview mode** - Show what will be replaced before confirming
- **Undo support** - Single undo for all replacements

#### 3. Navigation Integration
**Features**:
- **Search results panel** - List all matches with context
- **Jump to match** - Click search results to navigate
- **Next/previous** - F3/Shift+F3 to cycle through matches
- **Search within folded** - Option to search inside folded sections

### Application Polish

#### 1. User Experience
- **Keyboard shortcuts** - Comprehensive shortcut system
- **Status bar** - Show document info, cursor position, search status
- **Progress indicators** - For long operations (large file search)
- **Error handling** - Graceful error messages and recovery
- **Help system** - Built-in help with keyboard shortcut reference

#### 2. Performance Optimization
- **Large file handling** - Efficient rendering for 10,000+ line documents
- **Search optimization** - Fast text search with indexing
- **Memory management** - Efficient memory usage for large documents
- **Lazy loading** - Load document sections on demand

#### Implementation Tasks
- [ ] Implement comprehensive find/replace dialog
- [ ] Add regex support with error handling
- [ ] Create search results panel with navigation
- [ ] Optimize performance for large documents
- [ ] Add comprehensive keyboard shortcuts
- [ ] Create help system and documentation
- [ ] Polish UI with status bar and progress indicators

## Technical Implementation Details

### Command-Line Tool Architecture

```python
# Enhanced CLI structure
class LogLogCLI:
    def __init__(self):
        self.parser = self._create_argument_parser()
    
    def _create_argument_parser(self):
        parser = argparse.ArgumentParser(
            prog='loglog',
            description='LogLog format processor and converter'
        )
        
        # Input file
        parser.add_argument('file', help='Input .log file')
        
        # Output format options (mutually exclusive)
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('--to_html', action='store_true')
        format_group.add_argument('--to_md', action='store_true')
        format_group.add_argument('--to_pdf', action='store_true')
        
        # Options
        parser.add_argument('--theme', choices=['light', 'dark'], default='light')
        parser.add_argument('--output', '-o', help='Output file name')
        parser.add_argument('--watch', action='store_true', help='Watch file for changes')
        parser.add_argument('--batch', action='store_true', help='Batch process multiple files')
        
        # Utility commands
        parser.add_argument('--stats', action='store_true', help='Show document statistics')
        parser.add_argument('--validate', action='store_true', help='Validate format')
        
        return parser
    
    def convert_to_html(self, file_path, theme='light', interactive=True):
        """Convert loglog file to interactive HTML"""
        # Implementation using existing loglog.py code
        
    def convert_to_pdf(self, file_path, style='default'):
        """Convert loglog file to PDF via HTML intermediate"""
        # Generate HTML first, then convert to PDF using weasyprint
```

### GUI Application Architecture

```python
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject

class LogLogViewer(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.loglog.viewer')
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        self.window = LogLogWindow(application=app)
        self.window.present()

class LogLogWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Main layout: HeaderBar + HPaned (sidebar + main view)
        self.setup_header_bar()
        self.setup_main_layout()
        self.setup_document_view()
        self.setup_outline_sidebar()
    
    def setup_document_view(self):
        """Custom widget for rendering loglog content"""
        self.document_view = LogLogDocumentView()
        # Implement custom rendering with folding support
    
    def setup_outline_sidebar(self):
        """TreeView showing document structure"""
        self.outline_view = Gtk.TreeView()
        # Populate with document hierarchy

class LogLogDocumentView(Gtk.Widget):
    """Custom widget for displaying loglog documents with folding"""
    
    def __init__(self):
        super().__init__()
        self.document = None
        self.folded_sections = set()
        
    def load_document(self, file_path):
        """Load and parse loglog document"""
        with open(file_path, 'r') as f:
            content = f.read()
        self.document = build_tree_from_string(content)
        self.queue_draw()  # Trigger redraw
    
    def toggle_fold(self, line_number):
        """Toggle folding for section at line number"""
        # Implementation for folding/unfolding
```

### File Integration

```bash
# Create .desktop file for application launcher
cat > ~/.local/share/applications/loglog-viewer.desktop << EOF
[Desktop Entry]
Name=LogLog Viewer
Comment=View and edit LogLog hierarchical documents
Exec=loglog-viewer %f
Icon=loglog-viewer
Terminal=false
Type=Application
Categories=Office;TextEditor;
MimeType=text/x-loglog;
EOF

# Create MIME type for .log files
cat > ~/.local/share/mime/packages/loglog.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="text/x-loglog">
        <comment>LogLog hierarchical document</comment>
        <glob pattern="*.log"/>
        <glob pattern="*.loglog"/>
    </mime-type>
</mime-info>
EOF

# Update MIME database
update-mime-database ~/.local/share/mime
```

## Development Timeline

### Week 1-2: Enhanced CLI
- [ ] **Days 1-3**: Enhance argument parsing and add PDF conversion
- [ ] **Days 4-7**: Implement batch processing and file watching
- [ ] **Days 8-10**: Add utility commands (stats, validate, outline)
- [ ] **Testing**: Comprehensive CLI testing with various file types

### Week 3-4: GUI Viewer
- [ ] **Days 1-3**: Set up GTK4 application structure and basic window
- [ ] **Days 4-7**: Implement document rendering with folding support
- [ ] **Days 8-10**: Add outline sidebar and navigation features
- [ ] **Days 11-14**: File integration (associations, auto-reload, drag-drop)

### Week 5-6: Light Editing
- [ ] **Days 1-3**: Implement basic line editing (add, delete, move)
- [ ] **Days 4-7**: Add indentation management and TODO toggles
- [ ] **Days 8-10**: Structure operations (cut/copy/paste with indent preservation)
- [ ] **Days 11-14**: Undo/redo system and editing polish

### Week 7-8: Find/Replace + Polish
- [ ] **Days 1-3**: Implement find functionality with highlighting
- [ ] **Days 4-7**: Add replace functionality with preview mode
- [ ] **Days 8-10**: Performance optimization for large documents
- [ ] **Days 11-14**: UI polish, keyboard shortcuts, help system

## Distribution Plan

### Package Structure
```
loglog-tools/
├── bin/
│   ├── loglog              # CLI tool
│   └── loglog-viewer       # GUI application
├── lib/python3/
│   └── loglog/             # Python modules
│       ├── __init__.py
│       ├── core.py         # Existing loglog.py functionality
│       ├── cli.py          # CLI implementation
│       └── gui/            # GTK GUI modules
├── share/
│   ├── applications/       # .desktop files
│   ├── mime/packages/      # MIME type definitions
│   └── icons/              # Application icons
└── docs/
    ├── man/loglog.1        # Man page for CLI
    └── html/               # User documentation
```

### Installation Methods

1. **PyPI Package** (Primary):
```bash
pip install loglog-tools
# Installs CLI tool and GUI with dependencies
```

2. **System Package** (Future):
```bash
# Debian/Ubuntu
sudo apt install loglog-tools

# Fedora/RHEL
sudo dnf install loglog-tools

# Arch Linux
yay -S loglog-tools-git
```

3. **Flatpak** (GUI only):
```bash
flatpak install flathub com.loglog.Viewer
```

## User Workflow Examples

### Command-Line Workflow
```bash
# User edits with favorite editor
vim meeting_notes.log

# Quick conversion to HTML for sharing
loglog meeting_notes.log --to_html --theme dark

# Generate PDF report
loglog meeting_notes.log --to_pdf --style professional

# Watch file and auto-generate HTML for live preview
loglog meeting_notes.log --watch --to_html &
firefox meeting_notes.html
# HTML updates automatically as you edit in vim
```

### GUI Workflow
```bash
# Open file in viewer
loglog-viewer project_plan.log

# Or double-click .log file in file manager
# Viewer opens with:
# - Interactive folding (click triangles)
# - Outline sidebar for navigation
# - Find functionality (Ctrl+F)

# Switch to edit mode when needed
# - Add new tasks with Enter
# - Indent/outdent with Tab/Shift+Tab
# - Toggle TODO status with Spacebar
# - Find and replace project names

# File auto-reloads if edited externally
# Switch back to favorite editor for heavy editing
```

### Hybrid Workflow
```bash
# Heavy editing in favorite editor
emacs large_document.log

# Quick structural changes in GUI
loglog-viewer large_document.log
# - Bulk indent sections
# - Toggle multiple TODOs
# - Find/replace with preview

# Convert for sharing
loglog large_document.log --to_html --theme dark
```

## Success Metrics

### Technical Goals
- **CLI Performance**: Convert 1000-line document to HTML in < 1 second
- **GUI Performance**: Smooth interaction with 5000+ line documents
- **Memory Usage**: GUI uses < 50MB for typical documents
- **Startup Time**: GUI launches in < 2 seconds

### User Experience Goals
- **Learning Curve**: New users productive within 10 minutes
- **Integration**: Seamless file association and editor workflow
- **Reliability**: 99%+ uptime, graceful error handling
- **Feature Completeness**: All mobile app viewing features available

### Adoption Goals
- **CLI Usage**: 80% of users try CLI tools
- **GUI Usage**: 60% of users prefer GUI for viewing
- **Workflow Integration**: 40% of users integrate with existing editors
- **Community**: Active GitHub issues and feature requests

This focused approach respects existing text editor preferences while providing specialized tools for loglog format handling. The incremental development path allows early feedback and ensures each component is solid before adding complexity.