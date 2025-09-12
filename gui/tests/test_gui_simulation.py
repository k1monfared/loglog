#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def simulate_gui_file_loading():
    """Exactly simulate what the GUI does when loading a file"""
    try:
        print("="*60)
        print("SIMULATING GUI FILE LOADING PROCESS")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        
        # Create GUI
        app = ModernLogLogGUI()
        print("✓ GUI created")
        
        # Load the same file
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Read file content (like GUI does)
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"✓ File read ({len(content)} chars)")
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return
            
        # Call load_file like the GUI does
        try:
            app.load_file(test_file)
            print("✓ load_file() called")
        except Exception as e:
            print(f"✗ Error in load_file(): {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Check the tree state
        try:
            if hasattr(app, 'tree_renderer') and app.tree_renderer.active_viewport:
                viewport = app.tree_renderer.active_viewport
                tree = viewport.tree
                visible_nodes = tree.get_visible_nodes()
                all_nodes = tree.get_all_nodes()
                
                print(f"✓ Tree state:")
                print(f"   Active viewport: {viewport}")
                print(f"   Tree: {tree}")
                print(f"   All nodes: {len(all_nodes)}")
                print(f"   Visible nodes: {len(visible_nodes)}")
                print(f"   Node widgets: {len(viewport.node_widgets)}")
                
                if visible_nodes:
                    print(f"   First visible: {repr(visible_nodes[0].content[:50])}")
                else:
                    print("   ❌ NO VISIBLE NODES - This is the problem!")
                    
                # Check tree root
                if tree.root:
                    print(f"   Root children: {len(tree.root.children)}")
                    if tree.root.children:
                        print(f"   First child: {repr(tree.root.children[0].content[:50])}")
                        
            else:
                print("✗ No active viewport found")
                
        except Exception as e:
            print(f"✗ Error checking tree state: {e}")
            import traceback
            traceback.print_exc()
            
        print("="*60)
        
    except Exception as e:
        print(f"✗ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_gui_file_loading()