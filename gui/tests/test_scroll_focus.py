#!/usr/bin/env python3
"""Test scroll event focus and binding conflicts"""

import sys
sys.stderr = sys.stdout

def test_scroll_focus():
    print("="*60)
    print("TESTING SCROLL EVENT FOCUS AND BINDINGS")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create document
        scroll_content = """Test Document
Item 1 - Testing focus
Item 2 - Testing focus  
Item 3 - Testing focus
Item 4 - Testing focus
Item 5 - Testing focus
Item 6 - Testing focus
Item 7 - Testing focus
Item 8 - Testing focus
Item 9 - Testing focus
Item 10 - Testing focus
Item 11 - Testing focus
Item 12 - Testing focus
Item 13 - Testing focus
Item 14 - Testing focus
Item 15 - Testing focus
Item 16 - Testing focus
Item 17 - Testing focus
Item 18 - Testing focus
Item 19 - Testing focus
Item 20 - Testing focus"""
        
        app = ModernLogLogGUI()
        
        # Don't show window
        app.root.withdraw() 
        
        test_file = "/tmp/focus_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        app.root.update_idletasks()
        
        print(f"🔍 Analyzing scroll event bindings...")
        
        # Check all widgets that might have mouse wheel bindings
        widgets_to_check = [
            ("viewport.canvas", viewport.canvas),
            ("viewport.scrollable_frame", viewport.scrollable_frame),
            ("file_tree", app.file_tree.file_tree if hasattr(app.file_tree, 'file_tree') else None),
            ("main_content_frame", app.main_content if hasattr(app, 'main_content') else None)
        ]
        
        for name, widget in widgets_to_check:
            if widget:
                bindings = widget.bind("<MouseWheel>")
                print(f"   • {name}: MouseWheel binding = {bool(bindings)}")
            else:
                print(f"   • {name}: Widget not found")
                
        # Check focus 
        current_focus = app.root.focus_get()
        print(f"\\n🎯 Current focus widget: {current_focus}")
        
        # Force focus to canvas
        viewport.canvas.focus_set()
        app.root.update_idletasks()
        new_focus = app.root.focus_get()
        print(f"🎯 After setting focus to canvas: {new_focus}")
        
        # Test programmatic scrolling
        print(f"\\n📐 Testing programmatic canvas scrolling...")
        
        # Get initial position
        initial_view = viewport.canvas.canvasy(0)
        print(f"   • Initial canvas top: {initial_view}")
        
        # Try yview_scroll
        viewport.canvas.yview_scroll(5, "units")
        app.root.update_idletasks()
        
        after_yview = viewport.canvas.canvasy(0)
        print(f"   • After yview_scroll(5, 'units'): {after_yview}")
        
        # Try yview_moveto
        viewport.canvas.yview_moveto(0.3)
        app.root.update_idletasks()
        
        after_moveto = viewport.canvas.canvasy(0)
        print(f"   • After yview_moveto(0.3): {after_moveto}")
        
        # Check if ANY scrolling worked
        scrolling_works = (
            abs(after_yview - initial_view) > 1 or 
            abs(after_moveto - initial_view) > 1
        )
        
        print(f"\\n📊 SCROLL ANALYSIS:")
        print(f"   • Scroll region: {viewport.canvas.cget('scrollregion')}")
        print(f"   • Canvas size: {viewport.canvas.winfo_width()}x{viewport.canvas.winfo_height()}")
        print(f"   • Scrollable frame size: {viewport.scrollable_frame.winfo_reqwidth()}x{viewport.scrollable_frame.winfo_reqheight()}")
        print(f"   • Programmatic scrolling: {scrolling_works}")
        
        if scrolling_works:
            print(f"\\n✅ Canvas scrolling mechanism is FUNCTIONAL")
            print(f"   → Problem is likely in mouse wheel event handling")
        else:
            print(f"\\n❌ Canvas scrolling mechanism is BROKEN")
            print(f"   → Problem is in the underlying scroll setup")
            
        # Test direct mouse wheel function call
        print(f"\\n🖱️  Testing direct mouse wheel handler...")
        
        # Find the actual bound function
        mouse_wheel_func = viewport.canvas.bind("<MouseWheel>")
        if mouse_wheel_func:
            print(f"   • Mouse wheel handler found: {mouse_wheel_func}")
            
            # Create a mock event and test the handler
            class MockEvent:
                def __init__(self):
                    self.delta = -120
                    self.x = 100
                    self.y = 100
            
            try:
                # Get current position before mock event
                before_mock = viewport.canvas.canvasy(0)
                
                # Manually call the yview_scroll that should happen
                viewport.canvas.yview_scroll(1, "units")  # Simulate scroll down
                app.root.update_idletasks()
                
                after_mock = viewport.canvas.canvasy(0)
                
                print(f"   • Before manual scroll: {before_mock}")
                print(f"   • After manual scroll: {after_mock}")
                
                manual_scroll_works = abs(after_mock - before_mock) > 1
                print(f"   • Manual yview_scroll works: {manual_scroll_works}")
                
            except Exception as e:
                print(f"   • Error testing manual scroll: {e}")
        else:
            print(f"   • No mouse wheel handler found!")
            
        app.root.destroy()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scroll_focus()