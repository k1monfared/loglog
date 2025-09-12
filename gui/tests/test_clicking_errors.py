#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def test_clicking_with_proper_content():
    """Test clicking with properly loaded content to trigger the errors"""
    try:
        print("="*60)
        print("TESTING CLICKING WITH LOADED CONTENT")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        
        # Create GUI
        app = ModernLogLogGUI()
        print("✓ GUI created")
        
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content properly (using the working method)
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Set up tabs and viewport properly 
        app.tabs[test_file] = {
            'tree_state': None,
            'modified': False,
            'is_temporary': False
        }
        app.tab_bar.add_tab(test_file, False)
        
        # Use switch_to_file directly (we know this works)
        app.tree_renderer.switch_to_file(test_file, content)
        app.current_file = test_file
        
        print(f"✓ Content loaded using working method")
        
        # Verify content is loaded
        viewport = app.tree_renderer.active_viewport
        tree = viewport.tree
        visible_nodes = tree.get_visible_nodes()
        print(f"✓ Verified: {len(visible_nodes)} visible nodes")
        
        if visible_nodes:
            print(f"   First node: {repr(visible_nodes[0].content[:50])}")
            
            # Now test clicking on the first node (this should trigger the error you see)
            print(f"\n🖱️ Testing node interaction...")
            
            first_node = visible_nodes[0]
            
            # Try to set focus (this might trigger the AttributeError)
            try:
                print("   Calling tree_renderer.set_focus()...")
                app.tree_renderer.set_focus(first_node)
                print("   ✓ set_focus succeeded")
            except Exception as e:
                print(f"   ❌ set_focus failed: {e}")
                import traceback
                traceback.print_exc()
                
            # Try to create a widget for the first node (this might reveal widget creation issues)
            try:
                print("   Testing widget creation...")
                widget = viewport.create_node_widget(first_node)
                print(f"   ✓ Widget created: {widget}")
                
                # Try clicking on the widget
                print("   Simulating widget click...")
                widget.on_click(None)  # Simulate click event
                print("   ✓ Widget click succeeded")
                
            except Exception as e:
                print(f"   ❌ Widget interaction failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clicking_with_proper_content()