#!/usr/bin/env python3
"""Test root node type creation"""

def test_root_type():
    print("="*60)
    print("TESTING ROOT NODE TYPE")
    print("="*60)
    
    try:
        from loglog_tree_model import LogLogTree, LogLogNode, NodeType
        
        # Test 1: Create standalone node
        print("🧪 Test 1: Standalone LogLogNode")
        standalone_root = LogLogNode("", NodeType.ROOT)
        print(f"   Content: {repr(standalone_root.content)}")
        print(f"   Type: {standalone_root.node_type}")
        print(f"   Is ROOT?: {standalone_root.node_type == NodeType.ROOT}")
        
        # Test 2: Create tree and check root
        print(f"\n🧪 Test 2: LogLogTree root")
        tree = LogLogTree()
        print(f"   Content: {repr(tree.root.content)}")
        print(f"   Type: {tree.root.node_type}")
        print(f"   Is ROOT?: {tree.root.node_type == NodeType.ROOT}")
        
        # Test 3: Parse empty content
        print(f"\n🧪 Test 3: Parse empty text")
        tree.load_from_text("")
        print(f"   Content: {repr(tree.root.content)}")
        print(f"   Type: {tree.root.node_type}")
        print(f"   Is ROOT?: {tree.root.node_type == NodeType.ROOT}")
        
        # Test 4: Parse actual content
        print(f"\n🧪 Test 4: Parse test content")
        test_content = "- \n    - \n        - Sample LogLog Tree"
        tree.load_from_text(test_content)
        print(f"   Content: {repr(tree.root.content)}")
        print(f"   Type: {tree.root.node_type}")
        print(f"   Is ROOT?: {tree.root.node_type == NodeType.ROOT}")
        print(f"   Children count: {len(tree.root.children)}")
        if tree.root.children:
            first_child = tree.root.children[0]
            print(f"   First child content: {repr(first_child.content)}")
            print(f"   First child type: {first_child.node_type}")
        
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_root_type()