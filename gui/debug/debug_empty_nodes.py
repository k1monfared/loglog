#!/usr/bin/env python3
"""Debug empty nodes appearing on top"""

import sys
sys.stderr = sys.stdout

def debug_empty_nodes():
    print("="*60)
    print("DEBUGGING EMPTY NODES")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content and examine parsing
        with open(test_file, 'r') as f:
            content = f.read()
        
        print("📄 Raw file content:")
        lines = content.split('\n')
        for i, line in enumerate(lines[:10], 1):  # First 10 lines
            print(f"   Line {i}: {repr(line)}")
        
        # Load into GUI and examine tree structure
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        viewport = app.tree_renderer.active_viewport
        tree = viewport.tree
        all_nodes = tree.get_all_nodes()
        visible_nodes = tree.get_visible_nodes()
        
        print(f"\n🌲 Tree structure analysis:")
        print(f"   Total nodes: {len(all_nodes)}")
        print(f"   Visible nodes: {len(visible_nodes)}")
        
        print(f"\n🔍 First 10 visible nodes:")
        for i, node in enumerate(visible_nodes[:10]):
            # Calculate depth by counting parents
            depth = 0
            current = node.parent
            while current:
                depth += 1
                current = current.parent
            print(f"   Node {i}: depth={depth}, content={repr(node.content)}, todo={node.todo_status}")
        
        # Check for any nodes with suspicious content (excluding ROOT)
        from loglog_tree_model import NodeType
        empty_content_nodes = [n for n in all_nodes if not n.content.strip() and n.node_type != NodeType.ROOT]
        print(f"\n⚠️  Non-root nodes with empty/whitespace-only content: {len(empty_content_nodes)}")
        for i, node in enumerate(empty_content_nodes):
            # Calculate depth by counting parents
            depth = 0
            current = node.parent
            while current:
                depth += 1
                current = current.parent
            print(f"   Empty node {i}: depth={depth}, content={repr(node.content)}, parent={node.parent.content if node.parent else 'None'}")
        
        # Check widget creation
        print(f"\n🎨 Widget analysis:")
        print(f"   Node widgets created: {len(viewport.node_widgets)}")
        
        # Look for duplicate or incorrectly created widgets
        widget_nodes = list(viewport.node_widgets.keys())
        widget_content = [node.content for node in widget_nodes]
        print(f"   First 5 widget contents: {widget_content[:5]}")
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_empty_nodes()