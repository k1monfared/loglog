#!/usr/bin/env python3
"""Test arrow key selection behavior"""

import sys
sys.stderr = sys.stdout

def test_arrow_selection():
    print("="*60)
    print("TESTING ARROW KEY SELECTION BEHAVIOR")
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
        
        if len(visible_nodes) >= 3:
            # Test single selection behavior with arrow keys
            print(f"\n🧪 Testing arrow key selection behavior:")
            
            # Step 1: Select first node
            first_node = visible_nodes[0]
            app.tree_renderer.select_single_node(first_node)
            
            selected_count = len(tree.selection.get_selected_nodes())
            focused_node = tree.selection.focused_node
            print(f"   1. Initial selection: {selected_count} nodes, focused on: {repr(focused_node.content[:20])}")
            
            # Step 2: Move down - should select only second node
            app.tree_renderer.move_focus_down()
            
            selected_count = len(tree.selection.get_selected_nodes())
            focused_node = tree.selection.focused_node
            print(f"   2. After move down: {selected_count} nodes, focused on: {repr(focused_node.content[:20])}")
            
            # Step 3: Move down again - should select only third node  
            app.tree_renderer.move_focus_down()
            
            selected_count = len(tree.selection.get_selected_nodes())
            focused_node = tree.selection.focused_node
            print(f"   3. After move down again: {selected_count} nodes, focused on: {repr(focused_node.content[:20])}")
            
            # Step 4: Move up - should select only second node
            app.tree_renderer.move_focus_up()
            
            selected_count = len(tree.selection.get_selected_nodes())
            focused_node = tree.selection.focused_node
            print(f"   4. After move up: {selected_count} nodes, focused on: {repr(focused_node.content[:20])}")
            
            # Verify only one node is selected each time
            if selected_count == 1:
                print(f"   ✓ Correct: Only 1 node selected (file browser behavior)")
            else:
                print(f"   ✗ Error: {selected_count} nodes selected (should be 1)")
                
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arrow_selection()