#!/usr/bin/env python3
"""Test performance with large documents"""

import sys
import time
sys.stderr = sys.stdout

def create_large_test_document():
    """Create a large LogLog document for performance testing"""
    
    content = []
    content.append("Large Performance Test Document")
    
    # Create 1000 top-level items
    for i in range(1000):
        content.append(f"\tItem {i+1} - This is a test item")
        
        # Every 10th item has children
        if i % 10 == 0:
            for j in range(10):
                content.append(f"\t\tChild {j+1} of Item {i+1}")
                
                # Some children have grandchildren
                if j % 3 == 0:
                    for k in range(5):
                        content.append(f"\t\t\tGrandchild {k+1}")
    
    return "\n".join(content)

def test_performance():
    print("="*60)
    print("PERFORMANCE TESTING WITH LARGE DOCUMENT")
    print("="*60)
    
    try:
        from loglog_gui import ModernLogLogGUI
        
        # Create large test document
        print("📝 Creating large test document...")
        start_time = time.time()
        large_content = create_large_test_document()
        creation_time = time.time() - start_time
        
        lines = large_content.count('\n') + 1
        print(f"✓ Created document with {lines:,} lines in {creation_time:.3f}s")
        
        # Save to file
        test_file = "/tmp/performance_test.log"
        with open(test_file, 'w') as f:
            f.write(large_content)
        
        print(f"✓ Saved to {test_file}")
        
        # Initialize GUI
        print("\n🚀 Initializing GUI...")
        start_time = time.time()
        app = ModernLogLogGUI()
        init_time = time.time() - start_time
        print(f"✓ GUI initialized in {init_time:.3f}s")
        
        # Load large document
        print("\n📂 Loading large document into GUI...")
        start_time = time.time()
        
        app.tabs[test_file] = {'tree_state': None, 'modified': False, 'is_temporary': False}
        app.tab_bar.add_tab(test_file, False)
        app.tree_renderer.switch_to_file(test_file, large_content)
        
        load_time = time.time() - start_time
        print(f"✓ Document loaded in {load_time:.3f}s")
        
        # Test viewport creation
        viewport = app.tree_renderer.active_viewport
        if viewport:
            visible_nodes = viewport.tree.get_visible_nodes()
            print(f"✓ {len(visible_nodes)} visible nodes created")
            
            # Test refresh performance
            print("\n🔄 Testing refresh performance...")
            start_time = time.time()
            for i in range(10):
                viewport.refresh_display()
            refresh_time = (time.time() - start_time) / 10
            print(f"✓ Average refresh time: {refresh_time:.3f}s")
            
            # Test folding performance
            if len(visible_nodes) > 0:
                print("\n📁 Testing fold/unfold performance...")
                test_node = visible_nodes[0]
                
                start_time = time.time()
                test_node.is_folded = True
                viewport.refresh_display()
                fold_time = time.time() - start_time
                print(f"✓ Fold operation: {fold_time:.3f}s")
                
                start_time = time.time()
                test_node.is_folded = False
                viewport.refresh_display()
                unfold_time = time.time() - start_time
                print(f"✓ Unfold operation: {unfold_time:.3f}s")
        
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Document size:     {lines:,} lines")
        print(f"Creation time:     {creation_time:.3f}s")
        print(f"GUI init time:     {init_time:.3f}s") 
        print(f"Load time:         {load_time:.3f}s")
        print(f"Refresh time:      {refresh_time:.3f}s")
        print(f"Fold time:         {fold_time:.3f}s")
        print(f"Unfold time:       {unfold_time:.3f}s")
        print("="*60)
        
        # Performance rating
        total_time = creation_time + init_time + load_time
        if total_time < 0.5:
            print("🚀 Performance: EXCELLENT (< 0.5s)")
        elif total_time < 1.0:
            print("✅ Performance: GOOD (< 1.0s)")
        elif total_time < 2.0:
            print("⚠️  Performance: ACCEPTABLE (< 2.0s)")
        else:
            print("🐌 Performance: NEEDS OPTIMIZATION (> 2.0s)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_performance()