#!/usr/bin/env python3
from loglog import build_tree_from_file

test_files = [
    "test_input.txt",
    "test_input_shallow.txt", 
    "test_input_deep.txt",
    "test_input_todos.txt",
    "test_input_flat.txt"
]

print("Generating fresh markdown outputs for all test files...")
print("="*60)

for test_file in test_files:
    try:
        root = build_tree_from_file(test_file)
        shallowest_depth = root._get_shallowest_leaf_depth()
        markdown_output = root.to_md()
        
        # Generate output filename
        output_file = test_file.replace(".txt", "_output.md")
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(markdown_output)
        
        print(f"✓ {test_file} -> {output_file}")
        print(f"  Shallowest leaf depth: {shallowest_depth}")
        
    except Exception as e:
        print(f"✗ Error processing {test_file}: {e}")

print("\nAll outputs generated successfully!")