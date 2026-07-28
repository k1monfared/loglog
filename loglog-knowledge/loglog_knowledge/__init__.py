"""
LogLog Knowledge Graph Service

An independent Python package that creates contextual knowledge graphs
from LogLog hierarchical documents using Claude API.
"""

from .kg_core import KnowledgeGraph, Entity, Relationship, Context, EntityType, RelationshipType
from .claude_client import ClaudeClient
from .loglog_processor import LogLogProcessor
from .kg_builder import KnowledgeGraphBuilder, BuilderConfig
from .kg_query import KnowledgeGraphQuery
from .persistence import KnowledgeGraphPersistence

__version__ = "0.1.0"
__author__ = "LogLog Knowledge Graph"

__all__ = [
    "KnowledgeGraph",
    "Entity",
    "Relationship",
    "Context",
    "EntityType",
    "RelationshipType",
    "ClaudeClient",
    "LogLogProcessor",
    "KnowledgeGraphBuilder",
    "BuilderConfig",
    "KnowledgeGraphQuery",
    "KnowledgeGraphPersistence",
]