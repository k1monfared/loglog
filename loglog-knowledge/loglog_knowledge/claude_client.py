"""
Claude API client for knowledge graph operations.

This module handles all interactions with the Anthropic Claude API,
including entity extraction, relationship identification, and querying.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import aiohttp
from anthropic import Anthropic, AsyncAnthropic
from pydantic import BaseModel, Field

from .kg_core import EntityType, RelationshipType


logger = logging.getLogger(__name__)


class EntityExtractionResponse(BaseModel):
    """Response model for entity extraction from Claude API."""
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    processing_notes: Optional[str] = None


class RelationshipExtractionResponse(BaseModel):
    """Response model for relationship extraction from Claude API."""
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    processing_notes: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for knowledge graph queries."""
    answer: str
    relevant_entities: List[str] = Field(default_factory=list)
    relevant_relationships: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)


@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting."""
    requests_per_minute: int = 50
    tokens_per_minute: int = 100000
    max_retries: int = 3
    backoff_factor: float = 2.0


class ClaudeClient:
    """
    Async client for interacting with Claude API for knowledge graph operations.

    Handles rate limiting, error handling, and response parsing for
    entity extraction, relationship identification, and querying.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20250114",
        rate_limit_config: Optional[RateLimitConfig] = None,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.rate_limit_config = rate_limit_config or RateLimitConfig()

        # Initialize both sync and async clients
        self.sync_client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)

        # Rate limiting tracking
        self._request_times: List[float] = []
        self._token_usage: List[tuple[float, int]] = []

    async def _check_rate_limits(self, estimated_tokens: int = 1000) -> None:
        """Check and enforce rate limits before making a request."""
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old request times
        self._request_times = [t for t in self._request_times if t > minute_ago]
        self._token_usage = [(t, tokens) for t, tokens in self._token_usage if t > minute_ago]

        # Check request rate limit
        if len(self._request_times) >= self.rate_limit_config.requests_per_minute:
            sleep_time = 60 - (current_time - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

        # Check token rate limit
        total_tokens = sum(tokens for _, tokens in self._token_usage)
        if total_tokens + estimated_tokens > self.rate_limit_config.tokens_per_minute:
            sleep_time = 60 - (current_time - self._token_usage[0][0])
            if sleep_time > 0:
                logger.info(f"Token limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

    async def _make_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Make a request to Claude API with retry logic and rate limiting."""
        await self._check_rate_limits(estimated_tokens=max_tokens)

        messages = [{"role": "user", "content": prompt}]

        for attempt in range(self.rate_limit_config.max_retries):
            try:
                response = await self.async_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages,
                )

                # Track usage for rate limiting
                current_time = time.time()
                self._request_times.append(current_time)
                if hasattr(response, 'usage'):
                    token_count = response.usage.input_tokens + response.usage.output_tokens
                    self._token_usage.append((current_time, token_count))

                return {
                    "content": response.content[0].text,
                    "usage": response.usage if hasattr(response, 'usage') else None
                }

            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")

                if attempt == self.rate_limit_config.max_retries - 1:
                    raise

                # Exponential backoff
                sleep_time = self.rate_limit_config.backoff_factor ** attempt
                await asyncio.sleep(sleep_time)

        raise RuntimeError("Max retries exceeded")

    async def extract_entities(
        self,
        text: str,
        context_info: Optional[Dict[str, Any]] = None
    ) -> EntityExtractionResponse:
        """
        Extract entities from text using Claude API.

        Args:
            text: The text to analyze for entities
            context_info: Additional context information (document path, depth, etc.)

        Returns:
            EntityExtractionResponse with extracted entities and confidence
        """
        context_str = ""
        if context_info:
            context_str = f"""
Context Information:
- Document: {context_info.get('document_path', 'unknown')}
- Depth Level: {context_info.get('depth_level', 0)}
- Section: {context_info.get('section_title', 'unknown')}
- TODO Status: {context_info.get('todo_status', 'none')}
- Hashtags: {', '.join(context_info.get('hashtags', []))}
"""

        system_prompt = f"""You are an expert at extracting entities from hierarchical LogLog documents.

LogLog documents use a nested list structure where everything is a list item with indentation indicating hierarchy.
Your task is to extract meaningful entities from the given text while being aware of the hierarchical context.

Entity types to identify:
- CONCEPT: Abstract ideas, methodologies, technologies
- PERSON: Names of individuals
- PROJECT: Named projects, initiatives, or efforts
- TASK: Specific tasks or action items
- DECISION: Decisions made or to be made
- TOPIC: Subject areas or themes
- LOCATION: Places, locations, or venues
- DATE: Time references, deadlines, or dates

Return your response as valid JSON with this structure:
{{
    "entities": [
        {{
            "name": "entity name",
            "type": "CONCEPT|PERSON|PROJECT|TASK|DECISION|TOPIC|LOCATION|DATE",
            "description": "brief description of the entity",
            "aliases": ["alternative names"],
            "properties": {{"any additional properties": "value"}}
        }}
    ],
    "confidence": 0.85,
    "processing_notes": "any notes about the extraction process"
}}

Be conservative in entity extraction - only extract clear, meaningful entities.
Consider the hierarchical context when determining entity importance.
{context_str}"""

        prompt = f"""Analyze this LogLog document text and extract entities:

{text}

Remember to consider the hierarchical structure and context when extracting entities."""

        try:
            response = await self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.1
            )

            # Parse JSON response
            content = response["content"]
            try:
                data = json.loads(content)
                return EntityExtractionResponse(**data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                return EntityExtractionResponse(
                    entities=[],
                    confidence=0.0,
                    processing_notes="Failed to parse response"
                )

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return EntityExtractionResponse(
                entities=[],
                confidence=0.0,
                processing_notes=f"Error: {str(e)}"
            )

    async def extract_relationships(
        self,
        text: str,
        entities: List[Dict[str, Any]],
        context_info: Optional[Dict[str, Any]] = None
    ) -> RelationshipExtractionResponse:
        """
        Extract relationships between entities using Claude API.

        Args:
            text: The text to analyze for relationships
            entities: List of entities found in the text
            context_info: Additional context information

        Returns:
            RelationshipExtractionResponse with extracted relationships and confidence
        """
        entities_str = "\n".join([
            f"- {entity['name']} ({entity['type']}): {entity['description']}"
            for entity in entities
        ])

        context_str = ""
        if context_info:
            context_str = f"""
Context Information:
- Document: {context_info.get('document_path', 'unknown')}
- Depth Level: {context_info.get('depth_level', 0)}
- Section: {context_info.get('section_title', 'unknown')}
"""

        system_prompt = f"""You are an expert at identifying relationships between entities in hierarchical LogLog documents.

Given a list of entities and the text they were extracted from, identify meaningful relationships between them.

Relationship types to identify:
- RELATED_TO: General relationship or connection
- CONTAINS: One entity contains or includes another
- DEPENDS_ON: One entity depends on another
- MENTIONS: One entity is mentioned in context of another
- PART_OF: One entity is part of another
- LEADS_TO: One entity leads to or results in another
- CONFLICTS_WITH: Entities that conflict or contradict
- SIMILAR_TO: Entities that are similar or comparable

Return your response as valid JSON with this structure:
{{
    "relationships": [
        {{
            "source_entity": "entity name",
            "target_entity": "entity name",
            "relationship_type": "RELATED_TO|CONTAINS|DEPENDS_ON|etc",
            "description": "description of the relationship",
            "properties": {{"any additional properties": "value"}}
        }}
    ],
    "confidence": 0.85,
    "processing_notes": "any notes about the extraction process"
}}

Only identify relationships that are clearly implied or stated in the text.
Consider the hierarchical structure when determining relationships.
{context_str}"""

        prompt = f"""Analyze the relationships between these entities in the given text:

Entities:
{entities_str}

Text:
{text}

Identify meaningful relationships between the entities based on the text content and LogLog structure."""

        try:
            response = await self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.1
            )

            # Parse JSON response
            content = response["content"]
            try:
                data = json.loads(content)
                return RelationshipExtractionResponse(**data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                return RelationshipExtractionResponse(
                    relationships=[],
                    confidence=0.0,
                    processing_notes="Failed to parse response"
                )

        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return RelationshipExtractionResponse(
                relationships=[],
                confidence=0.0,
                processing_notes=f"Error: {str(e)}"
            )

    async def query_knowledge_graph(
        self,
        query: str,
        graph_data: Dict[str, Any],
        max_entities: int = 20
    ) -> QueryResponse:
        """
        Query the knowledge graph using natural language.

        Args:
            query: Natural language query
            graph_data: Serialized knowledge graph data
            max_entities: Maximum number of entities to include in context

        Returns:
            QueryResponse with answer and relevant information
        """
        # Summarize graph data for context
        entities_summary = []
        relationships_summary = []

        entities = graph_data.get("entities", {})
        relationships = graph_data.get("relationships", {})

        for entity_id, entity_data in list(entities.items())[:max_entities]:
            entities_summary.append(
                f"- {entity_data['name']} ({entity_data['entity_type']}): {entity_data['description']}"
            )

        for rel_id, rel_data in list(relationships.items())[:max_entities]:
            source_name = entities.get(rel_data['source_entity_id'], {}).get('name', 'Unknown')
            target_name = entities.get(rel_data['target_entity_id'], {}).get('name', 'Unknown')
            relationships_summary.append(
                f"- {source_name} {rel_data['relationship_type']} {target_name}: {rel_data['description']}"
            )

        system_prompt = """You are an expert at answering questions about knowledge graphs built from LogLog documents.

You will be given a natural language query and information about entities and relationships in the knowledge graph.
Provide accurate, helpful answers based on the available information.

Return your response as valid JSON with this structure:
{
    "answer": "detailed answer to the query",
    "relevant_entities": ["list of entity names that were relevant"],
    "relevant_relationships": ["list of relationship descriptions that were relevant"],
    "confidence": 0.85,
    "sources": ["list of source contexts or documents if available"]
}

Be honest about limitations in the available data and provide the most helpful answer possible."""

        prompt = f"""Answer this query about the knowledge graph:

Query: {query}

Available Entities:
{chr(10).join(entities_summary[:20])}

Available Relationships:
{chr(10).join(relationships_summary[:20])}

Provide a comprehensive answer based on the available information."""

        try:
            response = await self._make_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.2
            )

            # Parse JSON response
            content = response["content"]
            try:
                data = json.loads(content)
                return QueryResponse(**data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                return QueryResponse(
                    answer="Failed to parse response from Claude API",
                    confidence=0.0
                )

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return QueryResponse(
                answer=f"Error processing query: {str(e)}",
                confidence=0.0
            )

    def extract_entities_sync(
        self,
        text: str,
        context_info: Optional[Dict[str, Any]] = None
    ) -> EntityExtractionResponse:
        """Synchronous version of extract_entities."""
        return asyncio.run(self.extract_entities(text, context_info))

    def extract_relationships_sync(
        self,
        text: str,
        entities: List[Dict[str, Any]],
        context_info: Optional[Dict[str, Any]] = None
    ) -> RelationshipExtractionResponse:
        """Synchronous version of extract_relationships."""
        return asyncio.run(self.extract_relationships(text, entities, context_info))

    def query_knowledge_graph_sync(
        self,
        query: str,
        graph_data: Dict[str, Any],
        max_entities: int = 20
    ) -> QueryResponse:
        """Synchronous version of query_knowledge_graph."""
        return asyncio.run(self.query_knowledge_graph(query, graph_data, max_entities))