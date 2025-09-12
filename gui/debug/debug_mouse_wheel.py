#!/usr/bin/env python3
"""Debug mouse wheel events to see what's actually happening"""

import sys
sys.stderr = sys.stdout

def debug_mouse_wheel():
    print("="*60)
    print("MOUSE WHEEL EVENT DEBUGGING")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create content
        lines = []
        for i in range(40):
            lines.append(f'    Line {i+1} - Debug mouse wheel events')
        
        content = 'Mouse Wheel Debug\\n' + '\\n'.join(lines)
        
        with open('/tmp/mousewheel_debug.log', 'w') as f:
            f.write(content)
        
        app = ModernLogLogGUI()
        app.root.geometry('900x600')
        
        # Load file
        app.tabs['/tmp/mousewheel_debug.log'] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab('/tmp/mousewheel_debug.log', False)
        app.tree_renderer.switch_to_file('/tmp/mousewheel_debug.log', content)
        
        viewport = app.tree_renderer.active_viewport
        app.root.update_idletasks()
        
        print(f"📋 Setup complete:")
        print(f"   Canvas size: {viewport.canvas.winfo_width()}x{viewport.canvas.winfo_height()}")
        print(f"   Scroll region: {viewport.canvas.cget('scrollregion')}")
        
        # Add debug handlers that log all events
        event_count = 0
        
        def debug_mousewheel(event):
            nonlocal event_count
            event_count += 1
            
            print(f"\\n🖱️  MOUSE WHEEL EVENT #{event_count}:")
            print(f"   • Widget: {event.widget}")
            print(f"   • Delta: {getattr(event, 'delta', 'N/A')}")
            print(f"   • Num: {getattr(event, 'num', 'N/A')}")
            print(f"   • X,Y: {event.x},{event.y}")
            
            # Get position before scroll
            pos_before = viewport.canvas.canvasy(0)
            
            # Calculate delta like our handler does
            if hasattr(event, 'delta') and event.delta:
                delta = int(-1 * (event.delta / 120))
                delta = max(-3, min(3, delta))  # Cap
                print(f"   • Calculated delta: {delta}")
            elif hasattr(event, 'num'):
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
                else:
                    delta = 0
                print(f"   • Linux delta: {delta}")
            else:
                delta = 0
                print(f"   • No delta calculated")
            
            # Try manual scroll
            if delta != 0:
                viewport.canvas.yview_scroll(delta, "units")
                app.root.update_idletasks()
            
            pos_after = viewport.canvas.canvasy(0)
            print(f"   • Position: {pos_before} -> {pos_after}")
            print(f"   • Moved: {abs(pos_after - pos_before) > 0}")
            
            return "break"  # Prevent other handlers
        
        def debug_button4(event):
            print(f"\\n🔘 BUTTON-4 EVENT (Linux scroll up)")
            debug_mousewheel(event)
            return "break"
            
        def debug_button5(event):
            print(f"\\n🔘 BUTTON-5 EVENT (Linux scroll down)")
            debug_mousewheel(event)
            return "break"
        
        # Replace existing bindings with debug versions
        viewport.canvas.bind("<MouseWheel>", debug_mousewheel)
        viewport.canvas.bind("<Button-4>", debug_button4)
        viewport.canvas.bind("<Button-5>", debug_button5)
        
        viewport.scrollable_frame.bind("<MouseWheel>", debug_mousewheel)
        viewport.scrollable_frame.bind("<Button-4>", debug_button4)
        viewport.scrollable_frame.bind("<Button-5>", debug_button5)
        
        print(f"\\n🔧 Debug handlers installed")
        print(f"\\n🖱️  INSTRUCTIONS:")
        print(f"   1. Move mouse over the FILE CONTENT area (right panel)")
        print(f"   2. Scroll with mouse wheel")
        print(f"   3. Watch the debug output above")
        print(f"   4. Each scroll should generate an event with details")
        
        # Set focus to canvas
        viewport.canvas.focus_set()
        
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mouse_wheel()