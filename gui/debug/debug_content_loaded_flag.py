#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def debug_content_loaded_flag():
    """Debug the _content_loaded flag issue"""
    try:
        print("="*60)
        print("DEBUGGING _content_loaded FLAG")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        
        # Create GUI
        app = ModernLogLogGUI()
        print("✓ GUI created")
        
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Check viewport state before load_file
        print("\n🔍 Before load_file:")
        if test_file in app.tree_renderer.viewports:
            viewport = app.tree_renderer.viewports[test_file]
            flag = getattr(viewport, '_content_loaded', 'Not set')
            print(f"   Viewport exists: {viewport}")
            print(f"   _content_loaded flag: {flag}")
        else:
            print("   No viewport exists yet")
        
        # Read content manually
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"   Content length: {len(content)} chars")
        
        # Call load_file and trace what happens
        print(f"\n📂 Calling load_file({test_file})...")
        
        # Let's manually trace the execution
        try:
            # Check if file is already open
            if test_file in app.tabs:
                print("   ❌ File already in tabs - will switch instead of load")
                
            # Create tab (mimicking load_file)
            print("   Creating new tab...")
            app.tabs[test_file] = {
                'tree_state': None,
                'modified': False,
                'is_temporary': False
            }
            app.tab_bar.add_tab(test_file, False)
            
            # Check viewport after tab creation
            print("\n🔍 After tab creation:")
            viewport = app.tree_renderer.get_or_create_viewport(test_file)
            flag = getattr(viewport, '_content_loaded', 'Not set')
            print(f"   Viewport: {viewport}")
            print(f"   _content_loaded flag: {flag}")
            
            # Now call switch_to_file manually
            print(f"\n🔄 Calling switch_to_file with content...")
            app.tree_renderer.switch_to_file(test_file, content)
            
            # Check result
            print("\n✅ After switch_to_file:")
            tree = viewport.tree
            print(f"   Visible nodes: {len(tree.get_visible_nodes())}")
            print(f"   _content_loaded flag: {getattr(viewport, '_content_loaded', 'Not set')}")
            
        except Exception as e:
            print(f"✗ Error during manual trace: {e}")
            import traceback
            traceback.print_exc()
            
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_content_loaded_flag()