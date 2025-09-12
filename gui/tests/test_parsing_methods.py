#!/usr/bin/env python3
import sys
sys.stderr = sys.stdout

def test_both_parsing_methods():
    """Test both parsing methods to see the difference"""
    try:
        from loglog_tree_model import LogLogTree
        
        test_file = "/home/k1/Projects/loglog/test_tree.log"
        with open(test_file, 'r') as f:
            content = f.read()
        
        print("="*60)
        print("TESTING BOTH PARSING METHODS")
        print("="*60)
        
        # Test method 1: parse_loglog_text (the one that works)
        print("\n1. Testing parse_loglog_text():")
        tree1 = LogLogTree()
        tree1.parse_loglog_text(content)
        visible1 = tree1.get_visible_nodes()
        print(f"   Visible nodes: {len(visible1)}")
        
        # Test method 2: load_from_text (the one GUI uses)
        print("\n2. Testing load_from_text():")
        tree2 = LogLogTree()
        tree2.load_from_text(content)
        visible2 = tree2.get_visible_nodes()
        print(f"   Visible nodes: {len(visible2)}")
        
        print(f"\n✓ Method comparison:")
        print(f"   parse_loglog_text: {len(visible1)} nodes")
        print(f"   load_from_text: {len(visible2)} nodes")
        
        if len(visible1) != len(visible2):
            print("❌ MISMATCH FOUND - This is the problem!")
        else:
            print("✅ Both methods work the same")
            
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_both_parsing_methods()