#!/usr/bin/env python3
from loglog import build_tree_from_file

# Load test data from file
root = build_tree_from_file("test_input.txt")
markdown_output = root.to_md()

# Save the output to file
with open("test_output.md", "w") as f:
    f.write(markdown_output)

print("Generated Markdown:")
print(markdown_output)
print(f"\nOutput saved to test_output.md")