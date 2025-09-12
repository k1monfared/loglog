#!/usr/bin/env python3
"""Test the new Shift+Click selection behavior"""

import sys
sys.stderr = sys.stdout

def test_shift_selection():
    print("="*60)
    print("TESTING IMPROVED SHIFT+CLICK SELECTION")
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
        
        # Test anchor-based selection
        if len(visible_nodes) >= 5:
            print(f"\n🧪 Testing anchor-based Shift+Click behavior:")
            
            # Step 1: Select first node (this becomes the anchor)
            first_node = visible_nodes[0]
            app.tree_renderer.select_single_node(first_node)
            print(f"   1. Selected anchor node: {repr(first_node.content[:30])}")
            print(f"      Anchor: {app.tree_renderer.selection_anchor == first_node}")
            print(f"      Selected count: {len(tree.selection.get_selected_nodes())}")
            
            # Step 2: Shift+Click third node (should select range 0-2)
            third_node = visible_nodes[2]
            # Simulate shift+click by directly testing the logic
            anchor_node = app.tree_renderer.selection_anchor
            if anchor_node in visible_nodes and third_node in visible_nodes:
                start_idx = visible_nodes.index(anchor_node)
                end_idx = visible_nodes.index(third_node)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                # Manually clear ALL selections
                for selected_node in list(tree.selection.selected_nodes):
                    tree.selection.remove_from_selection(selected_node)
                for i in range(start_idx, end_idx + 1):
                    tree.selection.add_to_selection(visible_nodes[i])
                tree.selection.set_focus(third_node)
                
            print(f"   2. Shift+Clicked node 2: {repr(third_node.content[:30])}")
            print(f"      Selected count: {len(tree.selection.get_selected_nodes())}")
            print(f"      Selected nodes: {[n.content[:20] for n in tree.selection.get_selected_nodes()]}")
            
            # Step 3: Shift+Click fifth node (should select range 0-4, expanding from anchor)
            fifth_node = visible_nodes[4]
            anchor_node = app.tree_renderer.selection_anchor
            if anchor_node in visible_nodes and fifth_node in visible_nodes:
                start_idx = visible_nodes.index(anchor_node)
                end_idx = visible_nodes.index(fifth_node)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                # Manually clear ALL selections
                for selected_node in list(tree.selection.selected_nodes):
                    tree.selection.remove_from_selection(selected_node)
                for i in range(start_idx, end_idx + 1):
                    tree.selection.add_to_selection(visible_nodes[i])
                tree.selection.set_focus(fifth_node)
                
            print(f"   3. Shift+Clicked node 4: {repr(fifth_node.content[:30])}")
            print(f"      Selected count: {len(tree.selection.get_selected_nodes())}")
            print(f"      Selected nodes: {[n.content[:20] for n in tree.selection.get_selected_nodes()]}")
            
            # Step 4: Shift+Click second node (should select range 0-1, shrinking from anchor)
            second_node = visible_nodes[1]
            anchor_node = app.tree_renderer.selection_anchor
            if anchor_node in visible_nodes and second_node in visible_nodes:
                start_idx = visible_nodes.index(anchor_node)
                end_idx = visible_nodes.index(second_node)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                # Manually clear ALL selections
                for selected_node in list(tree.selection.selected_nodes):
                    tree.selection.remove_from_selection(selected_node)
                for i in range(start_idx, end_idx + 1):
                    tree.selection.add_to_selection(visible_nodes[i])
                tree.selection.set_focus(second_node)
                
            print(f"   4. Shift+Clicked node 1: {repr(second_node.content[:30])}")
            print(f"      Selected count: {len(tree.selection.get_selected_nodes())}")
            print(f"      Selected nodes: {[n.content[:20] for n in tree.selection.get_selected_nodes()]}")
            
            print(f"\n✓ Anchor remains: {app.tree_renderer.selection_anchor == first_node}")
            
        else:
            print("   ❌ Not enough visible nodes to test anchor behavior")
        
        print("="*60)
        print("✓ Test completed - ready for manual testing")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_shift_selection()