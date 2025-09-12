#!/usr/bin/env python3
import sys
import time
sys.stderr = sys.stdout

def test_async_loading():
    """Test GUI loading with proper async handling"""
    try:
        print("="*60)
        print("TESTING ASYNC LOADING")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        
        # Create GUI
        app = ModernLogLogGUI()
        print("✓ GUI created")
        
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load file
        print(f"📂 Loading file: {test_file}")
        app.load_file(test_file)
        print("✓ load_file() called")
        
        # Check state immediately (should be empty due to async)
        print("\n⏱️ Immediate state check:")
        if app.tree_renderer.active_viewport:
            tree = app.tree_renderer.active_viewport.tree
            print(f"   Visible nodes: {len(tree.get_visible_nodes())}")
        else:
            print("   No active viewport")
        
        # Process pending idle events (this should trigger the content loading)
        print("\n🔄 Processing pending events...")
        app.root.update_idletasks()
        
        # Check state after processing
        print("\n✅ After processing events:")
        if app.tree_renderer.active_viewport:
            tree = app.tree_renderer.active_viewport.tree
            visible_nodes = tree.get_visible_nodes()
            print(f"   Visible nodes: {len(visible_nodes)}")
            print(f"   Root children: {len(tree.root.children) if tree.root else 0}")
            
            if visible_nodes:
                print(f"   First visible: {repr(visible_nodes[0].content[:50])}")
                print("   ✅ SUCCESS - Content loaded properly!")
            else:
                print("   ❌ Still no visible nodes after processing events")
        else:
            print("   ❌ No active viewport")
            
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_async_loading()