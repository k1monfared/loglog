#!/usr/bin/env python3
"""Test file content scrolling specifically"""

import sys
sys.stderr = sys.stdout

def test_content_scrolling():
    print("="*60)
    print("TESTING FILE CONTENT AREA SCROLLING")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create test content with many lines
        lines = []
        for i in range(80):
            lines.append(f'    Content Line {i+1} - This is a line in the main file content area (right panel)')
            if i % 10 == 9:
                lines.append(f'        Nested content under line {i+1}')
                lines.append(f'        More nested content under line {i+1}')
        
        content = 'File Content Scrolling Test\\n' + '\\n'.join(lines)
        
        with open('/tmp/content_scroll_test.log', 'w') as f:
            f.write(content)
        
        app = ModernLogLogGUI()
        app.root.geometry("1000x700")
        
        # Load the file
        app.open_file('/tmp/content_scroll_test.log')
        
        # Get the content viewport 
        viewport = app.tree_renderer.active_viewport
        app.root.update_idletasks()
        
        print(f"📋 File Content Area Analysis:")
        print(f"   • Active viewport: {viewport is not None}")
        
        if viewport:
            print(f"   • Canvas size: {viewport.canvas.winfo_width()}x{viewport.canvas.winfo_height()}")
            print(f"   • Scroll region: {viewport.canvas.cget('scrollregion')}")
            print(f"   • Frame size: {viewport.scrollable_frame.winfo_reqwidth()}x{viewport.scrollable_frame.winfo_reqheight()}")
            
            # Check bindings
            canvas_wheel = viewport.canvas.bind("<MouseWheel>")
            canvas_btn4 = viewport.canvas.bind("<Button-4>") 
            canvas_btn5 = viewport.canvas.bind("<Button-5>")
            
            print(f"\\n🖱️  Content Canvas Mouse Bindings:")
            print(f"   • MouseWheel: {bool(canvas_wheel)}")
            print(f"   • Button-4 (Linux up): {bool(canvas_btn4)}")
            print(f"   • Button-5 (Linux down): {bool(canvas_btn5)}")
            
            # Check TreeView bindings (potential conflict)
            tree_wheel = app.file_tree.file_tree.bind("<MouseWheel>") if hasattr(app.file_tree, 'file_tree') else None
            tree_btn4 = app.file_tree.file_tree.bind("<Button-4>") if hasattr(app.file_tree, 'file_tree') else None
            tree_btn5 = app.file_tree.file_tree.bind("<Button-5>") if hasattr(app.file_tree, 'file_tree') else None
            
            print(f"\\n🌳 Directory TreeView Mouse Bindings (potential conflict):")
            print(f"   • MouseWheel: {bool(tree_wheel)}")
            print(f"   • Button-4: {bool(tree_btn4)}")  
            print(f"   • Button-5: {bool(tree_btn5)}")
            
            # Test programmatic scrolling
            print(f"\\n🧪 Testing programmatic content scrolling:")
            pos_before = viewport.canvas.canvasy(0)
            viewport.canvas.yview_scroll(10, "units")
            app.root.update_idletasks()
            pos_after = viewport.canvas.canvasy(0)
            
            print(f"   • Before scroll: {pos_before}")
            print(f"   • After yview_scroll(10, 'units'): {pos_after}")
            print(f"   • Programmatic scrolling works: {abs(pos_after - pos_before) > 1}")
            
            # Focus analysis
            current_focus = app.root.focus_get()
            print(f"\\n🎯 Focus Analysis:")
            print(f"   • Current focus widget: {current_focus}")
            print(f"   • Focus widget type: {type(current_focus).__name__ if current_focus else 'None'}")
            
            # Try setting focus to canvas
            viewport.canvas.focus_set()
            app.root.update_idletasks()
            new_focus = app.root.focus_get()
            print(f"   • After canvas.focus_set(): {new_focus}")
            print(f"   • Canvas has focus: {new_focus == viewport.canvas}")
            
        print(f"\\n🔍 DIAGNOSIS:")
        print(f"   Mouse wheel events may be:")
        print(f"   1. Not reaching the canvas (focus issue)")
        print(f"   2. Being intercepted by TreeView") 
        print(f"   3. Canvas events not properly bound")
        print(f"   4. Event handler not executing properly")
        
        print(f"\\n🖱️  MANUAL TEST:")
        print(f"   1. Move mouse over the FILE CONTENT (right panel)")
        print(f"   2. Try scrolling with mouse wheel")
        print(f"   3. Check if content scrolls up/down")
        print(f"   4. Also try clicking in content area first, then scroll")
        
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_content_scrolling()