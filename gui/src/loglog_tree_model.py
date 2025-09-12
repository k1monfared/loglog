#!/usr/bin/env python3
"""
LogLog Tree Model - Platform Agnostic Core
A tree-first architecture where all operations happen on tree nodes,
and text serialization only occurs during save operations.
"""

import re
import uuid
from typing import List, Set, Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass


class TodoStatus(Enum):
    """TODO status enumeration"""
    PENDING = "pending"      # []
    PROGRESS = "progress"    # [-] 
    COMPLETE = "complete"    # [x]
    UNKNOWN = "unknown"      # [?]


class NodeType(Enum):
    """Node type enumeration"""
    ROOT = "root"
    ITEM = "item"
    TODO = "todo"


@dataclass
class TreeChangeEvent:
    """Event fired when tree structure changes"""
    event_type: str  # "node_added", "node_removed", "node_modified", "selection_changed"
    node: 'LogLogNode'
    old_parent: Optional['LogLogNode'] = None
    new_parent: Optional['LogLogNode'] = None
    old_value: Any = None
    new_value: Any = None


class LogLogNode:
    """
    Core LogLog node with all business logic.
    Platform-agnostic - contains no UI-specific code.
    """
    
    def __init__(self, content: str = "", node_type: NodeType = NodeType.ITEM):
        # Core content
        self.id = str(uuid.uuid4())
        self.content = content.strip()
        self.node_type = node_type
        
        # TODO-specific
        self.todo_status: Optional[TodoStatus] = None
        self._parse_todo_status()
        
        # Hierarchy
        self.children: List['LogLogNode'] = []
        self.parent: Optional['LogLogNode'] = None
        
        # UI State (separate from content)
        self.is_folded = False
        self.is_selected = False
        self.is_focused = False
        self.is_editing = False
        
        # Extracted metadata
        self.hashtags: Set[str] = set()
        self._extract_hashtags()
        
        # Observers for change notifications
        self._observers: List[Callable] = []
    
    def _parse_todo_status(self):
        """Parse TODO status from content"""
        content = self.content.strip()
        if content.startswith('[]'):
            self.node_type = NodeType.TODO
            self.todo_status = TodoStatus.PENDING
            self.content = content[2:].strip()
        elif content.startswith('[x]'):
            self.node_type = NodeType.TODO  
            self.todo_status = TodoStatus.COMPLETE
            self.content = content[3:].strip()
        elif content.startswith('[-]'):
            self.node_type = NodeType.TODO
            self.todo_status = TodoStatus.PROGRESS
            self.content = content[3:].strip()
        elif content.startswith('[?]'):
            self.node_type = NodeType.TODO
            self.todo_status = TodoStatus.UNKNOWN
            self.content = content[3:].strip()
        else:
            # Only set to ITEM if not already ROOT
            if self.node_type != NodeType.ROOT:
                self.node_type = NodeType.ITEM
            self.todo_status = None
    
    def _extract_hashtags(self):
        """Extract hashtags from content"""
        self.hashtags = set(re.findall(r'#\w+', self.content))
    
    def add_observer(self, observer: Callable):
        """Add change observer"""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable):
        """Remove change observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event: TreeChangeEvent):
        """Notify all observers of changes"""
        for observer in self._observers:
            try:
                observer(event)
            except Exception as e:
                print(f"Observer error: {e}")
    
    # Core Tree Operations
    
    def add_child(self, child_node: 'LogLogNode', position: Optional[int] = None):
        """Add child node at specific position"""
        if child_node.parent:
            child_node.remove_from_parent()
        
        if position is None:
            position = len(self.children)
        
        self.children.insert(position, child_node)
        child_node.parent = self
        
        # Propagate observers
        child_node._observers = self._observers
        
        self._notify_observers(TreeChangeEvent(
            "node_added", child_node, None, self
        ))
    
    def remove_from_parent(self):
        """Remove this node from its parent"""
        if self.parent:
            old_parent = self.parent
            self.parent.children.remove(self)
            self.parent = None
            
            self._notify_observers(TreeChangeEvent(
                "node_removed", self, old_parent, None
            ))
    
    def move_to_parent(self, new_parent: 'LogLogNode', position: Optional[int] = None):
        """Move this node to new parent"""
        old_parent = self.parent
        self.remove_from_parent()
        new_parent.add_child(self, position)
        
        self._notify_observers(TreeChangeEvent(
            "node_moved", self, old_parent, new_parent
        ))
    
    def move_up(self) -> bool:
        """Move node up among siblings"""
        if not self.parent:
            return False
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index > 0:
            siblings[current_index], siblings[current_index - 1] = \
                siblings[current_index - 1], siblings[current_index]
            
            self._notify_observers(TreeChangeEvent(
                "node_moved", self, self.parent, self.parent
            ))
            return True
        return False
    
    def move_down(self) -> bool:
        """Move node down among siblings"""
        if not self.parent:
            return False
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index < len(siblings) - 1:
            siblings[current_index], siblings[current_index + 1] = \
                siblings[current_index + 1], siblings[current_index]
            
            self._notify_observers(TreeChangeEvent(
                "node_moved", self, self.parent, self.parent
            ))
            return True
        return False
    
    def indent(self) -> bool:
        """Increase indentation (move under previous sibling)"""
        if not self.parent:
            return False
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index > 0:
            new_parent = siblings[current_index - 1]
            self.move_to_parent(new_parent)
            return True
        return False
    
    def outdent(self) -> bool:
        """Decrease indentation (move to parent's level)"""
        if not self.parent or not self.parent.parent:
            return False
        
        grandparent = self.parent.parent
        parent_index = grandparent.children.index(self.parent)
        self.move_to_parent(grandparent, parent_index + 1)
        return True
    
    # TODO Operations
    
    def cycle_todo_status(self):
        """Cycle through TODO statuses: [] → [-] → [x] → []"""
        old_status = self.todo_status
        
        if self.node_type != NodeType.TODO:
            # Convert to TODO
            self.node_type = NodeType.TODO
            self.todo_status = TodoStatus.PENDING
        else:
            # Cycle existing TODO
            if self.todo_status == TodoStatus.PENDING:
                self.todo_status = TodoStatus.PROGRESS
            elif self.todo_status == TodoStatus.PROGRESS:
                self.todo_status = TodoStatus.COMPLETE
            elif self.todo_status == TodoStatus.COMPLETE:
                self.todo_status = TodoStatus.PENDING
            else:  # UNKNOWN
                self.todo_status = TodoStatus.PENDING
        
        self._notify_observers(TreeChangeEvent(
            "node_modified", self, old_value=old_status, new_value=self.todo_status
        ))
    
    def set_todo_status(self, status: Optional[TodoStatus]):
        """Set specific TODO status"""
        old_status = self.todo_status
        old_type = self.node_type
        
        if status is None:
            self.node_type = NodeType.ITEM
            self.todo_status = None
        else:
            self.node_type = NodeType.TODO
            self.todo_status = status
        
        if old_status != status or old_type != self.node_type:
            self._notify_observers(TreeChangeEvent(
                "node_modified", self, old_value=old_status, new_value=status
            ))
    
    # Content Operations
    
    def set_content(self, new_content: str):
        """Set node content and re-parse metadata"""
        old_content = self.content
        self.content = new_content.strip()
        self._extract_hashtags()
        
        if old_content != self.content:
            self._notify_observers(TreeChangeEvent(
                "node_modified", self, old_value=old_content, new_value=self.content
            ))
    
    def split_content(self, position: int) -> 'LogLogNode':
        """Split content at position, create new sibling with remainder"""
        if position >= len(self.content):
            # Create empty sibling
            new_node = LogLogNode("", NodeType.ITEM)
        else:
            # Split content
            remaining_content = self.content[position:].strip()
            self.set_content(self.content[:position].strip())
            new_node = LogLogNode(remaining_content, NodeType.ITEM)
        
        # Insert as next sibling
        if self.parent:
            sibling_index = self.parent.children.index(self) + 1
            self.parent.add_child(new_node, sibling_index)
        
        return new_node
    
    def merge_with_previous(self) -> bool:
        """Merge content with previous sibling"""
        if not self.parent:
            return False
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index > 0:
            previous_sibling = siblings[current_index - 1]
            
            # Merge content
            if previous_sibling.content and self.content:
                previous_sibling.set_content(previous_sibling.content + " " + self.content)
            elif self.content:
                previous_sibling.set_content(self.content)
            
            # Move children to previous sibling
            for child in self.children[:]:
                child.move_to_parent(previous_sibling)
            
            # Remove this node
            self.remove_from_parent()
            return True
        return False
    
    # Folding Operations
    
    def toggle_fold(self, recursive: bool = False):
        """Toggle fold state"""
        old_state = self.is_folded
        self.is_folded = not self.is_folded
        
        if recursive:
            for child in self.children:
                child.is_folded = self.is_folded
                if recursive:
                    child.toggle_fold(recursive=True)
        
        self._notify_observers(TreeChangeEvent(
            "node_modified", self, old_value=old_state, new_value=self.is_folded
        ))
    
    def fold_all_children(self):
        """Fold all children recursively"""
        for child in self.children:
            child.is_folded = True
            child.fold_all_children()
        
        self._notify_observers(TreeChangeEvent(
            "node_modified", self
        ))
    
    def unfold_all_children(self):
        """Unfold all children recursively"""
        for child in self.children:
            child.is_folded = False
            child.unfold_all_children()
        
        self._notify_observers(TreeChangeEvent(
            "node_modified", self
        ))
    
    # Serialization
    
    def serialize_to_loglog(self, level: int = 0) -> str:
        """Convert subtree to LogLog text format"""
        lines = []
        
        if self.node_type != NodeType.ROOT:
            # Build line content
            indent = "    " * level
            
            if self.node_type == NodeType.TODO:
                if self.todo_status == TodoStatus.PENDING:
                    prefix = "[]"
                elif self.todo_status == TodoStatus.PROGRESS:
                    prefix = "[-]"
                elif self.todo_status == TodoStatus.COMPLETE:
                    prefix = "[x]"
                elif self.todo_status == TodoStatus.UNKNOWN:
                    prefix = "[?]"
                else:
                    prefix = "[]"
                
                line = f"{indent}{prefix} {self.content}"
            else:
                line = f"{indent}- {self.content}"
            
            lines.append(line)
        
        # Serialize children
        if not self.is_folded:
            for child in self.children:
                lines.extend(child.serialize_to_loglog(level + (0 if self.node_type == NodeType.ROOT else 1)).split('\n'))
        
        return '\n'.join(line for line in lines if line.strip())
    
    # Search Operations
    
    def search(self, query: str, case_sensitive: bool = False) -> List['LogLogNode']:
        """Search for query in this subtree"""
        results = []
        search_content = self.content if case_sensitive else self.content.lower()
        search_query = query if case_sensitive else query.lower()
        
        if search_query in search_content:
            results.append(self)
        
        # Search children (even if folded for search purposes)
        for child in self.children:
            results.extend(child.search(query, case_sensitive))
        
        return results
    
    # Navigation Helpers
    
    def get_next_sibling(self) -> Optional['LogLogNode']:
        """Get next sibling in parent's children"""
        if not self.parent:
            return None
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index < len(siblings) - 1:
            return siblings[current_index + 1]
        return None
    
    def get_previous_sibling(self) -> Optional['LogLogNode']:
        """Get previous sibling in parent's children"""
        if not self.parent:
            return None
        
        siblings = self.parent.children
        current_index = siblings.index(self)
        
        if current_index > 0:
            return siblings[current_index - 1]
        return None
    
    def get_first_child(self) -> Optional['LogLogNode']:
        """Get first child if any"""
        return self.children[0] if self.children else None
    
    def get_last_descendant(self) -> 'LogLogNode':
        """Get last visible descendant (for navigation)"""
        if not self.children or self.is_folded:
            return self
        return self.children[-1].get_last_descendant()
    
    def get_level(self) -> int:
        """Get nesting level (root = 0)"""
        level = 0
        node = self.parent
        while node and node.node_type != NodeType.ROOT:
            level += 1
            node = node.parent
        return level
    
    def __str__(self):
        return f"LogLogNode(id={self.id[:8]}, content='{self.content[:30]}', type={self.node_type})"
    
    def __repr__(self):
        return self.__str__()


class SelectionManager:
    """Manages selection state across the tree"""
    
    def __init__(self, tree: 'LogLogTree'):
        self.tree = tree
        self.selected_nodes: Set[LogLogNode] = set()
        self.focused_node: Optional[LogLogNode] = None
        self.anchor_node: Optional[LogLogNode] = None
    
    def set_focus(self, node: Optional[LogLogNode]):
        """Set focus to specific node"""
        old_focus = self.focused_node
        
        if old_focus:
            old_focus.is_focused = False
        
        self.focused_node = node
        if node:
            node.is_focused = True
            # Focused node is always selected
            self.add_to_selection(node)
        
        if old_focus != node:
            self.tree._notify_observers(TreeChangeEvent(
                "focus_changed", node, old_value=old_focus, new_value=node
            ))
    
    def add_to_selection(self, node: LogLogNode):
        """Add node to selection"""
        if node not in self.selected_nodes:
            self.selected_nodes.add(node)
            node.is_selected = True
            
            self.tree._notify_observers(TreeChangeEvent(
                "selection_changed", node
            ))
    
    def remove_from_selection(self, node: LogLogNode):
        """Remove node from selection"""
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
            node.is_selected = False
            
            self.tree._notify_observers(TreeChangeEvent(
                "selection_changed", node
            ))
    
    def toggle_selection(self, node: LogLogNode):
        """Toggle selection of node"""
        if node in self.selected_nodes:
            self.remove_from_selection(node)
        else:
            self.add_to_selection(node)
    
    def clear_selection(self):
        """Clear all selections except focused"""
        for node in list(self.selected_nodes):
            if node != self.focused_node:
                self.remove_from_selection(node)
    
    def select_range(self, start_node: LogLogNode, end_node: LogLogNode):
        """Select range of nodes in visual order"""
        self.clear_selection()
        
        # Get all visible nodes in order
        visible_nodes = self.tree.get_visible_nodes()
        
        try:
            start_index = visible_nodes.index(start_node)
            end_index = visible_nodes.index(end_node)
            
            # Ensure start <= end
            if start_index > end_index:
                start_index, end_index = end_index, start_index
            
            # Select range
            for i in range(start_index, end_index + 1):
                self.add_to_selection(visible_nodes[i])
            
            self.anchor_node = start_node
            
        except ValueError:
            # One of the nodes not in visible list
            self.add_to_selection(start_node)
            self.add_to_selection(end_node)
    
    def get_selected_nodes(self) -> List[LogLogNode]:
        """Get all selected nodes as list"""
        return list(self.selected_nodes)
    
    def has_selection(self) -> bool:
        """Check if any nodes are selected"""
        return len(self.selected_nodes) > 0


class LogLogTree:
    """
    Tree container with high-level operations.
    Platform-agnostic tree management.
    """
    
    def __init__(self):
        self.root = LogLogNode("", NodeType.ROOT)
        self.selection = SelectionManager(self)
        self._observers: List[Callable] = []
        self._node_index: Dict[str, LogLogNode] = {}
        self._build_index()
    
    def add_observer(self, observer: Callable):
        """Add tree change observer"""
        self._observers.append(observer)
        # Also add to all nodes
        self._propagate_observers()
    
    def remove_observer(self, observer: Callable):
        """Remove tree change observer"""
        if observer in self._observers:
            self._observers.remove(observer)
        self._propagate_observers()
    
    def _propagate_observers(self):
        """Propagate observers to all nodes"""
        for node in self.get_all_nodes():
            node._observers = self._observers[:]
    
    def _notify_observers(self, event: TreeChangeEvent):
        """Notify all observers of changes"""
        for observer in self._observers:
            try:
                observer(event)
            except Exception as e:
                print(f"Tree observer error: {e}")
    
    def _build_index(self):
        """Build node ID index for fast lookups"""
        self._node_index = {}
        for node in self.get_all_nodes():
            self._node_index[node.id] = node
    
    def get_node_by_id(self, node_id: str) -> Optional[LogLogNode]:
        """Get node by ID (fast lookup)"""
        return self._node_index.get(node_id)
    
    def get_all_nodes(self) -> List[LogLogNode]:
        """Get flat list of all nodes"""
        nodes = []
        
        def collect_nodes(node):
            if node.node_type != NodeType.ROOT:
                nodes.append(node)
            for child in node.children:
                collect_nodes(child)
        
        collect_nodes(self.root)
        return nodes
    
    def get_visible_nodes(self) -> List[LogLogNode]:
        """Get list of visible nodes (respecting fold states)"""
        visible = []
        
        def collect_visible(node, include_self=True):
            if node.node_type != NodeType.ROOT and include_self:
                visible.append(node)
            
            if not node.is_folded:
                for child in node.children:
                    collect_visible(child, True)
        
        collect_visible(self.root, False)
        return visible
    
    def search(self, query: str, case_sensitive: bool = False, 
               scope_node: Optional[LogLogNode] = None) -> List[LogLogNode]:
        """Search within tree or subtree"""
        search_root = scope_node or self.root
        return search_root.search(query, case_sensitive)
    
    def serialize(self) -> str:
        """Convert entire tree to LogLog text"""
        return self.root.serialize_to_loglog()
    
    def load_from_text(self, text: str):
        """Load tree from LogLog text format"""
        # Clear existing tree
        self.root = LogLogNode("", NodeType.ROOT)
        self.selection = SelectionManager(self)
        
        if not text.strip():
            return
        
        lines = text.split('\n')
        stack = [self.root]  # Stack of parent nodes
        
        for line in lines:
            if not line.strip():
                continue
            
            # Calculate indentation level
            level = 0
            content = line.lstrip()
            for char in line:
                if char == ' ':
                    level += 1
                elif char == '\t':
                    level += 4
                else:
                    break
            
            level = level // 4  # Convert spaces to levels
            
            # Remove leading dash or TODO marker
            if content.startswith('- '):
                content = content[2:]
            
            # Create node
            node = LogLogNode(content)
            
            # Find correct parent based on level
            while len(stack) > level + 1:
                stack.pop()
            
            parent = stack[-1]
            parent.add_child(node)
            stack.append(node)
        
        self._build_index()
        self._propagate_observers()
    
    def parse_loglog_text(self, text: str):
        """Parse LogLog text into tree structure (alias for load_from_text)"""
        self.load_from_text(text)
    
    def apply_operation_to_selection(self, operation: Callable[[LogLogNode], None]):
        """Apply operation to all selected nodes"""
        selected_nodes = self.selection.get_selected_nodes()
        for node in selected_nodes:
            try:
                operation(node)
            except Exception as e:
                print(f"Operation failed on node {node.id}: {e}")
    
    # Navigation operations
    
    def get_next_visible_node(self, current: LogLogNode) -> Optional[LogLogNode]:
        """Get next node in visual order"""
        visible_nodes = self.get_visible_nodes()
        try:
            current_index = visible_nodes.index(current)
            if current_index < len(visible_nodes) - 1:
                return visible_nodes[current_index + 1]
        except ValueError:
            pass
        return None
    
    def get_previous_visible_node(self, current: LogLogNode) -> Optional[LogLogNode]:
        """Get previous node in visual order"""
        visible_nodes = self.get_visible_nodes()
        try:
            current_index = visible_nodes.index(current)
            if current_index > 0:
                return visible_nodes[current_index - 1]
        except ValueError:
            pass
        return None
    
    def focus_mode(self, node: LogLogNode):
        """Focus mode - fold everything except path to node"""
        # Unfold path to node
        current = node
        while current and current.node_type != NodeType.ROOT:
            current.is_folded = False
            current = current.parent
        
        # Fold everything else
        def fold_others(check_node, target_path):
            if check_node == node:
                return
            
            in_path = False
            current = node
            while current:
                if current == check_node:
                    in_path = True
                    break
                current = current.parent
            
            if not in_path:
                check_node.is_folded = True
            
            for child in check_node.children:
                fold_others(child, target_path)
        
        for child in self.root.children:
            fold_others(child, None)
        
        self._notify_observers(TreeChangeEvent("tree_modified", node))


def create_sample_tree() -> LogLogTree:
    """Create a sample LogLog tree for testing"""
    tree = LogLogTree()
    
    # Create sample content
    root_item = LogLogNode("Project Planning", NodeType.ITEM)
    tree.root.add_child(root_item)
    
    phase1 = LogLogNode("Phase 1: Research", NodeType.ITEM) 
    root_item.add_child(phase1)
    
    todo1 = LogLogNode("Literature review #research", NodeType.TODO)
    todo1.todo_status = TodoStatus.PENDING
    phase1.add_child(todo1)
    
    todo2 = LogLogNode("Market analysis", NodeType.TODO)
    todo2.todo_status = TodoStatus.COMPLETE
    phase1.add_child(todo2)
    
    phase2 = LogLogNode("Phase 2: Development", NodeType.ITEM)
    root_item.add_child(phase2)
    
    todo3 = LogLogNode("Design mockups", NodeType.TODO)
    todo3.todo_status = TodoStatus.PROGRESS
    phase2.add_child(todo3)
    
    return tree


if __name__ == "__main__":
    # Test the tree model
    tree = create_sample_tree()
    
    print("=== Tree Structure ===")
    print(tree.serialize())
    
    print("\n=== Search Test ===")
    results = tree.search("research")
    for result in results:
        print(f"Found: {result.content}")
    
    print("\n=== Navigation Test ===")
    visible = tree.get_visible_nodes()
    for i, node in enumerate(visible):
        print(f"{i}: {node.content} (level {node.get_level()})")
    
    print("\n=== Selection Test ===")
    tree.selection.set_focus(visible[0])
    tree.selection.select_range(visible[0], visible[2])
    print(f"Selected: {len(tree.selection.get_selected_nodes())} nodes")
    
    print("\n=== TODO Cycling Test ===")
    todo_node = next(n for n in visible if n.node_type == NodeType.TODO)
    print(f"Before: {todo_node.todo_status}")
    todo_node.cycle_todo_status()
    print(f"After: {todo_node.todo_status}")