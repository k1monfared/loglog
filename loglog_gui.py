#!/usr/bin/env python3
"""
LogLog GUI - Modern Design
A modern, sleek desktop GUI inspired by Obsidian, Sublime Text, and Notion.
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import re
import subprocess
from loglog_tree_model import LogLogTree, LogLogNode, SelectionManager

class TreeNodeWidget(tk.Frame):
    """GUI widget representing a single tree node"""
    
    def __init__(self, parent, node, system_theme, tree_renderer):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.node = node
        self.system_theme = system_theme
        self.tree_renderer = tree_renderer
        self.is_editing = False
        
        # Create UI elements
        self.setup_ui()
        self.update_from_node()
        
        # Bind events
        self.bind_events()
    
    def setup_ui(self):
        """Create the visual elements for this node"""
        # Main container
        self.content_frame = tk.Frame(self, bg=self.system_theme.get_color('bg'))
        self.content_frame.pack(fill='x', anchor='w')
        
        # Indentation (based on node depth)
        self.indent_frame = tk.Frame(self.content_frame, bg=self.system_theme.get_color('bg'))
        self.indent_frame.pack(side='left')
        
        # Fold triangle (if has children)
        self.triangle_label = tk.Label(
            self.content_frame,
            text="",
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg'),
            cursor="hand2"
        )
        self.triangle_label.pack(side='left')
        
        # TODO checkbox (if TODO item)
        self.checkbox_label = tk.Label(
            self.content_frame,
            text="",
            font=self.system_theme.get_system_font('monospace'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg'),
            cursor="hand2"
        )
        self.checkbox_label.pack(side='left', padx=(5, 0))
        
        # Content text
        self.content_label = tk.Label(
            self.content_frame,
            text="",
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg'),
            anchor='w',
            cursor="hand2"
        )
        self.content_label.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Edit entry (hidden by default)
        self.edit_entry = tk.Entry(
            self.content_frame,
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg'),
            relief='flat',
            bd=1
        )
    
    def update_from_node(self):
        """Update the visual representation from the node data"""
        # Update indentation
        depth = self.get_node_depth()
        indent_width = depth * 20  # 20 pixels per level
        self.indent_frame.config(width=indent_width)
        
        # Update fold triangle
        if self.node.children:
            triangle = "▼" if not self.node.is_folded else "▶"
            self.triangle_label.config(text=triangle)
        else:
            self.triangle_label.config(text="")
        
        # Update TODO checkbox
        checkbox_text = ""
        if self.node.todo_status:
            status_map = {
                "pending": "[]",
                "progress": "[-]", 
                "complete": "[x]",
                "unknown": "[?]"
            }
            checkbox_text = status_map.get(self.node.todo_status.value, "[]")
        self.checkbox_label.config(text=checkbox_text)
        
        # Update content text
        self.content_label.config(text=self.node.content or "")
        
        # Update colors based on focus/selection
        self.update_selection_state()
    
    def get_node_depth(self):
        """Calculate the depth of this node in the tree"""
        depth = 0
        parent = self.node.parent
        while parent and parent.node_type.value != "root":
            depth += 1
            parent = parent.parent
        return depth
    
    def update_selection_state(self):
        """Update visual state based on focus/selection"""
        bg_color = self.system_theme.get_color('bg')
        fg_color = self.system_theme.get_color('fg')
        
        # Check if this node is focused or selected
        tree = self.tree_renderer.tree
        if tree.selection.focused_node == self.node:
            bg_color = self.system_theme.get_color('select_bg')
            fg_color = self.system_theme.get_color('select_fg')
        elif self.node in tree.selection.get_selected_nodes():
            # Slightly different color for selected but not focused
            bg_color = self.system_theme.get_color('select_bg')
            fg_color = self.system_theme.get_color('select_fg')
        
        # Apply colors to all elements
        self.config(bg=bg_color)
        self.content_frame.config(bg=bg_color)
        self.indent_frame.config(bg=bg_color)
        self.triangle_label.config(bg=bg_color, fg=fg_color)
        self.checkbox_label.config(bg=bg_color, fg=fg_color)
        self.content_label.config(bg=bg_color, fg=fg_color)
    
    def bind_events(self):
        """Bind mouse and keyboard events"""
        # Click to focus
        def on_click(event):
            if event.state & 0x4:  # Ctrl key held
                # Ctrl+Click: Toggle individual selection
                self.tree_renderer.tree.selection.toggle_selection(self.node)
                self.tree_renderer.update_selection_display()
            else:
                # Regular click: Set focus and clear other selections
                self.tree_renderer.set_focus(self.node)
            return "break"
        
        # Double-click to edit
        def on_double_click(event):
            self.start_editing()
            return "break"
        
        # Triangle click to toggle fold
        def on_triangle_click(event):
            if self.node.children:
                self.node.toggle_fold()
                self.tree_renderer.refresh_display()
            return "break"
        
        # Checkbox click to cycle TODO status
        def on_checkbox_click(event):
            if self.node.todo_status is not None:
                self.node.cycle_todo_status()
                self.update_from_node()
            return "break"
        
        # Bind events to all clickable elements
        for widget in [self, self.content_frame, self.content_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
        
        self.triangle_label.bind("<Button-1>", on_triangle_click)
        self.checkbox_label.bind("<Button-1>", on_checkbox_click)
    
    def start_editing(self):
        """Enter edit mode for this node"""
        if self.is_editing:
            return
            
        self.is_editing = True
        
        # Hide content label, show edit entry
        self.content_label.pack_forget()
        self.edit_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Set initial value
        self.edit_entry.delete(0, 'end')
        self.edit_entry.insert(0, self.node.content)
        self.edit_entry.focus_set()
        
        # Bind edit events
        def on_enter(event):
            self.finish_editing(save=True)
            return "break"
            
        def on_escape(event):
            self.finish_editing(save=False)
            return "break"
        
        self.edit_entry.bind("<Return>", on_enter)
        self.edit_entry.bind("<Escape>", on_escape)
        self.edit_entry.bind("<FocusOut>", lambda e: self.finish_editing(save=True))
    
    def finish_editing(self, save=True):
        """Exit edit mode"""
        if not self.is_editing:
            return
            
        if save:
            # Update node content
            new_content = self.edit_entry.get().strip()
            self.node.content = new_content
            
            # Re-parse TODO status if needed
            self.node._parse_todo_status()
        
        # Hide edit entry, show content label
        self.edit_entry.pack_forget()
        self.content_label.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        self.is_editing = False
        self.update_from_node()
        
        # Notify tree renderer of change
        self.tree_renderer.on_node_modified(self.node)

class TreeRenderer(tk.Frame):
    """Renders a LogLogTree as GUI widgets"""
    
    def __init__(self, parent, system_theme):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.system_theme = system_theme
        self.tree = LogLogTree()
        self.node_widgets = {}  # node_id -> TreeNodeWidget mapping
        
        # Create scrollable container
        self.setup_scrollable_container()
        
        # Bind keyboard events
        self.focus_set()
        self.bind_keyboard_events()
    
    def setup_scrollable_container(self):
        """Create scrollable container for tree nodes"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=self.system_theme.get_color('bg'),
            highlightthickness=0
        )
        
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bg=self.system_theme.get_color('bg')
        )
        
        # Create scrollable frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.system_theme.get_color('bg'))
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize to adjust scrollable frame width
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.bind_mouse_wheel()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update scrollable frame width to match canvas
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def bind_mouse_wheel(self):
        """Bind mouse wheel scrolling"""
        def on_mouse_wheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind to canvas and scrollable frame
        self.canvas.bind("<MouseWheel>", on_mouse_wheel)
        self.scrollable_frame.bind("<MouseWheel>", on_mouse_wheel)
    
    def bind_keyboard_events(self):
        """Bind keyboard navigation events"""
        def on_key(event):
            return self.handle_keyboard_event(event)
        
        # Make sure this widget can receive focus
        self.bind("<Button-1>", lambda e: self.focus_set())
        self.bind("<Key>", on_key)
    
    def load_from_file(self, file_path):
        """Load LogLog file into tree and render"""
        try:
            self.tree.load_from_file(file_path)
            self.refresh_display()
            return True
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return False
    
    def load_from_text(self, text):
        """Load LogLog text into tree and render"""
        try:
            self.tree.load_from_text(text)
            self.refresh_display()
            return True
        except Exception as e:
            print(f"Error loading text: {e}")
            return False
    
    def save_to_file(self, file_path):
        """Save tree to LogLog file"""
        try:
            content = self.tree.serialize()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return False
    
    def get_content_as_text(self):
        """Get tree content as LogLog text"""
        return self.tree.serialize()
    
    def refresh_display(self):
        """Rebuild the entire display from the tree"""
        # Clear existing widgets
        for widget in self.node_widgets.values():
            widget.destroy()
        self.node_widgets.clear()
        
        # Create widgets for visible nodes
        visible_nodes = self.tree.get_visible_nodes()
        for node in visible_nodes:
            self.create_node_widget(node)
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def create_node_widget(self, node):
        """Create a widget for a tree node"""
        widget = TreeNodeWidget(
            self.scrollable_frame,
            node,
            self.system_theme,
            self
        )
        widget.pack(fill='x', pady=1)
        self.node_widgets[node.id] = widget
        return widget
    
    def set_focus(self, node):
        """Set focus to a specific node"""
        # Update tree selection
        self.tree.selection.set_focus(node)
        
        # Update visual states
        self.update_selection_display()
        
        # Ensure node is visible by scrolling if necessary
        self.ensure_node_visible(node)
    
    def update_selection_display(self):
        """Update visual selection state for all widgets"""
        for widget in self.node_widgets.values():
            widget.update_selection_state()
    
    def ensure_node_visible(self, node):
        """Scroll to ensure node is visible"""
        if node.id not in self.node_widgets:
            return
            
        widget = self.node_widgets[node.id]
        
        # Get widget position relative to scrollable frame
        widget.update_idletasks()
        widget_top = widget.winfo_y()
        widget_height = widget.winfo_height()
        
        # Get canvas dimensions
        canvas_height = self.canvas.winfo_height()
        
        # Calculate scroll position
        scroll_top, scroll_bottom = self.canvas.yview()
        scrollable_height = self.scrollable_frame.winfo_reqheight()
        
        # Convert to pixel coordinates
        visible_top = scroll_top * scrollable_height
        visible_bottom = scroll_bottom * scrollable_height
        
        # Check if widget is visible
        if widget_top < visible_top or widget_top + widget_height > visible_bottom:
            # Scroll to make widget visible
            new_scroll_top = max(0, widget_top - canvas_height // 4)
            scroll_fraction = new_scroll_top / scrollable_height if scrollable_height > 0 else 0
            self.canvas.yview_moveto(scroll_fraction)
    
    def handle_keyboard_event(self, event):
        """Handle keyboard navigation"""
        focused_node = self.tree.selection.focused_node
        if not focused_node:
            # Set focus to first visible node
            visible_nodes = self.tree.get_visible_nodes()
            if visible_nodes:
                self.set_focus(visible_nodes[0])
            return "break"
        
        if event.keysym == "Up":
            if event.state & 0x1:  # Shift key
                self.extend_selection_up()
            else:
                self.move_focus_up()
        elif event.keysym == "Down":
            if event.state & 0x1:  # Shift key
                self.extend_selection_down()
            else:
                self.move_focus_down()
        elif event.keysym == "Left":
            if event.state & 0x1:  # Shift key
                self.extend_selection_to_parent()
            else:
                self.move_focus_left()
        elif event.keysym == "Right":
            if event.state & 0x1:  # Shift key
                self.extend_selection_to_children()
            else:
                self.move_focus_right()
        elif event.keysym == "Return":
            self.start_editing_focused()
        elif event.keysym == "space":
            self.toggle_todo_status()
        elif event.char == "?" and focused_node.todo_status:
            focused_node.set_todo_status("unknown")
            self.update_selection_display()
        elif event.char == "-" and focused_node.todo_status:
            focused_node.set_todo_status("progress")
            self.update_selection_display()
        elif event.keysym in ["1", "2", "3", "4", "5", "6", "7", "8", "9"] and (event.state & 0x4):  # Ctrl key
            level = int(event.keysym)
            if event.state & 0x20000:  # Alt key (focus mode)
                self.focus_mode(level)
            else:
                self.fold_to_level(level)
        elif event.keysym == "0" and (event.state & 0x4):  # Ctrl+0
            self.unfold_all()
        
        return "break"
    
    def move_focus_up(self):
        """Move focus to previous visible node"""
        visible_nodes = self.tree.get_visible_nodes()
        focused_node = self.tree.selection.focused_node
        
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index > 0:
                self.set_focus(visible_nodes[current_index - 1])
        except (ValueError, IndexError):
            pass
    
    def move_focus_down(self):
        """Move focus to next visible node"""
        visible_nodes = self.tree.get_visible_nodes()
        focused_node = self.tree.selection.focused_node
        
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index < len(visible_nodes) - 1:
                self.set_focus(visible_nodes[current_index + 1])
        except (ValueError, IndexError):
            pass
    
    def move_focus_left(self):
        """Move focus to parent or fold current node"""
        focused_node = self.tree.selection.focused_node
        
        if focused_node.children and not focused_node.is_folded:
            # Fold current node
            focused_node.toggle_fold()
            self.refresh_display()
        elif focused_node.parent and focused_node.parent.node_type.value != "root":
            # Move to parent
            self.set_focus(focused_node.parent)
    
    def move_focus_right(self):
        """Move to first child or unfold current node"""
        focused_node = self.tree.selection.focused_node
        
        if focused_node.children:
            if focused_node.is_folded:
                # Unfold current node
                focused_node.toggle_fold()
                self.refresh_display()
            else:
                # Move to first child
                self.set_focus(focused_node.children[0])
    
    def start_editing_focused(self):
        """Start editing the focused node"""
        focused_node = self.tree.selection.focused_node
        if focused_node and focused_node.id in self.node_widgets:
            self.node_widgets[focused_node.id].start_editing()
    
    def toggle_todo_status(self):
        """Toggle TODO status of all selected nodes"""
        selected_nodes = self.tree.selection.get_selected_nodes()
        focused_node = self.tree.selection.focused_node
        
        # If nothing selected, operate on focused node
        if not selected_nodes and focused_node:
            selected_nodes = [focused_node]
        
        # Apply operation to all selected nodes
        for node in selected_nodes:
            node.cycle_todo_status()
        
        self.update_selection_display()
    
    def extend_selection_up(self):
        """Extend selection upward from anchor"""
        visible_nodes = self.tree.get_visible_nodes()
        focused_node = self.tree.selection.focused_node
        
        if not focused_node or not visible_nodes:
            return
            
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index > 0:
                target_node = visible_nodes[current_index - 1]
                self._extend_selection_to_node(target_node)
        except (ValueError, IndexError):
            pass
    
    def extend_selection_down(self):
        """Extend selection downward from anchor"""
        visible_nodes = self.tree.get_visible_nodes()
        focused_node = self.tree.selection.focused_node
        
        if not focused_node or not visible_nodes:
            return
            
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index < len(visible_nodes) - 1:
                target_node = visible_nodes[current_index + 1]
                self._extend_selection_to_node(target_node)
        except (ValueError, IndexError):
            pass
    
    def extend_selection_to_parent(self):
        """Extend selection up the hierarchy"""
        focused_node = self.tree.selection.focused_node
        if focused_node and focused_node.parent and focused_node.parent.node_type.value != "root":
            self._extend_selection_to_node(focused_node.parent)
    
    def extend_selection_to_children(self):
        """Extend selection down the hierarchy"""
        focused_node = self.tree.selection.focused_node
        if focused_node and focused_node.children:
            # Select all visible children
            for child in focused_node.children:
                self._extend_selection_to_node(child, move_focus=False)
    
    def _extend_selection_to_node(self, target_node, move_focus=True):
        """Helper method to extend selection to a specific node"""
        selection = self.tree.selection
        
        # Add target node to selection
        selection.toggle_selection(target_node)
        
        # Move focus to target if requested
        if move_focus:
            selection.set_focus(target_node)
        
        # Update visual display
        self.update_selection_display()
        
        # Ensure target node is visible
        if move_focus:
            self.ensure_node_visible(target_node)
    
    def unfold_all(self):
        """Unfold all nodes in the tree"""
        all_nodes = self.tree.get_all_nodes()
        for node in all_nodes:
            if node.is_folded:
                node.is_folded = False
        self.refresh_display()
    
    def fold_to_level(self, max_level):
        """Fold all nodes deeper than max_level"""
        def fold_recursive(node, current_level=0):
            if current_level >= max_level:
                node.is_folded = True
            else:
                node.is_folded = False
                for child in node.children:
                    fold_recursive(child, current_level + 1)
        
        fold_recursive(self.tree.root)
        self.refresh_display()
    
    def focus_mode(self, max_level):
        """Focus mode: fold everything except current branch to max_level"""
        focused_node = self.tree.selection.focused_node
        if not focused_node:
            # No focus, fall back to regular fold
            self.fold_to_level(max_level)
            return
        
        # Get path to focused node
        path_nodes = []
        current = focused_node
        while current and current.node_type.value != "root":
            path_nodes.append(current)
            current = current.parent
        path_nodes.reverse()  # Root to focused
        
        def fold_with_focus(node, current_level=0, in_path=False):
            # Check if this node is in the path to focused node
            node_in_path = node in path_nodes
            
            if current_level >= max_level and not node_in_path:
                node.is_folded = True
            else:
                node.is_folded = False
                for child in node.children:
                    fold_with_focus(child, current_level + 1, node_in_path)
        
        fold_with_focus(self.tree.root)
        self.refresh_display()
    
    def on_node_modified(self, node):
        """Called when a node is modified"""
        # Notify parent GUI that content has changed
        if hasattr(self, 'gui') and self.gui:
            self.gui.on_text_modified()

class SystemTheme:
    """System theme integration using tkinter's built-in theme support"""
    
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        
        # Try to use system theme
        try:
            # Get available themes
            available_themes = self.style.theme_names()
            
            # Prefer system themes in order of preference
            preferred_themes = ['vista', 'xpnative', 'winnative', 'aqua', 'clam', 'alt', 'default']
            selected_theme = None
            
            for theme in preferred_themes:
                if theme in available_themes:
                    selected_theme = theme
                    break
                    
            if selected_theme:
                self.style.theme_use(selected_theme)
                
        except tk.TclError:
            # Fallback to default
            pass
        
        # Get system colors
        self._setup_system_colors()
    
    def _setup_system_colors(self):
        """Extract system colors from tkinter"""
        try:
            # Create temporary widget to extract system colors
            temp_frame = tk.Frame(self.root)
            temp_text = tk.Text(temp_frame)
            temp_button = tk.Button(temp_frame)
            
            # Extract system colors
            self.colors = {
                'bg': temp_frame.cget('bg'),
                'fg': temp_text.cget('fg'),
                'select_bg': temp_text.cget('selectbackground'),
                'select_fg': temp_text.cget('selectforeground'),
                'button_bg': temp_button.cget('bg'),
                'button_fg': temp_button.cget('fg'),
                'insert_bg': temp_text.cget('insertbackground'),
                'disabled_fg': temp_text.cget('disabledforeground'),
            }
            
            # Clean up temporary widgets
            temp_frame.destroy()
            
            # Set semantic colors based on system colors
            self.semantic_colors = {
                'error': '#d73a49',  # Keep these for consistency
                'warning': '#f66a0a',
                'success': '#28a745',
                'todo_pending': self.colors['fg'],
                'todo_completed': self.colors['disabled_fg'],
                'todo_progress': '#f66a0a',
                'hashtag': self.colors['select_bg'],
                'bullet': self.colors['fg'],
            }
            
        except (tk.TclError, KeyError):
            # Fallback colors if system colors can't be extracted
            self.colors = {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'button_bg': '#f0f0f0',
                'button_fg': '#000000',
                'insert_bg': '#000000',
                'disabled_fg': '#808080',
            }
            self.semantic_colors = {
                'error': '#d73a49',
                'warning': '#f66a0a', 
                'success': '#28a745',
                'todo_pending': '#d73a49',
                'todo_completed': '#808080',
                'todo_progress': '#f66a0a',
                'hashtag': '#0078d4',
                'bullet': '#000000',
            }
    
    def get_color(self, color_name):
        """Get system color by name"""
        if color_name in self.colors:
            return self.colors[color_name]
        elif color_name in self.semantic_colors:
            return self.semantic_colors[color_name]
        else:
            return self.colors['fg']  # Default fallback
    
    def get_system_font(self, font_type='default'):
        """Get system font"""
        try:
            if font_type == 'monospace':
                # Try to get a monospace system font
                import tkinter.font as tkFont
                default_font = tkFont.nametofont('TkFixedFont')
                return (default_font.cget('family'), default_font.cget('size'))
            else:
                # Default system font
                import tkinter.font as tkFont
                default_font = tkFont.nametofont('TkDefaultFont')
                return (default_font.cget('family'), default_font.cget('size'))
        except:
            # Fallback fonts
            if font_type == 'monospace':
                return ('Courier', 10)
            else:
                return ('Arial', 9)

class ModernSettings:
    """Enhanced settings with modern themes"""
    
    def __init__(self):
        self.settings_dir = Path.home() / '.loglog'
        self.settings_file = self.settings_dir / 'gui_settings.json'
        self.settings = self._load_default_settings()
        self.load()
    
    def _load_default_settings(self):
        return {
            'font_family': '',  # Empty means use system default
            'font_size': 0,     # 0 means use system default
            'line_height': 1.2,
            'tab_size': 4,
            'word_wrap': True,
            'auto_save': True,
            'auto_save_interval': 30000,
            'recent_files': [],
            'max_recent_files': 10,
            'window_geometry': '1200x800',
            'sidebar_width': 280,
            'show_minimap': False,
            'vim_mode': False,
            'bracket_matching': True
        }
    
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    def load(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save(self):
        try:
            self.settings_dir.mkdir(exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

class ModernScrolledText(tk.Frame):
    """Modern styled scrolled text widget"""
    
    def __init__(self, parent, system_theme, **kwargs):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.system_theme = system_theme
        
        # Create text widget
        self.text = tk.Text(
            self, 
            bg=system_theme.get_color('bg'),
            fg=system_theme.get_color('fg'),
            insertbackground=system_theme.get_color('insert_bg'),
            selectbackground=system_theme.get_color('select_bg'),
            selectforeground=system_theme.get_color('select_fg'),
            font=kwargs.get('font', system_theme.get_system_font('monospace')),
            relief='flat',
            bd=0,
            padx=20,
            pady=15,
            **{k: v for k, v in kwargs.items() if k != 'font'}
        )
        
        # Create scrollbar
        self.scrollbar = tk.Scrollbar(
            self, 
            command=self.text.yview,
            bg=system_theme.get_color('bg'),
            troughcolor=system_theme.get_color('bg'),
            activebackground=system_theme.get_color('select_bg')
        )
        self.text.config(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.text.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Delegate text methods
        for method in ['get', 'insert', 'delete', 'index', 'mark_set', 'see', 'tag_add', 
                      'tag_remove', 'tag_config', 'bind', 'event_generate', 'edit_undo', 
                      'edit_redo', 'config', 'configure']:
            setattr(self, method, getattr(self.text, method))

class ModernFileTree(tk.Frame):
    """Modern file tree with sleek styling"""
    
    def __init__(self, parent, system_theme, on_file_select=None):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.system_theme = system_theme
        self.on_file_select = on_file_select
        self.current_dir = Path.home()
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=self.system_theme.get_color('bg'), height=50)
        header.pack(fill='x', padx=15, pady=(15, 10))
        header.pack_propagate(False)
        
        # Modern title
        title_label = tk.Label(
            header, 
            text="FILES",
            font=('Segoe UI', 11, 'bold'),
            fg=self.system_theme.get_color('disabled_fg'),
            bg=self.system_theme.get_color('bg')
        )
        title_label.pack(side='left', anchor='w')
        
        # Directory path
        self.path_frame = tk.Frame(self, bg=self.system_theme.get_color('bg'))
        self.path_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Breadcrumb-style path
        self.path_label = tk.Label(
            self.path_frame,
            text=str(self.current_dir),
            font=('Segoe UI', 9),
            fg=self.system_theme.get_color('select_bg'),
            bg=self.system_theme.get_color('bg'),
            cursor='hand2'
        )
        self.path_label.pack(side='left', anchor='w')
        self.path_label.bind('<Button-1>', lambda e: self.change_directory())
        
        # Modern file list
        list_frame = tk.Frame(self, bg=self.system_theme.get_color('bg'))
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.file_listbox = tk.Listbox(
            list_frame,
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            selectbackground=self.system_theme.get_color('select_bg'),
            selectforeground='white',
            font=('Segoe UI', 10),
            relief='flat',
            bd=0,
            highlightthickness=0,
            activestyle='none'
        )
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.file_listbox.yview,
            bg=self.system_theme.get_color('bg'),
            troughcolor=self.system_theme.get_color('bg'),
            activebackground=self.system_theme.get_color('select_bg'),
            width=8
        )
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.file_listbox.bind('<Double-Button-1>', self.on_double_click)
        self.file_listbox.bind('<Return>', self.on_double_click)
        
        self.refresh_files()
    
    def change_directory(self):
        new_dir = filedialog.askdirectory(initialdir=self.current_dir, title="Select Directory")
        if new_dir:
            self.current_dir = Path(new_dir)
            self.path_label.config(text=str(self.current_dir))
            self.refresh_files()
    
    def refresh_files(self):
        self.file_listbox.delete(0, tk.END)
        
        try:
            # Parent directory
            if self.current_dir.parent != self.current_dir:
                self.file_listbox.insert(tk.END, "↑ ..")
            
            # Directories with modern icons
            directories = [d for d in self.current_dir.iterdir() 
                          if d.is_dir() and not d.name.startswith('.')]
            for directory in sorted(directories):
                self.file_listbox.insert(tk.END, f"📁 {directory.name}")
            
            # LogLog files with document icon
            log_files = [f for f in self.current_dir.iterdir() 
                        if f.is_file() and f.suffix in ['.log', '.loglog']]
            for log_file in sorted(log_files):
                self.file_listbox.insert(tk.END, f"📝 {log_file.name}")
                
        except PermissionError:
            self.file_listbox.insert(tk.END, "❌ Access denied")
    
    def on_double_click(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])
        
        if item.startswith("↑ .."):
            self.current_dir = self.current_dir.parent
            self.path_label.config(text=str(self.current_dir))
            self.refresh_files()
        elif item.startswith("📁 "):
            dirname = item[2:]
            new_dir = self.current_dir / dirname
            if new_dir.is_dir():
                self.current_dir = new_dir
                self.path_label.config(text=str(self.current_dir))
                self.refresh_files()
        elif item.startswith("📝 "):
            filename = item[2:]
            file_path = self.current_dir / filename
            if self.on_file_select and file_path.exists():
                self.on_file_select(str(file_path))

class ModernSyntaxHighlighter:
    """Enhanced syntax highlighter with modern styling"""
    
    def __init__(self, text_widget, system_theme):
        self.text_widget = text_widget
        self.system_theme = system_theme
        self.setup_tags()
    
    def setup_tags(self):
        # Configure modern text styling
        self.text_widget.tag_config('todo_pending', 
            foreground=self.system_theme.get_color('todo_pending'), 
            font=('JetBrains Mono', 12, 'bold'))
        
        self.text_widget.tag_config('todo_completed', 
            foreground=self.system_theme.get_color('todo_completed'), 
            overstrike=True,
            font=('JetBrains Mono', 12))
        
        self.text_widget.tag_config('todo_in_progress', 
            foreground=self.system_theme.get_color('todo_progress'), 
            font=('JetBrains Mono', 12, 'bold'))
        
        self.text_widget.tag_config('hashtag', 
            foreground=self.system_theme.get_color('hashtag'), 
            font=('JetBrains Mono', 12, 'bold'))
        
        self.text_widget.tag_config('bullet', 
            foreground=self.system_theme.get_color('bullet'),
            font=('JetBrains Mono', 12, 'bold'))
        
        # Modern indentation with subtle guides
        for i in range(1, 8):
            indent_px = 25 * i
            self.text_widget.tag_config(f'indent_{i}', 
                lmargin1=indent_px, 
                lmargin2=indent_px)
    
    def highlight_all(self):
        # Remove existing tags
        for tag in ['todo_pending', 'todo_completed', 'todo_in_progress', 'hashtag', 'bullet']:
            self.text_widget.tag_remove(tag, 1.0, 'end')
        
        content = self.text_widget.get(1.0, 'end')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            self.highlight_line_content(i, line)
    
    def highlight_line_content(self, line_num: int, line_content: str):
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        
        # Enhanced TODO highlighting
        if '[]' in line_content:
            self.text_widget.tag_add('todo_pending', line_start, line_end)
        elif '[x]' in line_content:
            self.text_widget.tag_add('todo_completed', line_start, line_end)
        elif '[-]' in line_content:
            self.text_widget.tag_add('todo_in_progress', line_start, line_end)
        
        # Enhanced hashtag highlighting
        hashtag_pattern = r'#\w+'
        for match in re.finditer(hashtag_pattern, line_content):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            self.text_widget.tag_add('hashtag', start_pos, end_pos)
        
        # Bullet highlighting
        if line_content.strip().startswith('- '):
            bullet_end = f"{line_num}.{line_content.find('- ') + 2}"
            self.text_widget.tag_add('bullet', line_start, bullet_end)
        
        # Smart indentation
        indent_level = 0
        for char in line_content:
            if char == ' ':
                indent_level += 1
            elif char == '\t':
                indent_level += 4
            else:
                break
        
        if indent_level >= 4:
            tag_level = min((indent_level // 4), 7)
            if tag_level > 0:
                self.text_widget.tag_add(f'indent_{tag_level}', line_start, line_end)

class ModernStatusBar(tk.Frame):
    """Sleek status bar inspired by modern editors"""
    
    def __init__(self, parent, system_theme):
        super().__init__(parent, bg=system_theme.get_color('select_bg'), height=28)
        self.system_theme = system_theme
        self.pack_propagate(False)
        
        # Left side - status
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=('Segoe UI', 9),
            fg='white',
            bg=system_theme.get_color('select_bg'),
            padx=15
        )
        self.status_label.pack(side='left', fill='y')
        
        # Right side - cursor info
        self.cursor_label = tk.Label(
            self,
            text="Ln 1, Col 1",
            font=('Segoe UI', 9),
            fg='white',
            bg=system_theme.get_color('select_bg'),
            padx=15
        )
        self.cursor_label.pack(side='right', fill='y')

class ModernLogLogGUI:
    """Main GUI class with system theme integration"""
    
    def __init__(self):
        self.settings = ModernSettings()
        self.current_file = None
        self.file_modified = False
        self.auto_save_timer = None
        
        self.setup_main_window()
        # Initialize system theme after window is created
        self.system_theme = SystemTheme(self.root)
        self.apply_system_theme()
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        self.setup_theme()
        
        self.update_recent_files_menu()
        
        if self.settings.get('auto_save'):
            self.schedule_auto_save()
    
    def setup_main_window(self):
        self.root = tk.Tk()
        self.root.title("LogLog")
        self.root.geometry(self.settings.get('window_geometry'))
        # Background color will be set after system theme is initialized
        
        # Modern window styling
        if sys.platform.startswith('win'):
            try:
                # Windows 10/11 dark title bar
                self.root.tk.call('tk', 'windowingsystem')
                self.root.tk.call('set', 'theme', 'dark')
            except:
                pass
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_menu(self):
        # Modern menu styling
        self.menubar = tk.Menu(self.root, 
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            activebackground=self.system_theme.get_color('select_bg'),
            activeforeground='white',
            font=('Segoe UI', 9))
        self.root.config(menu=self.menubar)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0,
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            activebackground=self.system_theme.get_color('select_bg'))
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        
        # Recent files
        self.recent_menu = tk.Menu(self.file_menu, tearoff=0,
            bg=self.system_theme.get_color('bg'), fg=self.system_theme.get_color('fg'))
        self.file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Preferences...", command=self.show_preferences)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit menu  
        self.edit_menu = tk.Menu(self.menubar, tearoff=0,
            bg=self.system_theme.get_color('bg'), fg=self.system_theme.get_color('fg'))
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find...", command=self.show_find, accelerator="Ctrl+F")
        
        # View menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0,
            bg=self.system_theme.get_color('bg'), fg=self.system_theme.get_color('fg'))
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Command Palette", command=self.show_command_palette, accelerator="Ctrl+Shift+P")
        self.view_menu.add_separator()
        # Theme is now system-integrated
        self.view_menu.add_separator()
        self.view_menu.add_command(label="TODOs", command=self.show_todos)
        self.view_menu.add_command(label="Document Stats", command=self.show_stats)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        
        # Export menu
        self.export_menu = tk.Menu(self.menubar, tearoff=0,
            bg=self.system_theme.get_color('bg'), fg=self.system_theme.get_color('fg'))
        self.menubar.add_cascade(label="Export", menu=self.export_menu)
        self.export_menu.add_command(label="Export to HTML...", command=self.convert_to_html)
        self.export_menu.add_command(label="Export to Markdown...", command=self.convert_to_markdown)
        self.export_menu.add_command(label="Export to LaTeX...", command=self.convert_to_latex)
    
    def setup_ui(self):
        # Main container with modern layout
        self.main_paned = tk.PanedWindow(
            self.root, 
            orient='horizontal',
            bg=self.system_theme.get_color('bg'),
            sashwidth=1,
            sashrelief='flat',
            sashpad=0,
            bd=0
        )
        self.main_paned.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        
        # Left sidebar
        self.sidebar_width = self.settings.get('sidebar_width', 280)
        self.file_tree = ModernFileTree(
            self.main_paned, 
            self.system_theme, 
            on_file_select=self.load_file
        )
        self.main_paned.add(self.file_tree, width=self.sidebar_width, minsize=200)
        
        # Right editor panel
        editor_container = tk.Frame(self.main_paned, bg=self.system_theme.get_color('bg'))
        self.main_paned.add(editor_container, minsize=400)
        
        # Editor header with modern styling
        editor_header = tk.Frame(editor_container, bg=self.system_theme.get_color('bg'), height=50)
        editor_header.pack(fill='x', padx=20, pady=(15, 0))
        editor_header.pack_propagate(False)
        
        # File name with modern typography
        self.file_label = tk.Label(
            editor_header,
            text="Untitled",
            font=('Segoe UI', 14, 'bold'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg')
        )
        self.file_label.pack(side='left', anchor='w')
        
        # Modified indicator
        self.modified_label = tk.Label(
            editor_header,
            text="",
            font=('Segoe UI', 14),
            fg=self.system_theme.get_color('warning'),
            bg=self.system_theme.get_color('bg')
        )
        self.modified_label.pack(side='left', padx=(10, 0), anchor='w')
        
        # Modern editor
        editor_frame = tk.Frame(editor_container, bg=self.system_theme.get_color('bg'))
        editor_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # Replace text editor with tree renderer
        self.tree_renderer = TreeRenderer(
            editor_frame,
            self.system_theme
        )
        self.tree_renderer.pack(fill='both', expand=True)
        
        # Connect tree renderer to GUI for change notifications
        self.tree_renderer.gui = self
        
        # Keep text_editor reference for compatibility, but make it point to tree renderer
        self.text_editor = self.tree_renderer
        
        # Modern status bar
        self.status_bar = ModernStatusBar(self.root, self.system_theme)
        self.status_bar.grid(row=2, column=0, sticky='ew')
    
    def setup_bindings(self):
        # Enhanced keyboard shortcuts
        bindings = [
            ('<Control-n>', self.new_file),
            ('<Control-o>', self.open_file), 
            ('<Control-s>', self.save_file),
            ('<Control-Shift-S>', self.save_as_file),
            ('<Control-q>', self.on_closing),
            ('<Control-z>', self.undo),
            ('<Control-y>', self.redo),
            ('<Control-x>', self.cut),
            ('<Control-c>', self.copy),
            ('<Control-v>', self.paste),
            ('<Control-f>', self.show_find),
            ('<Control-Shift-F>', self.show_scoped_find),
            ('<Control-Shift-P>', self.show_command_palette),
            # Theme toggling removed - using system theme
            ('<Control-plus>', self.zoom_in),
            ('<Control-minus>', self.zoom_out),
            ('<F11>', self.toggle_fullscreen)
        ]
        
        for binding, command in bindings:
            self.root.bind(binding, lambda e, cmd=command: cmd())
        
        # Tree renderer handles its own events
    
    def apply_system_theme(self):
        """Apply system theme styling to all elements"""
        # Set main window background
        self.root.configure(bg=self.system_theme.get_color('bg'))
        
        # Configure ttk styles to use system theme
        self.system_theme.style.configure('System.TFrame', 
                                         background=self.system_theme.get_color('bg'))
        self.system_theme.style.configure('System.TLabel', 
                                         background=self.system_theme.get_color('bg'),
                                         foreground=self.system_theme.get_color('fg'))
        self.system_theme.style.configure('System.TButton',
                                         background=self.system_theme.get_color('button_bg'),
                                         foreground=self.system_theme.get_color('button_fg'))
        
    def setup_theme(self):
        """Apply theme styling to all elements (kept for compatibility)"""
        # This method now delegates to system theme
        self.apply_system_theme()
    
    def show_command_palette(self):
        """Modern command palette (Sublime/VS Code style)"""
        palette = tk.Toplevel(self.root)
        palette.title("Command Palette")
        palette.geometry("500x300")
        palette.configure(bg=self.system_theme.get_color('bg'))
        palette.transient(self.root)
        palette.grab_set()
        
        # Center the palette
        palette.geometry(f"+{self.root.winfo_rootx() + 350}+{self.root.winfo_rooty() + 150}")
        
        # Search entry
        search_frame = tk.Frame(palette, bg=self.system_theme.get_color('bg'))
        search_frame.pack(fill='x', padx=20, pady=20)
        
        search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 12),
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            relief='flat',
            bd=5
        )
        search_entry.pack(fill='x')
        search_entry.focus()
        
        # Command list
        commands = [
            ("New File", self.new_file),
            ("Open File", self.open_file),
            ("Save File", self.save_file),
            # Theme is now system-integrated
            ("Show TODOs", self.show_todos),
            ("Document Stats", self.show_stats),
            ("Export to HTML", self.convert_to_html),
            ("Export to Markdown", self.convert_to_markdown),
        ]
        
        command_list = tk.Listbox(
            palette,
            font=('Segoe UI', 10),
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            selectbackground=self.system_theme.get_color('select_bg'),
            relief='flat',
            bd=0
        )
        command_list.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        for name, _ in commands:
            command_list.insert(tk.END, name)
        
        def execute_command(event=None):
            selection = command_list.curselection()
            if selection:
                _, command = commands[selection[0]]
                palette.destroy()
                command()
        
        command_list.bind('<Double-Button-1>', execute_command)
        command_list.bind('<Return>', execute_command)
        search_entry.bind('<Return>', execute_command)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    # File operations (same as before but with modern status updates)
    def new_file(self):
        if self.check_unsaved_changes():
            self.current_file = None
            self.file_modified = False
            # Create a new empty tree
            self.tree_renderer.load_from_text("")
            self.update_title()
            self.update_status("📄 New file created")
    
    def load_file(self, file_path: str):
        try:
            # Load file using tree renderer
            if self.tree_renderer.load_from_file(file_path):
                self.current_file = file_path
                self.file_modified = False
                self.update_title()
                self.add_to_recent_files(file_path)
                self.update_status(f"📂 Opened {os.path.basename(file_path)}")
            else:
                raise Exception("Failed to load file into tree")
            
        except Exception as e:
            self.show_modern_error("Failed to open file", str(e))
    
    def save_file(self):
        if self.current_file:
            try:
                # Save using tree renderer
                if self.tree_renderer.save_to_file(self.current_file):
                    self.file_modified = False
                    self.update_title()
                    self.update_status(f"💾 Saved {os.path.basename(self.current_file)}")
                else:
                    raise Exception("Failed to save file from tree")
                
            except Exception as e:
                self.show_modern_error("Save failed", str(e))
        else:
            self.save_as_file()
    
    def update_title(self):
        title = "LogLog"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - LogLog"
            self.file_label.config(text=filename)
        else:
            self.file_label.config(text="Untitled")
        
        if self.file_modified:
            title = "● " + title
            self.modified_label.config(text="●")
        else:
            self.modified_label.config(text="")
        
        self.root.title(title)
    
    def update_status(self, message: str):
        self.status_bar.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_bar.status_label.config(text="Ready"))
    
    def update_cursor_position(self, event=None):
        # For tree renderer, show focused node info
        focused_node = self.tree_renderer.tree.selection.focused_node
        if focused_node:
            node_count = len(self.tree_renderer.tree.get_visible_nodes())
            visible_nodes = self.tree_renderer.tree.get_visible_nodes()
            try:
                node_index = visible_nodes.index(focused_node) + 1
                self.status_bar.cursor_label.config(text=f"Node {node_index} of {node_count}")
            except ValueError:
                self.status_bar.cursor_label.config(text=f"{node_count} nodes")
        else:
            self.status_bar.cursor_label.config(text="No selection")
    
    def show_modern_error(self, title, message):
        """Modern error dialog"""
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title(title)
        error_dialog.configure(bg=self.system_theme.get_color('bg'))
        error_dialog.geometry("400x150")
        error_dialog.transient(self.root)
        error_dialog.grab_set()
        
        # Error message
        msg_label = tk.Label(
            error_dialog,
            text=message,
            font=('Segoe UI', 10),
            fg=self.system_theme.get_color('error'),
            bg=self.system_theme.get_color('bg'),
            wraplength=350
        )
        msg_label.pack(pady=20, padx=20)
        
        # OK button
        ok_button = tk.Button(
            error_dialog,
            text="OK",
            font=('Segoe UI', 9),
            bg=self.system_theme.get_color('select_bg'),
            fg='white',
            relief='flat',
            padx=20,
            command=error_dialog.destroy
        )
        ok_button.pack(pady=10)
    
    # Implement other methods similar to original but with modern styling...
    def on_text_modified(self, event=None):
        if not self.file_modified:
            self.file_modified = True
            self.update_title()
        
        # Update cursor position display
        self.update_cursor_position()
        
        if self.settings.get('auto_save'):
            self.schedule_auto_save()
    
    # Additional methods would go here (save_as_file, open_file, show_find, etc.)
    # For brevity, I'll implement key ones...
    
    def open_file(self):
        if not self.check_unsaved_changes():
            return
            
        file_path = filedialog.askopenfilename(
            title="Open LogLog File",
            filetypes=[
                ("LogLog files", "*.log *.loglog"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save LogLog File",
            defaultextension=".log",
            filetypes=[
                ("LogLog files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                content = self.text_editor.get(1.0, 'end-1c')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.current_file = file_path
                self.file_modified = False
                self.update_title()
                self.add_to_recent_files(file_path)
                self.update_status(f"💾 Saved as {os.path.basename(file_path)}")
                
            except Exception as e:
                self.show_modern_error("Save failed", str(e))
    
    def show_find(self):
        """Show simple search dialog (Ctrl+F)"""
        self.show_search_dialog(scoped=False)
    
    def show_scoped_find(self):
        """Show scoped search dialog (Ctrl+Shift+F)"""
        self.show_search_dialog(scoped=True)
    
    def show_search_dialog(self, scoped=False):
        """Show search dialog"""
        # Create search dialog
        search_dialog = tk.Toplevel(self.root)
        search_dialog.title("Search" if not scoped else "Scoped Search")
        search_dialog.geometry("400x150")
        search_dialog.configure(bg=self.system_theme.get_color('bg'))
        search_dialog.transient(self.root)
        search_dialog.grab_set()
        
        # Center the dialog
        search_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Search input
        input_frame = tk.Frame(search_dialog, bg=self.system_theme.get_color('bg'))
        input_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            input_frame,
            text="Search for:" + (" (within selection)" if scoped else ""),
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg')
        ).pack(anchor='w')
        
        search_entry = tk.Entry(
            input_frame,
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('fg'),
            bg=self.system_theme.get_color('bg')
        )
        search_entry.pack(fill='x', pady=(5, 0))
        search_entry.focus_set()
        
        # Buttons
        button_frame = tk.Frame(search_dialog, bg=self.system_theme.get_color('bg'))
        button_frame.pack(fill='x', padx=20, pady=10)
        
        def do_search():
            term = search_entry.get().strip()
            if term:
                self.tree_search(term, scoped=scoped)
                search_dialog.destroy()
        
        def close_dialog():
            search_dialog.destroy()
        
        search_button = tk.Button(
            button_frame,
            text="Search",
            command=do_search,
            bg=self.system_theme.get_color('button_bg'),
            fg=self.system_theme.get_color('button_fg')
        )
        search_button.pack(side='right', padx=(10, 0))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=close_dialog,
            bg=self.system_theme.get_color('button_bg'),
            fg=self.system_theme.get_color('button_fg')
        )
        cancel_button.pack(side='right')
        
        # Bind Enter key to search
        search_entry.bind('<Return>', lambda e: do_search())
        search_dialog.bind('<Escape>', lambda e: close_dialog())
    
    def tree_search(self, term: str, scoped=False):
        """Search within the tree structure"""
        if scoped:
            # Search within selected nodes or focused node
            selected_nodes = self.tree_renderer.tree.selection.get_selected_nodes()
            focused_node = self.tree_renderer.tree.selection.focused_node
            
            if not selected_nodes and focused_node:
                selected_nodes = [focused_node]
            
            if not selected_nodes:
                self.update_status("No nodes selected for scoped search")
                return
            
            # Search within selected nodes and their children
            search_results = []
            for node in selected_nodes:
                results = node.search(term, case_sensitive=False)
                search_results.extend(results)
        else:
            # Simple search across entire tree
            search_results = self.tree_renderer.tree.search(term, case_sensitive=False)
        
        if search_results:
            # Focus first result
            self.tree_renderer.set_focus(search_results[0])
            
            # Unfold ancestors of all results to make them visible
            for result in search_results:
                self._unfold_ancestors(result)
            
            self.tree_renderer.refresh_display()
            
            # Update status
            if len(search_results) == 1:
                self.update_status(f"Found 1 match for '{term}'")
            else:
                self.update_status(f"Found {len(search_results)} matches for '{term}'")
        else:
            self.update_status(f"'{term}' not found")
    
    def _unfold_ancestors(self, node):
        """Unfold all ancestors of a node to make it visible"""
        parent = node.parent
        while parent and parent.node_type.value != "root":
            parent.is_folded = False
            parent = parent.parent
    
    def zoom_in(self):
        current_size = self.settings.get('font_size')
        new_size = min(current_size + 1, 24)
        self.settings.set('font_size', new_size)
        self.update_font()
    
    def zoom_out(self):
        current_size = self.settings.get('font_size')
        new_size = max(current_size - 1, 8)
        self.settings.set('font_size', new_size)
        self.update_font()
    
    def update_font(self):
        new_font = self.system_theme.get_system_font('monospace')
        self.text_editor.config(font=new_font)
        self.syntax_highlighter.setup_tags()
    
    def show_todos(self):
        if not self.current_file:
            self.update_status("⚠️ Please open a file first")
            return
        
        try:
            result = subprocess.run([
                sys.executable, 'loglog_cli.py', 'todos', self.current_file
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                self.show_modern_dialog("📋 TODO Items", result.stdout)
            else:
                self.show_modern_error("TODO extraction failed", result.stderr)
        except Exception as e:
            self.show_modern_error("Failed to extract TODOs", str(e))
    
    def show_stats(self):
        if not self.current_file:
            self.update_status("⚠️ Please open a file first")
            return
        
        try:
            result = subprocess.run([
                sys.executable, 'loglog_cli.py', 'stats', self.current_file
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                self.show_modern_dialog("📊 Document Statistics", result.stdout)
            else:
                self.show_modern_error("Stats generation failed", result.stderr)
        except Exception as e:
            self.show_modern_error("Failed to generate stats", str(e))
    
    def show_modern_dialog(self, title: str, content: str):
        """Modern styled dialog window"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("700x500")
        dialog.configure(bg=self.system_theme.get_color('bg'))
        dialog.transient(self.root)
        
        # Content area
        text_frame = tk.Frame(dialog, bg=self.system_theme.get_color('bg'))
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = ModernScrolledText(
            text_frame, 
            self.system_theme,
            font=('JetBrains Mono', 10), 
            wrap='word'
        )
        text_widget.pack(fill='both', expand=True)
        text_widget.insert(1.0, content)
        text_widget.config(state='disabled')
        
        # Close button
        button_frame = tk.Frame(dialog, bg=self.system_theme.get_color('bg'))
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=('Segoe UI', 9),
            bg=self.system_theme.get_color('select_bg'),
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=dialog.destroy
        )
        close_btn.pack(side='right')
    
    def convert_to_html(self):
        self.convert_file('html')
    
    def convert_to_markdown(self):
        self.convert_file('markdown')
    
    def convert_to_latex(self):
        self.convert_file('latex')
    
    def convert_file(self, format_type: str):
        if not self.current_file:
            self.update_status("⚠️ Please open a file first")
            return
        
        try:
            result = subprocess.run([
                sys.executable, 'loglog_cli.py', 'convert', self.current_file, 
                '--to', format_type, '--overwrite'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                self.update_status(f"✅ Exported to {format_type.upper()}")
            else:
                self.show_modern_error("Export failed", result.stderr)
        except Exception as e:
            self.show_modern_error("Export failed", str(e))
    
    def show_preferences(self):
        self.update_status("⚙️ Use View menu for theme and zoom options")
    
    # Implement remaining methods (undo, redo, cut, copy, paste, etc.)...
    def undo(self):
        try:
            self.text_editor.edit_undo()
        except:
            pass
    
    def redo(self):
        try:
            self.text_editor.edit_redo()
        except:
            pass
    
    def cut(self):
        try:
            self.text_editor.event_generate('<<Cut>>')
        except:
            pass
    
    def copy(self):
        try:
            self.text_editor.event_generate('<<Copy>>')
        except:
            pass
    
    def paste(self):
        try:
            self.text_editor.event_generate('<<Paste>>')
        except:
            pass
    
    def check_unsaved_changes(self) -> bool:
        if self.file_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save them?"
            )
            if result is True:
                self.save_file()
                return True
            elif result is False:
                return True
            else:
                return False
        return True
    
    def on_closing(self):
        if self.check_unsaved_changes():
            self.settings.set('window_geometry', self.root.geometry())
            self.root.destroy()
    
    def add_to_recent_files(self, file_path: str):
        recent_files = self.settings.get('recent_files', [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        
        max_recent = self.settings.get('max_recent_files', 10)
        recent_files = recent_files[:max_recent]
        
        self.settings.set('recent_files', recent_files)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        self.recent_menu.delete(0, 'end')
        
        recent_files = self.settings.get('recent_files', [])
        if not recent_files:
            self.recent_menu.add_command(label="No recent files", state='disabled')
        else:
            for file_path in recent_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(
                        label=filename,
                        command=lambda f=file_path: self.load_file(f)
                    )
    
    def schedule_auto_save(self):
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        interval = self.settings.get('auto_save_interval', 30000)
        self.auto_save_timer = self.root.after(interval, self.auto_save)
    
    def auto_save(self):
        if self.file_modified and self.current_file:
            self.save_file()

def main():
    """Launch the modern LogLog GUI"""
    app = ModernLogLogGUI()
    app.root.mainloop()

if __name__ == '__main__':
    main()