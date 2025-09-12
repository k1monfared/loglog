#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def test_drag_events():
    """Test if drag events are being triggered"""
    try:
        print("="*60)
        print("TESTING DRAG EVENTS")
        print("="*60)
        
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
        
        print(f"✓ Content loaded")
        print(f"   All nodes: {len(tree.get_all_nodes())}")
        print(f"   Visible nodes: {len(tree.get_visible_nodes())}")
        print(f"   Node widgets: {len(viewport.node_widgets)}")
        
        # Check drag state
        print(f"\n🔍 Drag state:")
        print(f"   is_dragging: {app.tree_renderer.is_dragging}")
        print(f"   drag_start_node: {app.tree_renderer.drag_start_node}")
        
        # Test drag methods
        visible_nodes = tree.get_visible_nodes()
        if len(visible_nodes) >= 2:
            first_node = visible_nodes[0]
            second_node = visible_nodes[1]
            
            print(f"\n🧪 Testing drag methods:")
            print(f"   First node: {repr(first_node.content[:30])}")
            print(f"   Second node: {repr(second_node.content[:30])}")
            
            # Test start drag
            app.tree_renderer.start_drag_selection(first_node)
            print(f"   After start_drag: is_dragging={app.tree_renderer.is_dragging}")
            
            # Test update drag
            app.tree_renderer.update_drag_selection(second_node)
            print(f"   After update_drag: selected_count={len(tree.selection.get_selected_nodes())}")
            
            # Test end drag
            app.tree_renderer.end_drag_selection()
            print(f"   After end_drag: is_dragging={app.tree_renderer.is_dragging}")
            
        else:
            print("   ❌ Not enough visible nodes to test drag")
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_drag_events()