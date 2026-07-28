"""
LogLog document processor for knowledge graph integration.

This module handles parsing LogLog documents and extracting contextual
information while preserving the hierarchical structure.
"""

import os
import re
import sys
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import hashlib

# Add the parent loglog directory to the path to import the loglog module
# This should point to /home/k1/Projects/loglog
loglog_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(loglog_parent_dir)

try:
    from loglog import TreeNode, build_tree_from_file, build_tree_from_text
    LOGLOG_AVAILABLE = True
except ImportError as e:
    # Fallback implementation if loglog module is not available
    class TreeNode:
        def __init__(self, name="", children=None, data=""):
            self.name = name
            self.children = children or []
            self.data = data
            self.type = "regular"

        def add_child(self, node):
            self.children.append(node)

    def build_tree_from_file(file_path):
        with open(file_path, "r") as file:
            text_lines = file.readlines()
        return build_tree_from_text(text_lines)

    def build_tree_from_text(text_lines):
        root = TreeNode(name="")
        root.type = "root"
        # Simplified parsing for fallback
        return root

    LOGLOG_AVAILABLE = False

from .kg_core import Context


@dataclass
class LogLogSection:
    """
    Represents a section of a LogLog document with its context information.
    """
    content: str
    depth: int
    hierarchical_path: List[str]
    parent_content: Optional[str]
    todo_status: Optional[str]
    hashtags: Set[str]
    line_number: int
    section_id: str


