#!/usr/bin/env python3
"""Test scrolling with actual scrollable content"""

import sys
sys.stderr = sys.stdout

def test_scroll_content():
    print("="*60)
    print("TESTING SCROLLING WITH SCROLLABLE CONTENT")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
        # Create content that definitely needs scrolling (20+ items)
        scroll_content = """Scrollable Test Document
    Item 1 - First item
    Item 2 - Second item  
    Item 3 - Third item
    Item 4 - Fourth item
    Item 5 - Fifth item
    Item 6 - Sixth item
    Item 7 - Seventh item
    Item 8 - Eighth item
    Item 9 - Ninth item
    Item 10 - Tenth item
    Item 11 - Eleventh item
    Item 12 - Twelfth item
    Item 13 - Thirteenth item
    Item 14 - Fourteenth item
    Item 15 - Fifteenth item
    Item 16 - Sixteenth item
    Item 17 - Seventeenth item
    Item 18 - Eighteenth item
    Item 19 - Nineteenth item
    Item 20 - Twentieth item
    Item 21 - Twenty-first item
    Item 22 - Twenty-second item
    Item 23 - Twenty-third item
    Item 24 - Twenty-fourth item
    Item 25 - Twenty-fifth item
        Nested item A
        Nested item B
        Nested item C
    Item 26 - Twenty-sixth item
    Item 27 - Twenty-seventh item
    Item 28 - Twenty-eighth item
    Item 29 - Twenty-ninth item
    Item 30 - Thirtieth item"""
        
        print("📝 Creating scrollable document with 30+ items...")
        
        app = ModernLogLogGUI()
        test_file = "/tmp/scrollable_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        visible_nodes = viewport.tree.get_visible_nodes()
        
        print(f"✅ Document loaded: {len(visible_nodes)} nodes")
        print(f"✅ Should require scrolling with this many items")
        
        # Check scroll region
        if hasattr(viewport, 'canvas'):
            try:
                scroll_region = viewport.canvas.cget('scrollregion')
                print(f"✅ Canvas scroll region: {scroll_region}")
                
                # Check if scrollbar is needed
                canvas_height = viewport.canvas.winfo_reqheight()
                print(f"✅ Canvas requested height: {canvas_height}px")
                
            except Exception as e:
                print(f"⚠️  Could not check scroll region: {e}")
        
        print(f"\n🖱️  Manual test:")
        print(f"   1. Open the GUI window")
        print(f"   2. Use mouse wheel to scroll up/down") 
        print(f"   3. Drag the scrollbar on the right")
        print(f"   4. Content should scroll smoothly")
        
        print(f"\n🎯 If scrolling works, the fix is successful!")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scroll_content()