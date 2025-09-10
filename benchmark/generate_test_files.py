#!/usr/bin/env python3
"""
Generate test LogLog files of various sizes for benchmarking
"""
import os
import random

def generate_loglog_content(num_items, max_depth=5):
    """Generate hierarchical LogLog content with nested items"""
    content_lines = []
    
    def generate_item(level=0, parent_index=0):
        if level > max_depth:
            return
        
        indent = "    " * level
        
        # Generate different types of items
        item_types = [
            "- Regular list item",
            "[] TODO item",
            "[x] Completed item", 
            "[-] In progress item",
            "[?] Unknown status item"
        ]
        
        # Add some hashtags for realism
        hashtags = ["#project", "#urgent", "#later", "#docs", "#bug", "#feature"]
        
        for i in range(random.randint(1, min(8, num_items // (level + 1)))):
            if len(content_lines) >= num_items:
                break
                
            item_type = random.choice(item_types)
            hashtag = random.choice(hashtags) if random.random() < 0.3 else ""
            
            content = f"{indent}{item_type} #{parent_index}.{i} {hashtag}"
            content_lines.append(content)
            
            # Recursively add children
            if level < max_depth and random.random() < 0.6:
                generate_item(level + 1, len(content_lines))
    
    # Generate top-level structure
    for i in range(min(10, num_items)):
        if len(content_lines) >= num_items:
            break
        generate_item(0, i)
    
    return "\n".join(content_lines[:num_items])

def create_test_files():
    """Create test files of various sizes"""
    test_sizes = [
        (10, "small.log"),
        (50, "medium.log"),
        (200, "large.log"),
        (500, "xlarge.log"),
        (1000, "huge.log"),
        (2000, "massive.log")
    ]
    
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    
    for size, filename in test_sizes:
        filepath = os.path.join(benchmark_dir, filename)
        content = generate_loglog_content(size)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created {filename} with {size} items ({len(content.splitlines())} lines)")

if __name__ == "__main__":
    create_test_files()