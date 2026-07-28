#!/usr/bin/env python3

"""
Debug tests for LogLog Knowledge Graph Service.

These tests help identify where the issue is occurring without requiring API keys.
"""

import sys
from pathlib import Path
import tempfile

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loglog_knowledge.loglog_processor import LogLogProcessor
from loglog_knowledge.kg_core import KnowledgeGraph, Entity, Relationship, Context, EntityType, RelationshipType

# Test LogLog content
TEST_LOGLOG_CONTENT = """
- Project Alpha Development
    - Team Members
        - John Smith - Project Manager
        - Sarah Johnson - Lead Developer
        - Mike Chen - UI/UX Designer
    - Phase 1: Planning
        [] Market research
        [x] Team formation
        [] Technical specification
    - Phase 2: Development
        [] Backend API development
        [] Frontend implementation
        [] Database design
    - Decisions
        - Use React for frontend #frontend #decision
        - PostgreSQL for database #database #decision
        - JWT for authentication #security #decision

- Meeting Notes
    - 2024-01-15 Kickoff Meeting
        - Project timeline discussed
        - Team roles assigned
        - Initial requirements gathered #meeting #planning
    - 2024-01-22 Technical Review
        - Architecture decisions made
        - Technology stack finalized #meeting #technical
"""


def test_loglog_processing():
    """Test LogLog document processing in detail."""
    print("🧪 Testing LogLog Processing...")

    processor = LogLogProcessor()

    # Check if original LogLog is available
    loglog_available = processor.is_loglog_available()
    print(f"📦 Original LogLog module available: {loglog_available}")

    # Test with our sample content
    print(f"📝 Processing content ({len(TEST_LOGLOG_CONTENT)} chars)")

    sections = processor.process_text(TEST_LOGLOG_CONTENT, "test.log")

    print(f"📊 Extracted {len(sections)} sections")

    if len(sections) == 0:
        print("❌ No sections extracted!")
        print("📝 Raw content preview:")
        lines = TEST_LOGLOG_CONTENT.split('\n')
        for i, line in enumerate(lines[:10]):
            print(f"  {i+1:2d}: '{line}'")
        return False

    # Print all sections for debugging
    print("📋 All extracted sections:")
    for i, section in enumerate(sections):
        print(f"  {i+1:2d}. Depth {section.depth}: '{section.content}'")
        print(f"      Path: {' > '.join(section.hierarchical_path)}")
        if section.hashtags:
            print(f"      Tags: {', '.join(section.hashtags)}")
        if section.todo_status:
            print(f"      TODO: {section.todo_status}")
        print()

    # Test grouping
    grouped = processor.group_sections_by_context(sections, max_section_size=500)
    print(f"📦 Grouped into {len(grouped)} batches")

    for i, group in enumerate(grouped):
        print(f"  Batch {i+1}: {len(group['content'])} chars, {len(group['sections'])} sections")
        print(f"    Content preview: {group['content'][:100]}...")
        print()

    return len(sections) > 0


def test_loglog_import():
    """Test importing the original LogLog module."""
    print("\n🔍 Testing LogLog Module Import...")

    try:
        # Try to import the original loglog module
        sys.path.append('/home/k1/Projects/loglog')
        from loglog import build_tree_from_text, TreeNode

        print("✅ Successfully imported original LogLog module")

        # Test parsing
        text_lines = TEST_LOGLOG_CONTENT.split('\n')
        print(f"📝 Parsing {len(text_lines)} lines")

        tree = build_tree_from_text(text_lines)

        print(f"🌳 Tree created:")
        print(f"  Type: {getattr(tree, 'type', 'unknown')}")
        print(f"  Children: {len(getattr(tree, 'children', []))}")
        print(f"  Data: '{getattr(tree, 'data', 'no data')}'")

        # Traverse and print structure
        def print_tree(node, depth=0, max_depth=3):
            if depth > max_depth:
                return

            indent = "  " * depth
            data = getattr(node, 'data', 'no data')
            children = getattr(node, 'children', [])
            node_type = getattr(node, 'type', 'unknown')

            print(f"{indent}- [{node_type}] '{data}' ({len(children)} children)")

            for child in children[:5]:  # Limit output
                print_tree(child, depth + 1, max_depth)

        print("\n🌳 Tree structure:")
        print_tree(tree)

        return True

    except ImportError as e:
        print(f"⚠️  Could not import original LogLog module: {e}")
        print("📝 This explains why the processor might not be working correctly")
        return False
    except Exception as e:
        print(f"❌ LogLog parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_graph_core():
    """Test core knowledge graph functionality."""
    print("\n🧠 Testing Knowledge Graph Core...")

    # Create a knowledge graph manually
    kg = KnowledgeGraph()

    # Add some test entities
    entities = [
        Entity(name="John Smith", entity_type=EntityType.PERSON, description="Project Manager"),
        Entity(name="Project Alpha", entity_type=EntityType.PROJECT, description="Development project"),
        Entity(name="React", entity_type=EntityType.CONCEPT, description="Frontend framework"),
    ]

    for entity in entities:
        kg.add_entity(entity)

    print(f"✅ Created knowledge graph with {len(kg.entities)} entities")

    # Add a relationship
    relationship = Relationship(
        source_entity_id=entities[0].id,  # John Smith
        target_entity_id=entities[1].id,  # Project Alpha
        relationship_type=RelationshipType.PART_OF,
        description="John manages Project Alpha"
    )

    kg.add_relationship(relationship)

    print(f"✅ Added {len(kg.relationships)} relationships")

    # Test statistics
    stats = kg.get_statistics()
    print(f"📊 Statistics: {stats['total_entities']} entities, {stats['total_relationships']} relationships")

    return True


def test_file_processing():
    """Test processing from actual file."""
    print("\n📁 Testing File Processing...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_file = Path(temp_dir) / "test.log"
        test_file.write_text(TEST_LOGLOG_CONTENT)

        print(f"📝 Created test file: {test_file}")

        # Process file
        processor = LogLogProcessor()

        try:
            sections = processor.process_file(str(test_file))
            print(f"📊 Processed file: {len(sections)} sections")

            if len(sections) > 0:
                print("✅ File processing works")
                return True
            else:
                print("❌ File processing returned no sections")
                return False

        except Exception as e:
            print(f"❌ File processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run all debug tests."""
    print("🔍 LogLog Knowledge Graph Debug Tests")
    print("=" * 50)

    tests = [
        ("LogLog Processing", test_loglog_processing),
        ("LogLog Import", test_loglog_import),
        ("Knowledge Graph Core", test_knowledge_graph_core),
        ("File Processing", test_file_processing),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n▶️ {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}")
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Debug Test Results:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")

    if passed != len(results):
        print("\n💡 Issues found:")
        for test_name, result in results:
            if not result:
                print(f"  - {test_name} failed")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)