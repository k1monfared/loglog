#!/usr/bin/env python3
"""Debug the LogLog text parsing to find the extra empty node"""

def debug_parsing():
    print("="*60)
    print("DEBUGGING LOGLOG PARSING")
    print("="*60)
    
    # Simulate the parsing logic
    test_content = """- 
    - 
        - Sample LogLog Tree"""
    
    print("📄 Test content:")
    print(repr(test_content))
    
    print("\n🔍 Line-by-line parsing simulation:")
    lines = test_content.split('\n')
    for i, line in enumerate(lines):
        if not line.strip():
            print(f"   Line {i}: SKIPPED (empty)")
            continue
            
        # Calculate indentation level
        level = 0
        content = line.lstrip()
        for char in line:
            if char == ' ':
                level += 1
            elif char == '\t':
                level += 4
            else:
                break
        
        level = level // 4  # Convert spaces to levels
        
        # Remove leading dash or TODO marker
        original_content = content
        if content.startswith('- '):
            content = content[2:]
        
        print(f"   Line {i}: raw={repr(line)}")
        print(f"      indent_chars={level*4}, level={level}")
        print(f"      before_dash={repr(original_content)}, after_dash={repr(content)}")
        print(f"      final_content={repr(content.strip())}")
        print()

if __name__ == "__main__":
    debug_parsing()