class LogLogProcessor:
    """
    Processes LogLog documents to extract contextual information
    for knowledge graph construction.
    """

    def __init__(self):
        self.hashtag_pattern = re.compile(r'#(\w+)')
        self.todo_patterns = {
            'pending': re.compile(r'^\[\s*\]'),
            'completed': re.compile(r'^\[x\]', re.IGNORECASE),
            'in_progress': re.compile(r'^\[-\]'),
            'unknown': re.compile(r'^\[.\]')
        }

    def is_loglog_available(self) -> bool:
        """Check if the original LogLog module is available."""
        return LOGLOG_AVAILABLE

    def process_file(self, file_path: str) -> List[LogLogSection]:
        """
        Process a LogLog file and extract sections with context information.

        Args:
            file_path: Path to the LogLog file

        Returns:
            List of LogLogSection objects with contextual information
        """
        try:
            tree = build_tree_from_file(file_path)
            return self._extract_sections_from_tree(tree, file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to process LogLog file {file_path}: {e}")

    def process_text(self, text: str, file_path: str = "unknown") -> List[LogLogSection]:
        """
        Process LogLog text content and extract sections with context information.

        Args:
            text: LogLog formatted text content
            file_path: Path identifier for the content

        Returns:
            List of LogLogSection objects with contextual information
        """
        try:
            text_lines = text.split('\n') if isinstance(text, str) else text
            tree = build_tree_from_text(text_lines)
            return self._extract_sections_from_tree(tree, file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to process LogLog text: {e}")

    def _extract_sections_from_tree(self, tree: TreeNode, file_path: str) -> List[LogLogSection]:
        """
        Extract sections from a TreeNode structure.

        Args:
            tree: Root TreeNode from LogLog parsing
            file_path: Path to the source file

        Returns:
            List of LogLogSection objects
        """
        sections = []

        def traverse_node(node: TreeNode, depth: int = 0, path: List[str] = None, line_num: int = 0):
            if path is None:
                path = []

            # Skip root node
            if hasattr(node, 'type') and node.type == "root":
                for i, child in enumerate(node.children):
                    traverse_node(child, 0, [], i)
                return

            # Extract content and metadata from current node
            content = self._clean_content(node.data)
            if not content.strip():
                return

            # Build hierarchical path
            current_path = path + [self._extract_title(content)]

            # Extract hashtags
            hashtags = self._extract_hashtags(content)

            # Determine TODO status
            todo_status = self._extract_todo_status(content)

            # Create section ID
            section_id = self._generate_section_id(file_path, current_path, depth, line_num)

            # Create section object
            section = LogLogSection(
                content=content,
                depth=depth,
                hierarchical_path=current_path,
                parent_content=path[-1] if path else None,
                todo_status=todo_status,
                hashtags=hashtags,
                line_number=line_num,
                section_id=section_id
            )

            sections.append(section)

            # Recursively process children
            for i, child in enumerate(node.children):
                traverse_node(child, depth + 1, current_path, line_num + i + 1)

        traverse_node(tree)
        return sections

    def _clean_content(self, content: str) -> str:
        """Clean content by removing TODO markers and excessive whitespace."""
        if not content:
            return ""

        # Remove leading dash and whitespace (but keep the content)
        content = re.sub(r'^-\s*', '', content)

        # Remove TODO markers
        for pattern in self.todo_patterns.values():
            content = pattern.sub('', content)

        return content.strip()

    def _extract_title(self, content: str, max_length: int = 50) -> str:
        """Extract a title from content for hierarchical path."""
        if not content:
            return "untitled"

        # Clean content first
        cleaned = self._clean_content(content)

        # Take first sentence or up to max_length characters
        first_sentence = cleaned.split('.')[0].strip()
        if first_sentence and len(first_sentence) <= max_length:
            return first_sentence

        # Truncate if too long
        if len(cleaned) > max_length:
            return cleaned[:max_length - 3] + "..."

        return cleaned if cleaned else "untitled"

    def _extract_hashtags(self, content: str) -> Set[str]:
        """Extract hashtags from content."""
        if not content:
            return set()

        return set(self.hashtag_pattern.findall(content))

    def _extract_todo_status(self, content: str) -> Optional[str]:
        """Extract TODO status from content."""
        if not content:
            return None

        for status, pattern in self.todo_patterns.items():
            if pattern.match(content.strip()):
                return status

        return None

    def _generate_section_id(self, file_path: str, path: List[str], depth: int, line_num: int) -> str:
        """Generate a unique ID for a section."""
        # Create a unique identifier based on file, path, depth, and line
        identifier_parts = [
            os.path.basename(file_path),
            str(depth),
            str(line_num),
        ] + path

        identifier_string = "|".join(identifier_parts)
        return hashlib.md5(identifier_string.encode()).hexdigest()[:12]

    def create_contexts(self, sections: List[LogLogSection], document_path: str) -> List[Context]:
        """
        Create Context objects from LogLogSection objects.

        Args:
            sections: List of LogLogSection objects
            document_path: Path to the document

        Returns:
            List of Context objects
        """
        contexts = []

        for section in sections:
            context = Context(
                document_path=document_path,
                hierarchical_path=section.hierarchical_path,
                depth_level=section.depth,
                section_title=section.hierarchical_path[-1] if section.hierarchical_path else "",
                todo_status=section.todo_status,
                hashtags=section.hashtags
            )
            contexts.append(context)

        return contexts

    def group_sections_by_context(self, sections: List[LogLogSection], max_section_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Group related sections together for efficient processing.

        Args:
            sections: List of LogLogSection objects
            max_section_size: Maximum character count per grouped section

        Returns:
            List of grouped sections with combined content and context info
        """
        grouped_sections = []
        current_group = {
            'content': [],
            'sections': [],
            'char_count': 0,
            'depth_range': [float('inf'), float('-inf')],
            'hashtags': set(),
            'todo_statuses': set(),
            'hierarchical_paths': []
        }

        def finalize_group():
            if current_group['sections']:
                # Combine content
                combined_content = '\n'.join(current_group['content'])

                # Create combined context info
                context_info = {
                    'document_path': sections[0].hierarchical_path[0] if sections else "unknown",
                    'depth_range': current_group['depth_range'],
                    'hashtags': list(current_group['hashtags']),
                    'todo_statuses': list(current_group['todo_statuses']),
                    'hierarchical_paths': current_group['hierarchical_paths'],
                    'section_count': len(current_group['sections'])
                }

                grouped_sections.append({
                    'content': combined_content,
                    'context_info': context_info,
                    'sections': current_group['sections'].copy()
                })

        for section in sections:
            # Check if adding this section would exceed size limit
            section_size = len(section.content)

            if (current_group['char_count'] + section_size > max_section_size and
                current_group['sections']):
                # Finalize current group and start new one
                finalize_group()
                current_group = {
                    'content': [],
                    'sections': [],
                    'char_count': 0,
                    'depth_range': [float('inf'), float('-inf')],
                    'hashtags': set(),
                    'todo_statuses': set(),
                    'hierarchical_paths': []
                }

            # Add section to current group
            current_group['content'].append(section.content)
            current_group['sections'].append(section)
            current_group['char_count'] += section_size

            # Update metadata
            current_group['depth_range'][0] = min(current_group['depth_range'][0], section.depth)
            current_group['depth_range'][1] = max(current_group['depth_range'][1], section.depth)
            current_group['hashtags'].update(section.hashtags)
            if section.todo_status:
                current_group['todo_statuses'].add(section.todo_status)
            current_group['hierarchical_paths'].append(section.hierarchical_path)

        # Finalize last group
        finalize_group()

        return grouped_sections

    def find_cross_references(self, sections: List[LogLogSection]) -> List[Dict[str, Any]]:
        """
        Find potential cross-references between sections based on content similarity
        and shared entities.

        Args:
            sections: List of LogLogSection objects

        Returns:
            List of cross-reference information
        """
        cross_refs = []

        # Build a simple word index for finding related sections
        word_to_sections = {}

        for i, section in enumerate(sections):
            # Extract meaningful words (excluding common stop words)
            words = self._extract_meaningful_words(section.content)

            for word in words:
                if word not in word_to_sections:
                    word_to_sections[word] = []
                word_to_sections[word].append((i, section))

        # Find sections with shared words
        processed_pairs = set()

        for word, section_list in word_to_sections.items():
            if len(section_list) < 2:
                continue

            # Check all pairs of sections that share this word
            for i in range(len(section_list)):
                for j in range(i + 1, len(section_list)):
                    idx1, section1 = section_list[i]
                    idx2, section2 = section_list[j]

                    pair_key = tuple(sorted([idx1, idx2]))
                    if pair_key in processed_pairs:
                        continue

                    processed_pairs.add(pair_key)

                    # Calculate similarity score
                    similarity = self._calculate_section_similarity(section1, section2)

                    if similarity > 0.3:  # Threshold for considering sections related
                        cross_refs.append({
                            'section1_id': section1.section_id,
                            'section2_id': section2.section_id,
                            'similarity_score': similarity,
                            'shared_words': [word],
                            'relationship_type': self._infer_relationship_type(section1, section2)
                        })

        return cross_refs

    def _extract_meaningful_words(self, content: str, min_length: int = 3) -> Set[str]:
        """Extract meaningful words from content, excluding common stop words."""
        if not content:
            return set()

        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'
        }

        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())

        # Filter meaningful words
        meaningful_words = {
            word for word in words
            if len(word) >= min_length and word not in stop_words
        }

        return meaningful_words

    def _calculate_section_similarity(self, section1: LogLogSection, section2: LogLogSection) -> float:
        """Calculate similarity score between two sections."""
        # Get word sets
        words1 = self._extract_meaningful_words(section1.content)
        words2 = self._extract_meaningful_words(section2.content)

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        jaccard_similarity = intersection / union if union > 0 else 0.0

        # Boost similarity for shared hashtags
        hashtag_bonus = 0.2 * len(section1.hashtags.intersection(section2.hashtags))

        # Boost similarity for similar hierarchical positions
        depth_similarity = 0.1 if abs(section1.depth - section2.depth) <= 1 else 0.0

        return min(1.0, jaccard_similarity + hashtag_bonus + depth_similarity)

    def _infer_relationship_type(self, section1: LogLogSection, section2: LogLogSection) -> str:
        """Infer the type of relationship between two sections."""
        # Check hierarchical relationship
        if section1.depth + 1 == section2.depth:
            return "CONTAINS"
        elif section2.depth + 1 == section1.depth:
            return "PART_OF"
        elif section1.depth == section2.depth:
            return "SIMILAR_TO"
        else:
            return "RELATED_TO"