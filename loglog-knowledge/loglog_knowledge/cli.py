"""
Command-line interface for LogLog Knowledge Graph Service.

This module provides the main CLI commands for building, querying,
and managing knowledge graphs from LogLog documents.
"""

import os
import sys
import asyncio
import logging
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
import json

from .kg_builder import KnowledgeGraphBuilder, BuilderConfig
from .kg_query import KnowledgeGraphQuery
from .persistence import KnowledgeGraphPersistence
from .kg_core import KnowledgeGraph


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()


def get_claude_api_key() -> str:
    """Get Claude API key from environment or user input."""
    # Try CLAUDE_API_LOGLOG first, then fall back to CLAUDE_API_KEY
    api_key = os.getenv('CLAUDE_API_LOGLOG') or os.getenv('CLAUDE_API_KEY')
    if not api_key:
        api_key = click.prompt('Claude API Key', hide_input=True, type=str)
        if not api_key:
            console.print("[red]Claude API key is required[/red]")
            sys.exit(1)
    return api_key


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--db-path', default='loglog_knowledge.db', help='Path to SQLite database')
@click.pass_context
def cli(ctx, verbose, db_path):
    """LogLog Knowledge Graph CLI - Build and query knowledge graphs from LogLog documents."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Store common options in context
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--name', '-n', help='Name for the knowledge graph')
@click.option('--save/--no-save', default=True, help='Save to database')
@click.option('--export', '-e', type=click.Path(), help='Export to JSON file')
@click.option('--max-section-size', default=1000, help='Maximum section size for processing')
@click.option('--min-entity-confidence', default=0.6, help='Minimum confidence for entities')
@click.option('--min-relationship-confidence', default=0.5, help='Minimum confidence for relationships')
@click.pass_context
def build(ctx, file_path, name, save, export, max_section_size, min_entity_confidence, min_relationship_confidence):
    """Build a knowledge graph from a LogLog file."""
    console.print(f"[bold blue]Building knowledge graph from:[/bold blue] {file_path}")

    try:
        # Get API key
        api_key = get_claude_api_key()

        # Setup configuration
        config = BuilderConfig(
            max_section_size=max_section_size,
            min_entity_confidence=min_entity_confidence,
            min_relationship_confidence=min_relationship_confidence
        )

        # Initialize builder
        builder = KnowledgeGraphBuilder(api_key, config)

        # Build knowledge graph with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Building knowledge graph...", total=None)

            # Use asyncio for the async build method
            kg = asyncio.run(builder.build_from_file(file_path))

            progress.update(task, completed=True, description="Knowledge graph built successfully")

        # Display statistics
        stats = kg.get_statistics()
        stats_table = Table(title="Knowledge Graph Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="magenta")

        stats_table.add_row("Total Entities", str(stats['total_entities']))
        stats_table.add_row("Total Relationships", str(stats['total_relationships']))
        stats_table.add_row("Total Contexts", str(stats['total_contexts']))
        stats_table.add_row("Graph Density", f"{stats['graph_density']:.3f}")
        stats_table.add_row("Connected Components", str(stats['connected_components']))

        console.print(stats_table)

        # Save to database if requested
        if save:
            with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
                graph_name = name or f"KG-{os.path.basename(file_path)}"
                kg_id = persistence.save_knowledge_graph(kg, graph_name)
                console.print(f"[green]Knowledge graph saved with ID:[/green] {kg_id}")

        # Export to JSON if requested
        if export:
            kg.to_json(export)
            console.print(f"[green]Knowledge graph exported to:[/green] {export}")

        console.print("[bold green]Knowledge graph build completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[red]Error building knowledge graph: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--kg-id', help='Knowledge graph ID (if not provided, uses most recent)')
@click.option('--kg-file', type=click.Path(exists=True), help='Load knowledge graph from JSON file')
@click.option('--max-entities', default=20, help='Maximum entities to include in context')
@click.pass_context
def query(ctx, query, kg_id, kg_file, max_entities):
    """Query a knowledge graph with natural language."""
    console.print(f"[bold blue]Query:[/bold blue] {query}")

    try:
        # Load knowledge graph
        kg = None

        if kg_file:
            # Load from JSON file
            kg = KnowledgeGraph.from_json(kg_file)
            console.print(f"[dim]Loaded knowledge graph from file: {kg_file}[/dim]")
        else:
            # Load from database
            with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
                if kg_id:
                    kg = persistence.load_knowledge_graph(kg_id)
                else:
                    # Use most recent knowledge graph
                    graphs = persistence.list_knowledge_graphs()
                    if graphs:
                        kg_id = graphs[0]['id']
                        kg = persistence.load_knowledge_graph(kg_id)
                        console.print(f"[dim]Using most recent knowledge graph: {kg_id}[/dim]")

        if not kg:
            console.print("[red]No knowledge graph found. Build one first with 'loglog-kg build'[/red]")
            sys.exit(1)

        # Get API key and create query engine
        api_key = get_claude_api_key()
        query_engine = KnowledgeGraphQuery(kg, api_key)

        # Execute query with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing query...", total=None)

            result = asyncio.run(query_engine.query(query, max_entities))

            progress.update(task, completed=True, description="Query completed")

        # Display results
        console.print(Panel(
            result.answer,
            title="Answer",
            title_align="left",
            border_style="green"
        ))

        # Show confidence
        confidence_color = "green" if result.confidence > 0.7 else "yellow" if result.confidence > 0.4 else "red"
        console.print(f"[{confidence_color}]Confidence: {result.confidence:.2f}[/{confidence_color}]")

        # Show relevant entities if any
        if result.relevant_entities:
            entities_table = Table(title="Relevant Entities")
            entities_table.add_column("Name", style="cyan")
            entities_table.add_column("Type", style="magenta")
            entities_table.add_column("Description", style="dim")

            for entity in result.relevant_entities[:5]:  # Show top 5
                entities_table.add_row(
                    entity.name,
                    entity.entity_type.value,
                    entity.description[:50] + "..." if len(entity.description) > 50 else entity.description
                )

            console.print(entities_table)

    except Exception as e:
        console.print(f"[red]Error processing query: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--kg-id', help='Analyze specific knowledge graph')
@click.option('--document', help='Analyze specific document')
@click.pass_context
def analyze(ctx, kg_id, document):
    """Analyze knowledge graph or document."""
    try:
        # Load knowledge graph
        with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
            if kg_id:
                kg = persistence.load_knowledge_graph(kg_id)
            else:
                # Use most recent knowledge graph
                graphs = persistence.list_knowledge_graphs()
                if graphs:
                    kg_id = graphs[0]['id']
                    kg = persistence.load_knowledge_graph(kg_id)
                    console.print(f"[dim]Using most recent knowledge graph: {kg_id}[/dim]")

        if not kg:
            console.print("[red]No knowledge graph found[/red]")
            sys.exit(1)

        if document:
            # Analyze specific document
            api_key = get_claude_api_key()
            query_engine = KnowledgeGraphQuery(kg, api_key)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing document...", total=None)
                result = asyncio.run(query_engine.analyze_document(document))
                progress.update(task, completed=True, description="Analysis completed")

            # Display analysis results
            console.print(Panel(
                result.summary,
                title=f"Document Analysis: {document}",
                title_align="left",
                border_style="blue"
            ))

            if result.topics:
                console.print(f"[bold]Main Topics:[/bold] {', '.join(result.topics)}")

            if result.insights:
                console.print("\n[bold]Key Insights:[/bold]")
                for insight in result.insights:
                    console.print(f"• {insight}")

        else:
            # Analyze entire knowledge graph
            stats = kg.get_statistics()

            # Display comprehensive statistics
            stats_table = Table(title="Knowledge Graph Analysis")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="magenta")

            stats_table.add_row("Total Entities", str(stats['total_entities']))
            stats_table.add_row("Total Relationships", str(stats['total_relationships']))
            stats_table.add_row("Total Contexts", str(stats['total_contexts']))
            stats_table.add_row("Graph Density", f"{stats['graph_density']:.3f}")
            stats_table.add_row("Connected Components", str(stats['connected_components']))

            console.print(stats_table)

            # Show entity types distribution
            if stats['entity_types']:
                entity_types_table = Table(title="Entity Types Distribution")
                entity_types_table.add_column("Type", style="cyan")
                entity_types_table.add_column("Count", style="magenta")

                for entity_type, count in stats['entity_types'].items():
                    entity_types_table.add_row(entity_type.title(), str(count))

                console.print(entity_types_table)

            # Show relationship types distribution
            if stats['relationship_types']:
                rel_types_table = Table(title="Relationship Types Distribution")
                rel_types_table.add_column("Type", style="cyan")
                rel_types_table.add_column("Count", style="magenta")

                for rel_type, count in stats['relationship_types'].items():
                    rel_types_table.add_row(rel_type.title(), str(count))

                console.print(rel_types_table)

    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def list(ctx):
    """List all knowledge graphs in the database."""
    try:
        with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
            graphs = persistence.list_knowledge_graphs()

        if not graphs:
            console.print("[yellow]No knowledge graphs found in database[/yellow]")
            return

        table = Table(title="Knowledge Graphs")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Entities", justify="right")
        table.add_column("Relationships", justify="right")
        table.add_column("Updated", style="dim")

        for graph in graphs:
            table.add_row(
                graph['id'],
                graph['name'],
                str(graph['total_entities']),
                str(graph['total_relationships']),
                graph['updated_at'][:16]  # Show date and time without seconds
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing knowledge graphs: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('kg_id')
@click.argument('output_file', type=click.Path())
@click.option('--format', 'output_format', default='json', type=click.Choice(['json']),
              help='Output format')
@click.pass_context
def export(ctx, kg_id, output_file, output_format):
    """Export a knowledge graph to file."""
    try:
        with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
            kg = persistence.load_knowledge_graph(kg_id)

        if not kg:
            console.print(f"[red]Knowledge graph not found: {kg_id}[/red]")
            sys.exit(1)

        if output_format == 'json':
            kg.to_json(output_file)

        console.print(f"[green]Knowledge graph exported to: {output_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error exporting knowledge graph: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('kg_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, kg_id, confirm):
    """Delete a knowledge graph from the database."""
    if not confirm:
        if not click.confirm(f'Are you sure you want to delete knowledge graph {kg_id}?'):
            return

    try:
        with KnowledgeGraphPersistence(ctx.obj['db_path']) as persistence:
            success = persistence.delete_knowledge_graph(kg_id)

        if success:
            console.print(f"[green]Knowledge graph deleted: {kg_id}[/green]")
        else:
            console.print(f"[red]Failed to delete knowledge graph: {kg_id}[/red]")

    except Exception as e:
        console.print(f"[red]Error deleting knowledge graph: {e}[/red]")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()