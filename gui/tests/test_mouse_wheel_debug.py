#!/usr/bin/env python3
"""Debug mouse wheel event handling"""

import sys
sys.stderr = sys.stdout

def test_mouse_wheel_debug():
    print("="*60)
    print("MOUSE WHEEL EVENT DEBUG")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create large document 
        lines = []
        for i in range(50):
            lines.append(f'    Item {i} - Long line for mouse wheel testing')
        content = 'Mouse Wheel Test\\n' + '\\n'.join(lines)
        
        with open('/tmp/mousewheel_test.log', 'w') as f:
            f.write(content)
        
        app = ModernLogLogGUI() 
        app.root.geometry("800x600")
        
        app.tabs['/tmp/mousewheel_test.log'] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab('/tmp/mousewheel_test.log', False)
        app.tree_renderer.switch_to_file('/tmp/mousewheel_test.log', content)
        
        viewport = app.tree_renderer.active_viewport
        app.root.update_idletasks()
        
        # Counter for mouse wheel events
        event_count = 0
        scroll_positions = []
        
        def debug_mouse_wheel(event):
            nonlocal event_count, scroll_positions
            event_count += 1
            
            print(f"🖱️  Mouse wheel event #{event_count}:")
            print(f"   • Delta: {event.delta}")
            print(f"   • Calculated scroll: {int(-1 * (event.delta / 120))}")
            
            # Get position before
            pos_before = viewport.canvas.canvasy(0)
            
            # Do the actual scroll
            scroll_amount = int(-1 * (event.delta / 120))
            viewport.canvas.yview_scroll(scroll_amount, "units")
            
            # Get position after
            pos_after = viewport.canvas.canvasy(0)
            
            scroll_positions.append((pos_before, pos_after))
            
            print(f"   • Position: {pos_before} -> {pos_after} (diff: {pos_after - pos_before})")
            
            if len(scroll_positions) >= 3:
                print(f"\\n📊 MOUSE WHEEL SUMMARY after {event_count} events:")
                unique_positions = len(set([p[1] for p in scroll_positions]))
                print(f"   • Unique positions: {unique_positions}")
                if unique_positions > 1:
                    print(f"   ✅ MOUSE WHEEL SCROLLING IS WORKING!")
                else:
                    print(f"   ❌ MOUSE WHEEL SCROLLING IS BROKEN")
                    
        # Replace the existing mouse wheel handler
        viewport.canvas.bind("<MouseWheel>", debug_mouse_wheel)
        viewport.scrollable_frame.bind("<MouseWheel>", debug_mouse_wheel)
        
        print(f"🎯 Debug info:")
        print(f"   • Canvas size: {viewport.canvas.winfo_width()}x{viewport.canvas.winfo_height()}")
        print(f"   • Scroll region: {viewport.canvas.cget('scrollregion')}")
        print(f"   • Mouse wheel bound to canvas: {bool(viewport.canvas.bind('<MouseWheel>'))}") 
        
        print(f"\\n🖱️  MANUAL TEST: Use mouse wheel over the window")
        print(f"   Events will be logged here. Scroll up and down several times.")
        print(f"   Close window when done testing.")
        
        # Focus the canvas to ensure it receives events
        viewport.canvas.focus_set()
        
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mouse_wheel_debug()