#!/usr/bin/env python3

"""
Debug the LogLog processor step by step.
"""

import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loglog_knowledge.loglog_processor import LogLogProcessor

# Test LogLog content
TEST_LOGLOG_CONTENT = """
- Project Alpha Development
    - Team Members
        - John Smith - Project Manager
"""

def debug_processor_step_by_step():
    """Debug the processor step by step."""
    print("🔍 Debugging LogLog Processor Step by Step")
    print("=" * 50)

    processor = LogLogProcessor()

    # Step 1: Check the original loglog import in processor
    print("📦 Step 1: Testing LogLog module import in processor")

    # Let's see what happens in process_text
    print(f"📝 Input content: {repr(TEST_LOGLOG_CONTENT)}")

    try:
        # Step into the processor
        text_lines = TEST_LOGLOG_CONTENT.split('\n') if isinstance(TEST_LOGLOG_CONTENT, str) else TEST_LOGLOG_CONTENT
        print(f"📋 Split into {len(text_lines)} lines:")
        for i, line in enumerate(text_lines):
            print(f"  {i}: {repr(line)}")

        # Try to import and use the original LogLog
        sys.path.append('/home/k1/Projects/loglog')
        from loglog import build_tree_from_text

        print("\n🌳 Step 2: Building tree with original LogLog")
        tree = build_tree_from_text(text_lines)

        print(f"Tree type: {getattr(tree, 'type', 'unknown')}")
        print(f"Tree data: {getattr(tree, 'data', 'no data')}")
        print(f"Tree children: {len(getattr(tree, 'children', []))}")

        # Step 3: Now try our extraction method
        print("\n📊 Step 3: Extracting sections from tree")

        sections = processor._extract_sections_from_tree(tree, "test.log")
        print(f"Extracted {len(sections)} sections")

        if len(sections) == 0:
            print("\n🔍 Step 4: Debugging extraction process")

            # Let's manually traverse the tree to see what's happening
            def debug_traverse(node, depth=0, path=None):
                if path is None:
                    path = []

                indent = "  " * depth
                node_type = getattr(node, 'type', 'unknown')
                node_data = getattr(node, 'data', 'no data')
                children = getattr(node, 'children', [])

                print(f"{indent}Node: type={node_type}, data={repr(node_data)}, children={len(children)}")

                # Test our cleaning method
                cleaned = processor._clean_content(node_data)
                print(f"{indent}  Cleaned: {repr(cleaned)}")
                print(f"{indent}  Is empty after clean: {not cleaned.strip()}")

                # Test if this would be skipped
                if hasattr(node, 'type') and node.type == "root":
                    print(f"{indent}  -> This is root, will skip to children")
                elif not cleaned.strip():
                    print(f"{indent}  -> This will be SKIPPED (empty after cleaning)")
                else:
                    print(f"{indent}  -> This SHOULD be processed")

                for i, child in enumerate(children[:3]):  # Limit for debugging
                    debug_traverse(child, depth + 1, path + [cleaned] if cleaned.strip() else path)

            print("\n🌳 Tree traversal debug:")
            debug_traverse(tree)

        else:
            print("\n✅ Sections extracted successfully:")
            for i, section in enumerate(sections):
                print(f"  {i+1}. {section.content}")

        return len(sections) > 0

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_processor_step_by_step()