"""
Knowledge graph query engine for natural language querying and analysis.

This module provides intelligent querying capabilities for knowledge graphs
built from LogLog documents.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import json

from .kg_core import KnowledgeGraph, Entity, Relationship, Context, EntityType, RelationshipType
from .claude_client import ClaudeClient, QueryResponse


logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a knowledge graph query."""
    answer: str
    confidence: float
    relevant_entities: List[Entity]
    relevant_relationships: List[Relationship]
    sources: List[str]
    query_metadata: Dict[str, Any]


@dataclass
class AnalysisResult:
    """Result of knowledge graph analysis."""
    summary: str
    key_entities: List[Entity]
    important_relationships: List[Relationship]
    topics: List[str]
    insights: List[str]
    statistics: Dict[str, Any]


class KnowledgeGraphQuery:
    """
    Query engine for knowledge graphs with natural language support
    and advanced graph analysis capabilities.
    """

    def __init__(self, knowledge_graph: KnowledgeGraph, claude_api_key: str):
        self.kg = knowledge_graph
        self.claude_client = ClaudeClient(claude_api_key)

    async def query(self, question: str, max_entities: int = 20) -> QueryResult:
        """
        Query the knowledge graph with natural language.

        Args:
            question: Natural language question
            max_entities: Maximum number of entities to include in context

        Returns:
            QueryResult with answer and supporting information
        """
        logger.info(f"Processing query: {question}")

        try:
            # Prepare graph data for Claude
            graph_data = self._prepare_graph_context(max_entities)

            # Query Claude with the graph context
            response = await self.claude_client.query_knowledge_graph(
                question, graph_data, max_entities
            )

            # Find relevant entities and relationships
            relevant_entities = self._find_relevant_entities(response.relevant_entities)
            relevant_relationships = self._find_relevant_relationships(response.relevant_relationships)

            result = QueryResult(
                answer=response.answer,
                confidence=response.confidence,
                relevant_entities=relevant_entities,
                relevant_relationships=relevant_relationships,
                sources=response.sources,
                query_metadata={
                    'question': question,
                    'total_entities_searched': len(self.kg.entities),
                    'total_relationships_searched': len(self.kg.relationships),
                    'relevant_entity_count': len(relevant_entities),
                    'relevant_relationship_count': len(relevant_relationships)
                }
            )

            logger.info(f"Query completed with confidence: {response.confidence}")
            return result

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return QueryResult(
                answer=f"Sorry, I encountered an error processing your query: {str(e)}",
                confidence=0.0,
                relevant_entities=[],
                relevant_relationships=[],
                sources=[],
                query_metadata={'error': str(e)}
            )

    async def find_entity_contexts(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Find all contexts where an entity is mentioned.

        Args:
            entity_name: Name of the entity to search for

        Returns:
            List of context information for the entity
        """
        entities = self.kg.get_entity_by_name(entity_name)

        contexts_info = []
        for entity in entities:
            for context in entity.contexts.values():
                context_info = {
                    'entity_name': entity.name,
                    'entity_type': entity.entity_type.value,
                    'document_path': context.document_path,
                    'hierarchical_path': context.hierarchical_path,
                    'depth_level': context.depth_level,
                    'section_title': context.section_title,
                    'todo_status': context.todo_status,
                    'hashtags': list(context.hashtags),
                    'context_id': context.id
                }
                contexts_info.append(context_info)

        return contexts_info

    async def find_related_entities(
        self,
        entity_name: str,
        max_depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> List[Tuple[Entity, int, List[str]]]:
        """
        Find entities related to a given entity.

        Args:
            entity_name: Name of the entity to start from
            max_depth: Maximum relationship depth to explore
            relationship_types: Filter by specific relationship types

        Returns:
            List of (entity, depth, path) tuples
        """
        entities = self.kg.get_entity_by_name(entity_name)
        if not entities:
            return []

        start_entity = entities[0]  # Use first match
        related = []

        # Use graph traversal to find related entities
        visited = set()
        queue = [(start_entity.id, 0, [start_entity.name])]

        while queue:
            current_id, depth, path = queue.pop(0)

            if current_id in visited or depth >= max_depth:
                continue

            visited.add(current_id)

            # Get relationships from this entity
            for rel in self.kg.relationships.values():
                next_entity_id = None
                rel_path = path.copy()

                if rel.source_entity_id == current_id:
                    next_entity_id = rel.target_entity_id
                    rel_path.append(f"--{rel.relationship_type.value}-->")
                elif rel.target_entity_id == current_id:
                    next_entity_id = rel.source_entity_id
                    rel_path.append(f"<--{rel.relationship_type.value}--")

                if next_entity_id and next_entity_id not in visited:
                    # Filter by relationship types if specified
                    if relationship_types and rel.relationship_type not in relationship_types:
                        continue

                    next_entity = self.kg.get_entity(next_entity_id)
                    if next_entity:
                        rel_path.append(next_entity.name)
                        related.append((next_entity, depth + 1, rel_path))
                        queue.append((next_entity_id, depth + 1, rel_path))

        return related

    async def analyze_document(self, document_path: str) -> AnalysisResult:
        """
        Analyze a specific document in the knowledge graph.

        Args:
            document_path: Path to the document to analyze

        Returns:
            AnalysisResult with comprehensive analysis
        """
        logger.info(f"Analyzing document: {document_path}")

        try:
            # Get entities and relationships for this document
            entities = self.kg.get_entities_by_context_document(document_path)

            # Get relationships involving these entities
            entity_ids = {e.id for e in entities}
            relationships = [
                rel for rel in self.kg.relationships.values()
                if rel.source_entity_id in entity_ids or rel.target_entity_id in entity_ids
            ]

            # Prepare analysis prompt
            entity_summaries = []
            for entity in entities[:20]:  # Limit for Claude context
                contexts_count = len([ctx for ctx in entity.contexts.values()
                                    if ctx.document_path == document_path])
                entity_summaries.append(
                    f"- {entity.name} ({entity.entity_type.value}): {entity.description} "
                    f"(mentioned {contexts_count} times)"
                )

            relationship_summaries = []
            for rel in relationships[:15]:
                source = self.kg.get_entity(rel.source_entity_id)
                target = self.kg.get_entity(rel.target_entity_id)
                if source and target:
                    relationship_summaries.append(
                        f"- {source.name} {rel.relationship_type.value} {target.name}: {rel.description}"
                    )

            analysis_prompt = f"""Analyze this LogLog document based on its knowledge graph:

Document: {document_path}

Key Entities:
{chr(10).join(entity_summaries)}

Key Relationships:
{chr(10).join(relationship_summaries)}

Provide a comprehensive analysis including:
1. Document summary
2. Main topics and themes
3. Key insights and patterns
4. Important decisions or actions
5. Notable relationships between concepts

Return as JSON with this structure:
{{
    "summary": "comprehensive document summary",
    "main_topics": ["topic1", "topic2", "topic3"],
    "key_insights": ["insight1", "insight2"],
    "important_decisions": ["decision1", "decision2"],
    "relationship_patterns": ["pattern1", "pattern2"]
}}"""

            response = await self.claude_client._make_request(
                prompt=analysis_prompt,
                max_tokens=2000,
                temperature=0.2
            )

            # Parse analysis response
            try:
                analysis_data = json.loads(response["content"])
            except json.JSONDecodeError:
                analysis_data = {
                    "summary": response["content"],
                    "main_topics": [],
                    "key_insights": [],
                    "important_decisions": [],
                    "relationship_patterns": []
                }

            # Create analysis result
            result = AnalysisResult(
                summary=analysis_data.get("summary", "Analysis not available"),
                key_entities=entities[:10],  # Top entities
                important_relationships=relationships[:10],  # Top relationships
                topics=analysis_data.get("main_topics", []),
                insights=(
                    analysis_data.get("key_insights", []) +
                    analysis_data.get("important_decisions", []) +
                    analysis_data.get("relationship_patterns", [])
                ),
                statistics={
                    "total_entities": len(entities),
                    "total_relationships": len(relationships),
                    "entity_types": self._get_entity_type_counts(entities),
                    "relationship_types": self._get_relationship_type_counts(relationships),
                    "document_path": document_path
                }
            )

            logger.info(f"Document analysis completed: {len(entities)} entities, {len(relationships)} relationships")
            return result

        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return AnalysisResult(
                summary=f"Analysis failed: {str(e)}",
                key_entities=[],
                important_relationships=[],
                topics=[],
                insights=[],
                statistics={"error": str(e)}
            )

    async def find_topic_clusters(self, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
        """
        Find clusters of related topics in the knowledge graph.

        Args:
            min_cluster_size: Minimum number of entities in a cluster

        Returns:
            List of topic clusters with metadata
        """
        # Use hashtags and entity types to identify clusters
        hashtag_clusters = {}
        type_clusters = {}

        # Group by hashtags
        for entity in self.kg.entities.values():
            entity_hashtags = set()
            for context in entity.contexts.values():
                entity_hashtags.update(context.hashtags)

            for hashtag in entity_hashtags:
                if hashtag not in hashtag_clusters:
                    hashtag_clusters[hashtag] = []
                hashtag_clusters[hashtag].append(entity)

        # Group by entity types
        for entity in self.kg.entities.values():
            entity_type = entity.entity_type.value
            if entity_type not in type_clusters:
                type_clusters[entity_type] = []
            type_clusters[entity_type].append(entity)

        clusters = []

        # Process hashtag clusters
        for hashtag, entities in hashtag_clusters.items():
            if len(entities) >= min_cluster_size:
                clusters.append({
                    "type": "hashtag",
                    "name": f"#{hashtag}",
                    "entities": entities,
                    "size": len(entities),
                    "description": f"Entities related to #{hashtag}"
                })

        # Process type clusters
        for entity_type, entities in type_clusters.items():
            if len(entities) >= min_cluster_size:
                clusters.append({
                    "type": "entity_type",
                    "name": entity_type.title(),
                    "entities": entities,
                    "size": len(entities),
                    "description": f"All {entity_type} entities"
                })

        # Sort by size
        clusters.sort(key=lambda x: x["size"], reverse=True)
        return clusters

    def _prepare_graph_context(self, max_entities: int) -> Dict[str, Any]:
        """Prepare graph data for Claude API context."""
        # Select most important entities and relationships
        entities_data = {}
        relationships_data = {}

        # Sort entities by number of contexts (importance indicator)
        sorted_entities = sorted(
            self.kg.entities.items(),
            key=lambda x: len(x[1].contexts),
            reverse=True
        )

        for entity_id, entity in sorted_entities[:max_entities]:
            entities_data[entity_id] = entity.to_dict()

        # Get relationships involving the selected entities
        selected_entity_ids = set(entities_data.keys())
        for rel_id, relationship in self.kg.relationships.items():
            if (relationship.source_entity_id in selected_entity_ids or
                relationship.target_entity_id in selected_entity_ids):
                relationships_data[rel_id] = relationship.to_dict()

        return {
            "entities": entities_data,
            "relationships": relationships_data,
            "contexts": {ctx_id: ctx.to_dict() for ctx_id, ctx in self.kg.contexts.items()}
        }

    def _find_relevant_entities(self, entity_names: List[str]) -> List[Entity]:
        """Find Entity objects by names."""
        entities = []
        for name in entity_names:
            matching_entities = self.kg.get_entity_by_name(name)
            entities.extend(matching_entities)
        return entities

    def _find_relevant_relationships(self, relationship_descriptions: List[str]) -> List[Relationship]:
        """Find Relationship objects by descriptions (simplified matching)."""
        relationships = []
        for description in relationship_descriptions:
            # Simple matching by description content
            for rel in self.kg.relationships.values():
                if description.lower() in rel.description.lower():
                    relationships.append(rel)
                    break
        return relationships

    def _get_entity_type_counts(self, entities: List[Entity]) -> Dict[str, int]:
        """Get counts of entity types."""
        type_counts = {}
        for entity in entities:
            entity_type = entity.entity_type.value
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts

    def _get_relationship_type_counts(self, relationships: List[Relationship]) -> Dict[str, int]:
        """Get counts of relationship types."""
        type_counts = {}
        for relationship in relationships:
            rel_type = relationship.relationship_type.value
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts

    # Synchronous convenience methods
    def query_sync(self, question: str, max_entities: int = 20) -> QueryResult:
        """Synchronous version of query."""
        return asyncio.run(self.query(question, max_entities))

    def find_entity_contexts_sync(self, entity_name: str) -> List[Dict[str, Any]]:
        """Synchronous version of find_entity_contexts."""
        return asyncio.run(self.find_entity_contexts(entity_name))

    def find_related_entities_sync(
        self,
        entity_name: str,
        max_depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> List[Tuple[Entity, int, List[str]]]:
        """Synchronous version of find_related_entities."""
        return asyncio.run(self.find_related_entities(entity_name, max_depth, relationship_types))

    def analyze_document_sync(self, document_path: str) -> AnalysisResult:
        """Synchronous version of analyze_document."""
        return asyncio.run(self.analyze_document(document_path))

    def find_topic_clusters_sync(self, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
        """Synchronous version of find_topic_clusters."""
        return asyncio.run(self.find_topic_clusters(min_cluster_size))