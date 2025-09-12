#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def debug_mouse_events():
    """Debug mouse events to see what's happening"""
    try:
        print("="*60)
        print("DEBUGGING MOUSE EVENTS")
        print("="*60)
        
        # Add debugging to TreeRenderer drag methods
        from loglog_gui import TreeRenderer
        
        # Store original methods
        original_start = TreeRenderer.start_drag_selection
        original_update = TreeRenderer.update_drag_selection
        original_end = TreeRenderer.end_drag_selection
        
        # Add debug wrappers
        def debug_start_drag_selection(self, node):
            print(f"🔥 START_DRAG_SELECTION called with node: {repr(node.content[:30])}")
            return original_start(self, node)
        
        def debug_update_drag_selection(self, node):
            print(f"🔄 UPDATE_DRAG_SELECTION called with node: {repr(node.content[:30])}")
            print(f"   is_dragging: {self.is_dragging}")
            print(f"   drag_start_node: {self.drag_start_node}")
            return original_update(self, node)
        
        def debug_end_drag_selection(self):
            print(f"🛑 END_DRAG_SELECTION called")
            print(f"   was_dragging: {self.is_dragging}")
            return original_end(self)
        
        # Monkey patch with debug versions
        TreeRenderer.start_drag_selection = debug_start_drag_selection
        TreeRenderer.update_drag_selection = debug_update_drag_selection
        TreeRenderer.end_drag_selection = debug_end_drag_selection
        
        print("✓ Debug wrappers installed")
        print("✓ Now interact with the GUI to see mouse events...")
        print("✓ Look for 🔥 START, 🔄 UPDATE, 🛑 END messages")
        
        # Start GUI
        from loglog_gui import ModernLogLogGUI
        app = ModernLogLogGUI()
        
        print("✓ GUI started - try clicking and dragging on nodes!")
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mouse_events()