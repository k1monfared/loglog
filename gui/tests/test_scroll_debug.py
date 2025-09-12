#!/usr/bin/env python3
"""Debug scrolling issues by examining scroll region calculation"""

import sys
sys.stderr = sys.stdout

def test_scroll_debug():
    print("="*60)
    print("DEBUG SCROLLING - SCROLL REGION CALCULATION")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
        # Create content with many items to test scrolling
        scroll_content = """Scroll Debug Document
Item 1 - Testing scroll
Item 2 - Testing scroll  
Item 3 - Testing scroll
Item 4 - Testing scroll
Item 5 - Testing scroll
Item 6 - Testing scroll
Item 7 - Testing scroll
Item 8 - Testing scroll
Item 9 - Testing scroll
Item 10 - Testing scroll
Item 11 - Testing scroll
Item 12 - Testing scroll
Item 13 - Testing scroll
Item 14 - Testing scroll
Item 15 - Testing scroll
Item 16 - Testing scroll
Item 17 - Testing scroll
Item 18 - Testing scroll
Item 19 - Testing scroll
Item 20 - Testing scroll
Item 21 - Testing scroll
Item 22 - Testing scroll
Item 23 - Testing scroll
Item 24 - Testing scroll
Item 25 - Testing scroll"""
        
        app = ModernLogLogGUI()
        test_file = "/tmp/scroll_debug.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        
        print(f"🔍 Debug Info:")
        print(f"   • Active viewport: {viewport is not None}")
        
        if viewport:
            print(f"   • Has canvas: {hasattr(viewport, 'canvas')}")
            print(f"   • Has scrollable_frame: {hasattr(viewport, 'scrollable_frame')}")
            print(f"   • Has tree: {hasattr(viewport, 'tree')}")
            
            if hasattr(viewport, 'tree'):
                visible_nodes = viewport.tree.get_visible_nodes()
                print(f"   • Visible nodes: {len(visible_nodes)}")
                
            if hasattr(viewport, 'canvas'):
                # Force update before checking scroll region
                viewport.scrollable_frame.update_idletasks()
                
                # Check current scroll region
                current_scrollregion = viewport.canvas.cget('scrollregion')
                print(f"   • Current scroll region: '{current_scrollregion}'")
                
                # Try to get bbox
                try:
                    bbox = viewport.canvas.bbox("all")
                    print(f"   • Canvas bbox('all'): {bbox}")
                except Exception as e:
                    print(f"   • Canvas bbox error: {e}")
                
                # Manual call to _update_scroll_region
                print(f"\\n🔧 Manually calling _update_scroll_region...")
                viewport._update_scroll_region()
                
                # Check scroll region after manual update
                updated_scrollregion = viewport.canvas.cget('scrollregion')
                print(f"   • Updated scroll region: '{updated_scrollregion}'")
                
                # Check canvas dimensions
                canvas_width = viewport.canvas.winfo_width()
                canvas_height = viewport.canvas.winfo_height()
                print(f"   • Canvas size: {canvas_width}x{canvas_height}")
                
                # Check scrollable_frame dimensions
                if hasattr(viewport, 'scrollable_frame'):
                    frame_width = viewport.scrollable_frame.winfo_reqwidth()
                    frame_height = viewport.scrollable_frame.winfo_reqheight()
                    print(f"   • Frame requested size: {frame_width}x{frame_height}")
        
        print(f"\\n🎯 Analysis:")
        if viewport and hasattr(viewport, 'canvas'):
            scrollregion = viewport.canvas.cget('scrollregion')
            if not scrollregion or scrollregion == '':
                print("   ❌ Scroll region is empty - scrolling will not work")
                print("   🔧 This indicates the fallback calculation should activate")
            else:
                print("   ✅ Scroll region is set - scrolling should work")
                
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scroll_debug()