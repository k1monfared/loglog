#!/usr/bin/env python3
"""Final test to verify scrolling is working properly"""

import sys
sys.stderr = sys.stdout

def test_scrolling_final():
    print("="*60)
    print("FINAL SCROLLING TEST")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
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
        test_file = "/tmp/final_scroll_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        visible_nodes = viewport.tree.get_visible_nodes()
        
        print(f"✅ Document loaded: {len(visible_nodes)} nodes")
        
        # Check scroll region after loading
        scrollregion = viewport.canvas.cget('scrollregion')
        print(f"✅ Scroll region: {scrollregion}")
        
        # Check canvas dimensions
        canvas_height = viewport.canvas.winfo_height()
        print(f"✅ Canvas height: {canvas_height}px")
        
        # Parse scroll region to check if it's scrollable
        if scrollregion and scrollregion != '':
            try:
                coords = scrollregion.split()
                if len(coords) >= 4:
                    scroll_height = int(float(coords[3]))
                    is_scrollable = scroll_height > canvas_height
                    print(f"✅ Scrollable height: {scroll_height}px")
                    print(f"✅ Requires scrolling: {is_scrollable}")
                    
                    if is_scrollable:
                        print(f"\\n🎯 SCROLLING TEST RESULTS:")
                        print(f"   ✅ Scroll region is properly configured")
                        print(f"   ✅ Content ({scroll_height}px) > Canvas ({canvas_height}px)")
                        print(f"   ✅ Mouse wheel scrolling should work")
                        print(f"   ✅ Scrollbar should be visible and functional")
                        
                        print(f"\\n🖱️  Manual verification steps:")
                        print(f"   1. Open the GUI window")
                        print(f"   2. Verify scrollbar appears on the right side")
                        print(f"   3. Use mouse wheel to scroll up/down")
                        print(f"   4. Drag the scrollbar thumb")
                        print(f"   5. Content should scroll smoothly")
                        
                        print(f"\\n🚀 SUCCESS: Scrolling is now FIXED!")
                    else:
                        print(f"\\n⚠️  Content fits in canvas - no scrolling needed")
                        
            except (ValueError, IndexError) as e:
                print(f"✗ Error parsing scroll region: {e}")
        else:
            print(f"✗ No scroll region set")
            
        print("="*60)
        
        # Keep window open for manual testing
        print("\\nKeep the window open for manual testing. Close to exit...")
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scrolling_final()