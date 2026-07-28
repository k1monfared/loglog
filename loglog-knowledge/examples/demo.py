#!/usr/bin/env python3

"""
LogLog Knowledge Graph Service Demo

This script demonstrates the key features of the LogLog Knowledge Graph Service:
- Building knowledge graphs from LogLog documents
- Querying with natural language
- Analyzing document contents
- Persistent storage and retrieval
"""

import asyncio
import os
import tempfile
from pathlib import Path

from loglog_knowledge import (
    KnowledgeGraphBuilder,
    KnowledgeGraphQuery,
    BuilderConfig
)
from loglog_knowledge.persistence import KnowledgeGraphPersistence


# Sample LogLog content for demonstration
SAMPLE_LOGLOG_CONTENT = """
- Project Alpha Development
    - Phase 1: Planning and Research
        - Market analysis
            [] Research competitor products
            [x] Define target audience
            [] Survey potential customers #market #research
        - Technical specifications
            [x] Define system architecture
            [] Choose technology stack #technical #architecture
            - Database design
                - User management system
                - Product catalog structure
                [] Implement user authentication #database #security
        - Team formation
            - John Smith - Project Manager
            - Sarah Johnson - Lead Developer
            - Mike Chen - UI/UX Designer #team #roles

    - Phase 2: Development Sprint 1
        - Backend development
            [x] Set up development environment
            [] Implement REST API endpoints #backend #api
            [] Database integration #database
        - Frontend development
            [] Create user interface mockups
            [] Implement responsive design #frontend #ui
        - Quality assurance
            [] Unit testing framework
            [] Integration testing #testing #qa

    - Phase 3: Testing and Deployment
        - System testing
            [] Performance testing #testing #performance
            [] Security audit #security
        - Deployment preparation
            [] Production environment setup
            [] CI/CD pipeline configuration #deployment #automation
        - Go-live activities
            [] User training sessions #training
            [] Launch marketing campaign #marketing

- Technical Decisions Log
    - Database Selection
        - Considered PostgreSQL for ACID compliance #database #decision
        - MongoDB rejected due to complex relationships
        - Final choice: PostgreSQL with proper indexing

    - Authentication Strategy
        - JWT tokens for stateless authentication #security #authentication
        - OAuth integration for social logins
        - Two-factor authentication for admin users

    - Frontend Framework
        - React chosen for component reusability #frontend #react
        - TypeScript for better type safety #typescript
        - Material-UI for consistent design system

- Meeting Notes
    - 2024-01-15 Sprint Planning
        - Discussed Phase 1 timeline
        - John assigned market research tasks
        - Sarah will lead technical architecture #meeting #planning

    - 2024-01-22 Technical Review
        - Database schema approved
        - API design discussions
        - Security requirements defined #meeting #technical

    - 2024-01-29 Progress Review
        - Backend API 60% complete
        - Frontend mockups ready for review
        - Testing framework needs attention #meeting #progress
"""


