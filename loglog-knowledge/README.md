# LogLog Knowledge Graph Service

An independent Python package that creates contextual knowledge graphs from LogLog hierarchical documents using Claude API.

## Overview

LogLog Knowledge Graph Service analyzes LogLog documents to extract entities, relationships, and contextual information, building intelligent knowledge graphs that understand the hierarchical structure and can answer complex queries about document contents.

## Features

- **Context-Aware Entity Recognition**: Distinguishes between different contexts where the same entity is mentioned
- **Hierarchical Structure Preservation**: Maintains LogLog document structure in the knowledge graph
- **Intelligent Cross-Referencing**: Finds related topics and implicit relationships across documents
- **Natural Language Querying**: Ask questions about document contents in plain English
- **Incremental Processing**: Efficiently processes only changed document sections
- **Claude API Integration**: Leverages Claude for sophisticated text analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/loglog-knowledge.git
cd loglog-knowledge

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install loglog-knowledge
```

## Quick Start

```bash
# Set your Claude API key
export CLAUDE_API_LOGLOG="your-api-key-here"

# Build knowledge graph from LogLog file
loglog-kg build document.log

# Query the knowledge graph
loglog-kg query "What are the main topics discussed in the document?"

# Analyze relationships
loglog-kg analyze document.log --show-relationships
```

## Usage

### Building Knowledge Graphs

```python
from loglog_knowledge import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder(claude_api_key="your-key")
kg = builder.build_from_file("document.log")
```

### Querying Knowledge Graphs

```python
from loglog_knowledge import KnowledgeGraphQuery

query_engine = KnowledgeGraphQuery(kg, claude_api_key="your-key")
result = query_engine.query("Show me all contexts where Project A is discussed")
```

## CLI Commands

- `loglog-kg build <file>`: Build knowledge graph from LogLog file
- `loglog-kg query <question>`: Query the knowledge graph
- `loglog-kg analyze <file>`: Analyze document structure and relationships
- `loglog-kg export <format>`: Export knowledge graph to various formats

## Requirements

- Python 3.8+
- Claude API key (Anthropic) - set as `CLAUDE_API_LOGLOG` environment variable
- LogLog documents in `.log` format

## License

MIT License - see [LICENSE](LICENSE) for details.