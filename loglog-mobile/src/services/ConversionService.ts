import { TreeNode } from '../core/TreeNode';
import { buildTreeFromString } from '../core/parser';

export interface ExportOptions {
  headerLevels?: number;
  title?: string;
}

export class ConversionService {
  /**
   * Convert loglog content to HTML with interactive features
   */
  static toHtml(content: string, options: ExportOptions = {}): string {
    const { headerLevels = 4, title = 'Loglog Document' } = options;
    const root = buildTreeFromString(content);
    
    return this.generateInteractiveHtml(root, title);
  }

  /**
   * Convert loglog content to markdown
   */
  static toMarkdown(content: string, options: ExportOptions = {}): string {
    const { headerLevels = 4 } = options;
    const root = buildTreeFromString(content);
    
    return root.toMd(headerLevels);
  }

  /**
   * Generate interactive HTML with folding capabilities
   */
  private static generateInteractiveHtml(root: TreeNode, title: string): string {
    const contentHtml = this.generateHtmlContent(root);
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --border-color: #e0e0e0;
            --triangle-color: #666666;
            --todo-pending: #e74c3c;
            --todo-completed: #95a5a6;
            --focus-bg: rgba(33, 150, 243, 0.05);
            --focus-border: #2196f3;
        }

        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --border-color: #404040;
            --triangle-color: #888888;
            --todo-pending: #ff6b6b;
            --todo-completed: #6c7b7b;
            --focus-bg: rgba(100, 181, 246, 0.03);
            --focus-border: #64b5f6;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: all 0.3s ease;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
        }

        .title {
            font-size: 24px;
            font-weight: bold;
            color: var(--text-color);
        }

        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .theme-toggle, .help-toggle {
            background: none;
            border: 2px solid var(--border-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: var(--text-color);
            transition: all 0.2s ease;
        }

        .theme-toggle:hover, .help-toggle:hover {
            border-color: var(--focus-border);
            background-color: var(--focus-bg);
        }

        ul {
            list-style: none;
            padding-left: 0;
            margin: 0;
        }

        .tree-item {
            margin: 2px 0;
            position: relative;
        }

        .triangle {
            display: inline-block;
            width: 0;
            height: 0;
            margin-right: 5px;
            cursor: pointer;
            transition: transform 0.2s;
            user-select: none;
            border-left: 6px solid var(--triangle-color);
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
        }

        .triangle.expanded {
            transform: rotate(90deg);
        }

        .triangle.collapsed {
            transform: rotate(0deg);
        }

        .item-content {
            display: inline;
        }

        .children {
            margin-left: 20px;
        }

        .children.hidden {
            display: none;
        }

        .todo-completed {
            text-decoration: line-through;
            color: var(--todo-completed);
        }

        .todo-pending {
            color: var(--todo-pending);
            font-weight: bold;
        }

        .no-children {
            margin-left: 11px;
        }

        .help-box {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-color);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            font-size: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            max-width: 300px;
            transition: all 0.3s ease;
        }

        .help-box.minimized {
            width: 40px;
            height: 40px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 50%;
        }

        .help-content {
            line-height: 1.4;
        }

        .help-content h4 {
            margin: 0 0 8px 0;
            color: var(--focus-border);
        }

        .help-minimize {
            position: absolute;
            top: 5px;
            right: 8px;
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: var(--text-color);
        }

        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            
            .help-box {
                position: relative;
                top: auto;
                right: auto;
                margin: 20px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">${title}</h1>
            <div class="controls">
                <button class="theme-toggle" onclick="toggleTheme()">◐</button>
                <button class="help-toggle" onclick="toggleHelp()">?</button>
            </div>
        </div>
        
        <div class="content">
            ${contentHtml}
        </div>
        
        <div class="help-box" id="helpBox">
            <button class="help-minimize" onclick="toggleHelp()">×</button>
            <div class="help-content">
                <h4>Controls:</h4>
                <strong>Click triangles:</strong> Fold/unfold sections<br>
                <strong>Double-click items:</strong> Quick fold/unfold<br>
                <strong>Theme:</strong> Click ◐ to toggle dark/light mode
            </div>
        </div>
    </div>

    <script>
        // Theme management
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.body.setAttribute('data-theme', savedTheme);
        }

        // Help box management
        function toggleHelp() {
            const helpBox = document.getElementById('helpBox');
            helpBox.classList.toggle('minimized');
        }

        // Folding functionality
        function toggleFold(element) {
            const triangle = element;
            const listItem = triangle.parentElement;
            const children = listItem.querySelector('.children');
            
            if (children) {
                if (children.classList.contains('hidden')) {
                    children.classList.remove('hidden');
                    triangle.classList.remove('collapsed');
                    triangle.classList.add('expanded');
                } else {
                    children.classList.add('hidden');
                    triangle.classList.remove('expanded');
                    triangle.classList.add('collapsed');
                }
            }
        }

        // Add double-click folding
        document.addEventListener('dblclick', function(e) {
            const listItem = e.target.closest('.tree-item');
            if (listItem) {
                const triangle = listItem.querySelector('.triangle');
                if (triangle) {
                    toggleFold(triangle);
                }
            }
        });

        // Initialize all triangles as expanded
        document.querySelectorAll('.triangle').forEach(triangle => {
            triangle.classList.add('expanded');
            triangle.addEventListener('click', function() {
                toggleFold(this);
            });
        });
    </script>
</body>
</html>`;
  }

  /**
   * Generate HTML content from tree structure
   */
  private static generateHtmlContent(node: TreeNode, depth: number = 0): string {
    if (node.type === 'root') {
      let html = '<ul>';
      for (const child of node.children) {
        html += this.generateHtmlContent(child, depth);
      }
      html += '</ul>';
      return html;
    }

    const hasChildren = node.children.length > 0;
    const itemClass = hasChildren ? 'tree-item' : 'tree-item no-children';
    
    let html = `<li class="${itemClass}">`;
    
    // Add triangle for items with children
    if (hasChildren) {
      html += '<span class="triangle"></span>';
    }
    
    // Add content based on type
    if (node.type === 'todo') {
      const statusClass = node.status === true ? 'todo-completed' : 
                         node.status === false ? 'todo-pending' : 'todo-pending';
      const statusSymbol = node.status === true ? '☑' : 
                          node.status === false ? '☐' : '☒';
      html += `<span class="item-content ${statusClass}">${statusSymbol} ${this.escapeHtml(node.data)}</span>`;
    } else {
      html += `<span class="item-content">${this.escapeHtml(node.data)}</span>`;
    }
    
    // Add children
    if (hasChildren) {
      html += '<ul class="children">';
      for (const child of node.children) {
        html += this.generateHtmlContent(child, depth + 1);
      }
      html += '</ul>';
    }
    
    html += '</li>';
    return html;
  }

  /**
   * Escape HTML special characters
   */
  private static escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Generate a simple text export (plain loglog format)
   */
  static toText(content: string): string {
    return content; // Already in loglog format
  }
}