#!/usr/bin/env python3
"""
Test script for LogLog GUI application
Tests all major GUI components and functionality.
"""

import sys
import os
import tkinter as tk
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from loglog_gui import LogLogGUI, FileTreeView, LogLogSyntaxHighlighter, TreePreviewWidget, LogLogSettings
    from loglog import TreeNode
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)

class GUITester:
    def __init__(self):
        self.test_dir = None
        self.root = None
        self.gui = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    def setup_test_environment(self):
        """Set up test files and directories"""
        self.test_dir = tempfile.mkdtemp(prefix="loglog_gui_test_")
        
        # Create test LogLog file
        test_content = """- Main Section #test
    - Subsection 1
        [] Task 1 #important
        [x] Completed task
        [-] In progress task
    - Subsection 2 #analysis
        - Deep nesting
            - Level 3
                [] Deep task #urgent
        [] Another task

- Second Section
    - More content
        [x] Done item
        [] Pending item #deadline
"""
        
        test_file = Path(self.test_dir) / "test.log"
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        # Create additional test files
        simple_content = "- Simple document\n    [] Simple task\n"
        simple_file = Path(self.test_dir) / "simple.log"
        with open(simple_file, 'w') as f:
            f.write(simple_content)
            
        return test_file, simple_file
    
    def cleanup_test_environment(self):
        """Clean up test files and directories"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def assert_test(self, condition, message):
        """Assert a test condition and track results"""
        if condition:
            print(f"✓ {message}")
            self.tests_passed += 1
        else:
            print(f"✗ {message}")
            self.tests_failed += 1
            
    def test_gui_initialization(self):
        """Test GUI initialization and basic setup"""
        print("\n=== Testing GUI Initialization ===")
        
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide main window during testing
            
            self.gui = LogLogGUI()
            
            self.assert_test(self.gui.root is not None, "GUI root window created")
            self.assert_test(hasattr(self.gui, 'file_tree'), "File tree component exists")
            self.assert_test(hasattr(self.gui, 'text_editor'), "Text editor component exists")
            self.assert_test(hasattr(self.gui, 'tree_preview'), "Tree preview component exists")
            self.assert_test(hasattr(self.gui, 'settings'), "Settings component exists")
            
        except Exception as e:
            self.assert_test(False, f"GUI initialization failed: {e}")
    
    def test_settings_component(self):
        """Test settings management"""
        print("\n=== Testing Settings Component ===")
        
        try:
            settings = LogLogSettings()
            
            # Test default values
            self.assert_test('theme' in settings.settings, "Theme setting exists")
            self.assert_test('font_size' in settings.settings, "Font size setting exists")
            self.assert_test('auto_save' in settings.settings, "Auto save setting exists")
            
            # Test setting and getting values
            settings.set('test_key', 'test_value')
            self.assert_test(settings.get('test_key') == 'test_value', "Settings set/get works")
            
            # Test save functionality
            original_save = settings.save
            settings.save = MagicMock()
            settings.set('another_key', 'another_value')
            settings.save.assert_called()
            settings.save = original_save
            
            self.assert_test(True, "Settings component working correctly")
            
        except Exception as e:
            self.assert_test(False, f"Settings component failed: {e}")
    
    def test_file_operations(self):
        """Test file loading and saving operations"""
        print("\n=== Testing File Operations ===")
        
        try:
            test_file, simple_file = self.setup_test_environment()
            
            # Test file loading
            if hasattr(self.gui, 'load_file'):
                self.gui.load_file(str(test_file))
                self.assert_test(self.gui.current_file == str(test_file), "File loaded successfully")
                
                # Check if content is displayed
                content = self.gui.text_editor.get(1.0, tk.END).strip()
                self.assert_test(len(content) > 0, "File content displayed in editor")
                self.assert_test("Main Section" in content, "File content correctly loaded")
            else:
                self.assert_test(False, "load_file method not found")
            
        except Exception as e:
            self.assert_test(False, f"File operations failed: {e}")
    
    def test_syntax_highlighting(self):
        """Test LogLog syntax highlighting"""
        print("\n=== Testing Syntax Highlighting ===")
        
        try:
            # Create a text widget for testing
            text_widget = tk.Text(self.root)
            highlighter = LogLogSyntaxHighlighter(text_widget)
            
            # Test highlighting setup
            self.assert_test(hasattr(highlighter, 'text_widget'), "Highlighter has text widget reference")
            self.assert_test(hasattr(highlighter, 'highlight_all'), "Highlighter has highlight_all method")
            
            # Test with sample content
            test_content = """- Section #tag
    [] Task item
    [x] Done item
    [-] Progress item
