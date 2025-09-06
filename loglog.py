import os
import re


class TreeNode(object):
    def __init__(self, name="", children=None, data=""):
        self.name = name
        self.children = []
        self.data = data
        self.get_type()
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name

    def add_child(self, node):
        assert isinstance(node, TreeNode)
        self.children.append(node)

    def get_type(self):
        if self.is_todo():
            self.type = "todo"
            self.todo_status()
        else:
            self.type = "regular"
        # regular item
        regex = re.compile("- *")
        if re.match(regex, self.data.lower()):
            self.data = self.data[1:].strip()

    def is_todo(self):
        regex1 = re.compile(r"^\[.\]")
        regex2 = re.compile(r"^\[\]")
        if re.match(regex1, self.data.lower()) or re.match(regex2, self.data.lower()):
            return True
        else:
            return False

    def todo_status(self):
        if self.data.lower().startswith("[]"):
            done = False
            data = self.data[2:].strip()
        elif self.data.lower().startswith("[ ]"):
            done = False
            data = self.data[3:].strip()
        elif self.data.lower().startswith("[x]"):
            done = True
            data = self.data[3:].strip()
        elif self.data.lower().startswith("[-]"):
            done = "in_progress"
            data = self.data[3:].strip()
        else:
            done = None
            data = self.data[3:].strip()
        self.status = done
        # Extended status support: False=pending, True=completed, "in_progress"=in progress, None=unknown
        self.data = data

    def _get_shallowest_leaf_depth(self, current_depth=0):
        if not self.children:
            return current_depth
        
        min_depth = float('inf')
        for child in self.children:
            child_depth = child._get_shallowest_leaf_depth(current_depth + 1)
            min_depth = min(min_depth, child_depth)
        
        return min_depth
    
    def to_md(self, header_levels=4, _current_depth=0, _shallowest_leaf_depth=None):
        if self.type == "root":
            shallowest_leaf_depth = self._get_shallowest_leaf_depth()
            result = ""
            for child in self.children:
                child_result = child.to_md(header_levels, 1, shallowest_leaf_depth)
                if child_result is not None:
                    result += child_result
                if result and not result.endswith("\n\n"):
                    result += "\n"
            return result.rstrip() + "\n"
        
        if _shallowest_leaf_depth is None:
            _shallowest_leaf_depth = self._get_shallowest_leaf_depth()
        
        current_depth = _current_depth
        header_cutoff = min(_shallowest_leaf_depth, header_levels + 1)
        
        if current_depth < header_cutoff:
            header_level = current_depth
            header_prefix = "#" * header_level + " "
            
            if self.type == "todo":
                if self.status == True:
                    content = f"[x] {self.data}"
                elif self.status == False:
                    content = f"[ ] {self.data}"
                elif self.status == "in_progress":
                    content = f"[-] {self.data}"
                else:
                    content = f"[?] {self.data}"
            else:
                content = self.data
            
            result = f"{header_prefix}{content}\n\n"
        else:
            list_depth = current_depth - header_cutoff
            indent = "  " * list_depth
            
            if self.type == "todo":
                if self.status == True:
                    line_start = "- [x] "
                elif self.status == False:
                    line_start = "- [ ] "
                elif self.status == "in_progress":
                    line_start = "- [-] "
                else:
                    line_start = "- [?] "
            else:
                line_start = "- "
            
            result = f"{indent}{line_start}{self.data}\n"
        
        for child in self.children:
            child_result = child.to_md(header_levels, _current_depth + 1, _shallowest_leaf_depth)
            if child_result is not None:
                result += child_result
        
        return result
    
    def to_latex(self, header_levels=4):
        """
        Convert tree to LaTeX format by first converting to markdown,
        then using pandoc to convert markdown to LaTeX.
        
        Args:
            header_levels (int): Maximum number of header levels to use
            
        Returns:
            str: LaTeX content
        """
        import subprocess
        import tempfile
        import os
        
        # First convert to markdown
        md_content = self.to_md(header_levels)
        
        # Use pandoc to convert markdown to LaTeX
        try:
            # Create temporary file for markdown content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
                temp_md.write(md_content)
                temp_md_path = temp_md.name
            
            # Run pandoc to convert to LaTeX
            result = subprocess.run([
                'pandoc', 
                temp_md_path,
                '-t', 'latex',
                '--standalone'
            ], capture_output=True, text=True, check=True)
            
            latex_content = result.stdout
            
            # Clean up temporary file
            os.unlink(temp_md_path)
            
            return latex_content
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Pandoc is not installed or not found in PATH")
    
    def to_pdf(self, header_levels=4):
        """
        Convert tree to PDF format by first converting to LaTeX,
        then using pdflatex to convert LaTeX to PDF.
        
        Args:
            header_levels (int): Maximum number of header levels to use
            
        Returns:
            bytes: PDF content as bytes
        """
        import subprocess
        import tempfile
        import os
        
        # First convert to LaTeX
        latex_content = self.to_latex(header_levels)
        
        # Use pdflatex to convert LaTeX to PDF
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create temporary file for LaTeX content
                temp_tex_path = os.path.join(temp_dir, 'document.tex')
                with open(temp_tex_path, 'w') as temp_tex:
                    temp_tex.write(latex_content)
                
                # Run pdflatex to convert to PDF
                result = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', temp_dir,
                    temp_tex_path
                ], capture_output=True, text=True, cwd=temp_dir)
                
                # Check if PDF was created (pdflatex may succeed despite non-zero return code)
                pdf_path = os.path.join(temp_dir, 'document.pdf')
                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()
                        # If PDF has content, consider it successful
                        if len(pdf_content) > 0:
                            return pdf_content
                
                # If no PDF was created or it's empty, then it's a failure
                raise RuntimeError(f"pdflatex conversion failed (return code {result.returncode}): {result.stderr}")
                
        except FileNotFoundError:
            raise RuntimeError("pdflatex is not installed or not found in PATH")

    def to_html(self, title="Loglog Document"):
        """
        Convert tree structure to interactive HTML with foldable items.
        
        Args:
            title (str): Title for the HTML document
            
        Returns:
            str: Complete HTML document with interactive tree
        """
        if self.type == "root":
            # Generate HTML for all children
            content_html = ""
            for child in self.children:
                content_html += child.to_html()
            
            # Create complete HTML document
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #333333;
            --border-color: #ddd;
            --help-bg: #f0f0f0;
            --help-bg-hover: #e9e9e9;
            --help-collapsed-bg: #e0e0e0;
            --help-collapsed-hover: #d0d0d0;
            --help-text: #666;
            --help-collapsed-text: #888;
            --triangle-color: #666;
            --todo-pending: #e74c3c;
            --todo-completed: #95a5a6;
            --focused-bg: rgba(52, 152, 219, 0.05);
            --focused-border: #3498db;
        }}
        
        [data-theme="dark"] {{
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --border-color: #444;
            --help-bg: #2c2c2c;
            --help-bg-hover: #3a3a3a;
            --help-collapsed-bg: #404040;
            --help-collapsed-hover: #4a4a4a;
            --help-text: #aaa;
            --help-collapsed-text: #888;
            --triangle-color: #aaa;
            --todo-pending: #e74c3c;
            --todo-completed: #7f8c8d;
            --focused-bg: rgba(52, 152, 219, 0.03);
            --focused-border: #5dade2;
        }}
        
        body {{
            font-family: monospace;
            margin: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: background-color 0.3s, color 0.3s;
        }}
        
        h1 {{
            margin-bottom: 30px;
            font-size: 24px;
        }}
        
        ul {{
            margin: 0;
            padding-left: 20px;
            list-style: none;
        }}
        
        li {{
            margin: 2px 0;
            position: relative;
        }}
        
        .triangle {{
            display: inline-block;
            width: 0;
            height: 0;
            margin-right: 5px;
            cursor: pointer;
            transition: transform 0.2s;
            user-select: none;
        }}
        
        .triangle.expanded {{
            border-left: 6px solid var(--triangle-color);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            transform: rotate(90deg);
        }}
        
        .triangle.collapsed {{
            border-left: 6px solid var(--triangle-color);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            transform: rotate(0deg);
        }}
        
        .item-content {{
            display: inline;
        }}
        
        .children {{
            margin-left: 0px;
        }}
        
        .children.hidden {{
            display: none;
        }}
        
        .todo-completed {{
            text-decoration: line-through;
            color: var(--todo-completed);
        }}
        
        .todo-pending {{
            color: var(--todo-pending);
            font-weight: bold;
        }}
        
        .todo-in-progress {{
            color: #f39c12;
            font-weight: bold;
            font-style: italic;
        }}
        
        .no-children {{
            margin-left: 11px;
        }}
        
        .controls {{
            position: fixed;
            top: 10px;
            right: 10px;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }}
        
        .keyboard-help {{
            font-size: 12px;
            color: var(--help-text);
            background: var(--help-bg);
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            user-select: none;
            transition: all 0.3s ease;
            max-width: 300px;
            border: 1px solid var(--border-color);
            z-index: 1000;
            position: relative;
        }}
        
        .keyboard-help.collapsed {{
            padding: 6px 9px;
            font-size: 16px;
            background: var(--help-collapsed-bg);
            color: var(--help-collapsed-text);
            max-width: 25px;
            font-weight: bold;
        }}
        
        .keyboard-help:hover {{
            background: var(--help-bg-hover);
        }}
        
        .keyboard-help.collapsed:hover {{
            background: var(--help-collapsed-hover);
        }}
        
        .theme-toggle {{
            background: var(--help-bg);
            border: 1px solid var(--border-color);
            color: var(--help-text);
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-family: monospace;
            user-select: none;
            transition: all 0.3s ease;
        }}
        
        .theme-toggle:hover {{
            background: var(--help-bg-hover);
        }}
        
        .focused-branch {{
            background-color: var(--focused-bg);
            border-left: 3px solid transparent;
            padding-left: 8px;
            border-radius: 2px;
            transition: border-color 0.2s ease;
        }}
        
        .focused-branch.active {{
            border-left-color: var(--focused-border);
        }}
        
        .keyboard-focused {{
            background-color: var(--focused-bg);
            border-left: 3px solid var(--focused-border);
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="controls">
        <button class="theme-toggle" id="themeToggle">◐</button>
        <div class="keyboard-help collapsed" id="keyboardHelp" title="Click to show keyboard shortcuts">
            ?
        </div>
    </div>
    <h1>{title}</h1>
    <ul class="root-list">
{content_html}
    </ul>
    
    <script>
        let currentFocusedItem = null;
        let currentFocusedBranch = [];
        let helpVisible = false;
        let isDarkMode = false;
        let allItems = [];
        
        // Theme toggle functionality
        document.getElementById('themeToggle').addEventListener('click', function() {{
            const body = document.body;
            const button = document.getElementById('themeToggle');
            
            isDarkMode = !isDarkMode;
            
            if (isDarkMode) {{
                body.setAttribute('data-theme', 'dark');
                button.innerHTML = '○';
            }} else {{
                body.removeAttribute('data-theme');
                button.innerHTML = '●';
            }}
            
            // Store preference
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        }});
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {{
            // Load saved theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {{
                document.getElementById('themeToggle').click();
            }}
            
            // Initialize items list for keyboard navigation
            allItems = Array.from(document.querySelectorAll('li[data-level]'));
            
            // Add invisible borders to all items to prevent text movement
            allItems.forEach(item => {{
                item.classList.add('focused-branch');
            }});
            
            // Set first item as focused by default
            if (allItems.length > 0) {{
                setFocusedItem(allItems[0]);
            }}
        }});
        
        // Help toggle functionality
        document.getElementById('keyboardHelp').addEventListener('click', function() {{
            const helpDiv = document.getElementById('keyboardHelp');
            helpVisible = !helpVisible;
            
            if (helpVisible) {{
                helpDiv.classList.remove('collapsed');
                helpDiv.innerHTML = `Ctrl+1-9: Fold to level | Ctrl+0: Unfold all<br>
                    Ctrl+Alt+1-9: Focus mode (fold others to level)<br>
                    Up/Down: Navigate visible | Left/Right: Hierarchical<br>
                    Enter/Space: Toggle fold | Left: Always fold<br>
                    <small style="color: #999;">Click to hide</small>`;
                helpDiv.title = '';
            }} else {{
                helpDiv.classList.add('collapsed');
                helpDiv.innerHTML = `?`;
                helpDiv.title = 'Click to show keyboard shortcuts';
            }}
        }});
        
        // Click handler for triangles
        document.addEventListener('click', function(e) {{
            if (e.target.classList.contains('triangle')) {{
                const li = e.target.closest('li');
                const children = li.querySelector('.children');
                
                if (children) {{
                    children.classList.toggle('hidden');
                    e.target.classList.toggle('expanded');
                    e.target.classList.toggle('collapsed');
                }}
            }}
        }});
        
        // Keyboard navigation functions
        function setFocusedItem(item) {{
            // Clear previous focus
            if (currentFocusedItem) {{
                currentFocusedItem.classList.remove('keyboard-focused');
                // Clear branch highlighting
                currentFocusedBranch.forEach(branchItem => {{
                    branchItem.classList.remove('active');
                }});
            }}
            
            currentFocusedItem = item;
            
            if (item) {{
                item.classList.add('keyboard-focused');
                
                // Build branch path and highlight
                currentFocusedBranch = getBranchPath(item);
                currentFocusedBranch.forEach(branchItem => {{
                    branchItem.classList.add('active');
                }});
                
                // Scroll item into view if needed
                item.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}
        
        function getVisibleItems() {{
            return allItems.filter(item => {{
                // Check if item is visible (not inside a folded section)
                let current = item;
                while (current && current.hasAttribute('data-level')) {{
                    const parentUl = current.parentElement;
                    if (parentUl && parentUl.classList.contains('children') && parentUl.classList.contains('hidden')) {{
                        return false;
                    }}
                    // Move up to parent li
                    if (parentUl && parentUl.classList.contains('children')) {{
                        current = parentUl.parentElement;
                    }} else {{
                        break;
                    }}
                }}
                return true;
            }});
        }}
        
        function navigateUp() {{
            const visibleItems = getVisibleItems();
            const currentIndex = currentFocusedItem ? visibleItems.indexOf(currentFocusedItem) : -1;
            if (currentIndex > 0) {{
                setFocusedItem(visibleItems[currentIndex - 1]);
            }} else if (visibleItems.length > 0) {{
                setFocusedItem(visibleItems[0]);
            }}
        }}
        
        function navigateDown() {{
            const visibleItems = getVisibleItems();
            const currentIndex = currentFocusedItem ? visibleItems.indexOf(currentFocusedItem) : -1;
            if (currentIndex < visibleItems.length - 1) {{
                setFocusedItem(visibleItems[currentIndex + 1]);
            }} else if (visibleItems.length > 0) {{
                setFocusedItem(visibleItems[visibleItems.length - 1]);
            }}
        }}
        
        function navigateRight() {{
            if (!currentFocusedItem) return;
            
            const children = currentFocusedItem.querySelector('.children');
            const triangle = currentFocusedItem.querySelector('.triangle');
            
            if (children) {{
                if (children.classList.contains('hidden')) {{
                    // Current item is folded, unfold it and go to first child
                    children.classList.remove('hidden');
                    triangle.classList.remove('collapsed');
                    triangle.classList.add('expanded');
                    
                    // Find first child
                    const firstChild = children.querySelector('li[data-level]');
                    if (firstChild) {{
                        setFocusedItem(firstChild);
                    }}
                }} else {{
                    // Current item is already unfolded, go to first child
                    const firstChild = children.querySelector('li[data-level]');
                    if (firstChild) {{
                        setFocusedItem(firstChild);
                    }} else {{
                        // No children, go to next item in list
                        navigateToNextInHierarchy();
                    }}
                }}
            }} else {{
                // No children, go to next item in hierarchy
                navigateToNextInHierarchy();
            }}
        }}
        
        function navigateLeft() {{
            if (!currentFocusedItem) return;
            
            const children = currentFocusedItem.querySelector('.children');
            const triangle = currentFocusedItem.querySelector('.triangle');
            
            if (children && !children.classList.contains('hidden')) {{
                // Current item is unfolded, fold it and stay on same item
                children.classList.add('hidden');
                triangle.classList.remove('expanded');
                triangle.classList.add('collapsed');
            }} else {{
                // Current item is folded or has no children, go to parent
                const parentUl = currentFocusedItem.parentElement;
                if (parentUl && parentUl.classList.contains('children')) {{
                    const parentLi = parentUl.parentElement;
                    if (parentLi && parentLi.hasAttribute('data-level')) {{
                        setFocusedItem(parentLi);
                        
                        // Also fold the parent after navigating to it
                        const parentChildren = parentLi.querySelector('.children');
                        const parentTriangle = parentLi.querySelector('.triangle');
                        if (parentChildren && !parentChildren.classList.contains('hidden')) {{
                            parentChildren.classList.add('hidden');
                            parentTriangle.classList.remove('expanded');
                            parentTriangle.classList.add('collapsed');
                        }}
                    }}
                }}
            }}
        }}
        
        function navigateToNextInHierarchy() {{
            const currentIndex = allItems.indexOf(currentFocusedItem);
            if (currentIndex < allItems.length - 1) {{
                setFocusedItem(allItems[currentIndex + 1]);
            }}
        }}
        
        function toggleCurrentItem() {{
            if (currentFocusedItem) {{
                const triangle = currentFocusedItem.querySelector('.triangle');
                const children = currentFocusedItem.querySelector('.children');
                
                if (triangle && children) {{
                    children.classList.toggle('hidden');
                    triangle.classList.toggle('expanded');
                    triangle.classList.toggle('collapsed');
                }}
            }}
        }}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey) {{
                const key = e.key;
                
                if (key === '0') {{
                    // Unfold everything
                    e.preventDefault();
                    unfoldAll();
                }} else if (key >= '1' && key <= '9') {{
                    const level = parseInt(key);
                    
                    if (e.altKey) {{
                        // Focus mode: fold others to level, keep current branch unfolded
                        e.preventDefault();
                        focusMode(level + 1); // Adjust for 0-based vs 1-based indexing
                    }} else {{
                        // Regular fold to specific level
                        e.preventDefault();
                        foldToLevel(level + 1); // Adjust for 0-based vs 1-based indexing
                    }}
                }}
            }} else {{
                // Navigation keys
                switch(e.key) {{
                    case 'ArrowUp':
                        e.preventDefault();
                        navigateUp();
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        navigateDown();
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        navigateRight();
                        break;
                    case 'ArrowLeft':
                        e.preventDefault();
                        navigateLeft();
                        break;
                    case 'Enter':
                        e.preventDefault();
                        toggleCurrentItem();
                        break;
                    case ' ':  // Spacebar
                        e.preventDefault();
                        toggleCurrentItem();
                        break;
                }}
            }}
        }});
        
        function unfoldAll() {{
            const allChildren = document.querySelectorAll('.children');
            const allTriangles = document.querySelectorAll('.triangle');
            
            allChildren.forEach(children => children.classList.remove('hidden'));
            allTriangles.forEach(triangle => {{
                triangle.classList.remove('collapsed');
                triangle.classList.add('expanded');
            }});
        }}
        
        function foldToLevel(maxLevel) {{
            const allItems = document.querySelectorAll('li[data-level]');
            
            allItems.forEach(li => {{
                const level = parseInt(li.getAttribute('data-level'));
                const children = li.querySelector('.children');
                const triangle = li.querySelector('.triangle');
                
                if (children && triangle) {{
                    if (level >= maxLevel) {{
                        // Fold items at or beyond max level
                        children.classList.add('hidden');
                        triangle.classList.remove('expanded');
                        triangle.classList.add('collapsed');
                    }} else {{
                        // Unfold items below max level
                        children.classList.remove('hidden');
                        triangle.classList.remove('collapsed');
                        triangle.classList.add('expanded');
                    }}
                }}
            }});
        }}
        
        function getBranchPath(targetLi) {{
            const path = [];
            let current = targetLi;
            
            while (current && current.hasAttribute('data-level')) {{
                path.unshift(current);
                
                // Find parent li by traversing up the DOM
                const parentUl = current.parentElement;
                if (parentUl && parentUl.classList.contains('children')) {{
                    current = parentUl.parentElement;
                }} else {{
                    break;
                }}
            }}
            
            return path;
        }}
        
        function focusMode(maxLevel) {{
            if (!currentFocusedItem || currentFocusedBranch.length === 0) {{
                // No item focused, fall back to regular fold
                foldToLevel(maxLevel);
                return;
            }}
            
            const allItemsQuery = document.querySelectorAll('li[data-level]');
            const focusedSet = new Set(currentFocusedBranch);
            
            allItemsQuery.forEach(li => {{
                const level = parseInt(li.getAttribute('data-level'));
                const children = li.querySelector('.children');
                const triangle = li.querySelector('.triangle');
                
                if (children && triangle) {{
                    const isInFocusedBranch = focusedSet.has(li);
                    
                    if (isInFocusedBranch) {{
                        // Keep focused branch expanded
                        children.classList.remove('hidden');
                        triangle.classList.remove('collapsed');
                        triangle.classList.add('expanded');
                    }} else if (level >= maxLevel) {{
                        // Fold non-focused items at or beyond max level
                        children.classList.add('hidden');
                        triangle.classList.remove('expanded');
                        triangle.classList.add('collapsed');
                    }} else {{
                        // Unfold non-focused items below max level
                        children.classList.remove('hidden');
                        triangle.classList.remove('collapsed');
                        triangle.classList.add('expanded');
                    }}
                }}
            }});
        }}
        
    </script>
