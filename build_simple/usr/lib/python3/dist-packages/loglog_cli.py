#!/usr/bin/env python3
"""
LogLog Command Line Interface

A comprehensive CLI tool for the LogLog hierarchical note-taking format.
Supports file conversion, filtering, batch processing, and analysis operations.
"""

import argparse
import os
import sys
import glob
from pathlib import Path
import json
from typing import List, Optional, Dict, Any

# Import LogLog core functions
from loglog import (
    build_tree_from_file,
    build_tree_from_text,
    to_html_file,
    to_md_file, 
    to_latex_file,
    to_pdf_file,
    from_md_file,
    from_md_to_file,
    filter_by_hashtags,
    export_hashtag_filtered,
    export_todos_filtered,
    print_tree,
    print_tree_to_file
)


class LogLogCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            prog='loglog',
            description='LogLog hierarchical note-taking format CLI tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Convert single file to HTML
  loglog convert notes.log --to html
  
  # Convert multiple files to markdown
  loglog convert *.log --to md
  
  # Filter by hashtags and export
  loglog filter notes.log --hashtags important,decision --output filtered.log
  
  # Extract pending TODOs
  loglog todos notes.log --status pending --output todos.log
  
  # Batch convert all .log files in directory
  loglog batch-convert . --from log --to html
  
  # Display tree structure
  loglog show notes.log --depth 3
            """
        )
        
        # Global options
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='Enable verbose output')
        parser.add_argument('--version', action='version', version='LogLog CLI 1.0.0')
        
        # Create subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        self._add_convert_parser(subparsers)
        self._add_filter_parser(subparsers)
        self._add_todos_parser(subparsers)
        self._add_show_parser(subparsers)
        self._add_search_parser(subparsers)
        self._add_batch_parser(subparsers)
        self._add_stats_parser(subparsers)
        
        return parser
    
    def _add_convert_parser(self, subparsers):
        """Add convert command parser"""
        parser = subparsers.add_parser(
            'convert', 
            help='Convert LogLog files to other formats',
            description='Convert LogLog files to HTML, Markdown, LaTeX, or PDF'
        )
        parser.add_argument('files', nargs='+', help='Input files (supports wildcards)')
        parser.add_argument('--to', choices=['html', 'md', 'latex', 'pdf'], 
                          required=True, help='Target format')
        parser.add_argument('--header-levels', type=int, default=4,
                          help='Maximum header levels for conversion (default: 4)')
        parser.add_argument('--title', help='Custom title for HTML documents')
        parser.add_argument('--output-dir', help='Output directory (default: same as input)')
        parser.add_argument('--overwrite', action='store_true',
                          help='Overwrite existing files without prompt')
    
    def _add_filter_parser(self, subparsers):
        """Add filter command parser"""
        parser = subparsers.add_parser(
            'filter',
            help='Filter LogLog files by hashtags',
            description='Extract content containing specific hashtags'
        )
        parser.add_argument('file', help='Input LogLog file')
        parser.add_argument('--hashtags', required=True,
                          help='Comma-separated hashtags to filter by')
        parser.add_argument('--output', '-o', required=True, 
                          help='Output file path')
        parser.add_argument('--preserve-structure', action='store_true', default=True,
                          help='Preserve parent structure (default: true)')
    
    def _add_todos_parser(self, subparsers):
        """Add todos command parser"""
        parser = subparsers.add_parser(
            'todos',
            help='Extract and manage TODO items',
            description='Extract TODO items with optional status filtering'
        )
        parser.add_argument('file', help='Input LogLog file')
        parser.add_argument('--status', choices=['pending', 'completed', 'in_progress', 'all'],
                          default='all', help='Filter by TODO status')
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--format', choices=['log', 'json', 'csv'], default='log',
                          help='Output format')
    
    def _add_show_parser(self, subparsers):
        """Add show command parser"""
        parser = subparsers.add_parser(
            'show',
            help='Display LogLog file structure',
            description='Display the hierarchical structure of LogLog files'
        )
        parser.add_argument('file', help='Input LogLog file')
        parser.add_argument('--depth', type=int, help='Maximum depth to display')
        parser.add_argument('--numbered', action='store_true', 
                          help='Show node numbers')
        parser.add_argument('--compact', action='store_true',
                          help='Compact display without decoration')
    
    def _add_search_parser(self, subparsers):
        """Add search command parser"""
        parser = subparsers.add_parser(
            'search',
            help='Search content in LogLog files',
            description='Search for text patterns in LogLog files'
        )
        parser.add_argument('pattern', help='Search pattern (supports regex)')
        parser.add_argument('files', nargs='+', help='Files to search')
        parser.add_argument('--regex', action='store_true',
                          help='Treat pattern as regular expression')
        parser.add_argument('--case-sensitive', action='store_true',
                          help='Case sensitive search')
        parser.add_argument('--context', type=int, default=0,
                          help='Lines of context to show')
    
    def _add_batch_parser(self, subparsers):
        """Add batch processing parser"""
        parser = subparsers.add_parser(
            'batch-convert',
            help='Batch convert multiple files',
            description='Convert multiple LogLog files in batch'
        )
        parser.add_argument('directory', help='Directory to process')
        parser.add_argument('--from', dest='from_format', choices=['log', 'md'], 
                          default='log', help='Source format')
        parser.add_argument('--to', choices=['html', 'md', 'latex', 'pdf'], 
                          required=True, help='Target format')
        parser.add_argument('--recursive', '-r', action='store_true',
                          help='Process directories recursively')
        parser.add_argument('--pattern', default='*.log',
                          help='File pattern to match (default: *.log)')
    
    def _add_stats_parser(self, subparsers):
        """Add statistics parser"""
        parser = subparsers.add_parser(
            'stats',
            help='Show file statistics',
            description='Display statistics about LogLog files'
        )
        parser.add_argument('files', nargs='+', help='Files to analyze')
        parser.add_argument('--format', choices=['text', 'json'], default='text',
                          help='Output format')
    
    def run(self, args=None) -> int:
        """Run the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            # Route to appropriate handler
            handler_name = f'_handle_{parsed_args.command.replace("-", "_")}'
            handler = getattr(self, handler_name)
            return handler(parsed_args)
        
        except Exception as e:
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _handle_convert(self, args) -> int:
        """Handle convert command"""
        files = self._expand_file_patterns(args.files)
        
        if not files:
            print("No files found matching the pattern", file=sys.stderr)
            return 1
        
        success_count = 0
        for file_path in files:
            try:
                if args.verbose:
                    print(f"Converting {file_path} to {args.to}...")
                
                output_path = self._get_output_path(file_path, args.to, args.output_dir)
                
                if os.path.exists(output_path) and not args.overwrite:
                    response = input(f"File {output_path} exists. Overwrite? (y/N): ")
                    if response.lower() != 'y':
                        continue
                
                # Perform conversion
                if args.to == 'html':
                    title = args.title or os.path.splitext(os.path.basename(file_path))[0]
                    root = build_tree_from_file(file_path)
                    html_content = root.to_html(title)
                    with open(output_path, 'w') as f:
                        f.write(html_content)
                elif args.to == 'md':
                    to_md_file(file_path, args.header_levels)
                elif args.to == 'latex':
                    to_latex_file(file_path, args.header_levels)
                elif args.to == 'pdf':
                    to_pdf_file(file_path, args.header_levels)
                
                success_count += 1
                if args.verbose:
                    print(f"✓ Created {output_path}")
                    
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}", file=sys.stderr)
        
        print(f"Successfully converted {success_count}/{len(files)} files")
        return 0 if success_count > 0 else 1
    
    def _handle_filter(self, args) -> int:
        """Handle filter command"""
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}", file=sys.stderr)
            return 1
        
        hashtags = [tag.strip() for tag in args.hashtags.split(',')]
        
        try:
            if args.verbose:
                print(f"Filtering {args.file} for hashtags: {', '.join(hashtags)}")
            
            root = build_tree_from_file(args.file)
            filtered_tree = filter_by_hashtags(root, hashtags, args.preserve_structure)
            
            if filtered_tree is None or not filtered_tree.children:
                print("No content found matching the specified hashtags")
                return 1
            
            with open(args.output, 'w') as f:
                print_tree_to_file(filtered_tree, f)
            
            if args.verbose:
                print(f"✓ Filtered content saved to {args.output}")
            
            return 0
            
        except Exception as e:
            print(f"Failed to filter file: {e}", file=sys.stderr)
            return 1
    
    def _handle_todos(self, args) -> int:
        """Handle todos command"""
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}", file=sys.stderr)
            return 1
        
        try:
            root = build_tree_from_file(args.file)
            
            # Map status filter
            status_map = {
                'pending': False,
                'completed': True,
                'in_progress': 'in_progress',
                'all': None
            }
            status_filter = status_map[args.status]
            
            if args.format == 'log':
                if args.output:
                    export_todos_filtered(args.file, status_filter, 
                                        args.output.replace('.log', '').replace('_todos', ''))
                    if args.verbose:
                        print(f"✓ TODOs saved to {args.output}")
                else:
                    # Print to stdout
                    self._print_todos_to_stdout(root, status_filter)
            
            elif args.format == 'json':
                todos = self._extract_todos_as_json(root, status_filter)
                output = json.dumps(todos, indent=2)
                
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(output)
                else:
                    print(output)
            
            elif args.format == 'csv':
                todos = self._extract_todos_as_csv(root, status_filter)
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(todos)
                else:
                    print(todos)
            
            return 0
            
        except Exception as e:
            print(f"Failed to extract TODOs: {e}", file=sys.stderr)
            return 1
    
    def _handle_show(self, args) -> int:
        """Handle show command"""
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}", file=sys.stderr)
            return 1
        
        try:
            root = build_tree_from_file(args.file)
            
            # Set decoration based on compact flag
            decor = "- " if args.compact else "type"
            
            if args.depth:
                # TODO: Implement depth limiting
                print_tree(root, numbered=args.numbered, decor=decor)
            else:
                print_tree(root, numbered=args.numbered, decor=decor)
            
            return 0
            
        except Exception as e:
            print(f"Failed to display file: {e}", file=sys.stderr)
            return 1
    
    def _handle_search(self, args) -> int:
        """Handle search command"""
        import re
        
        files = self._expand_file_patterns(args.files)
        if not files:
            print("No files found matching the pattern", file=sys.stderr)
            return 1
        
        # Compile search pattern
        flags = 0 if args.case_sensitive else re.IGNORECASE
        pattern = re.compile(args.pattern) if args.regex else re.compile(re.escape(args.pattern), flags)
        
        found_matches = False
        
        for file_path in files:
            try:
                root = build_tree_from_file(file_path)
                matches = self._search_tree(root, pattern, file_path, args.context)
                if matches:
                    found_matches = True
                    for match in matches:
                        print(match)
                        
            except Exception as e:
                if args.verbose:
                    print(f"Failed to search {file_path}: {e}", file=sys.stderr)
        
        return 0 if found_matches else 1
    
    def _handle_batch_convert(self, args) -> int:
        """Handle batch convert command"""
        if not os.path.exists(args.directory):
            print(f"Directory not found: {args.directory}", file=sys.stderr)
            return 1
        
        # Find files to process
        if args.recursive:
            pattern = os.path.join(args.directory, '**', args.pattern)
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(args.directory, args.pattern)
            files = glob.glob(pattern)
        
        if not files:
            print(f"No files found matching pattern: {args.pattern}")
            return 1
        
        if args.verbose:
            print(f"Found {len(files)} files to convert")
        
        # Create temporary args for convert handler
        convert_args = argparse.Namespace(
            files=files,
            to=args.to,
            header_levels=4,
            title=None,
            output_dir=None,
            overwrite=True,
            verbose=args.verbose
        )
        
        return self._handle_convert(convert_args)
    
    def _handle_stats(self, args) -> int:
        """Handle stats command"""
        files = self._expand_file_patterns(args.files)
        if not files:
            print("No files found matching the pattern", file=sys.stderr)
            return 1
        
        all_stats = []
        
        for file_path in files:
            try:
                root = build_tree_from_file(file_path)
                stats = self._calculate_file_stats(root, file_path)
                all_stats.append(stats)
                
            except Exception as e:
                if args.verbose:
                    print(f"Failed to analyze {file_path}: {e}", file=sys.stderr)
        
        if args.format == 'json':
            print(json.dumps(all_stats, indent=2))
        else:
            self._print_stats(all_stats)
        
        return 0 if all_stats else 1
    
    # Helper methods
    
    def _expand_file_patterns(self, patterns: List[str]) -> List[str]:
        """Expand file patterns and wildcards"""
        files = []
        for pattern in patterns:
            if '*' in pattern or '?' in pattern:
                files.extend(glob.glob(pattern))
            elif os.path.exists(pattern):
                files.append(pattern)
        return sorted(set(files))  # Remove duplicates and sort
    
    def _get_output_path(self, input_path: str, format_type: str, output_dir: Optional[str]) -> str:
        """Generate output path for converted files"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        extensions = {
            'html': '.html',
            'md': '.md', 
            'latex': '.tex',
            'pdf': '.pdf'
        }
        
        extension = extensions.get(format_type, '.txt')
        filename = base_name + extension
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            return os.path.join(output_dir, filename)
        else:
            return os.path.join(os.path.dirname(input_path), filename)
    
    def _print_todos_to_stdout(self, root, status_filter):
        """Print TODO items to stdout"""
        def collect_todos(node, path=""):
            todos = []
            current_path = f"{path}/{node.data}" if path else node.data
            
            if node.type == "todo":
                if status_filter is None or node.status == status_filter:
                    status_symbol = {
                        True: "[x]",
                        False: "[ ]", 
                        "in_progress": "[-]"
                    }.get(node.status, "[?]")
                    todos.append(f"{status_symbol} {current_path}")
            
            for child in node.children:
                todos.extend(collect_todos(child, current_path))
            
            return todos
        
        todos = collect_todos(root)
        for todo in todos:
            print(todo)
    
    def _extract_todos_as_json(self, root, status_filter) -> List[Dict[str, Any]]:
        """Extract TODOs as JSON structure"""
        def collect_todos(node, path="", level=0):
            todos = []
            current_path = f"{path}/{node.data}" if path and node.data else node.data
            
            if node.type == "todo":
                if status_filter is None or node.status == status_filter:
                    todos.append({
                        "path": current_path,
                        "content": node.data,
                        "status": node.status,
                        "level": level
                    })
            
            for child in node.children:
                todos.extend(collect_todos(child, current_path, level + 1))
            
            return todos
        
        return collect_todos(root)
    
    def _extract_todos_as_csv(self, root, status_filter) -> str:
        """Extract TODOs as CSV format"""
        todos = self._extract_todos_as_json(root, status_filter)
        
        csv_lines = ["Path,Content,Status,Level"]
        for todo in todos:
            path = todo['path'].replace('"', '""')  # Escape quotes
            content = todo['content'].replace('"', '""')
            csv_lines.append(f'"{path}","{content}","{todo["status"]}",{todo["level"]}')
        
        return '\n'.join(csv_lines)
    
    def _search_tree(self, root, pattern, file_path: str, context: int) -> List[str]:
        """Search tree for pattern matches"""
        matches = []
        
        def search_node(node, path=""):
            current_path = f"{path} > {node.data}" if path and node.data else node.data or "root"
            
            if node.data and pattern.search(node.data):
                match_line = f"{file_path}:{current_path}"
                if context > 0:
                    # Add context (simplified - could be enhanced)
                    match_line += f"\n  {node.data}"
                matches.append(match_line)
            
            for child in node.children:
                search_node(child, current_path)
        
        search_node(root)
        return matches
    
    def _calculate_file_stats(self, root, file_path: str) -> Dict[str, Any]:
        """Calculate statistics for a LogLog file"""
        stats = {
            "file": file_path,
            "total_nodes": 0,
            "max_depth": 0,
            "todo_count": {"total": 0, "pending": 0, "completed": 0, "in_progress": 0},
            "hashtag_count": 0
        }
        
        def analyze_node(node, depth=0):
            stats["total_nodes"] += 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            if node.type == "todo":
                stats["todo_count"]["total"] += 1
                if node.status is True:
                    stats["todo_count"]["completed"] += 1
                elif node.status is False:
                    stats["todo_count"]["pending"] += 1
                elif node.status == "in_progress":
                    stats["todo_count"]["in_progress"] += 1
            
            # Count hashtags
            if node.data and '#' in node.data:
                import re
                hashtags = re.findall(r'#\w+', node.data)
                stats["hashtag_count"] += len(hashtags)
            
            for child in node.children:
                analyze_node(child, depth + 1)
        
        analyze_node(root)
        return stats
    
    def _print_stats(self, all_stats: List[Dict[str, Any]]):
        """Print statistics in text format"""
        for stats in all_stats:
            print(f"\n=== {stats['file']} ===")
            print(f"Total nodes: {stats['total_nodes']}")
            print(f"Maximum depth: {stats['max_depth']}")
            print(f"TODOs - Total: {stats['todo_count']['total']}, "
                  f"Pending: {stats['todo_count']['pending']}, "
                  f"Completed: {stats['todo_count']['completed']}, "
                  f"In Progress: {stats['todo_count']['in_progress']}")
            print(f"Hashtags found: {stats['hashtag_count']}")


def main():
    """Main entry point for the CLI"""
    cli = LogLogCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())