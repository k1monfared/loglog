#!/usr/bin/env python3
"""
LogLog GUI - Modern Design
A modern, sleek desktop GUI inspired by Obsidian, Sublime Text, and Notion.
"""

import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import re
import subprocess
from loglog_tree_model import LogLogTree, LogLogNode, SelectionManager
from interaction_controllers import InteractionManager

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
        # Simple click to select
        def on_click(event):
            # Exit edit mode when clicking outside of currently editing node
            self.tree_renderer.exit_edit_mode()
            
            if event.state & 0x4:  # Ctrl key held
                # Ctrl+Click: Toggle individual selection (preserve anchor)
                if self.tree_renderer.active_viewport:
                    selection = self.tree_renderer.active_viewport.tree.selection
                    selection.toggle_selection(self.node)
                    # Set anchor if this is the first selection
                    if not self.tree_renderer.selection_anchor and self.node in selection.selected_nodes:
                        self.tree_renderer.selection_anchor = self.node
                    self.tree_renderer.update_selection_display()
            elif event.state & 0x1:  # Shift key held
                # Shift+Click: Select range from anchor node to this node
                self._handle_shift_click()
            else:
                # Regular click: Select only this node (file browser behavior)
                self.tree_renderer.select_single_node(self.node)
            return "break"
        
        # Double-click to edit
        def on_double_click(event):
            # If multiple nodes are selected, first deselect others
            if self.tree_renderer.active_viewport:
                selected_nodes = self.tree_renderer.active_viewport.tree.selection.get_selected_nodes()
                if len(selected_nodes) > 1:
                    # Select only this node before editing
                    self.tree_renderer.select_single_node(self.node)
            
            self.start_editing()
            return "break"
        
        # Triangle click to toggle fold
        def on_triangle_click(event):
            if self.node.children:
                self.node.toggle_fold()
                # Use viewport's optimized refresh
                self.tree_renderer.on_node_fold_toggle(self.node)
            return "break"
        
        # Checkbox click to cycle TODO status
        def on_checkbox_click(event):
            if self.node.todo_status is not None:
                # Record action for undo/redo
                old_status = self.node.todo_status
                self.node.cycle_todo_status()
                if hasattr(self.tree_renderer, 'record_action'):
                    self.tree_renderer.record_action(
                        'todo_status',
                        node_id=self.node.id,
                        old_status=old_status,
                        new_status=self.node.todo_status
                    )
                self.update_from_node()
            return "break"
        
        # Bind events to all clickable elements
        for widget in [self, self.content_frame, self.content_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
        
        self.triangle_label.bind("<Button-1>", on_triangle_click)
        self.checkbox_label.bind("<Button-1>", on_checkbox_click)
    
    def _handle_shift_click(self):
        """Handle shift+click for range selection based on selection anchor"""
        if not self.tree_renderer.active_viewport:
            return
            
        selection = self.tree_renderer.active_viewport.tree.selection
        anchor_node = self.tree_renderer.selection_anchor
        
        if not anchor_node:
            # No anchor node, just select this one and set as anchor
            self.tree_renderer.select_single_node(self.node)
            return
        
        # Get visible nodes to determine selection range
        visible_nodes = self.tree_renderer.active_viewport.tree.get_visible_nodes()
        
        if anchor_node in visible_nodes and self.node in visible_nodes:
            start_idx = visible_nodes.index(anchor_node)
            end_idx = visible_nodes.index(self.node)
            
            # Ensure start <= end
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
            
            # Manually clear ALL selections (including focused node) 
            for selected_node in list(selection.selected_nodes):
                selection.remove_from_selection(selected_node)
            
            # Select range from anchor to clicked node
            for i in range(start_idx, end_idx + 1):
                selection.add_to_selection(visible_nodes[i])
            
            # Keep focus on the clicked node
            selection.set_focus(self.node)
            self.tree_renderer.update_selection_display()
    
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
            # Check if cursor is at end of text
            cursor_pos = self.edit_entry.index(tk.INSERT)
            text_length = len(self.edit_entry.get())
            
            if cursor_pos == text_length:
                # Cursor at end - create new sibling node
                self.finish_editing(save=True)
                self._create_new_sibling()
            else:
                # Cursor not at end - just finish editing
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
            if new_content != self.node.content:
                # Record action for undo/redo
                if hasattr(self.tree_renderer, 'record_action'):
                    self.tree_renderer.record_action(
                        'edit_node',
                        node_id=self.node.id,
                        old_content=self.node.content,
                        new_content=new_content
                    )
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
    
    def _create_new_sibling(self):
        """Create a new sibling node after the current node"""
        try:
            # Import the TreeNode class
            from loglog import TreeNode
            
            # Create new sibling node with same depth
            new_node = TreeNode("", self.node.depth)
            
            # Add it after current node
            if self.node.parent:
                parent = self.node.parent
                current_index = parent.children.index(self.node)
                parent.children.insert(current_index + 1, new_node)
                new_node.parent = parent
            else:
                # Handle root level nodes - add to the tree root
                if hasattr(self.tree_renderer, 'tree') and hasattr(self.tree_renderer.tree, 'root'):
                    tree_root = self.tree_renderer.tree.root
                    if self.node in tree_root.children:
                        current_index = tree_root.children.index(self.node)
                        tree_root.children.insert(current_index + 1, new_node)
                        new_node.parent = tree_root
            
            # Mark file as modified
            if hasattr(self.tree_renderer, 'on_node_modified'):
                self.tree_renderer.on_node_modified(new_node)
            
            # Refresh display and focus new node
            self.tree_renderer.refresh_display()
            
            # Focus and start editing the new node
            if hasattr(self.tree_renderer, 'set_focus'):
                self.tree_renderer.set_focus(new_node)
                # Use after_idle to ensure the widget is created before editing
                if hasattr(self.tree_renderer, 'after_idle'):
                    self.tree_renderer.after_idle(lambda: self._start_editing_new_node(new_node))
                else:
                    # Fallback for when tree_renderer doesn't have after_idle
                    print("Starting edit on new node")
            
        except Exception as e:
            print(f"Error creating sibling: {e}")
    
    def _start_editing_new_node(self, new_node):
        """Start editing a newly created node"""
        try:
            # Find the viewport and widget for the new node
            if hasattr(self.tree_renderer, 'node_widgets') and new_node.id in self.tree_renderer.node_widgets:
                widget = self.tree_renderer.node_widgets[new_node.id]
                widget.start_editing()
        except Exception as e:
            print(f"Error starting edit on new node: {e}")

class TabViewport(tk.Frame):
    """Persistent viewport for a single tab's tree content - industry standard approach"""
    
    def __init__(self, parent, system_theme, file_path):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.system_theme = system_theme
        self.file_path = file_path
        self.parent_tree_renderer = None  # Will be set by TreeRenderer
        self.tree = LogLogTree()
        self.node_widgets = {}  # node_id -> TreeNodeWidget mapping
        self.node_positions = {}  # node_id -> y_position for efficient positioning
        self.visible_nodes_cache = []  # Cache for visible nodes
        
        # Undo/Redo system
        self.undo_stack = []  # Stack of actions that can be undone
        self.redo_stack = []  # Stack of actions that can be redone
        self.max_undo_stack = 50  # Limit undo stack size
        
        # Performance optimization flags
        self._position_update_pending = False
        self._batch_updates = []
        self._virtual_scrolling_enabled = True  # Can be disabled if causing issues
        
        # Create scrollable container
        self.setup_scrollable_container()
        
        # Initially hidden (will be shown when tab is active)
        self.pack_forget()
    
    def setup_scrollable_container(self):
        """Create native Text widget with automatic scrolling"""
        # Use native Text widget for automatic scrolling - no more custom handling!
        self.text_widget = tk.Text(
            self,
            wrap=tk.NONE,
            font=('Courier', 10),  # Monospace font like a code editor
            bg=self.system_theme.get_color('bg'),
            fg=self.system_theme.get_color('fg'),
            insertbackground=self.system_theme.get_color('fg'),
            selectbackground=self.system_theme.get_color('select_bg'),
            selectforeground=self.system_theme.get_color('select_fg'),
            state='disabled',  # Read-only by default
            highlightthickness=0
        )
        
        # Native scrollbar automatically linked to Text widget
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.text_widget.yview,
            bg=self.system_theme.get_color('bg'),
            activebackground=self.system_theme.get_color('select_bg'),
            troughcolor=self.system_theme.get_color('bg'),
            width=16
        )
        
        # Link scrollbar to text widget - native scrolling!
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.text_widget.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        print("✅ Native Text widget scrolling setup - no custom handlers needed!")
        
        # Keep references for compatibility (some code expects these)
        self.canvas = self.text_widget  # Compatibility alias
        self.scrollable_frame = self.text_widget  # Compatibility alias
        
        # Initialize line-to-node mapping for click detection
        self.line_to_node = {}
        
        # Setup interactive click handling
        self.setup_text_click_handling()
        
        # Initialize comprehensive interaction manager
        self.interaction_manager = InteractionManager(self.tree, self)
        
        print("✅ Comprehensive interaction controllers initialized!")
    
    def on_text_configure(self, event):
        """Handle text widget resize - not needed with native Text widget"""
        pass  # Native Text widget handles its own sizing
    
    def bind_mouse_wheel_native(self):
        """Native Text widget has automatic scrolling - NO CUSTOM BINDINGS NEEDED!"""
        # Text widget handles ALL scrolling automatically:
        # - Mouse wheel (Windows/Mac/Linux) ✅
        # - Keyboard (Page Up/Down, Arrow keys) ✅  
        # - Scrollbar dragging ✅
        # - Focus management ✅
        # - Cross-platform compatibility ✅
        print("✅ Native scrolling active - mouse wheel, keyboard, scrollbar all work automatically!")
        pass  # Nothing to bind - it just works!
        
        # Virtual scrolling support - hook into existing scrollbar changes  
        # Note: Don't override yscrollcommand as it breaks scrollbar functionality
    
    def _schedule_viewport_refresh(self):
        """Schedule a viewport refresh with debouncing to avoid excessive updates"""
        if hasattr(self, '_refresh_pending'):
            self.after_cancel(self._refresh_pending)
        
        self._refresh_pending = self.after(200, self._do_viewport_refresh)  # 200ms debounce (slower)
    
    def _do_viewport_refresh(self):
        """Perform the actual viewport refresh"""
        if hasattr(self, '_refresh_pending'):
            del self._refresh_pending
        
        # Only refresh if we have content
        if hasattr(self, 'tree') and self.tree:
            self.refresh_display()
    
    def show(self):
        """Show this viewport"""
        self.pack(fill='both', expand=True)
        # Native Text widget handles geometry automatically - no complex setup needed!
        self.after_idle(self.update_idletasks)
    
    def hide(self):
        """Hide this viewport"""
        self.pack_forget()
    
    def load_content(self, content):
        """Load tree content efficiently"""
        self.tree.load_from_text(content)
        self.refresh_display()
    
    def refresh_display(self):
        """Native Text widget display - simply load content as text!"""
        # Get all tree-visible nodes (expanded hierarchy)
        all_visible_nodes = self.tree.get_visible_nodes()
        
        # Convert tree structure to plain text format + store line mappings for interactivity
        content_lines = []
        self.line_to_node = {}  # Maps line number to node for click detection
        line_number = 1  # Text widget lines start at 1
        
        for node in all_visible_nodes:
            # Calculate depth by traversing up to root
            depth = 0
            current = node
            while current and current.parent:
                depth += 1
                current = current.parent
            
            # Create indentation based on calculated depth
            indent = "    " * depth
            
            # Add expand/collapse indicator
            if len(node.children) > 0:
                if node.is_folded:
                    indicator = "▶ "  # Collapsed triangle (note: is_folded not is_expanded)
                else:
                    indicator = "▼ "  # Expanded triangle
            else:
                indicator = "  "  # No children
            
            # Add TODO status if applicable
            todo_prefix = ""
            if node.todo_status:
                todo_map = {'todo': '☐ ', 'doing': '◐ ', 'done': '☑ '}
                todo_prefix = todo_map.get(node.todo_status, '')
            
            # Combine line
            line = f"{indent}{indicator}{todo_prefix}{node.content}"
            content_lines.append(line)
            
            # Map line number to node for click detection
            self.line_to_node[line_number] = node
            line_number += 1
        
        # Load content into Text widget
        content_text = "\n".join(content_lines)
        
        # Update Text widget
        self.text_widget.configure(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', content_text)
        
        # Add selection highlighting for selected nodes
        self._update_selection_highlighting(all_visible_nodes)
        
        self.text_widget.configure(state='disabled')  # Make read-only
        
        print(f"✅ Native text display updated: {len(all_visible_nodes)} nodes with interactivity")
    
    def _update_selection_highlighting(self, all_visible_nodes):
        """Add visual selection highlighting to Text widget"""
        # Configure text tags for highlighting
        self.text_widget.tag_configure("selected", background=self.system_theme.get_color('select_bg'), 
                                       foreground=self.system_theme.get_color('select_fg'))
        
        # Apply selection highlighting
        line_number = 1
        for node in all_visible_nodes:
            if node.is_selected:
                line_start = f"{line_number}.0"
                line_end = f"{line_number}.end"
                self.text_widget.tag_add("selected", line_start, line_end)
            line_number += 1
    
    def setup_text_click_handling(self):
        """Setup click handling for Text widget interactivity"""
        def on_text_click(event):
            # Get the line number and character position that was clicked
            click_index = self.text_widget.index(f"@{event.x},{event.y}")
            line_number = int(click_index.split('.')[0])
            char_pos = int(click_index.split('.')[1])
            
            # Find the corresponding node
            if line_number in self.line_to_node:
                node = self.line_to_node[line_number]
                
                # Get the text of the clicked line to determine click position
                line_start = f"{line_number}.0"
                line_end = f"{line_number}.end"
                line_text = self.text_widget.get(line_start, line_end)
                
                # Find triangle position (after indentation, before content)
                depth = 0
                current = node
                while current and current.parent:
                    depth += 1
                    current = current.parent
                
                indent_length = depth * 4  # 4 spaces per indent level
                triangle_start = indent_length
                triangle_end = triangle_start + 2  # Triangle symbols are 2 chars (▼ )
                
                # Check if click was on triangle (only for nodes with children)
                clicked_on_triangle = (len(node.children) > 0 and 
                                     triangle_start <= char_pos < triangle_end)
                
                if clicked_on_triangle:
                    # Handle fold/unfold ONLY when clicking on triangle
                    node.is_folded = not node.is_folded
                    self.refresh_display()  # Refresh to show/hide children
                    print(f"✅ {'Folded' if node.is_folded else 'Unfolded'} node: {node.content[:30]}...")
                else:
                    # Handle selection when clicking on text content (not triangle)
                    # Clear other selections first
                    for n in self.tree.get_all_nodes():
                        n.is_selected = False
                    
                    # Select clicked node
                    node.is_selected = True
                    self.refresh_display()  # Refresh to show selection
                    print(f"✅ Selected node: {node.content[:30]}...")
                    
                    # Notify parent TreeRenderer of selection change (if it has a selection system)
                    if self.parent_tree_renderer and hasattr(self.parent_tree_renderer, 'selection_manager'):
                        self.parent_tree_renderer.selection_manager.set_selection([node])
            
            return "break"  # Prevent default text widget behavior
        
        # Bind click event to Text widget
        self.text_widget.bind("<Button-1>", on_text_click)
        
        # Add keyboard navigation
        self.setup_keyboard_navigation()
        
        print(f"✅ Text widget click and keyboard handling enabled")
    
    def setup_keyboard_navigation(self):
        """Setup keyboard navigation for tree interactions"""
        def get_selected_node():
            """Get the currently selected node"""
            for node in self.tree.get_all_nodes():
                if node.is_selected:
                    return node
            return None
        
        def get_visible_nodes_list():
            """Get list of currently visible nodes"""
            return self.tree.get_visible_nodes()
        
        def select_node(node):
            """Select a specific node"""
            # Clear other selections
            for n in self.tree.get_all_nodes():
                n.is_selected = False
            # Select the new node
            node.is_selected = True
            self.refresh_display()
            print(f"✅ Keyboard selected: {node.content[:30]}...")
        
        def on_key_up(event):
            """Move selection up"""
            current = get_selected_node()
            visible = get_visible_nodes_list()
            if current and visible and current in visible:
                current_idx = visible.index(current)
                if current_idx > 0:
                    select_node(visible[current_idx - 1])
            elif visible:
                select_node(visible[-1])  # Select last if none selected
            return "break"
        
        def on_key_down(event):
            """Move selection down"""
            current = get_selected_node()
            visible = get_visible_nodes_list()
            if current and visible and current in visible:
                current_idx = visible.index(current)
                if current_idx < len(visible) - 1:
                    select_node(visible[current_idx + 1])
            elif visible:
                select_node(visible[0])  # Select first if none selected
            return "break"
        
        def on_key_right(event):
            """Expand node if collapsed, or move to first child"""
            current = get_selected_node()
            if current and len(current.children) > 0:
                if current.is_folded:
                    current.is_folded = False
                    self.refresh_display()
                    print(f"✅ Keyboard expanded: {current.content[:30]}...")
                else:
                    # Move to first child if expanded
                    visible = get_visible_nodes_list()
                    if current in visible:
                        current_idx = visible.index(current)
                        if current_idx < len(visible) - 1:
                            select_node(visible[current_idx + 1])
            return "break"
        
        def on_key_left(event):
            """Collapse node if expanded, or move to parent"""
            current = get_selected_node()
            if current:
                if len(current.children) > 0 and not current.is_folded:
                    current.is_folded = True
                    self.refresh_display()
                    print(f"✅ Keyboard collapsed: {current.content[:30]}...")
                elif current.parent:
                    select_node(current.parent)
            return "break"
        
        def on_key_space(event):
            """Toggle fold/unfold of selected node"""
            current = get_selected_node()
            if current and len(current.children) > 0:
                current.is_folded = not current.is_folded
                self.refresh_display()
                print(f"✅ Keyboard {'collapsed' if current.is_folded else 'expanded'}: {current.content[:30]}...")
            return "break"
        
        def on_key_enter(event):
            """Activate/toggle selected node (same as space)"""
            return on_key_space(event)
        
        # Bind keyboard events - Text widget needs focus to receive keys
        self.text_widget.bind("<Up>", on_key_up)
        self.text_widget.bind("<Down>", on_key_down)
        self.text_widget.bind("<Right>", on_key_right)
        self.text_widget.bind("<Left>", on_key_left)
        self.text_widget.bind("<space>", on_key_space)
        self.text_widget.bind("<Return>", on_key_enter)
        
        # Make sure text widget can receive focus
        self.text_widget.focus_set()
        
        print(f"✅ Keyboard navigation setup: Up/Down (navigate), Left/Right (fold/expand), Space/Enter (toggle)")
    
    def update_node_positions(self, visible_nodes):
        """Not needed with native Text widget - content is just text!"""
        pass  # Text widget handles its own layout automatically
    
    def get_viewport_visible_nodes(self, all_visible_nodes):
        """Not needed with native Text widget - all nodes rendered as text!"""
        # With Text widget, we can render all nodes efficiently as plain text
        return all_visible_nodes
    
    def _update_virtual_scroll_region(self, all_visible_nodes):
        """Not needed with native Text widget - automatic scroll handling!"""
        pass  # Text widget handles scroll regions automatically

    def create_node_widget(self, node):
        """Not needed with native Text widget - content is rendered as text!"""
        pass  # Text widget displays content directly, no individual node widgets needed
    
    def _update_scroll_region(self):
        """Not needed with native Text widget - automatic scroll handling!"""
        pass  # Text widget handles scroll regions automatically
    
    def on_node_fold_toggle(self, node):
        """Handle node fold toggle with minimal impact"""
        # Only update affected part of the tree
        self.refresh_display()
    
    # Delegation methods for TreeNodeWidget compatibility
    def set_focus(self, node):
        """Delegate focus setting to parent TreeRenderer"""
        if self.parent_tree_renderer:
            self.parent_tree_renderer.set_focus(node)
        else:
            # Fallback: set focus on tree selection directly
            self.tree.selection.set_focus(node)
    
    def update_selection_display(self):
        """Delegate selection display update to parent TreeRenderer"""
        if self.parent_tree_renderer:
            self.parent_tree_renderer.update_selection_display()
        else:
            # Fallback: refresh display
            self.refresh_display()
    
    def on_node_modified(self, node):
        """Handle node modification"""
        if self.parent_tree_renderer and hasattr(self.parent_tree_renderer, 'gui'):
            # Notify GUI of changes
            gui = self.parent_tree_renderer.gui
            if hasattr(gui, 'mark_file_modified'):
                gui.mark_file_modified()
        # Refresh the display to show changes
        self.refresh_display()
    
    @property
    def active_viewport(self):
        """Return self for compatibility with TreeNodeWidget"""
        return self
    
    def record_action(self, action_type, **kwargs):
        """Record an action for undo/redo"""
        action = {
            'type': action_type,
            'timestamp': time.time(),
            **kwargs
        }
        
        # Add to undo stack
        self.undo_stack.append(action)
        
        # Clear redo stack (new action invalidates redo)
        self.redo_stack.clear()
        
        # Limit stack size
        if len(self.undo_stack) > self.max_undo_stack:
            self.undo_stack.pop(0)
    
    def undo_action(self):
        """Undo the last action"""
        if not self.undo_stack:
            return False
        
        action = self.undo_stack.pop()
        
        try:
            if action['type'] == 'edit_node':
                # Undo node content change
                node_id = action['node_id']
                old_content = action['old_content']
                
                # Find the node and restore content
                for node in self.tree.get_all_nodes():
                    if node.id == node_id:
                        # Record current state for redo
                        redo_action = {
                            'type': 'edit_node',
                            'node_id': node_id,
                            'old_content': node.content,
                            'new_content': old_content
                        }
                        self.redo_stack.append(redo_action)
                        
                        # Apply undo
                        node.content = old_content
                        self.refresh_display()
                        return True
            
            elif action['type'] == 'todo_status':
                # Undo TODO status change
                node_id = action['node_id']
                old_status = action['old_status']
                
                for node in self.tree.get_all_nodes():
                    if node.id == node_id:
                        # Record current state for redo
                        redo_action = {
                            'type': 'todo_status',
                            'node_id': node_id,
                            'old_status': node.todo_status,
                            'new_status': old_status
                        }
                        self.redo_stack.append(redo_action)
                        
                        # Apply undo
                        node.set_todo_status(old_status)
                        self.refresh_display()
                        return True
            
            elif action['type'] == 'add_node':
                # Undo node addition (remove the node)
                node_id = action['node_id']
                
                for node in self.tree.get_all_nodes():
                    if node.id == node_id:
                        # Record node data for redo
                        redo_action = {
                            'type': 'remove_node',
                            'node_data': {
                                'id': node.id,
                                'content': node.content,
                                'depth': node.depth,
                                'todo_status': node.todo_status,
                                'parent_id': node.parent.id if node.parent else None,
                                'position': node.parent.children.index(node) if node.parent else 0
                            }
                        }
                        self.redo_stack.append(redo_action)
                        
                        # Remove the node
                        if node.parent:
                            node.parent.children.remove(node)
                        self.refresh_display()
                        return True
            
            # Add action back to undo stack if it couldn't be processed
            self.undo_stack.append(action)
            return False
            
        except Exception as e:
            print(f"Undo error: {e}")
            # Put action back on stack
            self.undo_stack.append(action)
            return False
    
    def redo_action(self):
        """Redo the last undone action"""
        if not self.redo_stack:
            return False
        
        action = self.redo_stack.pop()
        
        try:
            if action['type'] == 'edit_node':
                # Redo node content change
                node_id = action['node_id']
                new_content = action['new_content']
                
                for node in self.tree.get_all_nodes():
                    if node.id == node_id:
                        # Record current state for undo
                        undo_action = {
                            'type': 'edit_node',
                            'node_id': node_id,
                            'old_content': node.content,
                            'new_content': new_content
                        }
                        self.undo_stack.append(undo_action)
                        
                        # Apply redo
                        node.content = new_content
                        self.refresh_display()
                        return True
            
            elif action['type'] == 'todo_status':
                # Redo TODO status change
                node_id = action['node_id']
                new_status = action['new_status']
                
                for node in self.tree.get_all_nodes():
                    if node.id == node_id:
                        # Record current state for undo
                        undo_action = {
                            'type': 'todo_status',
                            'node_id': node_id,
                            'old_status': node.todo_status,
                            'new_status': new_status
                        }
                        self.undo_stack.append(undo_action)
                        
                        # Apply redo
                        node.set_todo_status(new_status)
                        self.refresh_display()
                        return True
            
            # Add action back to redo stack if it couldn't be processed
            self.redo_stack.append(action)
            return False
            
        except Exception as e:
            print(f"Redo error: {e}")
            # Put action back on stack
            self.redo_stack.append(action)
            return False

class TreeRenderer(tk.Frame):
    """Multi-tab tree renderer with viewport management - industry standard approach"""
    
    def __init__(self, parent, system_theme):
        super().__init__(parent, bg=system_theme.get_color('bg'))
        self.system_theme = system_theme
        
        # Viewport management - each tab gets its own persistent viewport
        self.viewports = {}  # file_path -> TabViewport
        self.active_viewport = None
        self.current_file = None
        
        # Selection anchor for shift+click range operations
        self.selection_anchor = None
        
        # Create viewport container
        self.viewport_container = tk.Frame(self, bg=system_theme.get_color('bg'))
        self.viewport_container.pack(fill='both', expand=True)
        
        # Make widget focusable and bind keyboard events
        self.focus_set()
        self.config(takefocus=True)  # Ensure widget can receive focus
        self.bind_keyboard_events()
        
        # Make this widget focusable and ensure it captures focus when clicked
        self.bind("<Button-1>", self._on_click_focus)
        self.bind("<FocusIn>", self._on_focus_in)
    
    def get_or_create_viewport(self, file_path):
        """Get existing viewport or create new one for file"""
        if file_path not in self.viewports:
            viewport = TabViewport(self.viewport_container, self.system_theme, file_path)
            viewport.parent_tree_renderer = self  # Set parent reference
            self.viewports[file_path] = viewport
        return self.viewports[file_path]
    
    def switch_to_file(self, file_path, content=None):
        """Switch to a different file's viewport - instant switching"""
        # Hide current viewport
        if self.active_viewport:
            self.active_viewport.hide()
        
        # Get or create viewport for the file
        viewport = self.get_or_create_viewport(file_path)
        
        # Load content if provided and viewport is empty
        if content is not None and not hasattr(viewport, '_content_loaded'):
            viewport.load_content(content)
            viewport._content_loaded = True
        
        # Show the new viewport
        viewport.show()
        self.active_viewport = viewport
        self.current_file = file_path
        
        # Ensure TreeRenderer has focus for keyboard events
        self.after_idle(self.focus_set)
    
    def remove_viewport(self, file_path):
        """Remove viewport for closed tab"""
        if file_path in self.viewports:
            viewport = self.viewports[file_path]
            if viewport == self.active_viewport:
                self.active_viewport = None
            viewport.destroy()
            del self.viewports[file_path]
    
    # Delegate properties and methods to active viewport
    @property
    def tree(self):
        return self.active_viewport.tree if self.active_viewport else None
    
    def load_from_file(self, file_path):
        """Load file into current viewport"""
        if self.active_viewport:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.active_viewport.load_content(content)
                return True
            except Exception as e:
                print(f"Error loading file: {e}")
                return False
        return False
    
    def load_from_text(self, text):
        """Load text into current viewport"""
        if self.active_viewport:
            self.active_viewport.load_content(text)
            return True
        return False
    
    # Delegation methods - forward calls to active viewport
    def refresh_display(self):
        """Delegate to active viewport"""
        if self.active_viewport:
            self.active_viewport.refresh_display()
    
    def refresh_fold_display(self):
        """Delegate fold operations to active viewport"""
        if self.active_viewport:
            self.active_viewport.refresh_display()
    
    def set_focus(self, node):
        """Delegate focus operations to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree'):
            self.active_viewport.tree.selection.set_focus(node)
            self.update_selection_display()
    
    def select_single_node(self, node):
        """Select only this node (file browser behavior) - clear others, select this one, set focus"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree'):
            selection = self.active_viewport.tree.selection
            
            # Manually clear ALL selections (including focused node)
            for selected_node in list(selection.selected_nodes):
                selection.remove_from_selection(selected_node)
            
            # Set focus and add to selection
            selection.set_focus(node)
            selection.add_to_selection(node)
            
            # Set this node as the selection anchor for future shift+click operations
            self.selection_anchor = node
            
            self.update_selection_display()
    
    
    def update_selection_display(self):
        """Delegate selection updates to active viewport"""
        if self.active_viewport:
            for widget in self.active_viewport.node_widgets.values():
                widget.update_selection_state()
    
    def on_node_fold_toggle(self, node):
        """Delegate fold toggle to active viewport"""
        if self.active_viewport:
            self.active_viewport.on_node_fold_toggle(node)
    
    def ensure_node_visible(self, node):
        """Delegate scroll operations to active viewport"""
        if self.active_viewport and node.id in self.active_viewport.node_widgets:
            widget = self.active_viewport.node_widgets[node.id]
            # Simple scroll to widget logic
            widget.tk.call('::ttk::scrollableframe::center', widget)
    
    def get_content(self):
        """Get current viewport content"""
        if self.active_viewport and self.active_viewport.tree:
            return self.active_viewport.tree.serialize()
        return ""
    
    # Navigation delegation methods
    def move_focus_up(self):
        """Delegate navigation to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            visible_nodes = self.active_viewport.tree.get_visible_nodes()
            focused_node = self.active_viewport.tree.selection.focused_node
            try:
                current_index = visible_nodes.index(focused_node)
                if current_index > 0:
                    self.select_single_node(visible_nodes[current_index - 1])
            except (ValueError, IndexError):
                pass
    
    def move_focus_down(self):
        """Delegate navigation to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            visible_nodes = self.active_viewport.tree.get_visible_nodes()
            focused_node = self.active_viewport.tree.selection.focused_node
            try:
                current_index = visible_nodes.index(focused_node)
                if current_index < len(visible_nodes) - 1:
                    self.select_single_node(visible_nodes[current_index + 1])
            except (ValueError, IndexError):
                pass
    
    def move_focus_left(self):
        """Delegate navigation to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            focused_node = self.active_viewport.tree.selection.focused_node
            if focused_node.children and not focused_node.is_folded:
                focused_node.toggle_fold()
                self.refresh_fold_display()
            elif focused_node.parent and focused_node.parent.node_type.value != "root":
                self.select_single_node(focused_node.parent)
    
    def move_focus_right(self):
        """Delegate navigation to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            focused_node = self.active_viewport.tree.selection.focused_node
            if focused_node.children:
                if focused_node.is_folded:
                    focused_node.toggle_fold()
                    self.refresh_fold_display()
                else:
                    self.select_single_node(focused_node.children[0])
    
    def unfold_all(self):
        """Delegate to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            all_nodes = self.active_viewport.tree.get_all_nodes()
            for node in all_nodes:
                if node.is_folded:
                    node.is_folded = False
            self.refresh_fold_display()
    
    def fold_to_level(self, max_level):
        """Delegate to active viewport"""
        if self.active_viewport and hasattr(self.active_viewport, 'tree') and self.active_viewport.tree:
            def fold_recursive(node, current_level=0):
                if current_level >= max_level:
                    node.is_folded = True
                else:
                    node.is_folded = False
                    for child in node.children:
                        fold_recursive(child, current_level + 1)
            
            fold_recursive(self.active_viewport.tree.root)
            self.refresh_fold_display()
    
    def bind_keyboard_events(self):
        """Bind keyboard navigation events"""
        def on_key(event):
            result = self.handle_keyboard_event(event)
            return result if result else "break"  # Always break to prevent propagation
        
        # Make sure this widget can receive focus and capture all keyboard events
        self.bind("<Button-1>", lambda e: self.focus_set())
        
        # Bind specific key events for better capture
        self.bind("<Key>", on_key)
        self.bind("<KeyPress>", on_key)
        
        # Also bind specific navigation keys directly
        self.bind("<Up>", on_key)
        self.bind("<Down>", on_key)
        self.bind("<Left>", on_key)
        self.bind("<Right>", on_key)
        self.bind("<Return>", on_key)
        self.bind("<space>", on_key)
        self.bind("<Shift-Up>", on_key)
        self.bind("<Shift-Down>", on_key)
        self.bind("<Shift-Left>", on_key)
        self.bind("<Shift-Right>", on_key)
        
        # Focus on content when widget is shown
        self.bind("<Map>", lambda e: self.after_idle(self.focus_set))
    
    def _on_click_focus(self, event):
        """Handle clicks to ensure proper focus"""
        self.focus_set()
        # Ensure the active viewport also gets focus
        if self.active_viewport:
            self.active_viewport.focus_set()
        return "break"  # Prevent event propagation
    
    def _on_focus_in(self, event):
        """Handle focus events"""
        # Ensure the active viewport also gets focus
        if self.active_viewport:
            self.active_viewport.focus_set()
            # Set initial focus to first visible node if none selected
            if not self.active_viewport.tree.selection.focused_node:
                visible_nodes = self.active_viewport.tree.get_visible_nodes()
                if visible_nodes:
                    self.set_focus(visible_nodes[0])
    
    def load_from_file(self, file_path):
        """Load LogLog file into tree and render"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tree.load_from_text(content)
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
    
    def refresh_fold_display(self):
        """Fast refresh specifically optimized for fold operations"""
        # Use a deferred update to batch multiple fold operations
        if hasattr(self, '_fold_update_pending'):
            return
        
        self._fold_update_pending = True
        self.after_idle(self._do_fold_refresh)
    
    def _do_fold_refresh(self):
        """Perform the actual fold refresh - delegate to active viewport"""
        if hasattr(self, '_fold_update_pending'):
            del self._fold_update_pending
        
        if self.active_viewport:
            self.active_viewport.refresh_display()
    
    def _update_scroll_region(self):
        """Update scroll region efficiently with robust fallback"""
        try:
            if not hasattr(self, 'active_viewport') or not self.active_viewport:
                return
                
            viewport = self.active_viewport
            if hasattr(viewport, 'scrollable_frame') and hasattr(viewport, 'canvas'):
                viewport.scrollable_frame.update_idletasks()
                bbox = viewport.canvas.bbox("all")
                
                # If bbox is empty or None, calculate based on content
                if not bbox or bbox == '':
                    # Calculate scrollregion based on actual content
                    visible_nodes = viewport.tree.get_visible_nodes() if hasattr(viewport, 'tree') else []
                    if visible_nodes:
                        node_height = 25
                        total_height = len(visible_nodes) * node_height
                        scroll_region = (0, 0, 0, total_height)
                    else:
                        scroll_region = (0, 0, 0, 100)  # Minimum scrollable area
                else:
                    scroll_region = bbox
                    
                viewport.canvas.configure(scrollregion=scroll_region)
                
        except Exception as e:
            print(f"TreeRenderer scroll region update error: {e}")
            # Fallback to basic scrollable area
            if hasattr(self, 'active_viewport') and self.active_viewport and hasattr(self.active_viewport, 'canvas'):
                self.active_viewport.canvas.configure(scrollregion=(0, 0, 0, 500))
    
    def set_focus(self, node):
        """Set focus to a specific node"""
        # Update tree selection
        self.tree.selection.set_focus(node)
        
        # Update visual states
        self.update_selection_display()
        
        # Ensure node is visible by scrolling if necessary
        self.ensure_node_visible(node)
    
    def update_selection_display(self):
        """Delegate selection updates to active viewport"""
        if self.active_viewport:
            for widget in self.active_viewport.node_widgets.values():
                widget.update_selection_state()
    
    def batch_update_nodes(self, nodes):
        """Efficiently update multiple nodes at once"""
        # Defer updates to prevent multiple refresh calls
        if hasattr(self, '_batch_update_pending'):
            return
        
        self._batch_update_pending = True
        self.after_idle(lambda: self._do_batch_update(nodes))
    
    def _do_batch_update(self, nodes):
        """Delegate batch update to active viewport"""
        if hasattr(self, '_batch_update_pending'):
            del self._batch_update_pending
        
        if self.active_viewport:
            for node in nodes:
                if node.id in self.active_viewport.node_widgets:
                    self.active_viewport.node_widgets[node.id].update_from_node()
    
    def ensure_node_visible(self, node):
        """Delegate scroll operations to active viewport"""
        if not self.active_viewport or node.id not in self.active_viewport.node_widgets:
            return
            
        widget = self.active_viewport.node_widgets[node.id]
        
        # Get widget position relative to scrollable frame
        widget.update_idletasks()
        widget_top = widget.winfo_y()
        widget_height = widget.winfo_height()
        
        # Get canvas dimensions
        canvas_height = self.active_viewport.canvas.winfo_height()
        
        # Calculate scroll position
        scroll_top, scroll_bottom = self.active_viewport.canvas.yview()
        scrollable_height = self.active_viewport.scrollable_frame.winfo_reqheight()
        
        # Convert to pixel coordinates
        visible_top = scroll_top * scrollable_height
        visible_bottom = scroll_bottom * scrollable_height
        
        # Check if widget is visible
        if widget_top < visible_top or widget_top + widget_height > visible_bottom:
            # Scroll to make widget visible
            new_scroll_top = max(0, widget_top - canvas_height // 4)
            scroll_fraction = new_scroll_top / scrollable_height if scrollable_height > 0 else 0
            self.active_viewport.canvas.yview_moveto(scroll_fraction)
    
    def handle_keyboard_event(self, event):
        """Handle keyboard navigation"""
        if not self.active_viewport:
            return "break"
            
        focused_node = self.active_viewport.tree.selection.focused_node
        if not focused_node:
            # Set focus to first visible node
            visible_nodes = self.active_viewport.tree.get_visible_nodes()
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
            old_status = focused_node.todo_status
            focused_node.set_todo_status("unknown")
            self.record_action(
                'todo_status',
                node_id=focused_node.id,
                old_status=old_status,
                new_status=focused_node.todo_status
            )
            self.update_selection_display()
        elif event.char == "-" and focused_node.todo_status:
            old_status = focused_node.todo_status
            focused_node.set_todo_status("progress")
            self.record_action(
                'todo_status',
                node_id=focused_node.id,
                old_status=old_status,
                new_status=focused_node.todo_status
            )
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
        if not self.active_viewport:
            return
        visible_nodes = self.active_viewport.tree.get_visible_nodes()
        focused_node = self.active_viewport.tree.selection.focused_node
        
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index > 0:
                # File browser behavior: select only the newly focused node
                self.select_single_node(visible_nodes[current_index - 1])
        except (ValueError, IndexError):
            pass
    
    def move_focus_down(self):
        """Move focus to next visible node"""
        if not self.active_viewport:
            return
        visible_nodes = self.active_viewport.tree.get_visible_nodes()
        focused_node = self.active_viewport.tree.selection.focused_node
        
        try:
            current_index = visible_nodes.index(focused_node)
            if current_index < len(visible_nodes) - 1:
                # File browser behavior: select only the newly focused node
                self.select_single_node(visible_nodes[current_index + 1])
        except (ValueError, IndexError):
            pass
    
    def move_focus_left(self):
        """Move focus to parent or fold current node"""
        if not self.active_viewport:
            return
        focused_node = self.active_viewport.tree.selection.focused_node
        
        if focused_node.children and not focused_node.is_folded:
            # Fold current node
            focused_node.toggle_fold()
            self.refresh_fold_display()
        elif focused_node.parent and focused_node.parent.node_type.value != "root":
            # Move to parent with file browser behavior
            self.select_single_node(focused_node.parent)
    
    def move_focus_right(self):
        """Move to first child or unfold current node"""
        if not self.active_viewport:
            return
        focused_node = self.active_viewport.tree.selection.focused_node
        
        if focused_node.children:
            if focused_node.is_folded:
                # Unfold current node
                focused_node.toggle_fold()
                self.refresh_fold_display()
            else:
                # Move to first child with file browser behavior
                self.select_single_node(focused_node.children[0])
    
    def exit_edit_mode(self):
        """Exit edit mode on any currently editing node"""
        if self.active_viewport:
            for widget in self.active_viewport.node_widgets.values():
                if widget.is_editing:
                    widget.finish_editing(save=True)

    def record_action(self, action_type, **kwargs):
        """Delegate action recording to active viewport"""
        if self.active_viewport:
            self.active_viewport.record_action(action_type, **kwargs)

    def start_editing_focused(self):
        """Delegate start editing to active viewport"""
        if self.active_viewport:
            focused_node = self.active_viewport.tree.selection.focused_node
            if focused_node and focused_node.id in self.active_viewport.node_widgets:
                # If multiple nodes are selected, first select only the focused node
                selected_nodes = self.active_viewport.tree.selection.get_selected_nodes()
                if len(selected_nodes) > 1:
                    self.select_single_node(focused_node)
                
                self.active_viewport.node_widgets[focused_node.id].start_editing()
    
    def toggle_todo_status(self):
        """Toggle TODO status of all selected nodes"""
        if not self.active_viewport:
            return
            
        selected_nodes = self.active_viewport.tree.selection.get_selected_nodes()
        focused_node = self.active_viewport.tree.selection.focused_node
        
        # If nothing selected, operate on focused node
        if not selected_nodes and focused_node:
            selected_nodes = [focused_node]
        
        # Apply operation to all selected nodes
        for node in selected_nodes:
            old_status = node.todo_status
            node.cycle_todo_status()
            # Record action for undo/redo
            self.record_action(
                'todo_status',
                node_id=node.id,
                old_status=old_status,
                new_status=node.todo_status
            )
        
        self.update_selection_display()
    
    def extend_selection_up(self):
        """Extend selection upward from anchor"""
        if not self.active_viewport:
            return
        visible_nodes = self.active_viewport.tree.get_visible_nodes()
        focused_node = self.active_viewport.tree.selection.focused_node
        
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
        if not self.active_viewport:
            return
        visible_nodes = self.active_viewport.tree.get_visible_nodes()
        focused_node = self.active_viewport.tree.selection.focused_node
        
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
        self.refresh_fold_display()
    
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
        self.refresh_fold_display()
    
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
        self.refresh_fold_display()
    
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
        """Extract system colors from tkinter and detect dark mode"""
        try:
            # Create temporary widget to extract system colors
            temp_frame = tk.Frame(self.root)
            temp_text = tk.Text(temp_frame)
            temp_button = tk.Button(temp_frame)
            
            # Extract base system colors
            base_bg = temp_frame.cget('bg')
            base_fg = temp_text.cget('fg')
            
            # Clean up temporary widgets
            temp_frame.destroy()
            
            # Detect if we're in dark mode based on system colors
            # Check for environment variable override
            import os
            if os.environ.get('LOGLOG_LIGHT_MODE') == '1':
                # Explicit light mode override
                self.is_dark_mode = False
            elif os.environ.get('LOGLOG_DARK_MODE') == '1':
                # Explicit dark mode override
                self.is_dark_mode = True
            else:
                # Default to dark mode, but try to detect system preference
                system_dark = self._is_dark_color(base_bg)
                self.is_dark_mode = True  # Default to dark mode
            
            if self.is_dark_mode:
                # Use dark theme colors
                self.colors = {
                    'bg': '#2d2d30',
                    'fg': '#cccccc',
                    'select_bg': '#094771',
                    'select_fg': '#ffffff',
                    'button_bg': '#3c3c3c',
                    'button_fg': '#cccccc',
                    'insert_bg': '#ffffff',
                    'disabled_fg': '#808080',
                }
            else:
                # Use light theme colors or system defaults
                self.colors = {
                    'bg': base_bg if base_bg != 'SystemButtonFace' else '#ffffff',
                    'fg': base_fg if base_fg != 'SystemButtonText' else '#000000',
                    'select_bg': '#0078d4',
                    'select_fg': '#ffffff',
                    'button_bg': '#f0f0f0',
                    'button_fg': '#000000',
                    'insert_bg': '#000000',
                    'disabled_fg': '#808080',
                }
            
            # Set semantic colors based on theme
            if self.is_dark_mode:
                self.semantic_colors = {
                    'error': '#f14c4c',
                    'warning': '#ff8c00',
                    'success': '#4ec9b0',
                    'todo_pending': '#f14c4c',
                    'todo_completed': '#808080',
                    'todo_progress': '#ff8c00',
                    'hashtag': '#569cd6',
                    'bullet': '#cccccc',
                }
            else:
                self.semantic_colors = {
                    'error': '#d73a49',
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
    
    def _is_dark_color(self, color):
        """Check if a color is dark (for dark mode detection)"""
        try:
            # First try platform-specific dark mode detection
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                try:
                    import subprocess
                    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                          capture_output=True, text=True)
                    return result.returncode == 0 and 'Dark' in result.stdout
                except:
                    pass
            elif system == "Windows":
                try:
                    import winreg
                    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
                    value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
                    winreg.CloseKey(registry_key)
                    return value == 0
                except:
                    pass
            elif system == "Linux":
                try:
                    import subprocess
                    # Try GNOME
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'dark' in result.stdout.lower()
                except:
                    pass
            
            # Fallback to color analysis
            if color.startswith('#'):
                # Parse hex color
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                # Calculate luminance
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance < 0.5
            else:
                # For named colors, use simple heuristics
                dark_colors = ['black', 'darkgray', 'darkgrey', 'gray25', 'grey25']
                return color.lower() in dark_colors
        except:
            return False  # Default to light mode if detection fails
    
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
            font=self.system_theme.get_system_font('default'),
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
        
        # Import ttk for TreeView
        from tkinter import ttk
        
        # Create TreeView for hierarchical file structure
        self.file_tree = ttk.Treeview(
            list_frame,
            show='tree',  # Only show the tree column, not headers
            selectmode='extended'
        )
        
        # Configure TreeView styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',
            background=self.system_theme.get_color('bg'),
            foreground=self.system_theme.get_color('fg'),
            fieldbackground=self.system_theme.get_color('bg'),
            borderwidth=0,
            relief='flat'
        )
        style.configure('Treeview.Heading',
            background=self.system_theme.get_color('bg'),
            foreground=self.system_theme.get_color('fg')
        )
        
        # Configure selection colors
        style.map('Treeview', 
            background=[('selected', self.system_theme.get_color('select_bg'))],
            foreground=[('selected', 'white')]
        )
        
        # Custom scrollbar for TreeView
        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.file_tree.yview,
            bg=self.system_theme.get_color('bg'),
            troughcolor=self.system_theme.get_color('bg'),
            activebackground=self.system_theme.get_color('select_bg'),
            width=8
        )
        self.file_tree.config(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # TreeView event bindings
        self.file_tree.bind('<Double-Button-1>', self.on_treeview_double_click)
        self.file_tree.bind('<Return>', self.on_treeview_double_click)
        self.file_tree.bind('<<TreeviewOpen>>', self.on_folder_expand)
        self.file_tree.bind('<<TreeviewClose>>', self.on_folder_collapse)
        
        # CRITICAL FIX: Disable TreeView class mouse wheel bindings that intercept ALL events
        self.file_tree.bind_class("Treeview", "<MouseWheel>", "")
        self.file_tree.bind_class("Treeview", "<Button-4>", "")  
        self.file_tree.bind_class("Treeview", "<Button-5>", "")
        
        # Add back TreeView-specific mouse wheel scrolling (only when over TreeView)
        def treeview_scroll(event):
            # Only scroll if TreeView actually needs it (has many items)
            if len(self.file_tree.get_children()) > 10:
                # Standard TreeView scrolling
                if hasattr(event, 'delta') and event.delta:
                    delta = int(-1 * (event.delta / 120))
                    self.file_tree.yview_scroll(delta, "units")
                elif hasattr(event, 'num'):
                    if event.num == 4:
                        self.file_tree.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.file_tree.yview_scroll(1, "units")
            return "break"
        
        # Bind TreeView-specific scrolling only to this TreeView instance  
        self.file_tree.bind("<MouseWheel>", treeview_scroll)
        self.file_tree.bind("<Button-4>", treeview_scroll)
        self.file_tree.bind("<Button-5>", treeview_scroll)
        
        # Setup context menu
        self.setup_context_menu()
        
        self.refresh_files()
    
    def change_directory(self):
        new_dir = filedialog.askdirectory(initialdir=self.current_dir, title="Select Directory")
        if new_dir:
            self.current_dir = Path(new_dir)
            self.path_label.config(text=str(self.current_dir))
            self.refresh_files()
    
    def refresh_files(self):
        """Refresh the TreeView with hierarchical folder structure"""
        # Clear existing tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            # Add parent directory navigation if not at root
            if self.current_dir.parent != self.current_dir:
                self.file_tree.insert('', 'end', 
                    text='↑ ..',
                    values=('parent',),
                    tags=('parent',)
                )
            
            # Populate current directory
            self._populate_directory('', self.current_dir, is_root=True)
                
        except PermissionError:
            self.file_tree.insert('', 'end', text='❌ Access denied', tags=('error',))
    
    def _populate_directory(self, parent_id, directory_path, is_root=False):
        """Populate a directory in the TreeView with folders and files"""
        try:
            items = list(directory_path.iterdir())
            
            # Separate directories and files
            directories = [d for d in items if d.is_dir() and not d.name.startswith('.')]
            files = [f for f in items if f.is_file() and not f.name.startswith('.')]
            
            # Sort both lists
            directories.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            # Add directories first (with expand/collapse capability)
            for directory in directories:
                dir_id = self.file_tree.insert(parent_id, 'end',
                    text=f'📁 {directory.name}',
                    values=('directory', str(directory)),
                    tags=('directory',)
                )
                
                # Add a dummy child to make it expandable
                # This will be replaced with real content when expanded
                self.file_tree.insert(dir_id, 'end', text='Loading...')
            
            # Add files
            for file in files:
                icon = self.get_file_icon(file)
                display_name = self.get_display_name(file)
                self.file_tree.insert(parent_id, 'end',
                    text=f'{icon} {display_name}',
                    values=('file', str(file)),
                    tags=('file',)
                )
                
        except PermissionError:
            self.file_tree.insert(parent_id, 'end', 
                text='❌ Access denied',
                tags=('error',)
            )

    def get_file_icon(self, file_path):
        """Get appropriate icon for file type"""
        suffix = file_path.suffix.lower()
        
        # File type icon mapping
        icon_map = {
            # LogLog files
            '.log': '📝', '.loglog': '📝',
            
            # Programming files
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.html': '🌐', '.css': '🎨',
            '.cpp': '⚙️', '.c': '⚙️', '.java': '☕', '.cs': '🔷', '.php': '🟣',
            '.go': '🐹', '.rust': '🦀', '.rb': '💎', '.swift': '🐦',
            
            # Data files
            '.json': '📋', '.xml': '📄', '.yaml': '📋', '.yml': '📋',
            '.csv': '📊', '.sql': '🗂️', '.db': '🗃️',
            
            # Documents
            '.txt': '📄', '.md': '📖', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.odt': '📘', '.rtf': '📄',
            
            # Images
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.bmp': '🖼️', '.tiff': '🖼️', '.ico': '🖼️',
            
            # Archives
            '.zip': '📦', '.tar': '📦', '.gz': '📦', '.rar': '📦', '.7z': '📦',
            
            # Config files
            '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️', '.toml': '⚙️',
            '.properties': '⚙️',
            
            # Shell/scripts
            '.sh': '⚡', '.bat': '⚡', '.ps1': '⚡',
            
            # Media
            '.mp3': '🎵', '.wav': '🎵', '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬',
            
            # Special files
            '.gitignore': '🚫', '.gitattributes': '🔧', '.dockerfile': '🐳',
            '.makefile': '🔨', 'makefile': '🔨',
        }
        
        # Check if it's a special filename (no extension)
        filename = file_path.name.lower()
        if filename in ['makefile', 'dockerfile', 'readme']:
            return icon_map.get(filename, '📄')
        
        return icon_map.get(suffix, '📄')  # Default to document icon
    
    def get_display_name(self, file_path):
        """Get display name with optional styling for LogLog files"""
        name = file_path.name
        
        # Highlight LogLog files with bold styling (if supported)
        if file_path.suffix.lower() in ['.log', '.loglog']:
            return name  # Could add styling here if needed
        
        return name

    def on_folder_expand(self, event):
        """Handle folder expansion in TreeView"""
        item = self.file_tree.focus()
        if not item:
            return
        
        values = self.file_tree.item(item)['values']
        if len(values) >= 2 and values[0] == 'directory':
            directory_path = Path(values[1])
            
            # Remove dummy "Loading..." child
            children = self.file_tree.get_children(item)
            for child in children:
                if self.file_tree.item(child)['text'] == 'Loading...':
                    self.file_tree.delete(child)
            
            # Populate with actual directory contents
            self._populate_directory(item, directory_path)

    def on_folder_collapse(self, event):
        """Handle folder collapse in TreeView"""
        # Optional: Clear children to save memory (lazy loading)
        item = self.file_tree.focus()
        if not item:
            return
        
        # Could implement lazy loading by removing children and adding dummy back
        # For now, keep the children loaded for better UX

    def on_treeview_double_click(self, event):
        """Handle double-click on TreeView items"""
        item = self.file_tree.focus()
        if not item:
            return
        
        values = self.file_tree.item(item)['values']
        
        if not values:
            return
        
        if values[0] == 'parent':
            # Navigate to parent directory
            self.current_dir = self.current_dir.parent
            self.path_label.config(text=str(self.current_dir))
            self.refresh_files()
        elif values[0] == 'directory' and len(values) >= 2:
            # Navigate into directory
            new_dir = Path(values[1])
            if new_dir.is_dir():
                self.current_dir = new_dir
                self.path_label.config(text=str(self.current_dir))
                self.refresh_files()
        elif values[0] == 'file' and len(values) >= 2:
            # Open file
            file_path = Path(values[1])
            if self.on_file_select and file_path.exists():
                self.on_file_select(str(file_path))
    

    def setup_context_menu(self):
        """Setup right-click context menu for file tree items"""
        self.context_menu = tk.Menu(self, tearoff=0, bg=self.system_theme.get_color('bg'), 
                                  fg=self.system_theme.get_color('fg'))
        
        # File operations
        self.context_menu.add_command(label="Open", command=self.context_open_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="New File...", command=self.context_new_file)
        self.context_menu.add_command(label="New Folder...", command=self.context_new_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename...", command=self.context_rename)
        self.context_menu.add_command(label="Delete", command=self.context_delete)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Reveal in Explorer", command=self.context_reveal)
        
        # Bind right-click to show context menu
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        self.file_tree.bind("<Control-Button-1>", self.show_context_menu)  # Mac compatibility

    def show_context_menu(self, event):
        """Show context menu at mouse position"""
        # Find and select the item under cursor
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.file_tree.focus(item)
        
        # Show context menu
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def get_selected_item_path(self):
        """Get the path of the currently selected item"""
        selection = self.file_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        values = self.file_tree.item(item)['values']
        
        if not values:
            return None
        
        if values[0] == 'parent':
            return None
        elif values[0] == 'directory' and len(values) >= 2:
            return Path(values[1])
        elif values[0] == 'file' and len(values) >= 2:
            return Path(values[1])
        
        return None

    def context_open_file(self):
        """Open selected file"""
        path = self.get_selected_item_path()
        if path and path.is_file() and self.on_file_select:
            self.on_file_select(str(path))

    def context_new_file(self):
        """Create new LogLog file"""
        import tkinter.simpledialog as simpledialog
        filename = simpledialog.askstring("New File", "Enter filename (without extension):")
        if filename:
            new_file_path = self.current_dir / f"{filename}.log"
            try:
                new_file_path.write_text("Sample LogLog Tree\n\tWelcome to LogLog!\n\tStart organizing your thoughts here.\n")
                self.refresh_files()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not create file: {e}")

    def context_new_folder(self):
        """Create new folder"""
        import tkinter.simpledialog as simpledialog
        foldername = simpledialog.askstring("New Folder", "Enter folder name:")
        if foldername:
            new_folder_path = self.current_dir / foldername
            try:
                new_folder_path.mkdir(exist_ok=True)
                self.refresh_files()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not create folder: {e}")

    def context_rename(self):
        """Rename selected file/folder"""
        path = self.get_selected_item_path()
        if not path:
            return
        
        import tkinter.simpledialog as simpledialog
        current_name = path.name
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=current_name)
        if new_name and new_name != current_name:
            try:
                new_path = path.parent / new_name
                path.rename(new_path)
                self.refresh_files()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not rename: {e}")

    def context_delete(self):
        """Delete selected file/folder"""
        path = self.get_selected_item_path()
        if not path:
            return
        
        import tkinter.messagebox as messagebox
        result = messagebox.askyesno("Delete", f"Are you sure you want to delete '{path.name}'?")
        if result:
            try:
                if path.is_file():
                    path.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")

    def context_reveal(self):
        """Open file/folder location in system file manager"""
        path = self.get_selected_item_path()
        if not path:
            path = self.current_dir
        
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                subprocess.run(["explorer", str(path.parent)], check=True)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path.parent)], check=True) 
            else:  # Linux
                subprocess.run(["xdg-open", str(path.parent)], check=True)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not reveal in explorer: {e}")

