#!/usr/bin/env python3
import sys
import traceback
import threading
import time

# Redirect stderr to stdout for capture
sys.stderr = sys.stdout

def test_gui_operations():
    """Test GUI operations that should trigger errors"""
    try:
        print("="*60)
        print("TESTING GUI OPERATIONS")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        app = ModernLogLogGUI()
        
        print("✓ GUI initialized")
        
        # Test file loading
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        print(f"Loading test file: {test_file}")
        
        try:
            app.load_file(test_file)
            print("✓ File loaded successfully")
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            traceback.print_exc()
        
        # Test getting tree content
        try:
            if hasattr(app, 'tree_renderer') and app.tree_renderer.active_viewport:
                tree = app.tree_renderer.active_viewport.tree
                nodes = tree.get_visible_nodes()
                print(f"✓ Found {len(nodes)} visible nodes")
                
                # Try to interact with first node if it exists
                if nodes:
                    first_node = nodes[0]
                    print(f"✓ First node: {first_node.data[:50]}...")
                    
                    # Try setting focus (this should trigger the error)
                    try:
                        app.tree_renderer.set_focus(first_node)
                        print("✓ Focus set successfully")
                    except Exception as e:
                        print(f"✗ Error setting focus: {e}")
                        traceback.print_exc()
                        
        except Exception as e:
            print(f"✗ Error accessing tree: {e}")
            traceback.print_exc()
            
        print("="*60)
        print("TEST COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Critical error in test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_operations()