#!/usr/bin/env python3
"""Test canvas geometry issues with proper window sizing"""

import sys
sys.stderr = sys.stdout

def test_canvas_geometry():
    print("="*60)
    print("TESTING CANVAS GEOMETRY ISSUES")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create document
        scroll_content = """Test Document for Geometry
Item 1 - Testing geometry
Item 2 - Testing geometry  
Item 3 - Testing geometry
Item 4 - Testing geometry
Item 5 - Testing geometry
Item 6 - Testing geometry
Item 7 - Testing geometry
Item 8 - Testing geometry
Item 9 - Testing geometry
Item 10 - Testing geometry
Item 11 - Testing geometry
Item 12 - Testing geometry
Item 13 - Testing geometry
Item 14 - Testing geometry
Item 15 - Testing geometry
Item 16 - Testing geometry
Item 17 - Testing geometry
Item 18 - Testing geometry
Item 19 - Testing geometry
Item 20 - Testing geometry"""
        
        app = ModernLogLogGUI()
        
        # Set minimum window size to ensure proper geometry
        app.root.minsize(800, 600)
        app.root.geometry("900x700")
        
        test_file = "/tmp/geometry_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        
        # Force multiple geometry updates
        print(f"🔧 Forcing geometry updates...")
        app.root.update_idletasks()
        app.root.update()
        
        # Wait for after_idle callbacks
        def check_geometry():
            print(f"\\n📏 GEOMETRY ANALYSIS:")
            
            # Check window size
            window_width = app.root.winfo_width()
            window_height = app.root.winfo_height() 
            print(f"   • Window size: {window_width}x{window_height}")
            
            # Check viewport container size
            if hasattr(app.tree_renderer, 'viewport_container'):
                container_width = app.tree_renderer.viewport_container.winfo_width()
                container_height = app.tree_renderer.viewport_container.winfo_height()
                print(f"   • Viewport container: {container_width}x{container_height}")
            
            # Check viewport size
            viewport_width = viewport.winfo_width()
            viewport_height = viewport.winfo_height()
            print(f"   • Viewport size: {viewport_width}x{viewport_height}")
            
            # Check canvas size
            canvas_width = viewport.canvas.winfo_width()
            canvas_height = viewport.canvas.winfo_height()
            print(f"   • Canvas size: {canvas_width}x{canvas_height}")
            
            print(f"\\n🎯 DIAGNOSIS:")
            if canvas_width <= 1 or canvas_height <= 1:
                print(f"   ❌ Canvas is too small ({canvas_width}x{canvas_height})")
                print(f"   🔧 Canvas not getting proper size from parent")
                
                # Check parent chain
                parent = viewport.canvas.master
                print(f"   📍 Canvas parent: {parent}")
                if parent:
                    parent_width = parent.winfo_width()  
                    parent_height = parent.winfo_height()
                    print(f"   📍 Parent size: {parent_width}x{parent_height}")
                    
            else:
                print(f"   ✅ Canvas has reasonable size")
                
                # Test scrolling
                initial_view = viewport.canvas.canvasy(0)
                viewport.canvas.yview_scroll(5, "units")
                app.root.update_idletasks()
                after_scroll = viewport.canvas.canvasy(0)
                
                scroll_works = abs(after_scroll - initial_view) > 1
                print(f"   🖱️  Scrolling test: {scroll_works}")
                
            app.root.destroy()
        
        # Schedule geometry check after all updates
        app.root.after(100, check_geometry)
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_canvas_geometry()