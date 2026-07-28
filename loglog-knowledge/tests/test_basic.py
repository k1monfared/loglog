#!/usr/bin/env python3

"""
Basic tests for LogLog Knowledge Graph Service.

These tests verify core functionality without requiring Claude API access.
"""

import pytest
import tempfile
import os
from pathlib import Path

from loglog_knowledge.kg_core import (
    KnowledgeGraph, Entity, Relationship, Context,
    EntityType, RelationshipType
)
from loglog_knowledge.loglog_processor import LogLogProcessor, LogLogSection
from loglog_knowledge.persistence import KnowledgeGraphPersistence


# Sample LogLog content for testing
SAMPLE_LOGLOG = """
- Project Management
    - Team Members
        - John Doe - Project Manager
        - Jane Smith - Developer
    - Tasks
        [] Setup development environment
        [x] Create project structure
        [-] Implement core features
    - Meetings
        - Weekly standup #meeting
        - Sprint planning #meeting #planning
"""


class TestKnowledgeGraphCore:
    """Test core knowledge graph functionality."""

    def test_entity_creation(self):
        """Test entity creation and properties."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT,
            description="A test entity"
        )

        assert entity.name == "Test Entity"
        assert entity.entity_type == EntityType.CONCEPT
        assert entity.description == "A test entity"
        assert len(entity.contexts) == 0

    def test_relationship_creation(self):
        """Test relationship creation."""
        entity1 = Entity(name="Entity 1", entity_type=EntityType.PERSON)
        entity2 = Entity(name="Entity 2", entity_type=EntityType.PROJECT)

        relationship = Relationship(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type=RelationshipType.RELATED_TO,
            description="Test relationship"
        )

        assert relationship.source_entity_id == entity1.id
        assert relationship.target_entity_id == entity2.id
        assert relationship.relationship_type == RelationshipType.RELATED_TO

    def test_context_creation(self):
        """Test context creation."""
        context = Context(
            document_path="/test/path.log",
            hierarchical_path=["Project", "Tasks"],
            depth_level=2,
            todo_status="pending"
        )

        assert context.document_path == "/test/path.log"
        assert context.hierarchical_path == ["Project", "Tasks"]
        assert context.depth_level == 2
        assert context.todo_status == "pending"

    def test_knowledge_graph_operations(self):
        """Test knowledge graph basic operations."""
        kg = KnowledgeGraph()

        # Add entities
        entity1 = Entity(name="Person A", entity_type=EntityType.PERSON)
        entity2 = Entity(name="Project X", entity_type=EntityType.PROJECT)

        kg.add_entity(entity1)
        kg.add_entity(entity2)

        assert len(kg.entities) == 2
        assert kg.get_entity(entity1.id) == entity1

        # Add relationship
        relationship = Relationship(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type=RelationshipType.PART_OF
        )

        kg.add_relationship(relationship)
        assert len(kg.relationships) == 1

        # Test entity lookup
        found_entities = kg.get_entity_by_name("Person A")
        assert len(found_entities) == 1
        assert found_entities[0] == entity1

    def test_knowledge_graph_serialization(self):
        """Test knowledge graph JSON serialization."""
        kg = KnowledgeGraph()

        entity = Entity(name="Test Entity", entity_type=EntityType.CONCEPT)
        kg.add_entity(entity)

        # Test serialization
        data = kg.to_dict()
        assert "entities" in data
        assert "relationships" in data
        assert "contexts" in data

        # Test deserialization
        kg2 = KnowledgeGraph.from_dict(data)
        assert len(kg2.entities) == 1
        assert list(kg2.entities.values())[0].name == "Test Entity"


class TestLogLogProcessor:
    """Test LogLog document processing."""

    def test_process_text(self):
        """Test processing LogLog text content."""
        processor = LogLogProcessor()
        sections = processor.process_text(SAMPLE_LOGLOG, "test.log")

        assert len(sections) > 0

        # Check that we found some sections
        section_contents = [s.content for s in sections]
        assert any("Project Management" in content for content in section_contents)
        assert any("John Doe" in content for content in section_contents)

    def test_todo_status_extraction(self):
        """Test TODO status extraction."""
        processor = LogLogProcessor()

        # Test different TODO statuses
        test_cases = [
            ("[] Pending task", "pending"),
            ("[x] Completed task", "completed"),
            ("[-] In progress task", "in_progress"),
            ("[?] Unknown task", "unknown"),
            ("Regular task", None)
        ]

        for content, expected_status in test_cases:
            status = processor._extract_todo_status(content)
            assert status == expected_status

    def test_hashtag_extraction(self):
        """Test hashtag extraction."""
        processor = LogLogProcessor()

        content = "This is a test #important #meeting #planning"
        hashtags = processor._extract_hashtags(content)

        expected_hashtags = {"important", "meeting", "planning"}
        assert hashtags == expected_hashtags

    def test_section_grouping(self):
        """Test section grouping functionality."""
        processor = LogLogProcessor()
        sections = processor.process_text(SAMPLE_LOGLOG, "test.log")

        grouped = processor.group_sections_by_context(sections, max_section_size=500)
        assert len(grouped) > 0

        for group in grouped:
            assert "content" in group
            assert "context_info" in group
            assert "sections" in group


class TestPersistence:
    """Test database persistence functionality."""

    def test_database_initialization(self):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            with KnowledgeGraphPersistence(str(db_path)) as persistence:
                assert persistence.conn is not None
                assert db_path.exists()

    def test_save_and_load_knowledge_graph(self):
        """Test saving and loading knowledge graphs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            # Create test knowledge graph
            kg = KnowledgeGraph()
            entity = Entity(
                name="Test Entity",
                entity_type=EntityType.PERSON,
                description="A test person"
            )
            kg.add_entity(entity)

            # Save to database
            with KnowledgeGraphPersistence(str(db_path)) as persistence:
                kg_id = persistence.save_knowledge_graph(kg, "Test Graph")
                assert kg_id is not None

                # Load from database
                loaded_kg = persistence.load_knowledge_graph(kg_id)
                assert loaded_kg is not None
                assert len(loaded_kg.entities) == 1

                loaded_entity = list(loaded_kg.entities.values())[0]
                assert loaded_entity.name == "Test Entity"
                assert loaded_entity.entity_type == EntityType.PERSON

    def test_list_knowledge_graphs(self):
        """Test listing knowledge graphs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            with KnowledgeGraphPersistence(str(db_path)) as persistence:
                # Initially empty
                graphs = persistence.list_knowledge_graphs()
                assert len(graphs) == 0

                # Add a knowledge graph
                kg = KnowledgeGraph()
                kg_id = persistence.save_knowledge_graph(kg, "Test Graph")

                # Should show one graph
                graphs = persistence.list_knowledge_graphs()
                assert len(graphs) == 1
                assert graphs[0]['name'] == "Test Graph"
                assert graphs[0]['id'] == kg_id

    def test_delete_knowledge_graph(self):
        """Test deleting knowledge graphs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            with KnowledgeGraphPersistence(str(db_path)) as persistence:
                # Create and save knowledge graph
                kg = KnowledgeGraph()
                entity = Entity(name="Test Entity", entity_type=EntityType.CONCEPT)
                kg.add_entity(entity)

                kg_id = persistence.save_knowledge_graph(kg, "Test Graph")

                # Verify it exists
                assert persistence.load_knowledge_graph(kg_id) is not None

                # Delete it
                success = persistence.delete_knowledge_graph(kg_id)
                assert success

                # Verify it's gone
                assert persistence.load_knowledge_graph(kg_id) is None