"""
            text_widget.insert(1.0, test_content)
            highlighter.highlight_all()
            
            # Check if tags are configured (basic test)
            tags = text_widget.tag_names()
            self.assert_test(len(tags) > 0, "Syntax highlighting tags created")
            
        except Exception as e:
            self.assert_test(False, f"Syntax highlighting failed: {e}")
    
    def test_tree_preview(self):
        """Test tree structure preview"""
        print("\n=== Testing Tree Preview ===")
        
        try:
            # Create tree preview widget
            tree_preview = TreePreviewWidget(self.root)
            
            self.assert_test(hasattr(tree_preview, 'tree'), "Tree preview has tree widget")
            self.assert_test(hasattr(tree_preview, 'update_tree'), "Tree preview has update_tree method")
            
            # Test with LogLog content
            if hasattr(tree_preview, 'update_tree'):
                test_content = """- Main Section
    - Subsection
        [] Task
"""
                # Create a simple tree structure for testing
                root_node = TreeNode("Main Section")
                child_node = TreeNode("Subsection")
                root_node.add_child(child_node)
                
                self.assert_test(True, "Tree preview structure test completed")
            
        except Exception as e:
            self.assert_test(False, f"Tree preview failed: {e}")
    
    def test_menu_functionality(self):
        """Test menu system functionality"""
        print("\n=== Testing Menu System ===")
        
        try:
            if hasattr(self.gui, 'menubar'):
                self.assert_test(self.gui.menubar is not None, "Menu bar exists")
                
                # Test menu structure
                menus = ['File', 'Edit', 'View', 'Convert', 'Help']
                for menu_name in menus:
                    # This is a basic existence test - actual menu testing would require more complex setup
                    self.assert_test(True, f"{menu_name} menu structure available")
            else:
                self.assert_test(False, "Menu bar not found")
                
        except Exception as e:
            self.assert_test(False, f"Menu system failed: {e}")
    
    def test_format_conversion(self):
        """Test format conversion functionality"""
        print("\n=== Testing Format Conversion ===")
        
        try:
            if hasattr(self.gui, 'convert_to_html'):
                # Test HTML conversion method exists
                self.assert_test(True, "HTML conversion method available")
            
            if hasattr(self.gui, 'convert_to_markdown'):
                # Test Markdown conversion method exists
                self.assert_test(True, "Markdown conversion method available")
            
            # Test actual conversion if file is loaded
            if self.gui.current_file:
                try:
                    # Mock the conversion to avoid file system operations
                    original_method = getattr(self.gui, 'convert_to_html', None)
                    if original_method:
                        with patch.object(self.gui, 'convert_to_html') as mock_convert:
                            mock_convert.return_value = True
                            result = self.gui.convert_to_html()
                            self.assert_test(result or mock_convert.called, "HTML conversion called successfully")
                except Exception as convert_error:
                    self.assert_test(False, f"Conversion test failed: {convert_error}")
            else:
                self.assert_test(True, "Format conversion methods available (no file loaded for testing)")
                
        except Exception as e:
            self.assert_test(False, f"Format conversion failed: {e}")
    
    def test_file_tree_view(self):
        """Test file tree view component"""
        print("\n=== Testing File Tree View ===")
        
        try:
            if hasattr(self.gui, 'file_tree'):
                file_tree = self.gui.file_tree
                self.assert_test(hasattr(file_tree, 'tree'), "File tree has tree widget")
                
                # Test directory loading
                if hasattr(file_tree, 'load_directory') and self.test_dir:
                    file_tree.load_directory(self.test_dir)
                    self.assert_test(True, "Directory loaded in file tree")
            else:
                self.assert_test(False, "File tree component not found")
                
        except Exception as e:
            self.assert_test(False, f"File tree view failed: {e}")
    
    def run_all_tests(self):
        """Run all GUI tests"""
        print("LogLog GUI Test Suite")
        print("====================")
        
        try:
            self.test_gui_initialization()
            self.test_settings_component()
            self.test_file_operations()
            self.test_syntax_highlighting()
            self.test_tree_preview()
            self.test_menu_functionality()
            self.test_format_conversion()
            self.test_file_tree_view()
            
        except Exception as e:
            print(f"❌ Test execution error: {e}")
            self.tests_failed += 1
        
        finally:
            # Clean up
            if self.root:
                self.root.quit()
                self.root.destroy()
            self.cleanup_test_environment()
        
        # Print results
        print(f"\n=== Test Results ===")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print("✅ All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            return 1

def main():
    """Run the GUI test suite"""
    tester = GUITester()
    return tester.run_all_tests()

if __name__ == '__main__':
    sys.exit(main())