class ModernSyntaxHighlighter:
    """Enhanced syntax highlighter with modern styling"""
    
    def __init__(self, text_widget, system_theme):
        self.text_widget = text_widget
        self.system_theme = system_theme
        self.setup_tags()
    
    def setup_tags(self):
        # Configure modern text styling using system fonts
        system_font = self.system_theme.get_system_font('monospace')
        bold_font = (*system_font[:2], 'bold')
        
        self.text_widget.tag_config('todo_pending', 
            foreground=self.system_theme.get_color('todo_pending'), 
            font=bold_font)
        
        self.text_widget.tag_config('todo_completed', 
            foreground=self.system_theme.get_color('todo_completed'), 
            overstrike=True,
            font=system_font)
        
        self.text_widget.tag_config('todo_in_progress', 
            foreground=self.system_theme.get_color('todo_progress'), 
            font=bold_font)
        
        self.text_widget.tag_config('hashtag', 
            foreground=self.system_theme.get_color('hashtag'), 
            font=bold_font)
        
        self.text_widget.tag_config('bullet', 
            foreground=self.system_theme.get_color('bullet'),
            font=bold_font)
        
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

class TabBar(tk.Frame):
    """VS Code-style tab bar for multiple files"""
    
    def __init__(self, parent, system_theme, on_tab_select=None, on_tab_close=None, on_new_tab=None):
        super().__init__(parent, bg=system_theme.get_color('bg'), height=35)
        self.system_theme = system_theme
        self.on_tab_select = on_tab_select
        self.on_tab_close = on_tab_close
        self.on_new_tab = on_new_tab
        self.pack_propagate(False)
        
        self.tabs = {}  # file_path -> tab_frame
        self.active_tab = None
        
        # Scroll frame for tabs
        self.scroll_frame = tk.Frame(self, bg=system_theme.get_color('bg'))
        self.scroll_frame.pack(side='left', fill='both', expand=True)
        
        # New tab button
        self.new_tab_button = tk.Label(
            self,
            text="+",
            font=system_theme.get_system_font('default'),
            fg=system_theme.get_color('disabled_fg'),
            bg=system_theme.get_color('bg'),
            width=3,
            cursor="hand2"
        )
        self.new_tab_button.pack(side='right', pady=5, padx=5)
        if self.on_new_tab:
            self.new_tab_button.bind('<Button-1>', lambda e: self.on_new_tab())
    
    def add_tab(self, file_path, is_temporary=False):
        """Add a new tab"""
        if file_path in self.tabs:
            self.select_tab(file_path)
            return
        
        filename = os.path.basename(file_path) if file_path else "New File"
        
        # Create tab frame
        tab_frame = tk.Frame(self.scroll_frame, bg=self.system_theme.get_color('bg'))
        tab_frame.pack(side='left', fill='y', padx=1)
        
        # Tab label - make it more visible for debugging
        font_style = 'italic' if is_temporary else 'normal'
        tab_label = tk.Label(
            tab_frame,
            text=filename,
            font=(self.system_theme.get_system_font('default')[0], 
                  self.system_theme.get_system_font('default')[1], 
                  font_style),
            fg=self.system_theme.get_color('fg'),  # Use brighter foreground
            bg=self.system_theme.get_color('select_bg'),  # Use distinct background
            padx=12,
            pady=8,
            cursor="hand2",
            relief='raised',  # Add border for visibility
            bd=1
        )
        tab_label.pack(side='left')
        
        # Close button
        close_button = tk.Label(
            tab_frame,
            text="×",
            font=self.system_theme.get_system_font('default'),
            fg=self.system_theme.get_color('disabled_fg'),
            bg=self.system_theme.get_color('bg'),
            width=2,
            cursor="hand2"
        )
        close_button.pack(side='right')
        
        # Bind events
        def select_handler(e):
            self.select_tab(file_path)
            if self.on_tab_select:
                self.on_tab_select(file_path)
        
        def close_handler(e):
            self.close_tab(file_path)
            if self.on_tab_close:
                self.on_tab_close(file_path)
        
        tab_label.bind('<Button-1>', select_handler)
        tab_label.bind('<Button-2>', close_handler)  # Middle-click to close
        tab_label.bind('<Double-Button-1>', lambda e: self.make_tab_permanent(file_path))  # Double-click to pin
        close_button.bind('<Button-1>', close_handler)
        
        self.tabs[file_path] = {
            'frame': tab_frame,
            'label': tab_label,
            'close': close_button,
            'is_temporary': is_temporary
        }
        
        self.select_tab(file_path)
    
    def select_tab(self, file_path):
        """Select a tab and update visual state"""
        # Deselect previous tab
        if self.active_tab and self.active_tab in self.tabs:
            tab = self.tabs[self.active_tab]
            tab['label'].config(
                bg=self.system_theme.get_color('bg'),
                fg=self.system_theme.get_color('disabled_fg')
            )
            tab['close'].config(
                bg=self.system_theme.get_color('bg'),
                fg=self.system_theme.get_color('disabled_fg')
            )
        
        # Select new tab
        if file_path in self.tabs:
            tab = self.tabs[file_path]
            tab['label'].config(
                bg=self.system_theme.get_color('select_bg'),
                fg=self.system_theme.get_color('fg')
            )
            tab['close'].config(
                bg=self.system_theme.get_color('select_bg'),
                fg=self.system_theme.get_color('fg')
            )
            self.active_tab = file_path
            
            # Convert temporary tab to permanent if it becomes active
            if tab['is_temporary'] and file_path:
                tab['is_temporary'] = False
                tab['label'].config(font=self.system_theme.get_system_font('default'))
    
    def close_tab(self, file_path):
        """Close a tab"""
        if file_path in self.tabs:
            self.tabs[file_path]['frame'].destroy()
            del self.tabs[file_path]
            
            # Select another tab if this was active
            if self.active_tab == file_path:
                self.active_tab = None
                if self.tabs:
                    # Select the last tab
                    last_tab = list(self.tabs.keys())[-1]
                    self.select_tab(last_tab)
                    if self.on_tab_select:
                        self.on_tab_select(last_tab)
    
    def update_tab_modified(self, file_path, is_modified):
        """Update tab to show modified state"""
        if file_path in self.tabs:
            tab = self.tabs[file_path]
            filename = os.path.basename(file_path) if file_path else "New File"
            if is_modified:
                filename = "● " + filename
            tab['label'].config(text=filename)
    
    def get_active_tab(self):
        """Get the currently active tab"""
        return self.active_tab
    
    def make_tab_permanent(self, file_path):
        """Convert temporary tab to permanent (double-click behavior)"""
        if file_path in self.tabs:
            tab = self.tabs[file_path]
            if tab['is_temporary']:
                tab['is_temporary'] = False
                # Change from italic to normal font
                tab['label'].config(font=self.system_theme.get_system_font('default'))
                # Update visual indication
                filename = os.path.basename(file_path) if file_path else "New File"
                tab['label'].config(text=filename)  # Remove italic styling

