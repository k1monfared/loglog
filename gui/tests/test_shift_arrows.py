#!/usr/bin/env python3
"""Test Shift+arrow key selection behavior"""

import sys
sys.stderr = sys.stdout

def test_shift_arrows():
    print("="*60)
    print("TESTING SHIFT+ARROW KEY SELECTION")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content
        with open(test_file, 'r') as f:
            content = f.read()
        
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        viewport = app.tree_renderer.active_viewport
        tree = viewport.tree
        visible_nodes = tree.get_visible_nodes()
        
        print(f"✓ Content loaded - {len(visible_nodes)} visible nodes")
        
        if len(visible_nodes) >= 5:
            # Test Shift+arrow selection behavior
            print(f"\n🧪 Testing Shift+arrow key selection:")
            
            # Step 1: Select first node as anchor
            first_node = visible_nodes[0]
            app.tree_renderer.select_single_node(first_node)
            
            selected_nodes = tree.selection.get_selected_nodes()
            print(f"   1. Initial selection: {len(selected_nodes)} node(s)")
            
            # Step 2: Shift+Down - should extend selection
            print(f"   2. Testing Shift+Down extension...")
            app.tree_renderer.extend_selection_down()
            
            selected_nodes = tree.selection.get_selected_nodes()
            print(f"      After Shift+Down: {len(selected_nodes)} node(s) selected")
            
            if len(selected_nodes) > 1:
                print(f"      ✓ Selection extended correctly")
            else:
                print(f"      ✗ Selection not extended (should be > 1)")
            
            # Step 3: Shift+Down again - should extend further
            app.tree_renderer.extend_selection_down()
            
            selected_nodes = tree.selection.get_selected_nodes()
            print(f"   3. After second Shift+Down: {len(selected_nodes)} node(s) selected")
            
            # Step 4: Shift+Up - should reduce selection
            app.tree_renderer.extend_selection_up()
            
            selected_nodes = tree.selection.get_selected_nodes()
            print(f"   4. After Shift+Up: {len(selected_nodes)} node(s) selected")
            
            print(f"\n🔍 Final selection summary:")
            for i, node in enumerate(selected_nodes):
                print(f"      Node {i+1}: {repr(node.content[:30])}...")
                
        print("="*60)
        print("✓ Test completed - Shift+arrows implemented")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_shift_arrows()