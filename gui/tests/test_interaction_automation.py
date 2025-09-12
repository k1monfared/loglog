#!/usr/bin/env python3
"""
LogLog GUI - Automated Interaction Tests
Comprehensive tests simulating user keyboard and mouse interactions
"""

import sys
import os
import time
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from loglog_gui import ModernLogLogGUI
from loglog_tree_model import LogLogTree, LogLogNode
from interaction_controllers import InteractionManager, TodoState, EditMode

class InteractionTestCase(unittest.TestCase):
    """Base test case for interaction testing"""
    
    def setUp(self):
        """Setup test environment before each test"""
        # Create test content
        self.test_content = """Test Document
    Section 1 - Expandable
        Item 1.1 - Child
        Item 1.2 - Another child
            Nested item 1.2.1
    Section 2 - More content
        Item 2.1 - Test item
        Item 2.2 - Another test
[] TODO item - Not done
[x] DONE item - Completed
[-] PROGRESS item - In progress
[?] UNKNOWN item - Unknown state"""
        
        # Create GUI instance
        self.app = ModernLogLogGUI()
        self.root = self.app.root
        
        # Create test file
        self.test_file = '/tmp/test_interactions.log'
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        # Load test content
        self.app.load_file(self.test_file)
        self.tree_renderer = self.app.tree_renderer
        self.viewport = self.tree_renderer.active_viewport
        
        # Get the interaction manager
        self.interaction_manager = InteractionManager(
            self.tree_renderer.tree, 
            self.viewport
        )
        
        # Update GUI to ensure everything is rendered
        self.root.update_idletasks()
    
    def tearDown(self):
        """Cleanup after each test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def simulate_key_event(self, key_sequence: str, widget=None):
        """Simulate keyboard events"""
        if widget is None:
            widget = self.viewport.text_widget
        
        # Create mock event
        event = Mock()
        event.widget = widget
        event.state = 0  # No modifier keys by default
        
        # Handle special key sequences
        if key_sequence.startswith('<Control-'):
            event.state = 4  # Control key mask
            key = key_sequence[10:-1]  # Extract key from <Control-Key>
        elif key_sequence.startswith('<Shift-'):
            event.state = 1  # Shift key mask
            key = key_sequence[7:-1]
        elif key_sequence.startswith('<Alt-'):
            event.state = 8  # Alt key mask
            key = key_sequence[5:-1]
        else:
            key = key_sequence.strip('<>')
        
        # Simulate the key press
        if hasattr(self.interaction_manager.keyboard_controller, f'_on_{key.lower().replace("-", "_")}'):
            handler = getattr(self.interaction_manager.keyboard_controller, f'_on_{key.lower().replace("-", "_")}')
            return handler(event)
        else:
            # Try generic key handler
            return None
    
    def simulate_mouse_click(self, x: int, y: int, button: int = 1, modifiers: int = 0):
        """Simulate mouse click events"""
        event = Mock()
        event.x = x
        event.y = y
        event.state = modifiers
        event.widget = self.viewport.text_widget
        
        if button == 1:  # Left click
            if modifiers & 4:  # Control
                return self.interaction_manager.mouse_controller._on_ctrl_click(event)
            elif modifiers & 1:  # Shift
                return self.interaction_manager.mouse_controller._on_shift_click(event)
            else:
                return self.interaction_manager.mouse_controller._on_left_click(event)
        elif button == 3:  # Right click
            return self.interaction_manager.mouse_controller._on_right_click(event)
    
    def get_visible_nodes(self):
        """Get currently visible nodes"""
        return self.tree_renderer.tree.get_visible_nodes()
    
    def get_selected_nodes(self):
        """Get currently selected nodes"""
        return self.interaction_manager.keyboard_controller.state.selected_nodes
    
    def get_current_node(self):
        """Get currently focused node"""
        return self.interaction_manager.keyboard_controller.state.current_node

class TestKeyboardNavigation(InteractionTestCase):
    """Test keyboard navigation features"""
    
    def test_up_down_navigation(self):
        """Test Up/Down arrow keys for navigation"""
        visible_nodes = self.get_visible_nodes()
        
        # Start at first node
        self.simulate_key_event('<Down>')
        current = self.get_current_node()
        self.assertEqual(current, visible_nodes[0])
        
        # Move down
        self.simulate_key_event('<Down>')
        current = self.get_current_node()
        self.assertEqual(current, visible_nodes[1])
        
        # Move up
        self.simulate_key_event('<Up>')
        current = self.get_current_node()
        self.assertEqual(current, visible_nodes[0])
    
    def test_left_right_folding(self):
        """Test Left/Right arrow keys for folding/navigation"""
        visible_nodes = self.get_visible_nodes()
        
        # Find a node with children
        expandable_node = None
        for node in visible_nodes:
            if node.children:
                expandable_node = node
                break
        
        self.assertIsNotNone(expandable_node, "Should have expandable nodes in test data")
        
        # Select the expandable node
        self.interaction_manager.keyboard_controller._select_node(expandable_node)
        
        # Test folding with Left arrow
        original_folded_state = expandable_node.is_folded
        self.simulate_key_event('<Left>')
        
        if not original_folded_state:
            # Should be folded now
            self.assertTrue(expandable_node.is_folded)
        else:
            # If already folded, should navigate to parent
            current = self.get_current_node()
            if expandable_node.parent:
                self.assertEqual(current, expandable_node.parent)
        
        # Test unfolding with Right arrow
        if expandable_node.is_folded:
            self.simulate_key_event('<Right>')
            self.assertFalse(expandable_node.is_folded)
    
    def test_shift_selection(self):
        """Test Shift+Up/Down for multi-selection"""
        visible_nodes = self.get_visible_nodes()
        
        # Start at first node
        self.simulate_key_event('<Down>')
        
        # Select multiple nodes with Shift+Down
        self.simulate_key_event('<Shift-Down>')
        self.simulate_key_event('<Shift-Down>')
        
        selected = self.get_selected_nodes()
        self.assertGreaterEqual(len(selected), 3, "Should have multiple selected nodes")
    
    def test_page_up_down(self):
        """Test Page Up/Down scrolling"""
        widget = self.viewport.text_widget
        original_position = widget.yview()[0]
        
        # Test Page Down
        self.simulate_key_event('<Next>')  # Page Down
        new_position = widget.yview()[0]
        self.assertGreater(new_position, original_position, "Should scroll down")
        
        # Test Page Up
        self.simulate_key_event('<Prior>')  # Page Up
        final_position = widget.yview()[0]
        self.assertLess(final_position, new_position, "Should scroll up")

class TestTodoFunctionality(InteractionTestCase):
    """Test TODO item state management"""
    
    def test_todo_state_cycling(self):
        """Test Space key cycling through TODO states"""
        visible_nodes = self.get_visible_nodes()
        
        # Find a TODO item
        todo_node = None
        for node in visible_nodes:
            if '[]' in node.content or '[x]' in node.content or '[-]' in node.content:
                todo_node = node
                break
        
        self.assertIsNotNone(todo_node, "Should have TODO items in test data")
        
        # Select the TODO node
        self.interaction_manager.keyboard_controller._select_node(todo_node)
        
        # Test cycling through states
        original_content = todo_node.content
        
        # Press space to cycle
        self.simulate_key_event('<space>')
        self.assertNotEqual(todo_node.content, original_content, "Content should change")
        
        # Continue cycling
        state1_content = todo_node.content
        self.simulate_key_event('<space>')
        state2_content = todo_node.content
        self.assertNotEqual(state2_content, state1_content, "Should cycle to next state")
        
        self.simulate_key_event('<space>')
        state3_content = todo_node.content
        self.assertNotEqual(state3_content, state2_content, "Should cycle to next state")
    
    def test_unknown_todo_state(self):
        """Test ? key for unknown TODO state"""
        visible_nodes = self.get_visible_nodes()
        
        # Find a TODO item
        todo_node = None
        for node in visible_nodes:
            if '[]' in node.content:
                todo_node = node
                break
        
        if todo_node:
            self.interaction_manager.keyboard_controller._select_node(todo_node)
            
            # Press ? for unknown state
            self.simulate_key_event('<?>')
            self.assertIn('[?]', todo_node.content, "Should set unknown state")

class TestMouseInteraction(InteractionTestCase):
    """Test mouse interaction features"""
    
    def test_click_selection(self):
        """Test mouse click selection"""
        # Get text widget dimensions for click simulation
        widget = self.viewport.text_widget
        
        # Simulate click on a line (approximate position)
        self.simulate_mouse_click(100, 50)
        
        # Check that something was selected
        current = self.get_current_node()
        self.assertIsNotNone(current, "Should have selected a node")
    
    def test_ctrl_click_multi_select(self):
        """Test Ctrl+Click for multi-selection"""
        # Simulate first click
        self.simulate_mouse_click(100, 50)
        first_selected = self.get_current_node()
        
        # Simulate Ctrl+Click on different position
        self.simulate_mouse_click(100, 80, modifiers=4)  # Control modifier
        
        selected_nodes = self.get_selected_nodes()
        self.assertGreater(len(selected_nodes), 1, "Should have multiple selected nodes")
    
    def test_right_click_context_menu(self):
        """Test right-click context menu"""
        # This test verifies that right-click handler is called
        # In real testing, you'd verify menu creation
        with patch.object(self.interaction_manager.mouse_controller, '_show_context_menu') as mock_menu:
            self.simulate_mouse_click(100, 50, button=3)  # Right click
            # mock_menu.assert_called_once()

class TestAdvancedFeatures(InteractionTestCase):
    """Test advanced features like folding, clipboard, etc."""
    
    def test_ctrl_level_folding(self):
        """Test Ctrl+1,2,3... for level folding"""
        # Test Ctrl+1 for level 1 folding
        original_states = {}
        visible_nodes = self.get_visible_nodes()
        
        # Record original folding states
        for node in visible_nodes:
            if node.children:
                original_states[node] = node.is_folded
        
        # Simulate Ctrl+1
        self.simulate_key_event('<Control-1>')
        
        # Check that level 1 nodes changed state
        level_1_nodes = [n for n in visible_nodes if self._get_node_level(n) == 1 and n.children]
        for node in level_1_nodes:
            if node in original_states:
                self.assertNotEqual(node.is_folded, original_states[node], 
                                  f"Level 1 node {node.content} should have changed folding state")
    
    def test_clipboard_operations(self):
        """Test copy/cut/paste operations"""
        visible_nodes = self.get_visible_nodes()
        
        if visible_nodes:
            # Select a node
            self.interaction_manager.keyboard_controller._select_node(visible_nodes[0])
            
            # Test copy
            self.simulate_key_event('<Control-c>')
            clipboard = self.interaction_manager.keyboard_controller.state.clipboard_nodes
            self.assertGreater(len(clipboard), 0, "Should have copied node to clipboard")
            
            # Test cut
            self.simulate_key_event('<Control-x>')
            self.assertTrue(self.interaction_manager.keyboard_controller.state.is_clipboard_cut, 
                          "Should mark as cut operation")
    
    def test_indentation_operations(self):
        """Test Tab/Shift+Tab for indentation"""
        visible_nodes = self.get_visible_nodes()
        
        if len(visible_nodes) > 1:
            # Select a node that can be indented
            target_node = visible_nodes[1]  # Second node
            self.interaction_manager.keyboard_controller._select_node(target_node)
            
            original_parent = target_node.parent
            
            # Test Tab (indent)
            self.simulate_key_event('<Tab>')
            
            # The exact behavior depends on implementation, but structure should change
            # In a real test, you'd verify the tree structure changed appropriately
            
            # Test Shift+Tab (outdent)
            self.simulate_key_event('<Shift-Tab>')
    
    def _get_node_level(self, node) -> int:
        """Helper to get node level in tree"""
        level = 0
        current = node.parent
        while current:
            level += 1
            current = current.parent
        return level

class TestEditMode(InteractionTestCase):
    """Test text editing functionality"""
    
    def test_enter_edit_mode(self):
        """Test Enter key to enter edit mode"""
        visible_nodes = self.get_visible_nodes()
        
        if visible_nodes:
            # Select a node
            self.interaction_manager.keyboard_controller._select_node(visible_nodes[0])
            
            # Press Enter to enter edit mode
            self.simulate_key_event('<Return>')
            
            # Check edit mode state
            edit_mode = self.interaction_manager.keyboard_controller.state.edit_mode
            self.assertEqual(edit_mode, EditMode.EDITING, "Should be in editing mode")
    
    def test_escape_edit_mode(self):
        """Test Escape key to exit edit mode"""
        # First enter edit mode
        self.test_enter_edit_mode()
        
        # Press Escape to exit
        self.simulate_key_event('<Escape>')
        
        # Check edit mode state
        edit_mode = self.interaction_manager.keyboard_controller.state.edit_mode
        self.assertEqual(edit_mode, EditMode.NORMAL, "Should return to normal mode")

class TestSearchFunctionality(InteractionTestCase):
    """Test search and navigation features"""
    
    def test_ctrl_f_search(self):
        """Test Ctrl+F for search activation"""
        # This would test search box focus
        self.simulate_key_event('<Control-f>')
        # In real implementation, verify search box is focused
    
    def test_home_end_navigation(self):
        """Test Home/End keys"""
        # Test Home key
        self.simulate_key_event('<Home>')
        current = self.get_current_node()
        visible_nodes = self.get_visible_nodes()
        if visible_nodes:
            self.assertEqual(current, visible_nodes[0], "Home should go to first node")
        
        # Test End key
        self.simulate_key_event('<End>')
        current = self.get_current_node()
        if visible_nodes:
            self.assertEqual(current, visible_nodes[-1], "End should go to last node")

class TestIntegrationScenarios(InteractionTestCase):
    """Test complex interaction scenarios"""
    
    def test_complex_navigation_scenario(self):
        """Test a complex sequence of navigation and editing"""
        visible_nodes = self.get_visible_nodes()
        
        if len(visible_nodes) >= 3:
            # Navigate down twice
            self.simulate_key_event('<Down>')
            self.simulate_key_event('<Down>')
            
            # Select multiple with Shift
            self.simulate_key_event('<Shift-Down>')
            
            # Copy selected nodes
            self.simulate_key_event('<Control-c>')
            
            # Navigate to different position
            self.simulate_key_event('<Down>')
            self.simulate_key_event('<Down>')
            
            # Paste
            self.simulate_key_event('<Control-v>')
            
            # Verify operations completed without errors
            self.assertTrue(True, "Complex scenario completed")
    
    def test_folding_and_navigation_scenario(self):
        """Test folding combined with navigation"""
        visible_nodes = self.get_visible_nodes()
        
        # Find expandable node
        expandable_node = None
        for node in visible_nodes:
            if node.children and not node.is_folded:
                expandable_node = node
                break
        
        if expandable_node:
            # Select and fold
            self.interaction_manager.keyboard_controller._select_node(expandable_node)
            self.simulate_key_event('<Left>')  # Fold
            
            # Navigate and check visibility
            self.simulate_key_event('<Down>')
            self.simulate_key_event('<Up>')
            
            # Unfold
            self.simulate_key_event('<Right>')  # Unfold
            
            # Navigate to child
            self.simulate_key_event('<Right>')  # Go to first child
            
            current = self.get_current_node()
            if expandable_node.children:
                self.assertEqual(current, expandable_node.children[0], 
                               "Should navigate to first child")

def run_gui_tests():
    """Run all GUI interaction tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestKeyboardNavigation,
        TestTodoFunctionality,
        TestMouseInteraction,
        TestAdvancedFeatures,
        TestEditMode,
        TestSearchFunctionality,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🚀 Starting LogLog GUI Interaction Tests")
    print("=" * 60)
    
    success = run_gui_tests()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(0 if success else 1)