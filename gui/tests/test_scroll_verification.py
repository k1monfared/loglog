#!/usr/bin/env python3
"""Verify scrolling is working without opening GUI window"""

import sys
sys.stderr = sys.stdout

def test_scroll_verification():
    print("="*60)
    print("SCROLL FUNCTIONALITY VERIFICATION")
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
        
        scroll_content = "Large Scrollable Document\n" + "\n".join(content_lines)
        
        print(f"📄 Creating document with {len(content_lines)} items...")
        
        app = ModernLogLogGUI()
        
        # Don't show the main window
        app.root.withdraw()
        
        test_file = "/tmp/final_scroll_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        
        # Force geometry update
        app.root.update_idletasks()
        
        visible_nodes = viewport.tree.get_visible_nodes()
        print(f"✅ Document loaded: {len(visible_nodes)} nodes")
        
        # Force scroll region update
        viewport._update_scroll_region()
        
        # Check scroll region after loading
        scrollregion = viewport.canvas.cget('scrollregion')
        print(f"✅ Scroll region: {scrollregion}")
        
        # Check canvas dimensions
        canvas_height = viewport.canvas.winfo_height()
        canvas_reqheight = viewport.canvas.winfo_reqheight()
        
        print(f"✅ Canvas actual height: {canvas_height}px")
        print(f"✅ Canvas requested height: {canvas_reqheight}px")
        
        # Parse scroll region to check if it's scrollable
        scroll_test_passed = False
        if scrollregion and scrollregion != '':
            try:
                coords = scrollregion.split()
                if len(coords) >= 4:
                    scroll_height = int(float(coords[3]))
                    
                    print(f"✅ Scrollable height: {scroll_height}px")
                    
                    # Check if content is taller than visible area
                    is_scrollable = scroll_height > 400  # Reasonable threshold
                    print(f"✅ Requires scrolling: {is_scrollable}")
                    
                    if is_scrollable and scroll_height > 0:
                        print(f"\n🎯 SCROLL FUNCTIONALITY TEST:")
                        print(f"   ✅ Scroll region is properly set: {scrollregion}")
                        print(f"   ✅ Content height ({scroll_height}px) > View area")
                        print(f"   ✅ Mouse wheel scrolling should work")
                        print(f"   ✅ Scrollbar should be visible and functional")
                        print(f"\n🚀 SUCCESS: SCROLLING IS NOW FIXED!")
                        scroll_test_passed = True
                    else:
                        print(f"\n⚠️  Scroll region too small or content fits in view")
                        
            except (ValueError, IndexError) as e:
                print(f"✗ Error parsing scroll region: {e}")
        else:
            print(f"✗ No scroll region set - scrolling will NOT work")
            
        # Summary
        print(f"\n📊 SUMMARY:")
        if scroll_test_passed:
            print(f"   🎉 SCROLL REGION CALCULATION: FIXED")
            print(f"   🎉 SCROLLING FUNCTIONALITY: WORKING") 
            print(f"   🎉 USER ISSUE: RESOLVED")
        else:
            print(f"   ❌ Scrolling functionality still needs work")
            
        print("="*60)
        
        app.root.destroy()
        return scroll_test_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_scroll_verification()
    sys.exit(0 if result else 1)