#!/usr/bin/env python3
"""Simple keyboard navigation test without GUI complexity"""

import sys
sys.stderr = sys.stdout

def test_keyboard_simple():
    print("="*60)
    print("SIMPLE KEYBOARD TEST")  
    print("="*60)
    
    try:
        import tkinter as tk
        from loglog_gui import TreeRenderer, SystemTheme
        
        # Create minimal GUI with just TreeRenderer
        root = tk.Tk()
        root.title("Keyboard Test")
        root.geometry("400x300")
        
        theme = SystemTheme()
        tree_renderer = TreeRenderer(root, theme)
        tree_renderer.pack(fill='both', expand=True)
        
        # Load test content
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        with open(test_file, 'r') as f:
            content = f.read()
        
        tree_renderer.switch_to_file(test_file, content)
        
        # Force focus
        tree_renderer.focus_set()
        
        print(f"✓ Simple GUI created")
        print(f"✓ TreeRenderer has focus: {tree_renderer == root.focus_get()}")
        print(f"✓ Active viewport: {tree_renderer.active_viewport is not None}")
        
        # Add debug handler
        def debug_key(event):
            print(f"🔥 KEY EVENT: {event.keysym} - {event.char}")
            return tree_renderer.handle_keyboard_event(event)
        
        # Bind at root level to capture all events
        root.bind_all("<Key>", debug_key)
        
        print(f"\n🔍 Press arrow keys, Enter, Space...")
        print(f"🔍 Close window to exit")
        
        root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keyboard_simple()