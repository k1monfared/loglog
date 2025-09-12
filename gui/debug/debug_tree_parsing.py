#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def debug_tree_parsing():
    """Debug tree parsing step by step"""
    try:
        print("="*60)
        print("DEBUGGING TREE PARSING")
        print("="*60)
        
        # Test file content
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        print(f"Reading file: {test_file}")
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        print(f"File content ({len(content)} chars):")
        print("-" * 40)
        print(repr(content))
        print("-" * 40)
        
        # Test LogLogTree parsing
        from loglog_tree_model import LogLogTree
        tree = LogLogTree()
        
        print("✓ LogLogTree created")
        
        # Parse the content
        print("Parsing content...")
        tree.parse_loglog_text(content)
        
        print(f"✓ Content parsed")
        print(f"Root node: {tree.root}")
        print(f"Root children: {len(tree.root.children) if tree.root else 0}")
        
        if tree.root and tree.root.children:
            for i, child in enumerate(tree.root.children):
                print(f"  Child {i}: {repr(child.content[:50])}")
        
        # Test visible nodes
        visible = tree.get_visible_nodes()
        print(f"Visible nodes: {len(visible)}")
        
        if visible:
            for i, node in enumerate(visible[:5]):  # Show first 5
                print(f"  Visible {i}: {repr(node.content[:50])}")
        else:
            print("No visible nodes found - this is the problem!")
            
        # Test all nodes
        all_nodes = tree.get_all_nodes()
        print(f"All nodes: {len(all_nodes)}")
        
        if all_nodes:
            for i, node in enumerate(all_nodes[:5]):  # Show first 5
                print(f"  All {i}: {repr(node.content[:50])}")
                
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error in tree parsing debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tree_parsing()