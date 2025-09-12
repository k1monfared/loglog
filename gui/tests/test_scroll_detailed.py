#!/usr/bin/env python3
"""Detailed analysis of scroll region vs content size"""

import sys
sys.stderr = sys.stdout

def test_scroll_detailed():
    print("="*60)
    print("DETAILED SCROLL ANALYSIS")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        import tkinter as tk
        
        # Create LARGE document that definitely needs scrolling
        content_lines = []
        for i in range(1, 101):  # 100 items - much more than before
            content_lines.append(f"    Item {i} - This is a long line for scroll testing with enough content to force scrolling")
            if i % 5 == 0:
                content_lines.append(f"        Nested item {i}A - More detailed nested content")
                content_lines.append(f"        Nested item {i}B - Additional nested content for height")
                content_lines.append(f"        Nested item {i}C - Even more nested content to increase document height")
        
        scroll_content = "Large Scrollable Document\\n" + "\\n".join(content_lines)
        
        app = ModernLogLogGUI()
        app.root.minsize(800, 600)
        app.root.geometry("900x700")
        
        test_file = "/tmp/detailed_scroll_test.log"
        
        with open(test_file, 'w') as f:
            f.write(scroll_content)
        
        # Load document
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, scroll_content)
        
        viewport = app.tree_renderer.active_viewport
        
        # Force geometry updates
        app.root.update_idletasks()
        app.root.update()
        
        def analyze_scroll():
            print(f"\\n📊 COMPREHENSIVE SCROLL ANALYSIS:")
            
            # Basic dimensions
            canvas_width = viewport.canvas.winfo_width()
            canvas_height = viewport.canvas.winfo_height()
            print(f"   • Canvas size: {canvas_width}x{canvas_height}")
            
            # Scroll region
            scroll_region = viewport.canvas.cget('scrollregion')
            print(f"   • Scroll region: '{scroll_region}'")
            
            # Parse scroll region
            if scroll_region and scroll_region != '':
                coords = scroll_region.split()
                if len(coords) >= 4:
                    scroll_width = int(float(coords[2]))
                    scroll_height = int(float(coords[3]))
                    print(f"   • Scrollable area: {scroll_width}x{scroll_height}")
                    print(f"   • Content exceeds canvas: {scroll_height > canvas_height}")
                    
            # Check content
            visible_nodes = viewport.tree.get_visible_nodes() if hasattr(viewport, 'tree') else []
            print(f"   • Visible nodes: {len(visible_nodes)}")
            
            # Frame size
            frame_width = viewport.scrollable_frame.winfo_reqwidth()
            frame_height = viewport.scrollable_frame.winfo_reqheight() 
            print(f"   • Scrollable frame: {frame_width}x{frame_height}")
            
            # Current view position
            current_top = viewport.canvas.canvasy(0)
            current_view = viewport.canvas.yview()
            print(f"   • Current top position: {current_top}")
            print(f"   • Current yview: {current_view}")
            
            print(f"\\n🧪 SCROLL MECHANISM TESTS:")
            
            # Test 1: Large yview_scroll
            print(f"   Test 1: yview_scroll(20, 'units')")
            before_large = viewport.canvas.canvasy(0)
            viewport.canvas.yview_scroll(20, "units")
            app.root.update_idletasks()
            after_large = viewport.canvas.canvasy(0)
            large_scroll_worked = abs(after_large - before_large) > 1
            print(f"     Before: {before_large}, After: {after_large}, Worked: {large_scroll_worked}")
            
            # Test 2: yview_moveto different positions
            print(f"   Test 2: yview_moveto(0.5)")
            viewport.canvas.yview_moveto(0.5)
            app.root.update_idletasks()
            middle_pos = viewport.canvas.canvasy(0)
            print(f"     Middle position: {middle_pos}")
            
            print(f"   Test 3: yview_moveto(0.9)")
            viewport.canvas.yview_moveto(0.9)
            app.root.update_idletasks()
            bottom_pos = viewport.canvas.canvasy(0)
            print(f"     Bottom position: {bottom_pos}")
            
            # Test 4: Manual scrollbar interaction
            print(f"   Test 4: Manual scrollbar set")
            if hasattr(viewport, 'scrollbar'):
                viewport.scrollbar.set(0.7, 0.8) 
                app.root.update_idletasks()
                scrollbar_pos = viewport.canvas.canvasy(0)
                print(f"     After scrollbar.set(0.7, 0.8): {scrollbar_pos}")
            
            # Analysis
            positions = [before_large, after_large, middle_pos, bottom_pos]
            unique_positions = len(set(positions))
            
            print(f"\\n🎯 FINAL ANALYSIS:")
            print(f"   • Different scroll positions achieved: {unique_positions}")
            if unique_positions > 1:
                print(f"   ✅ SCROLLING IS WORKING! (programmatic)")
                print(f"   → The issue may be only with mouse wheel events")
            else:
                print(f"   ❌ SCROLLING IS BROKEN (all positions same)")
                print(f"   → Fundamental scrolling mechanism is broken")
                
            # Check if content is actually scrollable
            if scroll_region:
                coords = scroll_region.split()
                if len(coords) >= 4:
                    content_height = int(float(coords[3]))
                    if content_height <= canvas_height:
                        print(f"   ⚠️  Content ({content_height}px) fits in canvas ({canvas_height}px)")
                        print(f"   → No scrolling needed!")
                        
            app.root.destroy()
            return unique_positions > 1
        
        # Schedule analysis
        result = app.root.after(200, analyze_scroll)
        app.root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scroll_detailed()