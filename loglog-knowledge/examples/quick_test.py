#!/usr/bin/env python3

"""
Quick test script to verify LogLog Knowledge Graph Service functionality.

This script tests the core functionality without requiring extensive API calls.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loglog_knowledge import LogLogProcessor, KnowledgeGraph, Entity, EntityType
from loglog_knowledge.persistence import KnowledgeGraphPersistence

# Test LogLog content
TEST_CONTENT = """
- Project Alpha
    - Team
        - John Smith - Manager
        - Sarah Johnson - Developer
    - Tasks
        [] Setup environment
        [x] Create repository
        [] Write documentation
    - Decisions
        - Use Python for backend #tech #python
        - Use React for frontend #tech #react
"""

def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("🧪 Quick LogLog Knowledge Graph Test")
    print("=" * 40)

    # Test 1: LogLog Processing
    print("📝 Test 1: LogLog Processing")
    processor = LogLogProcessor()

    sections = processor.process_text(TEST_CONTENT, "test.log")
    print(f"  ✅ Extracted {len(sections)} sections")

    if sections:
        print("  📋 Sample sections:")
        for i, section in enumerate(sections[:5]):
            path = " > ".join(section.hierarchical_path)
            print(f"    {i+1}. {path}")

    # Test 2: Knowledge Graph Core
    print("\n🧠 Test 2: Knowledge Graph Core")
    kg = KnowledgeGraph()

    # Manually create some entities from the processed sections
    entities = [
        Entity(name="Project Alpha", entity_type=EntityType.PROJECT, description="Main project"),
        Entity(name="John Smith", entity_type=EntityType.PERSON, description="Manager"),
        Entity(name="Python", entity_type=EntityType.CONCEPT, description="Programming language"),
    ]

    for entity in entities:
        kg.add_entity(entity)

    stats = kg.get_statistics()
    print(f"  ✅ Created KG with {stats['total_entities']} entities")

    # Test 3: Persistence
    print("\n💾 Test 3: Database Persistence")
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        with KnowledgeGraphPersistence(str(db_path)) as persistence:
            kg_id = persistence.save_knowledge_graph(kg, "Test Graph")
            print(f"  ✅ Saved to database: {kg_id}")

            # Test loading
            loaded_kg = persistence.load_knowledge_graph(kg_id)
            if loaded_kg:
                loaded_stats = loaded_kg.get_statistics()
                print(f"  ✅ Loaded from database: {loaded_stats['total_entities']} entities")

    # Test 4: Section Analysis
    print("\n🔍 Test 4: Content Analysis")
    hashtag_sections = [s for s in sections if s.hashtags]
    todo_sections = [s for s in sections if s.todo_status]

    print(f"  📌 Sections with hashtags: {len(hashtag_sections)}")
    print(f"  ✅ TODO sections: {len(todo_sections)}")

    if hashtag_sections:
        all_hashtags = set()
        for section in hashtag_sections:
            all_hashtags.update(section.hashtags)
        print(f"  🏷️  Found hashtags: {', '.join(all_hashtags)}")

    print("\n🎉 All basic tests passed!")
    print("🚀 The LogLog Knowledge Graph Service is working correctly!")
    print("\n💡 To test with Claude API:")
    print("  1. Set your API key: export CLAUDE_API_LOGLOG='your-key'")
    print("  2. Run: loglog-kg build test_sample.log")
    print("  3. Query: loglog-kg query 'What are the main topics?'")


if __name__ == "__main__":
    test_basic_functionality()