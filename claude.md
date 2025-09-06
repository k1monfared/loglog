# Claude Code Instructions for Loglog Project


## Project Overview


- This is a hierarchical note-taking system using simple indented text format
- Every item is a list item, creating flexible nested structures
- Supports conversion to markdown, HTML, LaTeX, and PDF formats
- Focus on simplicity and minimal structure overhead
## Development Guidelines


- Code Style

  - Follow existing Python conventions in loglog.py
  - Use 4-space indentation consistently
  - Add docstrings to all public methods
  - Keep functions focused and single-purpose
- Testing Requirements

  - Write unit tests for all conversion functions
  - Test round-trip conversions (loglog → format → loglog)
  - Include edge cases and deeply nested structures
  - Validate export formats are properly formatted
- Documentation Standards

  - Use loglog format for ALL documentation and planning
  - Convert loglog documentation to markdown for sharing
  - keep an up-to-date wiki on how to use that explains all functionality. the wiki pulls from doc files exclusive to each functionality.
  - Keep README.md updated with latest functionality
  - Document algorithm changes and new features
  - each new feature that is being developed has it's own documentation file with a section on how to use, then how to use section then is pulled in the wiki.
## File Organization


- Project Structure

  - /tests/ - All test files and unit tests
  - /docs/ - Documentation in loglog format (with .md conversions)
    - /docs/mobile
      - /docs/mobile/android
    - /docs/linux/
      - /docs/linux/cli
      - /docs/linux/gui
    - /docs/planning/ - all roadmap files, todo lists, decisions
  - /demo/ - Example files showing format capabilities
  - loglog.py - Core functionality and conversion methods
- Naming Conventions

  - Test files: test_input_*.txt for loglog examples
  - Generated files: same base name with appropriate extensions
  - Documentation: descriptive names ending in .log, converted to .md
## Working with Conversions


- Available Methods

  - to_md() - Convert to markdown with hierarchical headers
  - to_html() - Interactive HTML with folding and keyboard navigation
  - to_latex() - LaTeX format via pandoc
  - to_pdf() - PDF generation via LaTeX
  - from_md() - Convert markdown back to loglog format
- File Convenience Functions

  - to_md_file() - Generate .md file with same base name
  - to_html_file() - Generate .html file with same base name
  - to_latex_file() - Generate .tex file with same base name
  - to_pdf_file() - Generate .pdf file with same base name
  - from_md_to_file() - Convert .md to .txt loglog file
## Todo Item Handling


- Syntax Recognition

  - [] - Pending todo item
  - [x] - Completed todo item
  - [?] - Unknown status todo item
  - [-] - in prorgess to do item
  - Regular items start with "-" or no prefix
- Conversion Behavior

  - HTML: Styled with checkboxes and strikethrough for completed
  - Markdown: Preserved as markdown todo syntax
  - LaTeX/PDF: Rendered as appropriate list formatting
## Key Algorithms


- Shallowest Leaf Depth

  - Find the minimum depth of leaf nodes (nodes without children)
  - Use this to determine header vs list item cutoff
  - Ensures proper hierarchical structure in conversions
- Round-trip Conversion

  - Test that loglog → markdown → loglog preserves structure
  - Handle paragraph separation and whitespace normalization
  - Maintain todo item syntax through conversions
## Development Workflow


- Feature Implementation

  - Write new functionality in loglog.py
  - Create test cases in /tests/ directory
  - Document changes in /docs/ using loglog format
  - Generate demonstration files in /demo/
  - Update README.md with new capabilities
- Testing Process

  - Run unit tests after any changes
  - Test with all example files in /tests/
  - Verify all export formats generate correctly
  - Check file naming conventions work properly
- Documentation Updates

  - Write planning and specifications in loglog format
  - Convert to markdown for sharing and review
  - Keep both .log and .md versions in sync
  - Include code examples and usage instructions
## Mobile App Development


- Active Development Planning

  - Mobile app plan documented in /docs/mobile_app_plan.log
  - Detailed development plan in /docs/mobile_development_plan.log
  - React Native with TypeScript chosen for implementation
  - Native JavaScript approach for optimal performance
  - 12-week development timeline with 6 phases
- Current Development Decisions

  - Android-first development using Expo framework
  - Port TreeNode class from Python to TypeScript
  - Full native implementation (no Python backend)
  - Touch gestures: long-press + drag for line selection
  - Swipe left/right for indent/outdent operations
  - Double-tap for folding/unfolding functionality
- Documentation Workflow for Mobile Development

  - All development decisions documented in /docs/ folder using loglog format
  - Convert all .log files to .md using loglog functions after updates
  - Keep both .log (source) and .md (sharing) versions in sync
  - Update mobile_development_plan.log regularly as development progresses
  - Document technical challenges and solutions in loglog format
## Quality Standards


- Code Quality

  - Maintain backward compatibility with existing loglog files
  - Handle edge cases gracefully (empty files, malformed input)
  - Provide clear error messages for conversion failures
  - Optimize performance for large nested structures
- User Experience

  - Keep the format simple and intuitive
  - Provide multiple export options for different use cases
  - Maintain the core philosophy of minimal structure overhead
  - Support both manual and programmatic file manipulation
