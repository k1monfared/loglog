#!/usr/bin/env python3

"""
Integration tests for LogLog Knowledge Graph Service.

These tests verify the complete workflow with actual Claude API calls.
Run with: CLAUDE_API_LOGLOG=your-key python tests/test_integration.py
"""

import os
import sys
import asyncio
import tempfile
import logging
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loglog_knowledge import (
    KnowledgeGraphBuilder,
    KnowledgeGraphQuery,
    BuilderConfig,
    LogLogProcessor
)
from loglog_knowledge.persistence import KnowledgeGraphPersistence

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

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

- Technical Requirements
    - Authentication System
        - User login/logout
        - JWT token management
        - Password reset functionality
    - Database Schema
        - User management
        - Project tracking
        - Activity logging
"""


async def test_loglog_processor():
    """Test LogLog document processing."""
    print("🧪 Testing LogLog Processor...")

    processor = LogLogProcessor()

    # Test with our sample content
    sections = processor.process_text(TEST_LOGLOG_CONTENT, "test.log")

    print(f"  📊 Extracted {len(sections)} sections")

    if len(sections) == 0:
        print("  ❌ No sections extracted - this is the problem!")
        return False

    # Print first few sections for debugging
    print("  📝 Sample sections:")
    for i, section in enumerate(sections[:5]):
        print(f"    {i+1}. Depth {section.depth}: {section.content[:50]}...")
        print(f"       Path: {' > '.join(section.hierarchical_path)}")
        if section.hashtags:
            print(f"       Tags: {', '.join(section.hashtags)}")

    # Test grouping
    grouped = processor.group_sections_by_context(sections, max_section_size=500)
    print(f"  📦 Grouped into {len(grouped)} batches")

    return len(sections) > 0


async def test_claude_api_connection():
    """Test Claude API connectivity."""
    print("\n🤖 Testing Claude API Connection...")

    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("  ❌ No API key found")
        return False

    from loglog_knowledge.claude_client import ClaudeClient

    client = ClaudeClient(api_key)

    # Test simple entity extraction
    test_text = "John Smith is the project manager for Project Alpha."

    try:
        response = await client.extract_entities(test_text)
        print(f"  ✅ API connection successful")
        print(f"  📊 Extracted {len(response.entities)} entities")
        print(f"  🎯 Confidence: {response.confidence}")

        if response.entities:
            for entity in response.entities:
                print(f"    • {entity['name']} ({entity['type']})")

        return True

    except Exception as e:
        print(f"  ❌ API connection failed: {e}")
        return False


async def test_knowledge_graph_building():
    """Test complete knowledge graph building process."""
    print("\n🔨 Testing Knowledge Graph Building...")

    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("  ❌ No API key found")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_file = Path(temp_dir) / "test.log"
        test_file.write_text(TEST_LOGLOG_CONTENT)

        print(f"  📝 Created test file: {test_file}")

        # Build knowledge graph
        config = BuilderConfig(
            max_section_size=500,
            min_entity_confidence=0.3,  # Lower threshold for testing
            min_relationship_confidence=0.3,
            batch_size=2
        )

        builder = KnowledgeGraphBuilder(api_key, config)

        try:
            print("  ⏳ Building knowledge graph...")
            kg = await builder.build_from_file(str(test_file))

            stats = kg.get_statistics()
            print(f"  📊 Results:")
            print(f"    • Entities: {stats['total_entities']}")
            print(f"    • Relationships: {stats['total_relationships']}")
            print(f"    • Contexts: {stats['total_contexts']}")

            if stats['total_entities'] == 0:
                print("  ❌ No entities extracted - debugging needed")

                # Debug: Check if sections were processed
                processor = LogLogProcessor()
                sections = processor.process_file(str(test_file))
                print(f"  🔍 Debug - Sections extracted: {len(sections)}")

                if sections:
                    grouped = processor.group_sections_by_context(sections)
                    print(f"  🔍 Debug - Grouped sections: {len(grouped)}")

                    if grouped:
                        print(f"  🔍 Debug - First group content preview:")
                        print(f"    {grouped[0]['content'][:200]}...")

                return False

            # Show sample entities
            print(f"  🏷️  Sample entities:")
            for i, (entity_id, entity) in enumerate(list(kg.entities.items())[:3]):
                print(f"    • {entity.name} ({entity.entity_type.value})")

            return True

        except Exception as e:
            print(f"  ❌ Knowledge graph building failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_querying():
    """Test querying functionality."""
    print("\n🔍 Testing Query Functionality...")

    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("  ❌ No API key found")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file and build KG
        test_file = Path(temp_dir) / "test.log"
        test_file.write_text(TEST_LOGLOG_CONTENT)

        config = BuilderConfig(
            max_section_size=500,
            min_entity_confidence=0.3,
            min_relationship_confidence=0.3
        )

        builder = KnowledgeGraphBuilder(api_key, config)

        try:
            kg = await builder.build_from_file(str(test_file))

            if len(kg.entities) == 0:
                print("  ❌ No entities to query")
                return False

            # Test querying
            query_engine = KnowledgeGraphQuery(kg, api_key)

            test_queries = [
                "Who are the team members?",
                "What are the main project phases?",
                "What technology decisions were made?"
            ]

            for query in test_queries:
                print(f"  🤔 Query: {query}")

                try:
                    result = await query_engine.query(query, max_entities=10)
                    print(f"    💡 Answer: {result.answer[:100]}...")
                    print(f"    🎯 Confidence: {result.confidence}")

                except Exception as e:
                    print(f"    ❌ Query failed: {e}")
                    return False

            return True

        except Exception as e:
            print(f"  ❌ Query testing failed: {e}")
            return False


async def test_persistence():
    """Test database persistence."""
    print("\n💾 Testing Persistence...")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        # Create a simple knowledge graph
        from loglog_knowledge.kg_core import KnowledgeGraph, Entity, EntityType

        kg = KnowledgeGraph()
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.PERSON,
            description="A test person"
        )
        kg.add_entity(entity)

        try:
            # Test save and load
            with KnowledgeGraphPersistence(str(db_path)) as persistence:
                kg_id = persistence.save_knowledge_graph(kg, "Test Graph")
                print(f"  ✅ Saved knowledge graph: {kg_id}")

                loaded_kg = persistence.load_knowledge_graph(kg_id)

                if loaded_kg and len(loaded_kg.entities) == 1:
                    print(f"  ✅ Successfully loaded knowledge graph")
                    return True
                else:
                    print(f"  ❌ Failed to load knowledge graph correctly")
                    return False

        except Exception as e:
            print(f"  ❌ Persistence test failed: {e}")
            return False


async def debug_loglog_parsing():
    """Debug LogLog parsing to see what's happening."""
    print("\n🔍 Debugging LogLog Parsing...")

    # Test with the actual loglog module
    try:
        # Try to import the original loglog module
        sys.path.append('/home/k1/Projects/loglog')
        from loglog import build_tree_from_text, TreeNode

        print("  ✅ Successfully imported original LogLog module")

        # Test parsing
        text_lines = TEST_LOGLOG_CONTENT.split('\n')
        tree = build_tree_from_text(text_lines)

        print(f"  🌳 Tree type: {getattr(tree, 'type', 'unknown')}")
        print(f"  📊 Children count: {len(getattr(tree, 'children', []))}")

        # Traverse and print structure
        def print_tree(node, depth=0):
            indent = "  " * depth
            data = getattr(node, 'data', 'no data')
            children = getattr(node, 'children', [])
            print(f"{indent}- {data} (children: {len(children)})")

            for child in children[:3]:  # Limit output
                print_tree(child, depth + 1)

        print("  🌳 Tree structure:")
        print_tree(tree)

        return True

    except ImportError as e:
        print(f"  ⚠️  Could not import original LogLog module: {e}")
        print("  📝 Using fallback implementation")
        return False
    except Exception as e:
        print(f"  ❌ LogLog parsing debug failed: {e}")
        return False


async def run_all_tests():
    """Run all integration tests."""
    print("🧪 LogLog Knowledge Graph Integration Tests")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("❌ No Claude API key found!")
        print("Set CLAUDE_API_LOGLOG or CLAUDE_API_KEY environment variable")
        return False

    print(f"✅ Found API key: {api_key[:10]}...")

    tests = [
        ("LogLog Processing", test_loglog_processor),
        ("LogLog Parsing Debug", debug_loglog_parsing),
        ("Claude API Connection", test_claude_api_connection),
        ("Knowledge Graph Building", test_knowledge_graph_building),
        ("Query Functionality", test_querying),
        ("Persistence", test_persistence),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}")
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed - check output above")
        return False


def main():
    """Main test runner."""
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()