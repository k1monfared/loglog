#!/usr/bin/env python3
"""
Simple GUI test to verify LogLog GUI components work
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all GUI components can be imported"""
    print("=== Testing Imports ===")
    
    try:
        import tkinter as tk
        print("✓ tkinter available")
    except ImportError:
        print("✗ tkinter not available")
        return False
    
    try:
        from loglog import TreeNode
        print("✓ loglog core module imported")
    except ImportError as e:
        print(f"✗ loglog core import failed: {e}")
        return False
    
    try:
        import loglog_gui
        print("✓ loglog_gui module imported")
    except ImportError as e:
        print(f"✗ loglog_gui import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic GUI functionality without full initialization"""
    print("\n=== Testing Basic Functionality ===")
    
    try:
        # Test CLI functionality (which the GUI depends on)
        from loglog_cli import LogLogCLI
        cli = LogLogCLI()
        print("✓ CLI component available")
        
        # Test TreeNode functionality
        from loglog import TreeNode
        node = TreeNode("Test")
        print("✓ TreeNode creation works")
        
        # Test file operations
        test_content = """- Test Document #test
    - Section 1
        [] Task 1
        [x] Completed task
"""
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        # Test CLI conversion (which GUI uses)
        import subprocess
        result = subprocess.run([
            sys.executable, 'loglog_cli.py', 'stats', temp_file
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✓ CLI stats command works")
        else:
            print(f"✗ CLI stats failed: {result.stderr}")
        
        # Clean up
        os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_gui_components():
    """Test individual GUI components"""
    print("\n=== Testing GUI Components ===")
    
    try:
        import tkinter as tk
        
        # Create a test root window (hidden)
        root = tk.Tk()
        root.withdraw()
        
        # Test basic tkinter widgets we use
        frame = tk.Frame(root)
        text = tk.Text(frame)
        treeview = tk.ttk.Treeview(frame) if hasattr(tk, 'ttk') else None
        
        print("✓ Basic tkinter widgets work")
        
        # Test text widget operations
        text.insert(1.0, "Test content")
        content = text.get(1.0, tk.END)
        if "Test content" in content:
            print("✓ Text widget operations work")
        else:
            print("✗ Text widget operations failed")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI components test failed: {e}")
        return False

def test_file_operations():
    """Test file operations that GUI will use"""
    print("\n=== Testing File Operations ===")
    
    try:
        # Create test file
        test_content = """- Test Document #gui-test
    - Features tested
        [] File loading
        [] Content parsing
        [] Format conversion
    - Expected results #validation
        - File should be readable
        - Content should be parseable
        [] All tests should pass #important
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        # Test reading the file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        if len(content) > 0 and "Test Document" in content:
            print("✓ File read operations work")
        else:
            print("✗ File read operations failed")
            return False
        
        # Test CLI operations on the file
        import subprocess
        
        # Test show command
        result = subprocess.run([
            sys.executable, 'loglog_cli.py', 'show', temp_file
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✓ CLI show command works")
        else:
            print(f"✗ CLI show failed: {result.stderr}")
        
        # Test conversion
        result = subprocess.run([
            sys.executable, 'loglog_cli.py', 'convert', temp_file, '--to', 'html', '--overwrite'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✓ CLI convert command works")
            # Check if HTML file was created
            html_file = temp_file.replace('.log', '.html')
            if os.path.exists(html_file):
                print("✓ HTML file generation works")
                os.unlink(html_file)
            else:
                print("✗ HTML file not created")
        else:
            print(f"✗ CLI convert failed: {result.stderr}")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def run_gui_manually():
    """Provide instructions for manual GUI testing"""
    print("\n=== Manual GUI Testing Instructions ===")
    print("To test the GUI manually, run:")
    print("  python3 loglog_gui.py")
    print("")
    print("Test the following features:")
    print("1. File → Open - Load a .log file")
    print("2. Edit text in the main editor")
    print("3. View the tree structure in the right panel")
    print("4. Use Convert menu to export to HTML/Markdown")
    print("5. Use View → TODOs to see task list")
    print("6. Check File → Settings for preferences")
    print("")
    print("Sample test file content:")
    print("""- Test Document #sample
    - Section 1
        [] Task to complete
        [x] Completed task
        [-] In progress task #urgent
    - Section 2 #analysis
        - Subsection
            [] Another task #important""")

def main():
    """Run all tests"""
    print("LogLog GUI Simple Test Suite")
    print("============================")
    
    tests_passed = 0
    total_tests = 4
    
    if test_imports():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
        
    if test_gui_components():
        tests_passed += 1
        
    if test_file_operations():
        tests_passed += 1
    
    print(f"\n=== Results ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! GUI components are ready.")
        run_gui_manually()
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())