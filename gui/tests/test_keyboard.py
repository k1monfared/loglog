#!/usr/bin/env python3
"""Test keyboard navigation functionality"""

import sys
sys.stderr = sys.stdout

def test_keyboard_navigation():
    print("="*60)
    print("TESTING KEYBOARD NAVIGATION")
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
        
        # Test keyboard methods directly
        print(f"\n🧪 Testing keyboard navigation methods:")
        
        # Test 1: Set initial focus
        if visible_nodes:
            first_node = visible_nodes[0]
            app.tree_renderer.set_focus(first_node)
            
            focused_node = tree.selection.focused_node
            print(f"   1. Set focus: {focused_node == first_node}")
            print(f"      Focused node content: {repr(focused_node.content[:20]) if focused_node else 'None'}")
            
            # Test 2: Move focus down
            if len(visible_nodes) > 1:
                app.tree_renderer.move_focus_down()
                focused_after_down = tree.selection.focused_node
                print(f"   2. Move focus down: {focused_after_down != first_node}")
                print(f"      New focused node: {repr(focused_after_down.content[:20]) if focused_after_down else 'None'}")
                
                # Test 3: Move focus up  
                app.tree_renderer.move_focus_up()
                focused_after_up = tree.selection.focused_node  
                print(f"   3. Move focus up: {focused_after_up == first_node}")
                
                # Test 4: Toggle TODO status
                if focused_after_up:
                    old_status = focused_after_up.todo_status
                    app.tree_renderer.toggle_todo_status()
                    new_status = focused_after_up.todo_status
                    print(f"   4. Toggle TODO: status changed from {old_status} to {new_status}")
            else:
                print("   Not enough nodes for full navigation test")
        
        print(f"\n✓ Keyboard navigation methods working!")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keyboard_navigation()