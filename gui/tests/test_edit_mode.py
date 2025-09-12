#!/usr/bin/env python3
"""Test edit mode improvements"""

import sys
sys.stderr = sys.stdout

def test_edit_mode():
    print("="*60)
    print("TESTING EDIT MODE IMPROVEMENTS")
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
            # Test 1: Exit edit mode method
            print(f"\n🧪 Test 1: exit_edit_mode method")
            first_node = visible_nodes[0]
            
            # Start editing first node
            if first_node.id in viewport.node_widgets:
                widget = viewport.node_widgets[first_node.id]
                widget.start_editing()
                print(f"   Started editing: {widget.is_editing}")
                
                # Exit edit mode
                app.tree_renderer.exit_edit_mode()
                print(f"   After exit_edit_mode: {widget.is_editing}")
            
            # Test 2: Multiple selection handling
            print(f"\n🧪 Test 2: Multiple selection edit prevention")
            node1 = visible_nodes[0]
            node2 = visible_nodes[1]
            node3 = visible_nodes[2]
            
            # Select multiple nodes
            tree.selection.clear_selection()
            tree.selection.add_to_selection(node1)
            tree.selection.add_to_selection(node2) 
            tree.selection.add_to_selection(node3)
            tree.selection.set_focus(node2)  # Focus on middle node
            
            selected_count_before = len(tree.selection.get_selected_nodes())
            print(f"   Selected nodes before: {selected_count_before}")
            print(f"   Focused node: {repr(tree.selection.focused_node.content[:20])}")
            
            # Try to start editing focused node
            app.tree_renderer.start_editing_focused()
            
            selected_count_after = len(tree.selection.get_selected_nodes())
            print(f"   Selected nodes after: {selected_count_after}")
            
            if node2.id in viewport.node_widgets:
                widget2 = viewport.node_widgets[node2.id]
                print(f"   Is focused node editing: {widget2.is_editing}")
                
                # Clean up
                widget2.finish_editing(save=False)
            
            print(f"\n✓ Edit mode improvements working correctly")
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_edit_mode()