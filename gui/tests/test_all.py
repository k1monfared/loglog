#!/usr/bin/env python3
from loglog import build_tree_from_file

test_files = [
    "test_input.txt",
    "test_input_shallow.txt", 
    "test_input_deep.txt",
    "test_input_todos.txt",
    "test_input_flat.txt"
]

for test_file in test_files:
    print(f"\n{'='*50}")
    print(f"Testing: {test_file}")
    print('='*50)
    
    try:
        root = build_tree_from_file(test_file)
        shallowest_depth = root._get_shallowest_leaf_depth()
        print(f"Shallowest leaf depth: {shallowest_depth}")
        
        markdown_output = root.to_md()
        
        # Save output file
        output_file = test_file.replace(".txt", "_output.md")
        with open(output_file, "w") as f:
            f.write(markdown_output)
        
        print(f"Output saved to: {output_file}")
        print("\nGenerated Markdown:")
        print("-" * 30)
        print(markdown_output)
        
    except Exception as e:
        print(f"Error processing {test_file}: {e}")