#!/usr/bin/env python3
"""Test if scrolling actually works by simulating mouse wheel events"""

import sys
sys.stderr = sys.stdout

def test_actual_scrolling():
    print("="*60)
    print("TESTING ACTUAL SCROLLING FUNCTIONALITY")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create document that definitely needs scrolling
        content_lines = []
        for i in range(1, 51):  # 50 items 
            content_lines.append(f"    Item {i} - This is line {i} for scrolling test")
            if i % 5 == 0:
                content_lines.append(f"        Nested item {i}A")
                content_lines.append(f"        Nested item {i}B")
        
        scroll_content = "Large Scrollable Document\\n" + "\\n".join(content_lines)
        
        print(f"📄 Creating document with {len(content_lines)} items...")
        
        app = ModernLogLogGUI()
        
        # Don't show the main window initially
        app.root.withdraw()
        
        test_file = "/tmp/scroll_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        
        # Force geometry update
        app.root.update_idletasks()
        app.root.deiconify()  # Show the window
        app.root.update_idletasks()
        
        print(f"✅ Window opened with document loaded")
        
        # Get initial canvas view
        initial_view = viewport.canvas.canvasy(0)  # Top visible coordinate
        print(f"✅ Initial canvas view position: {initial_view}")
        
        # Simulate mouse wheel scroll down (positive delta)
        print(f"\\n🖱️  Simulating mouse wheel scroll DOWN...")
        
        # Create mock mouse wheel event
        class MockMouseWheelEvent:
            def __init__(self, delta):
                self.delta = delta
                self.x = 100
                self.y = 100
                
        # Simulate mouse wheel down (scroll content up)
        mock_event = MockMouseWheelEvent(-120)  # Negative delta = scroll down
        
        # Get the mouse wheel event handler
        canvas_bindings = viewport.canvas.bind("<MouseWheel>")
        if canvas_bindings:
            # Trigger the event handler manually
            viewport.canvas.event_generate("<MouseWheel>", x=100, y=100, delta=-120)
            app.root.update_idletasks()
            
            # Check if canvas view changed
            after_scroll_view = viewport.canvas.canvasy(0)
            print(f"✅ Canvas view after scroll: {after_scroll_view}")
            
            view_changed = abs(after_scroll_view - initial_view) > 0
            print(f"✅ View position changed: {view_changed}")
            
            if view_changed:
                print(f"\\n🎉 SUCCESS: Mouse wheel scrolling is WORKING!")
                print(f"   • Scrolled from {initial_view} to {after_scroll_view}")
            else:
                print(f"\\n❌ FAILED: Mouse wheel scrolling is NOT working")
                print(f"   • View position unchanged: {initial_view}")
                
        else:
            print(f"\\n❌ No mouse wheel binding found on canvas")
            
        # Test scrollbar functionality
        print(f"\\n📜 Testing scrollbar functionality...")
        if hasattr(viewport, 'scrollbar'):
            try:
                # Get initial scrollbar position
                initial_scrollbar = viewport.scrollbar.get()
                print(f"✅ Initial scrollbar position: {initial_scrollbar}")
                
                # Move scrollbar programmatically
                viewport.scrollbar.set(0.3, 0.5)  # Move to 30%-50% position
                app.root.update_idletasks()
                
                # Check if canvas view changed
                scrollbar_view = viewport.canvas.canvasy(0)
                print(f"✅ Canvas view after scrollbar move: {scrollbar_view}")
                
                scrollbar_working = abs(scrollbar_view - initial_view) > 5
                print(f"✅ Scrollbar functionality: {scrollbar_working}")
                
                if scrollbar_working:
                    print(f"\\n🎉 SUCCESS: Scrollbar is WORKING!")
                else:
                    print(f"\\n❌ FAILED: Scrollbar is NOT working") 
                    
            except Exception as e:
                print(f"❌ Scrollbar test error: {e}")
        else:
            print(f"❌ No scrollbar found")
            
        # Summary
        print(f"\\n📊 SCROLLING TEST SUMMARY:")
        print(f"   • Canvas scroll region: {viewport.canvas.cget('scrollregion')}")
        print(f"   • Mouse wheel bindings: {bool(canvas_bindings)}")
        print(f"   • Scrollbar present: {hasattr(viewport, 'scrollbar')}")
        
        print(f"\\n🔧 Keep window open for manual verification...")
        print(f"   - Try scrolling with mouse wheel")
        print(f"   - Try dragging the scrollbar")
        print(f"   - Close window when done")
        
        # Keep window open for manual testing
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_actual_scrolling()