async def demo_knowledge_graph_service():
    """Demonstrate the complete knowledge graph service workflow."""

    print("🚀 LogLog Knowledge Graph Service Demo")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("❌ Claude API key not found")
        print("Please set your Claude API key:")
        print("  export CLAUDE_API_LOGLOG='your-key-here'")
        print("  or export CLAUDE_API_KEY='your-key-here'")
        return

    # Create temporary files and database
    with tempfile.TemporaryDirectory() as temp_dir:
        loglog_file = Path(temp_dir) / "project_alpha.log"
        db_path = Path(temp_dir) / "demo_knowledge.db"

        # Write sample LogLog content to file
        loglog_file.write_text(SAMPLE_LOGLOG_CONTENT)
        print(f"📝 Created sample LogLog file: {loglog_file}")

        # Step 1: Build Knowledge Graph
        print("\n🔨 Step 1: Building Knowledge Graph")
        print("-" * 30)

        config = BuilderConfig(
            max_section_size=800,
            min_entity_confidence=0.6,
            min_relationship_confidence=0.5,
            enable_cross_references=True
        )

        builder = KnowledgeGraphBuilder(api_key, config)

        print("⏳ Extracting entities and relationships from LogLog document...")
        kg = await builder.build_from_file(str(loglog_file))

        # Display statistics
        stats = kg.get_statistics()
        print(f"✅ Knowledge Graph built successfully!")
        print(f"   📊 Entities: {stats['total_entities']}")
        print(f"   🔗 Relationships: {stats['total_relationships']}")
        print(f"   📝 Contexts: {stats['total_contexts']}")
        print(f"   🌐 Graph Density: {stats['graph_density']:.3f}")

        # Show some sample entities
        print("\n🏷️  Sample Entities:")
        for i, (entity_id, entity) in enumerate(list(kg.entities.items())[:5]):
            print(f"   • {entity.name} ({entity.entity_type.value}): {entity.description[:50]}...")

        # Step 2: Save to Database
        print(f"\n💾 Step 2: Saving to Database")
        print("-" * 30)

        with KnowledgeGraphPersistence(str(db_path)) as persistence:
            kg_id = persistence.save_knowledge_graph(kg, "Project Alpha Demo")
            print(f"✅ Knowledge Graph saved with ID: {kg_id}")

        # Step 3: Query the Knowledge Graph
        print(f"\n🔍 Step 3: Querying Knowledge Graph")
        print("-" * 30)

        query_engine = KnowledgeGraphQuery(kg, api_key)

        # Sample queries
        queries = [
            "What are the main phases of Project Alpha?",
            "Who are the team members and what are their roles?",
            "What technical decisions were made and why?",
            "What tasks are still pending in the project?",
            "What security measures are being implemented?"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\n🤔 Query {i}: {query}")
            try:
                result = await query_engine.query(query, max_entities=15)
                print(f"💡 Answer: {result.answer[:200]}...")
                print(f"🎯 Confidence: {result.confidence:.2f}")
                if result.relevant_entities:
                    entity_names = [e.name for e in result.relevant_entities[:3]]
                    print(f"🏷️  Relevant Entities: {', '.join(entity_names)}")
            except Exception as e:
                print(f"❌ Query failed: {e}")

        # Step 4: Find Entity Contexts
        print(f"\n📍 Step 4: Finding Entity Contexts")
        print("-" * 30)

        # Look for "John Smith" entity contexts
        contexts = await query_engine.find_entity_contexts("John Smith")
        if contexts:
            print(f"📋 Found John Smith in {len(contexts)} contexts:")
            for ctx in contexts[:3]:
                path = " > ".join(ctx['hierarchical_path'])
                print(f"   • {ctx['document_path']} | {path}")

        # Step 5: Document Analysis
        print(f"\n📊 Step 5: Document Analysis")
        print("-" * 30)

        analysis = await query_engine.analyze_document(str(loglog_file))
        print(f"📄 Document Summary:")
        print(f"   {analysis.summary[:300]}...")

        if analysis.topics:
            print(f"🏷️  Main Topics: {', '.join(analysis.topics[:5])}")

        if analysis.insights:
            print(f"💡 Key Insights:")
            for insight in analysis.insights[:3]:
                print(f"   • {insight[:100]}...")

        # Step 6: Find Related Entities
        print(f"\n🕸️  Step 6: Finding Related Entities")
        print("-" * 30)

        related = await query_engine.find_related_entities("Project Alpha", max_depth=2)
        if related:
            print(f"🔗 Entities related to 'Project Alpha':")
            for entity, depth, path in related[:5]:
                print(f"   • {entity.name} (depth: {depth}) - {entity.entity_type.value}")

        # Step 7: Topic Clusters
        print(f"\n🎯 Step 7: Topic Clustering")
        print("-" * 30)

        clusters = await query_engine.find_topic_clusters(min_cluster_size=2)
        if clusters:
            print(f"📊 Found {len(clusters)} topic clusters:")
            for cluster in clusters[:3]:
                print(f"   • {cluster['name']}: {cluster['size']} entities ({cluster['description']})")

        # Step 8: Demonstrate Persistence
        print(f"\n🗄️  Step 8: Testing Persistence")
        print("-" * 30)

        with KnowledgeGraphPersistence(str(db_path)) as persistence:
            # List all graphs
            graphs = persistence.list_knowledge_graphs()
            print(f"📋 Knowledge Graphs in database: {len(graphs)}")
            for graph in graphs:
                print(f"   • {graph['name']} ({graph['id']}) - "
                      f"{graph['total_entities']} entities, {graph['total_relationships']} relationships")

            # Reload the graph
            print(f"🔄 Reloading knowledge graph from database...")
            reloaded_kg = persistence.load_knowledge_graph(kg_id)
            if reloaded_kg:
                reloaded_stats = reloaded_kg.get_statistics()
                print(f"✅ Successfully reloaded: {reloaded_stats['total_entities']} entities")

        print(f"\n🎉 Demo completed successfully!")
        print("=" * 50)
        print("💡 Next steps:")
        print("   • Try the CLI: loglog-kg build your_file.log")
        print("   • Query interactively: loglog-kg query 'your question'")
        print("   • Analyze documents: loglog-kg analyze --document your_file.log")


def main():
    """Main demo entry point."""
    print("Starting LogLog Knowledge Graph Demo...")
    print("This demo requires a Claude API key in the CLAUDE_API_LOGLOG or CLAUDE_API_KEY environment variable.")
    print()

    try:
        asyncio.run(demo_knowledge_graph_service())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()