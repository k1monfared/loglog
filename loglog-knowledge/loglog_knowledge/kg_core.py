"""
Core knowledge graph data structures and operations.

This module defines the fundamental data structures for representing
entities, relationships, contexts, and the knowledge graph itself.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import json


class EntityType(Enum):
    """Types of entities that can be extracted from LogLog documents."""
    CONCEPT = "concept"
    PERSON = "person"
    PROJECT = "project"
    TASK = "task"
    DECISION = "decision"
    TOPIC = "topic"
    LOCATION = "location"
    DATE = "date"
    UNKNOWN = "unknown"


class RelationshipType(Enum):
    """Types of relationships between entities."""
    RELATED_TO = "related_to"
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    MENTIONS = "mentions"
    PART_OF = "part_of"
    LEADS_TO = "leads_to"
    CONFLICTS_WITH = "conflicts_with"
    SIMILAR_TO = "similar_to"
    UNKNOWN = "unknown"


@dataclass
class Context:
    """
    Represents the context in which an entity or relationship appears.

    Contexts are crucial for distinguishing between different mentions
    of the same entity in different parts of a LogLog document.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_path: str = ""
    hierarchical_path: List[str] = field(default_factory=list)
    depth_level: int = 0
    parent_context: Optional[str] = None
    section_title: str = ""
    todo_status: Optional[str] = None
    hashtags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "id": self.id,
            "document_path": self.document_path,
            "hierarchical_path": self.hierarchical_path,
            "depth_level": self.depth_level,
            "parent_context": self.parent_context,
            "section_title": self.section_title,
            "todo_status": self.todo_status,
            "hashtags": list(self.hashtags),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        """Create context from dictionary."""
        context = cls(
            id=data["id"],
            document_path=data["document_path"],
            hierarchical_path=data["hierarchical_path"],
            depth_level=data["depth_level"],
            parent_context=data["parent_context"],
            section_title=data["section_title"],
            todo_status=data["todo_status"],
            hashtags=set(data["hashtags"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        return context


@dataclass
class Entity:
    """
    Represents an entity extracted from LogLog documents.

    Entities can appear in multiple contexts with different meanings
    or aspects, which are tracked separately.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    entity_type: EntityType = EntityType.UNKNOWN
    description: str = ""
    aliases: Set[str] = field(default_factory=set)
    contexts: Dict[str, Context] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_context(self, context: Context) -> None:
        """Add a context where this entity appears."""
        self.contexts[context.id] = context
        self.updated_at = datetime.now()

    def get_contexts_by_document(self, document_path: str) -> List[Context]:
        """Get all contexts for this entity in a specific document."""
        return [ctx for ctx in self.contexts.values()
                if ctx.document_path == document_path]

    def get_contexts_by_depth(self, depth: int) -> List[Context]:
        """Get all contexts for this entity at a specific depth level."""
        return [ctx for ctx in self.contexts.values()
                if ctx.depth_level == depth]

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "aliases": list(self.aliases),
            "contexts": {ctx_id: ctx.to_dict() for ctx_id, ctx in self.contexts.items()},
            "properties": self.properties,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        """Create entity from dictionary."""
        entity = cls(
            id=data["id"],
            name=data["name"],
            entity_type=EntityType(data["entity_type"]),
            description=data["description"],
            aliases=set(data["aliases"]),
            properties=data["properties"],
            confidence=data["confidence"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        entity.contexts = {
            ctx_id: Context.from_dict(ctx_data)
            for ctx_id, ctx_data in data["contexts"].items()
        }
        return entity


@dataclass
class Relationship:
    """
    Represents a relationship between two entities in the knowledge graph.

    Relationships are also context-aware, meaning the same entities
    can have different relationships in different contexts.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    relationship_type: RelationshipType = RelationshipType.UNKNOWN
    description: str = ""
    contexts: Dict[str, Context] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_context(self, context: Context) -> None:
        """Add a context where this relationship appears."""
        self.contexts[context.id] = context
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary for serialization."""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relationship_type": self.relationship_type.value,
            "description": self.description,
            "contexts": {ctx_id: ctx.to_dict() for ctx_id, ctx in self.contexts.items()},
            "properties": self.properties,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create relationship from dictionary."""
        relationship = cls(
            id=data["id"],
            source_entity_id=data["source_entity_id"],
            target_entity_id=data["target_entity_id"],
            relationship_type=RelationshipType(data["relationship_type"]),
            description=data["description"],
            properties=data["properties"],
            confidence=data["confidence"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        relationship.contexts = {
            ctx_id: Context.from_dict(ctx_data)
            for ctx_id, ctx_data in data["contexts"].items()
        }
        return relationship


class KnowledgeGraph:
    """
    Main knowledge graph class that manages entities, relationships, and contexts.

    Uses NetworkX for efficient graph operations while maintaining
    context-aware entity and relationship information.
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.contexts: Dict[str, Context] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the knowledge graph."""
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, entity=entity)

        # Add contexts to the global context store
        for context in entity.contexts.values():
            self.contexts[context.id] = context

        self.updated_at = datetime.now()

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the knowledge graph."""
        self.relationships[relationship.id] = relationship
        self.graph.add_edge(
            relationship.source_entity_id,
            relationship.target_entity_id,
            key=relationship.id,
            relationship=relationship
        )

        # Add contexts to the global context store
        for context in relationship.contexts.values():
            self.contexts[context.id] = context

        self.updated_at = datetime.now()

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def get_entity_by_name(self, name: str) -> List[Entity]:
        """Get entities by name (including aliases)."""
        matching_entities = []
        name_lower = name.lower()

        for entity in self.entities.values():
            if (entity.name.lower() == name_lower or
                any(alias.lower() == name_lower for alias in entity.aliases)):
                matching_entities.append(entity)

        return matching_entities

    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get a relationship by ID."""
        return self.relationships.get(relationship_id)

    def get_related_entities(self, entity_id: str, max_depth: int = 1) -> List[Tuple[Entity, int]]:
        """Get entities related to the given entity within max_depth hops."""
        if entity_id not in self.graph:
            return []

        related = []
        visited = set()
        queue = [(entity_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth >= max_depth:
                continue

            visited.add(current_id)

            # Get neighbors
            for neighbor_id in self.graph.neighbors(current_id):
                if neighbor_id not in visited:
                    entity = self.entities.get(neighbor_id)
                    if entity:
                        related.append((entity, depth + 1))
                        queue.append((neighbor_id, depth + 1))

        return related

    def find_path(self, source_entity_id: str, target_entity_id: str) -> List[str]:
        """Find the shortest path between two entities."""
        try:
            return nx.shortest_path(self.graph, source_entity_id, target_entity_id)
        except nx.NetworkXNoPath:
            return []

    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""
        return [entity for entity in self.entities.values()
                if entity.entity_type == entity_type]

    def get_entities_by_context_document(self, document_path: str) -> List[Entity]:
        """Get all entities that appear in a specific document."""
        entities = []
        for entity in self.entities.values():
            if any(ctx.document_path == document_path for ctx in entity.contexts.values()):
                entities.append(entity)
        return entities

    def get_entities_by_hashtag(self, hashtag: str) -> List[Entity]:
        """Get all entities that appear in contexts with a specific hashtag."""
        entities = []
        for entity in self.entities.values():
            if any(hashtag in ctx.hashtags for ctx in entity.contexts.values()):
                entities.append(entity)
        return entities

    def to_dict(self) -> Dict[str, Any]:
        """Convert knowledge graph to dictionary for serialization."""
        return {
            "entities": {entity_id: entity.to_dict() for entity_id, entity in self.entities.items()},
            "relationships": {rel_id: rel.to_dict() for rel_id, rel in self.relationships.items()},
            "contexts": {ctx_id: ctx.to_dict() for ctx_id, ctx in self.contexts.items()},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_json(self, filepath: str) -> None:
        """Export knowledge graph to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """Create knowledge graph from dictionary."""
        kg = cls()

        # Load entities
        for entity_data in data["entities"].values():
            entity = Entity.from_dict(entity_data)
            kg.add_entity(entity)

        # Load relationships
        for rel_data in data["relationships"].values():
            relationship = Relationship.from_dict(rel_data)
            kg.add_relationship(relationship)

        kg.created_at = datetime.fromisoformat(data["created_at"])
        kg.updated_at = datetime.fromisoformat(data["updated_at"])

        return kg

    @classmethod
    def from_json(cls, filepath: str) -> "KnowledgeGraph":
        """Load knowledge graph from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        entity_types = {}
        relationship_types = {}

        for entity in self.entities.values():
            entity_type = entity.entity_type.value
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        for relationship in self.relationships.values():
            rel_type = relationship.relationship_type.value
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "total_contexts": len(self.contexts),
            "entity_types": entity_types,
            "relationship_types": relationship_types,
            "graph_density": nx.density(self.graph),
            "connected_components": nx.number_weakly_connected_components(self.graph),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }