"""
Persistence layer for knowledge graphs using SQLite backend.

This module provides database storage and retrieval capabilities
for knowledge graphs, entities, relationships, and contexts.
"""

import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from .kg_core import KnowledgeGraph, Entity, Relationship, Context, EntityType, RelationshipType


logger = logging.getLogger(__name__)


class KnowledgeGraphPersistence:
    """
    Persistence manager for knowledge graphs using SQLite database.

    Provides methods to save, load, and manage knowledge graphs
    with full support for entities, relationships, and contexts.
    """

    def __init__(self, db_path: str = "loglog_knowledge.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access

            # Create tables
            self._create_tables()

            logger.info(f"Database initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _create_tables(self) -> None:
        """Create database tables for knowledge graph storage."""
        cursor = self.conn.cursor()

        # Knowledge graphs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graphs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT
            )
        """)

        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                kg_id TEXT,
                name TEXT NOT NULL,
                entity_type TEXT,
                description TEXT,
                aliases TEXT,
                properties TEXT,
                confidence REAL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (kg_id) REFERENCES knowledge_graphs (id)
            )
        """)

        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                kg_id TEXT,
                source_entity_id TEXT,
                target_entity_id TEXT,
                relationship_type TEXT,
                description TEXT,
                properties TEXT,
                confidence REAL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (kg_id) REFERENCES knowledge_graphs (id),
                FOREIGN KEY (source_entity_id) REFERENCES entities (id),
                FOREIGN KEY (target_entity_id) REFERENCES entities (id)
            )
        """)

        # Contexts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                id TEXT PRIMARY KEY,
                kg_id TEXT,
                document_path TEXT,
                hierarchical_path TEXT,
                depth_level INTEGER,
                parent_context TEXT,
                section_title TEXT,
                todo_status TEXT,
                hashtags TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (kg_id) REFERENCES knowledge_graphs (id)
            )
        """)

        # Entity-Context associations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_contexts (
                entity_id TEXT,
                context_id TEXT,
                PRIMARY KEY (entity_id, context_id),
                FOREIGN KEY (entity_id) REFERENCES entities (id),
                FOREIGN KEY (context_id) REFERENCES contexts (id)
            )
        """)

        # Relationship-Context associations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationship_contexts (
                relationship_id TEXT,
                context_id TEXT,
                PRIMARY KEY (relationship_id, context_id),
                FOREIGN KEY (relationship_id) REFERENCES relationships (id),
                FOREIGN KEY (context_id) REFERENCES contexts (id)
            )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities (name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities (entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_document ON contexts (document_path)")

        self.conn.commit()

    def save_knowledge_graph(self, kg: KnowledgeGraph, name: str, kg_id: Optional[str] = None) -> str:
        """
        Save a knowledge graph to the database.

        Args:
            kg: KnowledgeGraph object to save
            name: Human-readable name for the knowledge graph
            kg_id: Optional ID for the knowledge graph (generates if not provided)

        Returns:
            ID of the saved knowledge graph
        """
        try:
            if kg_id is None:
                kg_id = f"kg_{int(datetime.now().timestamp())}"

            cursor = self.conn.cursor()

            # Save knowledge graph metadata
            cursor.execute("""
                INSERT OR REPLACE INTO knowledge_graphs
                (id, name, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                kg_id,
                name,
                kg.created_at.isoformat(),
                kg.updated_at.isoformat(),
                json.dumps(kg.get_statistics())
            ))

            # Save contexts first (they're referenced by entities and relationships)
            for context in kg.contexts.values():
                self._save_context(cursor, kg_id, context)

            # Save entities
            for entity in kg.entities.values():
                self._save_entity(cursor, kg_id, entity)

            # Save relationships
            for relationship in kg.relationships.values():
                self._save_relationship(cursor, kg_id, relationship)

            self.conn.commit()
            logger.info(f"Knowledge graph saved with ID: {kg_id}")
            return kg_id

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save knowledge graph: {e}")
            raise

    def load_knowledge_graph(self, kg_id: str) -> Optional[KnowledgeGraph]:
        """
        Load a knowledge graph from the database.

        Args:
            kg_id: ID of the knowledge graph to load

        Returns:
            KnowledgeGraph object or None if not found
        """
        try:
            cursor = self.conn.cursor()

            # Check if knowledge graph exists
            cursor.execute("SELECT * FROM knowledge_graphs WHERE id = ?", (kg_id,))
            kg_row = cursor.fetchone()

            if not kg_row:
                logger.warning(f"Knowledge graph not found: {kg_id}")
                return None

            # Create new knowledge graph
            kg = KnowledgeGraph()
            kg.created_at = datetime.fromisoformat(kg_row['created_at'])
            kg.updated_at = datetime.fromisoformat(kg_row['updated_at'])

            # Load contexts
            contexts = self._load_contexts(cursor, kg_id)
            for context in contexts:
                kg.contexts[context.id] = context

            # Load entities
            entities = self._load_entities(cursor, kg_id, kg.contexts)
            for entity in entities:
                kg.entities[entity.id] = entity

            # Load relationships
            relationships = self._load_relationships(cursor, kg_id, kg.contexts)
            for relationship in relationships:
                kg.relationships[relationship.id] = relationship

            # Rebuild NetworkX graph
            for entity in kg.entities.values():
                kg.graph.add_node(entity.id, entity=entity)

            for relationship in kg.relationships.values():
                kg.graph.add_edge(
                    relationship.source_entity_id,
                    relationship.target_entity_id,
                    key=relationship.id,
                    relationship=relationship
                )

            logger.info(f"Knowledge graph loaded: {kg_id}")
            return kg

        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return None

    def list_knowledge_graphs(self) -> List[Dict[str, Any]]:
        """
        List all knowledge graphs in the database.

        Returns:
            List of knowledge graph information dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, name, created_at, updated_at, metadata
                FROM knowledge_graphs
                ORDER BY updated_at DESC
            """)

            graphs = []
            for row in cursor.fetchall():
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                graphs.append({
                    'id': row['id'],
                    'name': row['name'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'total_entities': metadata.get('total_entities', 0),
                    'total_relationships': metadata.get('total_relationships', 0),
                    'total_contexts': metadata.get('total_contexts', 0)
                })

            return graphs

        except Exception as e:
            logger.error(f"Failed to list knowledge graphs: {e}")
            return []

    def delete_knowledge_graph(self, kg_id: str) -> bool:
        """
        Delete a knowledge graph and all associated data.

        Args:
            kg_id: ID of the knowledge graph to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            # Delete in order due to foreign key constraints
            cursor.execute("DELETE FROM entity_contexts WHERE entity_id IN (SELECT id FROM entities WHERE kg_id = ?)", (kg_id,))
            cursor.execute("DELETE FROM relationship_contexts WHERE relationship_id IN (SELECT id FROM relationships WHERE kg_id = ?)", (kg_id,))
            cursor.execute("DELETE FROM relationships WHERE kg_id = ?", (kg_id,))
            cursor.execute("DELETE FROM entities WHERE kg_id = ?", (kg_id,))
            cursor.execute("DELETE FROM contexts WHERE kg_id = ?", (kg_id,))
            cursor.execute("DELETE FROM knowledge_graphs WHERE id = ?", (kg_id,))

            self.conn.commit()
            logger.info(f"Knowledge graph deleted: {kg_id}")
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to delete knowledge graph: {e}")
            return False

    def _save_context(self, cursor: sqlite3.Cursor, kg_id: str, context: Context) -> None:
        """Save a context to the database."""
        cursor.execute("""
            INSERT OR REPLACE INTO contexts
            (id, kg_id, document_path, hierarchical_path, depth_level,
             parent_context, section_title, todo_status, hashtags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            context.id,
            kg_id,
            context.document_path,
            json.dumps(context.hierarchical_path),
            context.depth_level,
            context.parent_context,
            context.section_title,
            context.todo_status,
            json.dumps(list(context.hashtags)),
            context.created_at.isoformat()
        ))

    def _save_entity(self, cursor: sqlite3.Cursor, kg_id: str, entity: Entity) -> None:
        """Save an entity to the database."""
        cursor.execute("""
            INSERT OR REPLACE INTO entities
            (id, kg_id, name, entity_type, description, aliases,
             properties, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.id,
            kg_id,
            entity.name,
            entity.entity_type.value,
            entity.description,
            json.dumps(list(entity.aliases)),
            json.dumps(entity.properties),
            entity.confidence,
            entity.created_at.isoformat(),
            entity.updated_at.isoformat()
        ))

        # Save entity-context associations
        for context_id in entity.contexts.keys():
            cursor.execute("""
                INSERT OR REPLACE INTO entity_contexts (entity_id, context_id)
                VALUES (?, ?)
            """, (entity.id, context_id))

    def _save_relationship(self, cursor: sqlite3.Cursor, kg_id: str, relationship: Relationship) -> None:
        """Save a relationship to the database."""
        cursor.execute("""
            INSERT OR REPLACE INTO relationships
            (id, kg_id, source_entity_id, target_entity_id, relationship_type,
             description, properties, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship.id,
            kg_id,
            relationship.source_entity_id,
            relationship.target_entity_id,
            relationship.relationship_type.value,
            relationship.description,
            json.dumps(relationship.properties),
            relationship.confidence,
            relationship.created_at.isoformat(),
            relationship.updated_at.isoformat()
        ))

        # Save relationship-context associations
        for context_id in relationship.contexts.keys():
            cursor.execute("""
                INSERT OR REPLACE INTO relationship_contexts (relationship_id, context_id)
                VALUES (?, ?)
            """, (relationship.id, context_id))

    def _load_contexts(self, cursor: sqlite3.Cursor, kg_id: str) -> List[Context]:
        """Load contexts from the database."""
        cursor.execute("SELECT * FROM contexts WHERE kg_id = ?", (kg_id,))
        contexts = []

        for row in cursor.fetchall():
            context = Context(
                id=row['id'],
                document_path=row['document_path'],
                hierarchical_path=json.loads(row['hierarchical_path']),
                depth_level=row['depth_level'],
                parent_context=row['parent_context'],
                section_title=row['section_title'],
                todo_status=row['todo_status'],
                hashtags=set(json.loads(row['hashtags'])),
                created_at=datetime.fromisoformat(row['created_at'])
            )
            contexts.append(context)

        return contexts

    def _load_entities(self, cursor: sqlite3.Cursor, kg_id: str, contexts: Dict[str, Context]) -> List[Entity]:
        """Load entities from the database."""
        cursor.execute("SELECT * FROM entities WHERE kg_id = ?", (kg_id,))
        entities = []

        for row in cursor.fetchall():
            entity = Entity(
                id=row['id'],
                name=row['name'],
                entity_type=EntityType(row['entity_type']),
                description=row['description'],
                aliases=set(json.loads(row['aliases'])),
                properties=json.loads(row['properties']),
                confidence=row['confidence'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )

            # Load entity contexts
            cursor.execute("SELECT context_id FROM entity_contexts WHERE entity_id = ?", (entity.id,))
            context_ids = [r[0] for r in cursor.fetchall()]

            for context_id in context_ids:
                if context_id in contexts:
                    entity.contexts[context_id] = contexts[context_id]

            entities.append(entity)

        return entities

    def _load_relationships(
        self,
        cursor: sqlite3.Cursor,
        kg_id: str,
        contexts: Dict[str, Context]
    ) -> List[Relationship]:
        """Load relationships from the database."""
        cursor.execute("SELECT * FROM relationships WHERE kg_id = ?", (kg_id,))
        relationships = []

        for row in cursor.fetchall():
            relationship = Relationship(
                id=row['id'],
                source_entity_id=row['source_entity_id'],
                target_entity_id=row['target_entity_id'],
                relationship_type=RelationshipType(row['relationship_type']),
                description=row['description'],
                properties=json.loads(row['properties']),
                confidence=row['confidence'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )

            # Load relationship contexts
            cursor.execute("SELECT context_id FROM relationship_contexts WHERE relationship_id = ?", (relationship.id,))
            context_ids = [r[0] for r in cursor.fetchall()]

            for context_id in context_ids:
                if context_id in contexts:
                    relationship.contexts[context_id] = contexts[context_id]

            relationships.append(relationship)

        return relationships

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()