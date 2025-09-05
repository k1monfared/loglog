#!/usr/bin/env python3
import sys
sys.path.append('..')  # Add parent directory to path to import loglog
from loglog import from_md, from_md_file, build_tree_from_text

def test_from_md():
    """Test markdown to loglog conversion"""
    
    print("Testing from_md() function...")
    print("="*50)
    
    # Test with the test markdown file
    try:
        result = from_md_file('test_md_reverse.md')
        
        print("Markdown input file: test_md_reverse.md")
        print("Converted to loglog:")
        print("-" * 30)
        print(result)
        
        # Save the result
        with open('test_md_reverse_output.txt', 'w') as f:
            f.write(result)
        print(f"Output saved to: test_md_reverse_output.txt")
        
        # Test round-trip conversion: markdown -> loglog -> tree -> markdown
        print("\n" + "="*50)
        print("Testing round-trip conversion...")
        print("-" * 30)
        
        # Convert markdown to loglog format
        loglog_text = from_md_file('test_md_reverse.md')
        
        # Convert loglog to tree structure
        loglog_lines = loglog_text.split('\n')
        tree = build_tree_from_text(loglog_lines)
        
        # Convert tree back to markdown
        markdown_result = tree.to_md()
        
        print("Original markdown -> loglog -> tree -> markdown:")
        print(markdown_result)
        
        # Save round-trip result
        with open('test_md_reverse_roundtrip.md', 'w') as f:
            f.write(markdown_result)
        print("Round-trip result saved to: test_md_reverse_roundtrip.md")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_from_md()
    if success:
        print("\n✓ All tests completed successfully!")
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)