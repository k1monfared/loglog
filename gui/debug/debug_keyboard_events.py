#!/usr/bin/env python3
"""Debug keyboard event capture in the GUI"""

import sys
sys.stderr = sys.stdout

def debug_keyboard_events():
    print("="*60)
    print("DEBUGGING KEYBOARD EVENT CAPTURE")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI, TreeRenderer
        
        # Store original method
        original_handle = TreeRenderer.handle_keyboard_event
        
        # Add debug wrapper
        def debug_handle_keyboard_event(self, event):
            print(f"🔥 KEYBOARD EVENT CAPTURED: {event.keysym}")
            print(f"   Widget: {self}")
            print(f"   Active viewport: {self.active_viewport}")
            print(f"   Event state: {event.state}")
            print(f"   Event char: {repr(event.char)}")
            result = original_handle(self, event)
            print(f"   Handler result: {result}")
            return result
        
        # Monkey patch with debug version
        TreeRenderer.handle_keyboard_event = debug_handle_keyboard_event
        
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content
        with open(test_file, 'r') as f:
            content = f.read()
        
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        print(f"✓ GUI loaded")
        print(f"✓ TreeRenderer focus: {app.tree_renderer.focus_get()}")
        print(f"✓ TreeRenderer has focus: {app.tree_renderer == app.root.focus_get()}")
        print(f"✓ Active viewport: {app.tree_renderer.active_viewport}")
        
        # Force focus to tree renderer
        app.tree_renderer.focus_set()
        print(f"✓ After focus_set - TreeRenderer has focus: {app.tree_renderer == app.root.focus_get()}")
        
        print("\n🔍 Try pressing arrow keys, Enter, or Space...")
        print("🔍 Look for '🔥 KEYBOARD EVENT CAPTURED' messages")
        print("🔍 Close the window to exit")
        
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_keyboard_events()