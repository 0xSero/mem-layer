"""Main CLI application."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from mem_layer import __version__
from mem_layer.api import MemoryAPI
from mem_layer.core.edge import EdgeType
from mem_layer.core.node import NodeType
from mem_layer.scope.types import ScopeType

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Mem-Layer: Graph-based memory management for AI models."""
    ctx.ensure_object(dict)


# Initialization commands


@cli.command()
@click.option("--scope", type=click.Choice(["user", "project", "personal"]), default="project")
@click.option("--name", help="Scope name")
def init(scope: str, name: str | None) -> None:
    """Initialize a new scope."""
    try:
        api = MemoryAPI()

        if not name:
            if scope == "project":
                name = Path.cwd().name
            else:
                name = "default"

        created_scope = api.create_scope(name, scope)
        console.print(f"[green]✓[/green] Initialized {scope} scope: {name}")
        console.print(f"  Path: {created_scope.path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


# Node operations


@cli.group()
def add() -> None:
    """Add nodes to memory."""
    pass


@add.command()
@click.argument("content")
@click.option("--tags", help="Comma-separated tags")
@click.option("--importance", type=float, default=0.5, help="Importance (0.0 to 1.0)")
@click.option("--scope", help="Scope name")
def entity(content: str, tags: str | None, importance: float, scope: str | None) -> None:
    """Add an entity node."""
    try:
        api = MemoryAPI(scope=scope)
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        node = api.add_entity(content, tags=tag_list, importance=importance)

        console.print(f"[green]✓[/green] Created entity: {node.id[:8]}")
        console.print(f"  Content: {content}")
        if tag_list:
            console.print(f"  Tags: {', '.join(tag_list)}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@add.command()
@click.argument("content")
@click.option("--tags", help="Comma-separated tags")
@click.option("--priority", type=click.Choice(["low", "normal", "high"]), default="normal")
@click.option("--scope", help="Scope name")
def note(content: str, tags: str | None, priority: str, scope: str | None) -> None:
    """Add a note node."""
    try:
        api = MemoryAPI(scope=scope)
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        node = api.add_note(content, tags=tag_list, priority=priority)

        console.print(f"[green]✓[/green] Created note: {node.id[:8]}")
        console.print(f"  Content: {content}")
        console.print(f"  Priority: {priority}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("source_id")
@click.argument("target_id")
@click.option(
    "--type",
    "relation_type",
    type=click.Choice([t.value for t in EdgeType]),
    default="relates_to",
)
def relate(source_id: str, target_id: str, relation_type: str) -> None:
    """Create a relationship between two nodes."""
    try:
        api = MemoryAPI()
        edge = api.relate(source_id, target_id, relation_type)

        console.print(f"[green]✓[/green] Created relationship: {edge.id[:8]}")
        console.print(f"  {source_id[:8]} --[{relation_type}]--> {target_id[:8]}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


# Query operations


@cli.command()
@click.argument("pattern")
@click.option("--scope", help="Scope to query")
@click.option("--limit", type=int, default=20, help="Maximum results")
def query(pattern: str, scope: str | None, limit: int) -> None:
    """Query the graph with pattern matching."""
    try:
        api = MemoryAPI(scope=scope)
        result = api.query(pattern, limit=limit)

        if not result.nodes:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Query Results ({result.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="white")
        table.add_column("Importance", style="yellow")
        table.add_column("Tags", style="green")

        for node in result.nodes:
            table.add_row(
                node.id[:8],
                node.type.value,
                node.content[:60] + ("..." if len(node.content) > 60 else ""),
                f"{node.importance:.2f}",
                ", ".join(node.tags[:3]),
            )

        console.print(table)
        console.print(f"Query time: {result.query_time_ms:.2f}ms")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("text")
@click.option("--scope", help="Scope to search")
@click.option("--limit", type=int, default=20, help="Maximum results")
def search(text: str, scope: str | None, limit: int) -> None:
    """Full-text search."""
    try:
        api = MemoryAPI(scope=scope)
        result = api.search(text, limit=limit)

        if not result.nodes:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Search Results ({result.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="white")
        table.add_column("Importance", style="yellow")

        for node in result.nodes:
            table.add_row(
                node.id[:8],
                node.type.value,
                node.content[:70] + ("..." if len(node.content) > 70 else ""),
                f"{node.importance:.2f}",
            )

        console.print(table)
        console.print(f"Search time: {result.query_time_ms:.2f}ms")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.option("--type", "node_type", help="Filter by node type")
@click.option("--scope", help="Scope to list")
@click.option("--limit", type=int, default=20, help="Maximum results")
def list(node_type: str | None, scope: str | None, limit: int) -> None:
    """List nodes."""
    try:
        api = MemoryAPI(scope=scope)

        filters = {}
        if node_type:
            filters["node_type"] = node_type

        result = api.query("*", limit=limit, **filters)

        if not result.nodes:
            console.print("[yellow]No nodes found[/yellow]")
            return

        table = Table(title=f"Nodes ({result.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="white")
        table.add_column("Created", style="blue")
        table.add_column("Importance", style="yellow")

        for node in result.nodes:
            table.add_row(
                node.id[:8],
                node.type.value,
                node.content[:50] + ("..." if len(node.content) > 50 else ""),
                node.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{node.importance:.2f}",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("node_id")
def show(node_id: str) -> None:
    """Show detailed information about a node."""
    try:
        api = MemoryAPI()

        # Find node by partial ID
        all_nodes = api.query("*", limit=1000).nodes
        matching = [n for n in all_nodes if n.id.startswith(node_id)]

        if not matching:
            console.print(f"[red]Node not found:[/red] {node_id}")
            return

        node = matching[0]

        console.print(f"\n[bold]Node: {node.id}[/bold]")
        console.print(f"Type: {node.type.value}")
        console.print(f"Scope: {node.scope}")
        console.print(f"\nContent:")
        console.print(f"  {node.content}")
        console.print(f"\nMetadata:")
        console.print(f"  Importance: {node.importance:.2f}")
        console.print(f"  Access count: {node.access_count}")
        console.print(f"  Created: {node.created_at}")
        console.print(f"  Updated: {node.updated_at}")
        console.print(f"  Created by: {node.created_by}")

        if node.tags:
            console.print(f"\nTags: {', '.join(node.tags)}")

        if node.metadata:
            console.print(f"\nCustom metadata:")
            for key, value in node.metadata.items():
                console.print(f"  {key}: {value}")

        # Show edges
        edges = api.get_edges(node.id)
        if edges:
            console.print(f"\n[bold]Relationships:[/bold]")
            for edge in edges:
                direction = "→" if edge.source_id == node.id else "←"
                other_id = edge.target_id if edge.source_id == node.id else edge.source_id
                console.print(f"  {direction} {edge.type.value} {direction} {other_id[:8]}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("node_id")
@click.option("--depth", type=int, default=2, help="Traversal depth")
def traverse(node_id: str, depth: int) -> None:
    """Traverse graph from a node."""
    try:
        api = MemoryAPI()

        # Find node by partial ID
        all_nodes = api.query("*", limit=1000).nodes
        matching = [n for n in all_nodes if n.id.startswith(node_id)]

        if not matching:
            console.print(f"[red]Node not found:[/red] {node_id}")
            return

        start_node = matching[0]
        result = api.traverse(start_node.id, max_depth=depth)

        console.print(f"\n[bold]Traversal from {start_node.id[:8]}[/bold]")
        console.print(f"Found {len(result.nodes)} nodes, {len(result.edges)} edges")

        table = Table(title=f"Reachable Nodes (depth ≤ {depth})")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="white")

        for node in result.nodes[:20]:  # Show first 20
            table.add_row(
                node.id[:8], node.type.value, node.content[:60] + ("..." if len(node.content) > 60 else "")
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("node_id")
@click.confirmation_option(prompt="Are you sure you want to delete this node?")
def delete(node_id: str) -> None:
    """Delete a node."""
    try:
        api = MemoryAPI()

        # Find node by partial ID
        all_nodes = api.query("*", limit=1000).nodes
        matching = [n for n in all_nodes if n.id.startswith(node_id)]

        if not matching:
            console.print(f"[red]Node not found:[/red] {node_id}")
            return

        node = matching[0]
        api.delete_node(node.id)

        console.print(f"[green]✓[/green] Deleted node: {node.id[:8]}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


# Graph operations


@cli.group()
def graph() -> None:
    """Graph operations."""
    pass


@graph.command()
@click.option("--scope", help="Scope to show stats for")
def stats(scope: str | None) -> None:
    """Show graph statistics."""
    try:
        api = MemoryAPI(scope=scope)
        stats_data = api.get_stats()

        console.print("\n[bold]Graph Statistics[/bold]")
        console.print(f"Nodes: {stats_data['node_count']}")
        console.print(f"Edges: {stats_data['edge_count']}")
        console.print(f"Average degree: {stats_data['average_degree']:.2f}")
        console.print(f"Connected: {stats_data['is_connected']}")

        if stats_data["node_types"]:
            console.print("\n[bold]Node Types:[/bold]")
            for ntype, count in stats_data["node_types"].items():
                console.print(f"  {ntype}: {count}")

        if stats_data["edge_types"]:
            console.print("\n[bold]Edge Types:[/bold]")
            for etype, count in stats_data["edge_types"].items():
                console.print(f"  {etype}: {count}")

        if stats_data["most_connected"]:
            console.print("\n[bold]Most Connected Nodes:[/bold]")
            for item in stats_data["most_connected"]:
                console.print(
                    f"  {item['node_id'][:8]}: {item['degree']} connections - {item['content']}"
                )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@graph.command()
@click.argument("output", type=click.Path())
@click.option("--format", type=click.Choice(["json", "graphml", "dot"]), default="json")
def export(output: str, format: str) -> None:
    """Export graph to file."""
    try:
        api = MemoryAPI()
        output_path = Path(output)

        api.export_graph(output_path, format=format)

        console.print(f"[green]✓[/green] Exported graph to {output_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@graph.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["json"]), default="json")
def import_file(input: str, format: str) -> None:
    """Import graph from file."""
    try:
        api = MemoryAPI()
        input_path = Path(input)

        api.import_graph(input_path, format=format)

        console.print(f"[green]✓[/green] Imported graph from {input_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


# Scope operations


@cli.group()
def scope() -> None:
    """Scope management."""
    pass


@scope.command()
def list_scopes() -> None:
    """List all scopes."""
    try:
        api = MemoryAPI()
        scopes = api.list_scopes()

        if not scopes:
            console.print("[yellow]No scopes found[/yellow]")
            return

        table = Table(title="Scopes")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Path", style="white")
        table.add_column("Active", style="green")

        active = api.get_active_scope()

        for s in scopes:
            is_active = "✓" if active and s.id == active.id else ""
            table.add_row(s.name, s.type.value, str(s.path), is_active)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@scope.command()
@click.argument("name")
@click.argument("type", type=click.Choice(["user", "project", "code", "personal"]))
def create(name: str, type: str) -> None:
    """Create a new scope."""
    try:
        api = MemoryAPI()
        created = api.create_scope(name, type)

        console.print(f"[green]✓[/green] Created {type} scope: {name}")
        console.print(f"  Path: {created.path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@scope.command()
@click.argument("name")
def switch(name: str) -> None:
    """Switch to a different scope."""
    try:
        api = MemoryAPI()
        api.switch_scope(name)

        console.print(f"[green]✓[/green] Switched to scope: {name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@scope.command()
@click.argument("name", required=False)
def info(name: str | None) -> None:
    """Show scope information."""
    try:
        api = MemoryAPI()

        if name:
            scope_obj = api.scope_manager.get_scope_by_name(name)
        else:
            scope_obj = api.get_active_scope()

        if not scope_obj:
            console.print("[yellow]No scope found[/yellow]")
            return

        console.print(f"\n[bold]Scope: {scope_obj.name}[/bold]")
        console.print(f"ID: {scope_obj.id}")
        console.print(f"Type: {scope_obj.type.value}")
        console.print(f"Path: {scope_obj.path}")

        if scope_obj.parent:
            console.print(f"Parent: {scope_obj.parent}")

        console.print(f"\n[bold]Configuration:[/bold]")
        console.print(f"  Max nodes: {scope_obj.config.max_nodes}")
        console.print(f"  Max edges: {scope_obj.config.max_edges}")
        console.print(f"  Temporal tracking: {scope_obj.config.enable_temporal}")
        console.print(f"  Auto-save: {scope_obj.config.auto_save}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
