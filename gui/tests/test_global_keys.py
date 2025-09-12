#!/usr/bin/env python3
"""Test global keyboard bindings"""

import sys
sys.stderr = sys.stdout

def test_global_keys():
    print("="*60)
    print("TESTING GLOBAL KEYBOARD BINDINGS")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI, TreeRenderer
        
        # Add debug to TreeRenderer keyboard handler
        original_handle = TreeRenderer.handle_keyboard_event
        def debug_handle(self, event):
            print(f"🔥 TreeRenderer.handle_keyboard_event called: {event.keysym}")
            result = original_handle(self, event)
            print(f"   Result: {result}")
            return result
        
        TreeRenderer.handle_keyboard_event = debug_handle
        
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content  
        with open(test_file, 'r') as f:
            content = f.read()
        
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        print(f"✓ GUI loaded")
        print(f"✓ Current focus: {app.root.focus_get()}")
        print(f"✓ Focus class: {app.root.focus_get().winfo_class() if app.root.focus_get() else 'None'}")
        
        # Set initial focus to a visible node
        viewport = app.tree_renderer.active_viewport
        if viewport and viewport.tree.get_visible_nodes():
            first_node = viewport.tree.get_visible_nodes()[0]
            app.tree_renderer.set_focus(first_node)
            print(f"✓ Set focus to first node: {repr(first_node.content[:20])}")
        
        print(f"\n🔍 Try pressing arrow keys, Enter, or Space...")
        print(f"🔍 Look for '🔥 TreeRenderer.handle_keyboard_event called' messages")
        print(f"🔍 Close window to exit")
        
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_global_keys()