class ModernLogLogGUI:
    """Main GUI class with system theme integration"""
    
    def __init__(self):
        self.settings = ModernSettings()
        self.current_file = None
        self.file_modified = False
        self.auto_save_timer = None
        
        # Tab system
        self.tabs = {}  # file_path -> tab_data
        self.active_tab = None
        self.tab_counter = 0
        
        self.setup_main_window()
        # Initialize system theme after window is created
        self.system_theme = SystemTheme(self.root)
        self.apply_system_theme()
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        self.setup_theme()
        
        self.update_recent_files_menu()
        
        # Create an initial tab so the tab bar is visible
        self.new_file()
        
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
        
        # Tab bar
        self.tab_bar = TabBar(
            editor_container,
            self.system_theme,
            on_tab_select=self.on_tab_select,
            on_tab_close=self.on_tab_close,
            on_new_tab=self.new_file
        )
        self.tab_bar.pack(fill='x', pady=(10, 0))
        
        # Editor container for content
        self.editor_content_frame = tk.Frame(editor_container, bg=self.system_theme.get_color('bg'))
        self.editor_content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # Create the tree renderer in the content frame
        self.tree_renderer = TreeRenderer(
            self.editor_content_frame,
            self.system_theme
        )
        self.tree_renderer.pack(fill='both', expand=True)
        
        # Connect tree renderer to GUI for change notifications
        self.tree_renderer.gui = self
        
        # Ensure tree renderer gets focus when content is shown
        self.editor_content_frame.bind("<FocusIn>", lambda e: self.tree_renderer.focus_set())
        self.editor_content_frame.bind("<Button-1>", lambda e: self.tree_renderer.focus_set())
    
    def on_tab_select(self, file_path):
        """Handle tab selection with optimized performance"""
        if file_path != self.current_file:
            # Save current tab state efficiently
            if self.current_file and self.current_file in self.tabs:
                self._save_tab_state(self.current_file)
            
            # Load new tab with fast switching
            self.current_file = file_path
            if file_path in self.tabs:
                self._load_tab_state(file_path)
                
                # Update title
                filename = os.path.basename(file_path)
                self.root.title(f"LogLog - {filename}")
                self.file_modified = self.tabs[file_path].get('modified', False)
    
    def _save_tab_state(self, file_path):
        """Efficiently save tab state without full tree serialization"""
        if file_path in self.tabs:
            # Cache the current tree content
            self.tabs[file_path]['tree_state'] = self._get_clean_tree_content()
            
            # Cache selection and focus state for restoration
            if hasattr(self.tree_renderer.tree, 'selection'):
                focused_node = self.tree_renderer.tree.selection.focused_node
                if focused_node:
                    self.tabs[file_path]['focused_node_id'] = focused_node.id
                
                selected_nodes = self.tree_renderer.tree.selection.selected_nodes
                if selected_nodes:
                    self.tabs[file_path]['selected_node_ids'] = [n.id for n in selected_nodes]
    
    def _load_tab_state(self, file_path):
        """Ultra-fast tab loading with viewport switching"""
        tab_data = self.tabs[file_path]
        
        # Get content for the tab
        tree_state = tab_data.get('tree_state')
        if tree_state:
            content = tree_state
        else:
            # Load from file (only if it exists on disk)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # New file that hasn't been saved yet
                content = ""
        
        # Instant viewport switch - no rendering delay
        self.tree_renderer.switch_to_file(file_path, content)
        
        # Restore focus and selection state (optional, can be skipped for speed)
        if 'focused_node_id' in tab_data or 'selected_node_ids' in tab_data:
            self.root.after_idle(lambda: self._restore_tab_selection(tab_data))
    
    def _restore_tab_selection(self, tab_data):
        """Restore selection and focus state for a tab"""
        try:
            # Restore focused node
            if 'focused_node_id' in tab_data:
                focused_id = tab_data['focused_node_id']
                all_nodes = self.tree_renderer.tree.get_all_nodes()
                for node in all_nodes:
                    if node.id == focused_id:
                        self.tree_renderer.set_focus(node)
                        break
            
            # Restore selected nodes
            if 'selected_node_ids' in tab_data:
                selected_ids = set(tab_data['selected_node_ids'])
                all_nodes = self.tree_renderer.tree.get_all_nodes()
                for node in all_nodes:
                    if node.id in selected_ids:
                        self.tree_renderer.tree.selection.add_to_selection(node)
                
                self.tree_renderer.update_selection_display()
        except Exception:
            # If restoration fails, just continue without selection
            pass
    
    def on_tab_close(self, file_path):
        """Handle tab close"""
        if file_path in self.tabs:
            tab_data = self.tabs[file_path]
            
            # Check for unsaved changes
            if tab_data.get('modified', False):
                response = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    f"Save changes to {os.path.basename(file_path)}?"
                )
                if response is True:  # Save
                    self.save_tab(file_path)
                elif response is None:  # Cancel
                    return False
            
            # Remove tab
            del self.tabs[file_path]
            
            # Remove viewport and handle tab switching
            self.tree_renderer.remove_viewport(file_path)
            
            # If this was the current file, switch to another tab or clear
            if file_path == self.current_file:
                self.current_file = None
                if self.tabs:
                    # Switch to last tab
                    last_tab = list(self.tabs.keys())[-1]
                    self.on_tab_select(last_tab)
                else:
                    # No tabs left - switch to empty viewport
                    self.tree_renderer.switch_to_file("", "")
                    self.root.title("LogLog")
                    self.file_modified = False
            
            return True
    
    def save_tab(self, file_path):
        """Save a specific tab"""
        if file_path in self.tabs:
            # Get content from tree
            content = self.tabs[file_path].get('tree_state', '')
            if file_path == self.current_file:
                content = self.tree_renderer.tree.serialize()
            
            # Write to file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Update tab state
                self.tabs[file_path]['modified'] = False
                self.tab_bar.update_tab_modified(file_path, False)
                
                if file_path == self.current_file:
                    self.file_modified = False
                    self.update_title()
                
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        
        return False
        
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
            # Tab management shortcuts
            ('<Control-t>', self.new_tab),
            ('<Control-w>', self.close_current_tab),
            ('<Control-Tab>', self.next_tab),
            ('<Control-Shift-Tab>', self.prev_tab),
            # Theme toggling removed - using system theme
            ('<Control-plus>', self.zoom_in),
            ('<Control-minus>', self.zoom_out),
            ('<F11>', self.toggle_fullscreen)
        ]
        
        for binding, command in bindings:
            self.root.bind(binding, lambda e, cmd=command: cmd())
        
        # Add navigation key bindings that delegate to TreeRenderer when appropriate
        def handle_nav_key(event):
            # Only handle navigation if not in an entry widget
            focus_widget = self.root.focus_get()
            if focus_widget and focus_widget.winfo_class() in ['Entry', 'Text']:
                return None  # Let the widget handle it
            
            # Delegate to TreeRenderer
            return self.tree_renderer.handle_keyboard_event(event)
        
        nav_bindings = [
            ('<Up>', handle_nav_key),
            ('<Down>', handle_nav_key), 
            ('<Left>', handle_nav_key),
            ('<Right>', handle_nav_key),
            ('<Return>', handle_nav_key),
            ('<space>', handle_nav_key),
            ('<Shift-Up>', handle_nav_key),
            ('<Shift-Down>', handle_nav_key),
            ('<Shift-Left>', handle_nav_key),
            ('<Shift-Right>', handle_nav_key)
        ]
        
        for binding, handler in nav_bindings:
            self.root.bind(binding, handler)
            
        # Note: Removed global mouse wheel handlers to prevent event multiplication
    
    def new_tab(self):
        """Create a new tab"""
        self.new_file()
    
    def close_current_tab(self):
        """Close the current tab"""
        if self.current_file:
            self.tab_bar.close_tab(self.current_file)
    
    def next_tab(self):
        """Switch to next tab"""
        tab_keys = list(self.tabs.keys())
        if len(tab_keys) <= 1:
            return
            
        current_index = tab_keys.index(self.current_file) if self.current_file in tab_keys else 0
        next_index = (current_index + 1) % len(tab_keys)
        next_file = tab_keys[next_index]
        
        self.tab_bar.select_tab(next_file)
        self.on_tab_select(next_file)
    
    def prev_tab(self):
        """Switch to previous tab"""
        tab_keys = list(self.tabs.keys())
        if len(tab_keys) <= 1:
            return
            
        current_index = tab_keys.index(self.current_file) if self.current_file in tab_keys else 0
        prev_index = (current_index - 1) % len(tab_keys)
        prev_file = tab_keys[prev_index]
        
        self.tab_bar.select_tab(prev_file)
        self.on_tab_select(prev_file)
        
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
        """Create a new file in a new tab"""
        # Generate unique name for new file
        new_file_name = f"Untitled-{self.tab_counter}.log"
        self.tab_counter += 1
        
        # Create new tab
        self.tabs[new_file_name] = {
            'tree_state': "",
            'modified': False,
            'is_temporary': False
        }
        
        # Add tab to tab bar
        self.tab_bar.add_tab(new_file_name, False)
        
        # Set as current file and switch to new viewport
        self.current_file = new_file_name
        self.file_modified = False
        
        # Use the new viewport system to create an empty file
        self.tree_renderer.switch_to_file(new_file_name, "")
        
        # Save the empty state
        self.tabs[new_file_name]['tree_state'] = ""
        
        self.update_title()
        self.update_status("📄 New file created")
    
    def load_file(self, file_path: str, is_temporary=False):
        """Load file into a new tab or switch to existing tab"""
        try:
            # Check if file is already open in a tab
            if file_path in self.tabs:
                # Switch to existing tab
                self.tab_bar.select_tab(file_path)
                self.on_tab_select(file_path)
                return
            
            # Create new tab
            self.tabs[file_path] = {
                'tree_state': None,
                'modified': False,
                'is_temporary': is_temporary
            }
            
            # Add tab to tab bar
            self.tab_bar.add_tab(file_path, is_temporary)
            
            # Load file content by switching to the file (this creates viewport and loads content)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.tree_renderer.switch_to_file(file_path, content)
                self.current_file = file_path
                self.file_modified = False
                
                # Save the original file content as the tab's tree state (not serialized)
                self.tabs[file_path]['tree_state'] = content
                
                self.update_title()
                self.add_to_recent_files(file_path)
                self.update_status(f"📂 Opened {os.path.basename(file_path)}")
                
                # Focus on content area after loading
                self.root.after_idle(self._focus_on_content)
            except Exception as load_error:
                raise Exception(f"Failed to load file: {load_error}")
            
        except Exception as e:
            # Clean up failed tab
            if file_path in self.tabs:
                del self.tabs[file_path]
                self.tab_bar.close_tab(file_path)
            self.show_modern_error("Failed to open file", str(e))
    
    def _focus_on_content(self):
        """Set focus to the content area instead of the file tree"""
        try:
            # Focus on tree renderer
            self.tree_renderer.focus_set()
            
            # If there's an active viewport, focus on it and select first node
            if self.tree_renderer.active_viewport:
                self.tree_renderer.active_viewport.focus_set()
                
                # Set initial focus to first visible node if none selected
                if not self.tree_renderer.active_viewport.tree.selection.focused_node:
                    visible_nodes = self.tree_renderer.active_viewport.tree.get_visible_nodes()
                    if visible_nodes:
                        self.tree_renderer.set_focus(visible_nodes[0])
        except Exception as e:
            pass  # Silently handle focus issues
    
    def mark_file_modified(self):
        """Mark the current file as modified"""
        if self.current_file:
            self.file_modified = True
            if self.current_file in self.tabs:
                self.tabs[self.current_file]['modified'] = True
                self.tab_bar.update_tab_modified(self.current_file, True)
    
    def save_file(self):
        if self.current_file:
            try:
                # Save using tree renderer
                if self.tree_renderer.save_to_file(self.current_file):
                    self.file_modified = False
                    
                    # Update tab state
                    if self.current_file in self.tabs:
                        self.tabs[self.current_file]['modified'] = False
                        self.tab_bar.update_tab_modified(self.current_file, False)
                    
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
        
        if self.file_modified:
            title = "● " + title
        
        self.root.title(title)
    
    def update_status(self, message: str):
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.status_label.config(text=message)
            self.root.after(3000, lambda: self.status_bar.status_label.config(text="Ready"))
    
    def update_cursor_position(self, event=None):
        # For tree renderer, show focused node info
        focused_node = self.tree_renderer.tree.selection.focused_node
        if hasattr(self, 'status_bar') and self.status_bar:
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
            # Update tab to show modified state
            if self.current_file and self.current_file in self.tabs:
                self.tabs[self.current_file]['modified'] = True
                self.tab_bar.update_tab_modified(self.current_file, True)
            self.update_title()
        
        # Save current tree state to the active tab
        if self.current_file and self.current_file in self.tabs:
            self.tabs[self.current_file]['tree_state'] = self._get_clean_tree_content()
        
        # Update cursor position display
        self.update_cursor_position()
        
        if self.settings.get('auto_save'):
            self.schedule_auto_save()
    
    def _get_clean_tree_content(self):
        """Get tree content without the empty root node that serialize() adds"""
        try:
            # Use the new viewport system to get content
            content = self.tree_renderer.get_content()
            if not content:
                return ""
            
            serialized = content
            
            # If it starts with "- \n    " (empty root + indent), remove that prefix
            if serialized.startswith('- \n    '):
                # Remove the empty root line and reduce indentation
                lines = serialized.split('\n')
                clean_lines = []
                for line in lines[1:]:  # Skip first empty root line
                    if line.startswith('    '):  # Remove one level of indentation
                        clean_lines.append(line[4:])
                    else:
                        clean_lines.append(line)
                return '\n'.join(clean_lines)
            else:
                return serialized
        except:
            # Fallback to original serialization
            return self.tree_renderer.tree.serialize()
    
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
        search_dialog.geometry("450x200")
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
        
        return search_results if search_results else []
    
    def tree_search_enhanced(self, term: str, scoped=False, case_sensitive=False, use_regex=False):
        """Enhanced search with additional options"""
        try:
            if scoped:
                # Search within selected nodes
                selected_nodes = self.tree_renderer.tree.selection.get_selected_nodes()
                focused_node = self.tree_renderer.tree.selection.focused_node
                
                if not selected_nodes and focused_node:
                    selected_nodes = [focused_node]
                
                if not selected_nodes:
                    self.update_status("No nodes selected for scoped search")
                    return []
                
                search_results = []
                for node in selected_nodes:
                    if use_regex:
                        results = node.search_regex(term, case_sensitive=case_sensitive)
                    else:
                        results = node.search(term, case_sensitive=case_sensitive)
                    search_results.extend(results)
            else:
                # Simple search across entire tree
                if use_regex:
                    search_results = self.tree_renderer.tree.search_regex(term, case_sensitive=case_sensitive)
                else:
                    search_results = self.tree_renderer.tree.search(term, case_sensitive=case_sensitive)
            
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
            
            return search_results
            
        except Exception as e:
            self.update_status(f"Search error: {e}")
            return []
    
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
        """Undo last operation on tree"""
        if self.tree_renderer and self.tree_renderer.active_viewport:
            viewport = self.tree_renderer.active_viewport
            if hasattr(viewport, 'undo_action'):
                success = viewport.undo_action()
                if success:
                    self.mark_file_modified()
                    self.update_status("↶ Undo successful")
                else:
                    self.update_status("Nothing to undo")
    
    def redo(self):
        """Redo last undone operation on tree"""
        if self.tree_renderer and self.tree_renderer.active_viewport:
            viewport = self.tree_renderer.active_viewport
            if hasattr(viewport, 'redo_action'):
                success = viewport.redo_action()
                if success:
                    self.mark_file_modified()
                    self.update_status("↷ Redo successful")
                else:
                    self.update_status("Nothing to redo")
    
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

# Compatibility aliases for backward compatibility
LogLogGUI = ModernLogLogGUI
LogLogSyntaxHighlighter = ModernSyntaxHighlighter

if __name__ == '__main__':
    main()