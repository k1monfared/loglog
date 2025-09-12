#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def test_refresh_widgets():
    """Test if refreshing widgets fixes the tree_renderer reference"""
    try:
        print("="*60)
        print("TESTING WIDGET REFRESH")
        print("="*60)
        
        from loglog_gui import ModernLogLogGUI
        
        # Create GUI and load content
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Set up and load content
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        viewport = app.tree_renderer.active_viewport
        print(f"✓ Content loaded, {len(viewport.tree.get_visible_nodes())} visible nodes")
        
        # Check existing widgets
        print(f"\n🔍 Existing widgets: {len(viewport.node_widgets)}")
        
        # Force refresh display (this should recreate widgets with correct tree_renderer)
        print("\n🔄 Forcing refresh display...")
        viewport.refresh_display()
        
        print(f"✓ After refresh: {len(viewport.node_widgets)} widgets")
        
        # Test clicking on first widget
        if viewport.node_widgets:
            first_widget_id = list(viewport.node_widgets.keys())[0]
            first_widget = viewport.node_widgets[first_widget_id]
            
            print(f"\n🖱️ Testing click on widget...")
            print(f"   Widget tree_renderer: {first_widget.tree_renderer}")
            print(f"   Is it TabViewport?: {type(first_widget.tree_renderer).__name__}")
            
            # Create a mock click event
            class MockEvent:
                def __init__(self):
                    self.state = 0  # No modifier keys
            
            try:
                # Simulate the on_click function from bind_events
                print("   Calling tree_renderer.set_focus()...")
                first_widget.tree_renderer.set_focus(first_widget.node)
                print("   ✅ Click succeeded!")
                
            except Exception as e:
                print(f"   ❌ Click failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n❌ No widgets created")
            
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refresh_widgets()