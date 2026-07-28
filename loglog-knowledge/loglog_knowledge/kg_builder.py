"""
Knowledge graph builder for LogLog documents.

This module coordinates the extraction of entities and relationships
from LogLog documents using Claude API and builds the knowledge graph.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import time

from .kg_core import (
    KnowledgeGraph, Entity, Relationship, Context,
    EntityType, RelationshipType
)
from .claude_client import ClaudeClient, EntityExtractionResponse, RelationshipExtractionResponse
from .loglog_processor import LogLogProcessor, LogLogSection


logger = logging.getLogger(__name__)


@dataclass
class BuilderConfig:
    """Configuration for knowledge graph builder."""
    max_section_size: int = 1000
    min_entity_confidence: float = 0.6
    min_relationship_confidence: float = 0.5
    batch_size: int = 5
    enable_cross_references: bool = True
    enable_incremental_updates: bool = True


class KnowledgeGraphBuilder:
    """
    Main knowledge graph builder that coordinates all components
    to extract entities and relationships from LogLog documents.
    """

    def __init__(
        self,
        claude_api_key: str,
        config: Optional[BuilderConfig] = None
    ):
        self.config = config or BuilderConfig()
        self.claude_client = ClaudeClient(claude_api_key)
        self.loglog_processor = LogLogProcessor()
        self.entity_cache: Dict[str, Entity] = {}
        self.relationship_cache: Dict[str, Relationship] = {}

    async def build_from_file(self, file_path: str) -> KnowledgeGraph:
        """
        Build a knowledge graph from a LogLog file.

        Args:
            file_path: Path to the LogLog file

        Returns:
            KnowledgeGraph object with extracted entities and relationships
        """
        logger.info(f"Building knowledge graph from file: {file_path}")

        try:
            # Process LogLog document
            sections = self.loglog_processor.process_file(file_path)
            logger.info(f"Extracted {len(sections)} sections from document")

            # Group sections for efficient processing
            grouped_sections = self.loglog_processor.group_sections_by_context(
                sections, self.config.max_section_size
            )
            logger.info(f"Grouped into {len(grouped_sections)} processing batches")

            # Build knowledge graph from grouped sections
            kg = await self._build_knowledge_graph(grouped_sections, file_path)

            # Add cross-references if enabled
            if self.config.enable_cross_references:
                await self._add_cross_references(kg, sections)

            logger.info(f"Knowledge graph built successfully: {len(kg.entities)} entities, "
                       f"{len(kg.relationships)} relationships")

            return kg

        except Exception as e:
            logger.error(f"Failed to build knowledge graph from {file_path}: {e}")
            raise

    async def build_from_text(self, text: str, source_name: str = "text_input") -> KnowledgeGraph:
        """
        Build a knowledge graph from LogLog text content.

        Args:
            text: LogLog formatted text
            source_name: Identifier for the text source

        Returns:
            KnowledgeGraph object with extracted entities and relationships
        """
        logger.info(f"Building knowledge graph from text: {source_name}")

        try:
            # Process LogLog text
            sections = self.loglog_processor.process_text(text, source_name)
            logger.info(f"Extracted {len(sections)} sections from text")

            # Group sections for efficient processing
            grouped_sections = self.loglog_processor.group_sections_by_context(
                sections, self.config.max_section_size
            )

            # Build knowledge graph
            kg = await self._build_knowledge_graph(grouped_sections, source_name)

            # Add cross-references if enabled
            if self.config.enable_cross_references:
                await self._add_cross_references(kg, sections)

            return kg

        except Exception as e:
            logger.error(f"Failed to build knowledge graph from text: {e}")
            raise

    async def update_knowledge_graph(
        self,
        kg: KnowledgeGraph,
        file_path: str,
        changed_sections: Optional[List[LogLogSection]] = None
    ) -> KnowledgeGraph:
        """
        Update an existing knowledge graph with changes from a document.

        Args:
            kg: Existing knowledge graph
            file_path: Path to the updated document
            changed_sections: Specific sections that changed (if known)

        Returns:
            Updated KnowledgeGraph object
        """
        if not self.config.enable_incremental_updates:
            # Full rebuild
            return await self.build_from_file(file_path)

        logger.info(f"Updating knowledge graph for file: {file_path}")

        try:
            if changed_sections is None:
                # Process entire file to identify changes
                sections = self.loglog_processor.process_file(file_path)
                # For now, process all sections. Future optimization:
                # compare with existing entities to identify actual changes
                changed_sections = sections

            if not changed_sections:
                logger.info("No changes detected")
                return kg

            # Group changed sections
            grouped_sections = self.loglog_processor.group_sections_by_context(
                changed_sections, self.config.max_section_size
            )

            # Extract and update entities/relationships
            await self._update_graph_sections(kg, grouped_sections, file_path)

            logger.info(f"Knowledge graph updated: {len(kg.entities)} entities, "
                       f"{len(kg.relationships)} relationships")

            return kg

        except Exception as e:
            logger.error(f"Failed to update knowledge graph: {e}")
            raise

    async def _build_knowledge_graph(
        self,
        grouped_sections: List[Dict[str, Any]],
        source_path: str
    ) -> KnowledgeGraph:
        """Build knowledge graph from grouped sections."""
        kg = KnowledgeGraph()

        # Process sections in batches
        for i in range(0, len(grouped_sections), self.config.batch_size):
            batch = grouped_sections[i:i + self.config.batch_size]
            await self._process_section_batch(kg, batch, source_path)

            # Add small delay to respect rate limits
            await asyncio.sleep(0.1)

        return kg

    async def _process_section_batch(
        self,
        kg: KnowledgeGraph,
        batch: List[Dict[str, Any]],
        source_path: str
    ) -> None:
        """Process a batch of grouped sections."""
        tasks = []

        for group in batch:
            task = self._process_section_group(kg, group, source_path)
            tasks.append(task)

        # Process batch concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_section_group(
        self,
        kg: KnowledgeGraph,
        group: Dict[str, Any],
        source_path: str
    ) -> None:
        """Process a single grouped section."""
        try:
            content = group['content']
            context_info = group['context_info']
            sections = group['sections']

            # Extract entities
            entity_response = await self.claude_client.extract_entities(
                content, context_info
            )

            if entity_response.confidence < self.config.min_entity_confidence:
                logger.warning(f"Low confidence entity extraction: {entity_response.confidence}")

            # Create entity objects and contexts
            entities = []
            for entity_data in entity_response.entities:
                entity = await self._create_entity_from_data(entity_data, sections, source_path)
                if entity:
                    entities.append(entity)
                    kg.add_entity(entity)

            # Extract relationships if we have entities
            if len(entities) >= 2:
                relationship_response = await self.claude_client.extract_relationships(
                    content, entity_response.entities, context_info
                )

                if relationship_response.confidence >= self.config.min_relationship_confidence:
                    # Create relationship objects
                    for rel_data in relationship_response.relationships:
                        relationship = await self._create_relationship_from_data(
                            rel_data, entities, sections, source_path
                        )
                        if relationship:
                            kg.add_relationship(relationship)

        except Exception as e:
            logger.error(f"Failed to process section group: {e}")

    async def _create_entity_from_data(
        self,
        entity_data: Dict[str, Any],
        sections: List[LogLogSection],
        source_path: str
    ) -> Optional[Entity]:
        """Create an Entity object from extracted data."""
        try:
            # Map string type to enum
            entity_type_str = entity_data.get('type', 'UNKNOWN')
            try:
                entity_type = EntityType(entity_type_str.lower())
            except ValueError:
                entity_type = EntityType.UNKNOWN

            # Create or get existing entity
            entity_name = entity_data['name']
            entity_key = f"{entity_name}:{entity_type.value}"

            if entity_key in self.entity_cache:
                entity = self.entity_cache[entity_key]
            else:
                entity = Entity(
                    name=entity_name,
                    entity_type=entity_type,
                    description=entity_data.get('description', ''),
                    aliases=set(entity_data.get('aliases', [])),
                    properties=entity_data.get('properties', {})
                )
                self.entity_cache[entity_key] = entity

            # Add contexts from sections
            for section in sections:
                context = Context(
                    document_path=source_path,
                    hierarchical_path=section.hierarchical_path,
                    depth_level=section.depth,
                    section_title=section.hierarchical_path[-1] if section.hierarchical_path else "",
                    todo_status=section.todo_status,
                    hashtags=section.hashtags
                )
                entity.add_context(context)

            return entity

        except Exception as e:
            logger.error(f"Failed to create entity from data: {e}")
            return None

    async def _create_relationship_from_data(
        self,
        rel_data: Dict[str, Any],
        entities: List[Entity],
        sections: List[LogLogSection],
        source_path: str
    ) -> Optional[Relationship]:
        """Create a Relationship object from extracted data."""
        try:
            # Find source and target entities
            source_name = rel_data.get('source_entity', '')
            target_name = rel_data.get('target_entity', '')

            source_entity = None
            target_entity = None

            for entity in entities:
                if entity.name.lower() == source_name.lower():
                    source_entity = entity
                elif entity.name.lower() == target_name.lower():
                    target_entity = entity

            if not source_entity or not target_entity:
                logger.warning(f"Could not find entities for relationship: {source_name} -> {target_name}")
                return None

            # Map string type to enum
            rel_type_str = rel_data.get('relationship_type', 'UNKNOWN')
            try:
                rel_type = RelationshipType(rel_type_str.lower())
            except ValueError:
                rel_type = RelationshipType.UNKNOWN

            # Create relationship
            relationship = Relationship(
                source_entity_id=source_entity.id,
                target_entity_id=target_entity.id,
                relationship_type=rel_type,
                description=rel_data.get('description', ''),
                properties=rel_data.get('properties', {})
            )

            # Add contexts from sections
            for section in sections:
                context = Context(
                    document_path=source_path,
                    hierarchical_path=section.hierarchical_path,
                    depth_level=section.depth,
                    section_title=section.hierarchical_path[-1] if section.hierarchical_path else "",
                    todo_status=section.todo_status,
                    hashtags=section.hashtags
                )
                relationship.add_context(context)

            return relationship

        except Exception as e:
            logger.error(f"Failed to create relationship from data: {e}")
            return None

    async def _add_cross_references(
        self,
        kg: KnowledgeGraph,
        sections: List[LogLogSection]
    ) -> None:
        """Add cross-references between related sections."""
        try:
            cross_refs = self.loglog_processor.find_cross_references(sections)
            logger.info(f"Found {len(cross_refs)} potential cross-references")

            for cross_ref in cross_refs:
                # Find entities in the referenced sections
                section1_entities = self._find_entities_in_section(kg, cross_ref['section1_id'])
                section2_entities = self._find_entities_in_section(kg, cross_ref['section2_id'])

                # Create relationships between related entities
                for entity1 in section1_entities[:2]:  # Limit to avoid too many relationships
                    for entity2 in section2_entities[:2]:
                        if entity1.id != entity2.id:
                            # Check if relationship already exists
                            existing = self._find_existing_relationship(kg, entity1.id, entity2.id)
                            if not existing:
                                rel_type_str = cross_ref.get('relationship_type', 'RELATED_TO')
                                try:
                                    rel_type = RelationshipType(rel_type_str.lower())
                                except ValueError:
                                    rel_type = RelationshipType.RELATED_TO

                                relationship = Relationship(
                                    source_entity_id=entity1.id,
                                    target_entity_id=entity2.id,
                                    relationship_type=rel_type,
                                    description=f"Cross-reference (similarity: {cross_ref['similarity_score']:.2f})",
                                    confidence=cross_ref['similarity_score']
                                )

                                kg.add_relationship(relationship)

        except Exception as e:
            logger.error(f"Failed to add cross-references: {e}")

    def _find_entities_in_section(self, kg: KnowledgeGraph, section_id: str) -> List[Entity]:
        """Find entities that appear in a specific section."""
        entities = []
        for entity in kg.entities.values():
            for context in entity.contexts.values():
                if hasattr(context, 'section_id') and context.section_id == section_id:
                    entities.append(entity)
                    break
        return entities

    def _find_existing_relationship(
        self,
        kg: KnowledgeGraph,
        source_id: str,
        target_id: str
    ) -> Optional[Relationship]:
        """Find existing relationship between two entities."""
        for relationship in kg.relationships.values():
            if ((relationship.source_entity_id == source_id and
                 relationship.target_entity_id == target_id) or
                (relationship.source_entity_id == target_id and
                 relationship.target_entity_id == source_id)):
                return relationship
        return None

    async def _update_graph_sections(
        self,
        kg: KnowledgeGraph,
        grouped_sections: List[Dict[str, Any]],
        source_path: str
    ) -> None:
        """Update specific sections in the knowledge graph."""
        # For incremental updates, we would:
        # 1. Remove entities/relationships from changed sections
        # 2. Re-extract entities/relationships from new content
        # 3. Update cross-references

        # For now, implement as additive updates
        for i in range(0, len(grouped_sections), self.config.batch_size):
            batch = grouped_sections[i:i + self.config.batch_size]
            await self._process_section_batch(kg, batch, source_path)
            await asyncio.sleep(0.1)

    # Synchronous convenience methods
    def build_from_file_sync(self, file_path: str) -> KnowledgeGraph:
        """Synchronous version of build_from_file."""
        return asyncio.run(self.build_from_file(file_path))

    def build_from_text_sync(self, text: str, source_name: str = "text_input") -> KnowledgeGraph:
        """Synchronous version of build_from_text."""
        return asyncio.run(self.build_from_text(text, source_name))

    def update_knowledge_graph_sync(
        self,
        kg: KnowledgeGraph,
        file_path: str,
        changed_sections: Optional[List[LogLogSection]] = None
    ) -> KnowledgeGraph:
        """Synchronous version of update_knowledge_graph."""
        return asyncio.run(self.update_knowledge_graph(kg, file_path, changed_sections))