</body>
</html>"""
            return html
        else:
            # Generate HTML for individual node
            has_children = len(self.children) > 0
            
            # Determine content and styling based on type
            if self.type == "todo":
                if self.status == True:
                    checkbox = "☑"
                    css_class = "todo-completed"
                elif self.status == False:
                    checkbox = "☐"
                    css_class = "todo-pending"
                elif self.status == "in_progress":
                    checkbox = "⚬"
                    css_class = "todo-in-progress"
                else:
                    checkbox = "☒"
                    css_class = "todo-pending"
                content = f"{checkbox} {self.data}"
            else:
                content = self.data
                css_class = ""
            
            # Calculate depth level for keyboard shortcuts
            level = self._calculate_depth()
            
            html = f'        <li data-level="{level}">\n'
            
            if has_children:
                html += f'            <span class="triangle expanded"></span>\n'
                html += f'            <span class="item-content {css_class}">{content}</span>\n'
                html += f'            <ul class="children">\n'
                
                for child in self.children:
                    html += child.to_html()
                
                html += f'            </ul>\n'
            else:
                html += f'            <span class="no-children item-content {css_class}">{content}</span>\n'
            
            html += f'        </li>\n'
            return html
    
    def _calculate_depth(self):
        """Calculate depth of current node from root"""
        if self.type == "root":
            return 0
        # This is a simple approximation - in a full implementation,
        # we'd track parent references to calculate exact depth
        return len(self.name.split('.'))


class Tree(object):
    def __init__(self):
        pass


def build_tree_from_text(text_lines):
    root = TreeNode(name="")  # Create a root node
    root.type = "root"
    stack = [(-1, root)]  # Stack to keep track of parent nodes at each level

    for line in text_lines:
        line = line.replace("\t", " " * 4)
        depth = 0
        while line.startswith(" " * 4):
            depth += 1
            line = line[4:]
        if len(line.strip()):
            while stack and depth <= stack[-1][0]:
                stack.pop()
            if stack:
                parent_depth, parent = stack[-1]
                node_numbering = parent.name + str(len(parent.children)) + "."
                node = TreeNode(name=node_numbering, data=line)
                parent.add_child(node)  # Add node as a child of the parent
            stack.append((depth, node))

    return root


def get_node(root, address):
    adr = [int(a) for a in address.split(".") if a != ""]
    parent = root
    while len(adr):
        node = parent.children[adr[0]]
        adr = adr[1:]
        parent = node
    return node


def print_tree(node, depth=0, numbered=False, decor="type"):
    if numbered:
        num_str = f"{node.name} "
    else:
        num_str = ""
    # decorate start of line
    line_start = decor
    if decor == "type":
        if node.type == "todo":
            if node.status == True:
                line_start = "[x] "
            elif node.status == False:
                line_start = "[] "
            else:
                line_start = "[?] "
        elif node.type == "regular":
            line_start = "- "
    # do not print root
    if node.type == "root":
        pass
    # print all children
    else:
        print_str = f"{' ' * 4 * (depth - 1)}{line_start}{num_str}{node.data}"
        print(print_str)
    for child in node.children:
        print_tree(child, depth + 1, numbered=numbered, decor=decor)


def build_tree_from_file(file_path):
    with open(file_path, "r") as file:
        text_lines = file.readlines()
    root = build_tree_from_text(text_lines)
    root.data = file_path
    return root


def from_md(markdown_text):
    """
    Convert markdown text to loglog format.
    
    Args:
        markdown_text (str): Markdown formatted text
        
    Returns:
        str: Text in loglog format with proper indentation
    """
    lines = markdown_text.split('\n')
    result_lines = []
    current_indent = 0
    in_paragraph = False
    paragraph_lines = []
    
    def flush_paragraph():
        """Add accumulated paragraph lines to result"""
        nonlocal paragraph_lines, in_paragraph
        if paragraph_lines:
            paragraph_text = ' '.join(paragraph_lines).strip()
            if paragraph_text:
                indent = '    ' * (current_indent // 4)
                result_lines.append(f"{indent}- {paragraph_text}")
            paragraph_lines = []
        in_paragraph = False
    
    def get_header_level(line):
        """Get header level from line (1 for #, 2 for ##, etc.)"""
        if line.startswith('#'):
            count = 0
            for char in line:
                if char == '#':
                    count += 1
                else:
                    break
            return count
        return 0
    
    def is_todo_item(line):
        """Check if line is a TODO list item"""
        stripped = line.lstrip()
        if stripped.startswith('- [') and len(stripped) > 4 and stripped[3] in ' x?':
            return True
        return False
    
    def get_list_indent_level(line):
        """Get indentation level of list item"""
        indent_count = 0
        for char in line:
            if char == ' ':
                indent_count += 1
            elif char == '\t':
                indent_count += 4
            else:
                break
        return indent_count
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Empty line - might end paragraph or just be spacing
        if not line.strip():
            if in_paragraph:
                flush_paragraph()
            i += 1
            continue
        
        # Header
        header_level = get_header_level(line)
        if header_level > 0:
            flush_paragraph()
            header_text = line[header_level:].strip()
            header_indent = '    ' * (header_level - 1)
            result_lines.append(f"{header_indent}- {header_text}")
            current_indent = header_level * 4  # Content under header is indented one level deeper
        
        # TODO list item
        elif is_todo_item(line):
            flush_paragraph()
            list_indent = get_list_indent_level(line)
            todo_text = line.lstrip()[2:]  # Remove "- " prefix
            # Convert markdown indentation (2 spaces per level) to loglog (4 spaces per level)
            total_indent_levels = current_indent // 4 + list_indent // 2
            indent = '    ' * total_indent_levels
            result_lines.append(f"{indent}{todo_text}")
        
        # Regular list item
        elif line.lstrip().startswith('- '):
            flush_paragraph()
            list_indent = get_list_indent_level(line)
            list_text = line.lstrip()[2:]  # Remove "- " prefix
            # Convert markdown indentation (2 spaces per level) to loglog (4 spaces per level)
            total_indent_levels = current_indent // 4 + list_indent // 2
            indent = '    ' * total_indent_levels
            result_lines.append(f"{indent}- {list_text}")
        
        # Regular paragraph text
        else:
            # Accumulate paragraph lines
            if not in_paragraph:
                in_paragraph = True
                paragraph_lines = []
            paragraph_lines.append(line.strip())
        
        i += 1
    
    # Flush any remaining paragraph
    flush_paragraph()
    
    return '\n'.join(result_lines) + '\n'


def from_md_file(file_path):
    """
    Read markdown from file and convert to loglog format.
    
    Args:
        file_path (str): Path to markdown file
        
    Returns:
        str: Text in loglog format
    """
    with open(file_path, 'r') as f:
        markdown_text = f.read()
    return from_md(markdown_text)


def to_html_file(input_file_path, title=None):
    """
    Convert loglog file to HTML file with same base name.
    
    Args:
        input_file_path (str): Path to input loglog file
        title (str): Optional title for HTML document. If None, uses filename.
        
    Returns:
        str: Path to generated HTML file
    """
    import os
    
    # Generate output path with .html extension
    base_name = os.path.splitext(input_file_path)[0]
    output_path = base_name + '.html'
    
    # Use filename as title if not provided
    if title is None:
        title = os.path.basename(base_name)
    
    # Build tree and generate HTML
    root = build_tree_from_file(input_file_path)
    html_content = root.to_html(title)
    
    # Write HTML file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return output_path


def to_md_file(input_file_path, header_levels=4):
    """
    Convert loglog file to Markdown file with same base name.
    
    Args:
        input_file_path (str): Path to input loglog file
        header_levels (int): Maximum number of header levels to use
        
    Returns:
        str: Path to generated Markdown file
    """
    import os
    
    # Generate output path with .md extension
    base_name = os.path.splitext(input_file_path)[0]
    output_path = base_name + '.md'
    
    # Build tree and generate Markdown
    root = build_tree_from_file(input_file_path)
    md_content = root.to_md(header_levels)
    
    # Write Markdown file
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    return output_path


def from_md_to_file(input_md_path):
    """
    Convert markdown file to loglog file with same base name.
    
    Args:
        input_md_path (str): Path to input markdown file
        
    Returns:
        str: Path to generated loglog file
    """
    import os
    
    # Generate output path with .txt extension
    base_name = os.path.splitext(input_md_path)[0]
    output_path = base_name + '.txt'
    
    # Convert markdown to loglog format
    loglog_content = from_md_file(input_md_path)
    
    # Write loglog file
    with open(output_path, 'w') as f:
        f.write(loglog_content)
    
    return output_path


def to_latex_file(input_file_path, header_levels=4):
    """
    Convert loglog file to LaTeX file with same base name.
    
    Args:
        input_file_path (str): Path to input loglog file
        header_levels (int): Maximum number of header levels to use
        
    Returns:
        str: Path to generated LaTeX file
    """
    import os
    
    # Generate output path with .tex extension
    base_name = os.path.splitext(input_file_path)[0]
    output_path = base_name + '.tex'
    
    # Build tree and generate LaTeX
    root = build_tree_from_file(input_file_path)
    latex_content = root.to_latex(header_levels)
    
    # Write LaTeX to file
    with open(output_path, 'w') as f:
        f.write(latex_content)
    
    return output_path


def to_pdf_file(input_file_path, header_levels=4):
    """
    Convert loglog file to PDF file with same base name.
    
    Args:
        input_file_path (str): Path to input loglog file
        header_levels (int): Maximum number of header levels to use
        
    Returns:
        str: Path to generated PDF file
    """
    import os
    
    # Generate output path with .pdf extension
    base_name = os.path.splitext(input_file_path)[0]
    output_path = base_name + '.pdf'
    
    # Build tree and generate PDF
    root = build_tree_from_file(input_file_path)
    pdf_content = root.to_pdf(header_levels)
    
    # Write PDF to file
    with open(output_path, 'wb') as f:
        f.write(pdf_content)
    
    return output_path


def filter_by_hashtags(root, hashtags, preserve_structure=True, include_children=True):
    """
    Filter tree to include only branches that contain specified hashtags.
    
    Args:
        root (TreeNode): Root node of the tree
        hashtags (str or list): Hashtag(s) to search for (with or without #)
        preserve_structure (bool): Whether to preserve parent structure
        
    Returns:
        TreeNode: New tree with filtered content
    """
    if isinstance(hashtags, str):
        hashtags = [hashtags]
    
    # Normalize hashtags (ensure they start with #)
    normalized_tags = []
    for tag in hashtags:
        if not tag.startswith('#'):
            tag = '#' + tag
        normalized_tags.append(tag.lower())
    
    def has_hashtag(node):
        """Check if node contains any of the hashtags"""
        content = node.data.lower()
        return any(tag in content for tag in normalized_tags)
    
    def collect_matching_branches(node, path=[]):
        """Collect all branches that contain hashtags"""
        matching_branches = []
        current_path = path + [node]
        
        # Check if current node has hashtag
        if has_hashtag(node):
            matching_branches.append(current_path)
        
        # Recursively check children
        for child in node.children:
            matching_branches.extend(collect_matching_branches(child, current_path))
        
        return matching_branches
    
    def build_filtered_tree(matching_branches):
        """Build new tree from matching branches"""
        if not matching_branches:
            return None
        
        # Create new root
        filtered_root = TreeNode(name="", data="")
        filtered_root.type = "root"
        
        # Build structure from matching branches
        for branch in matching_branches:
            current = filtered_root
            
            # Skip root node in branch
            for i, node in enumerate(branch[1:], 1):
                # Find or create child at this level
                child = None
                for existing_child in current.children:
                    if existing_child.name == node.name:
                        child = existing_child
                        break
                
                if child is None:
                    # Create new child
                    child = TreeNode(name=node.name, data=node.data)
                    child.type = node.type
                    if hasattr(node, 'status'):
                        child.status = node.status
                    current.add_child(child)
                
                current = child
        
        return filtered_root
    
    # Collect all matching branches
    matching_branches = collect_matching_branches(root)
    
    # Build filtered tree
    return build_filtered_tree(matching_branches)


def export_hashtag_filtered(input_file_path, hashtags, output_suffix=None):
    """
    Export filtered content based on hashtags to a new file.
    
    Args:
        input_file_path (str): Path to input loglog file
        hashtags (str or list): Hashtag(s) to filter by
        output_suffix (str): Suffix for output filename (auto-generated if None)
        
    Returns:
        str: Path to generated filtered file
    """
    import os
    
    # Build tree from file
    root = build_tree_from_file(input_file_path)
    
    # Filter by hashtags
    filtered_tree = filter_by_hashtags(root, hashtags)
    
    if filtered_tree is None:
        raise ValueError(f"No content found with hashtags: {hashtags}")
    
    # Generate output filename
    base_name = os.path.splitext(input_file_path)[0]
    
    if output_suffix is None:
        if isinstance(hashtags, str):
            tag_suffix = hashtags.replace('#', '').replace(' ', '_')
        else:
            tag_suffix = '_'.join([tag.replace('#', '') for tag in hashtags])
        output_suffix = f"_{tag_suffix}"
    
    output_path = f"{base_name}{output_suffix}.log"
    
    # Write filtered content
    with open(output_path, 'w') as f:
        print_tree_to_file(filtered_tree, f)
    
    return output_path


def print_tree_to_file(node, file_handle, depth=0):
    """
    Print tree structure to file in loglog format.
    
    Args:
        node (TreeNode): Node to print
        file_handle: File handle to write to
        depth (int): Current depth level
    """
    # Don't print root node
    if node.type == "root":
        for child in node.children:
            print_tree_to_file(child, file_handle, depth)
        return
    
    # Generate indentation
    indent = "    " * depth
    
    # Generate line prefix based on type
    if node.type == "todo":
        if node.status == True:
            prefix = "[x] "
        elif node.status == False:
            prefix = "[] "
        elif node.status == "in_progress":
            prefix = "[-] "
        else:
            prefix = "[?] "
    else:
        prefix = "- " if not node.data.startswith('-') else ""
    
    # Write the line
    file_handle.write(f"{indent}{prefix}{node.data}\n")
    
    # Write children
    for child in node.children:
        print_tree_to_file(child, file_handle, depth + 1)


def export_todos_filtered(input_file_path, status_filter=None, output_suffix="_todos"):
    """
    Export TODO items with optional status filtering.
    
    Args:
        input_file_path (str): Path to input loglog file
        status_filter: Filter by status (True=completed, False=pending, "in_progress"=in progress, None=all)
        output_suffix (str): Suffix for output filename
        
    Returns:
        str: Path to generated filtered file
    """
    import os
    
    # Build tree from file
    root = build_tree_from_file(input_file_path)
    
    def collect_todo_branches(node, path=[]):
        """Collect branches containing TODO items"""
        matching_branches = []
        current_path = path + [node]
        
        # Check if current node is a TODO with matching status
        if node.type == "todo":
            if status_filter is None or node.status == status_filter:
                matching_branches.append(current_path)
        
        # Recursively check children
        for child in node.children:
            matching_branches.extend(collect_todo_branches(child, current_path))
        
        return matching_branches
    
    # Collect TODO branches
    todo_branches = collect_todo_branches(root)
    
    if not todo_branches:
        status_desc = "all" if status_filter is None else ("completed" if status_filter else "pending")
        raise ValueError(f"No {status_desc} TODO items found")
    
    # Build filtered tree
    filtered_root = TreeNode(name="", data="")
    filtered_root.type = "root"
    
    for branch in todo_branches:
        current = filtered_root
        
        # Skip root node in branch
        for node in branch[1:]:
            # Find or create child at this level
            child = None
            for existing_child in current.children:
                if existing_child.name == node.name:
                    child = existing_child
                    break
            
            if child is None:
                # Create new child
                child = TreeNode(name=node.name, data=node.data)
                child.type = node.type
                if hasattr(node, 'status'):
                    child.status = node.status
                current.add_child(child)
            
            current = child
    
    # Generate output filename
    base_name = os.path.splitext(input_file_path)[0]
    if status_filter is not None:
        status_suffix = "_completed" if status_filter else "_pending"
        output_suffix += status_suffix
    
    output_path = f"{base_name}{output_suffix}.log"
    
    # Write filtered content
    with open(output_path, 'w') as f:
        print_tree_to_file(filtered_root, f)
    
    return output_path