def run_basic_tests():
    """Run basic tests without pytest."""
    print("🧪 Running Basic LogLog Knowledge Graph Tests")
    print("=" * 50)

    # Test core functionality
    print("📊 Testing Core Knowledge Graph...")
    test_core = TestKnowledgeGraphCore()
    test_core.test_entity_creation()
    test_core.test_relationship_creation()
    test_core.test_context_creation()
    test_core.test_knowledge_graph_operations()
    test_core.test_knowledge_graph_serialization()
    print("✅ Core tests passed")

    # Test LogLog processor
    print("📝 Testing LogLog Processor...")
    test_processor = TestLogLogProcessor()
    test_processor.test_process_text()
    test_processor.test_todo_status_extraction()
    test_processor.test_hashtag_extraction()
    test_processor.test_section_grouping()
    print("✅ Processor tests passed")

    # Test persistence
    print("💾 Testing Persistence...")
    test_persistence = TestPersistence()
    test_persistence.test_database_initialization()
    test_persistence.test_save_and_load_knowledge_graph()
    test_persistence.test_list_knowledge_graphs()
    test_persistence.test_delete_knowledge_graph()
    print("✅ Persistence tests passed")

    print("\n🎉 All basic tests completed successfully!")
    print("=" * 50)
    print("💡 To run full tests with Claude API integration:")
    print("   export CLAUDE_API_KEY='your-key' && python -m pytest tests/")


if __name__ == "__main__":
    run_basic_tests()