#!/usr/bin/env python3
"""Debug node types and structure to find the extra empty node"""

import sys
sys.stderr = sys.stdout

def debug_node_types():
    print("="*60)
    print("DEBUGGING NODE TYPES AND STRUCTURE")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        from loglog_tree_model import NodeType
        
        app = ModernLogLogGUI()
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        
        # Load content and examine parsing
        with open(test_file, 'r') as f:
            content = f.read()
        
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, content)
        
        viewport = app.tree_renderer.active_viewport
        tree = viewport.tree
        
        print(f"🔍 ROOT node analysis:")
        print(f"   Root content: {repr(tree.root.content)}")
        print(f"   Root node_type: {tree.root.node_type}")
        print(f"   Root has parent: {tree.root.parent is not None}")
        print(f"   Root children count: {len(tree.root.children)}")
        
        print(f"\n🌲 All nodes with types:")
        all_nodes = tree.get_all_nodes()  # This excludes ROOT
        for i, node in enumerate(all_nodes[:10]):
            # Calculate depth by counting parents
            depth = 0
            current = node.parent
            while current:
                depth += 1
                current = current.parent
            
            print(f"   Node {i}: depth={depth}, type={node.node_type}, content={repr(node.content[:30])}")
        
        print(f"\n⚠️  Manual traversal from root:")
        def traverse_from_root(node, depth=0, prefix=""):
            print(f"   {prefix}Node: depth={depth}, type={node.node_type}, content={repr(node.content[:30])}")
            for i, child in enumerate(node.children):
                traverse_from_root(child, depth + 1, prefix + "  ")
        
        traverse_from_root(tree.root)
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_node_types()