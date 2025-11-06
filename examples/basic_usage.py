"""Basic usage example for Mem-Layer."""

from mem_layer import MemoryAPI, NodeType, EdgeType

def main():
    """Demonstrate basic Mem-Layer operations."""
    print("=== Mem-Layer Basic Usage Example ===\n")

    # Initialize API with a test scope
    api = MemoryAPI(scope="example")
    print("✓ Initialized Memory API with 'example' scope\n")

    # Create some entities
    print("Creating entities...")
    user_auth = api.create_node(
        type=NodeType.ENTITY,
        content="User authentication system",
        tags=["auth", "security"],
        importance=0.9,
    )
    print(f"  Created: {user_auth.content} (ID: {user_auth.id[:8]})")

    database = api.create_node(
        type=NodeType.ENTITY,
        content="PostgreSQL database",
        tags=["database", "infrastructure"],
        importance=0.8,
    )
    print(f"  Created: {database.content} (ID: {database.id[:8]})")

    api_server = api.create_node(
        type=NodeType.ENTITY,
        content="FastAPI server",
        tags=["api", "backend"],
        importance=0.85,
    )
    print(f"  Created: {api_server.content} (ID: {api_server.id[:8]})\n")

    # Create relationships
    print("Creating relationships...")
    edge1 = api.create_edge(
        source_id=user_auth.id,
        target_id=database.id,
        type=EdgeType.DEPENDS_ON,
        weight=0.9,
    )
    print(f"  {user_auth.content} → DEPENDS_ON → {database.content}")

    edge2 = api.create_edge(
        source_id=api_server.id,
        target_id=user_auth.id,
        type=EdgeType.USES,
        weight=0.8,
    )
    print(f"  {api_server.content} → USES → {user_auth.content}\n")

    # Add some notes
    print("Adding notes...")
    note1 = api.add_note(
        "Need to implement rate limiting on auth endpoints",
        tags=["todo", "security"],
        priority="high",
    )
    print(f"  Note: {note1.content[:50]}...")

    note2 = api.add_note(
        "Consider adding Redis cache for session management",
        tags=["performance", "caching"],
        priority="normal",
    )
    print(f"  Note: {note2.content[:50]}...\n")

    # Query examples
    print("Querying...")

    # Query by type
    print("  All entities:")
    result = api.query("type:entity")
    for node in result.nodes:
        print(f"    - {node.content}")

    # Query by tag
    print("\n  Nodes tagged with 'security':")
    result = api.query("tags:security")
    for node in result.nodes:
        print(f"    - {node.content}")

    # Query by importance
    print("\n  High importance nodes (>0.8):")
    result = api.query("importance:>0.8")
    for node in result.nodes:
        print(f"    - {node.content} (importance: {node.importance})")

    # Full-text search
    print("\n  Search for 'database':")
    result = api.search("database")
    for node in result.nodes:
        print(f"    - {node.content}\n")

    # Traverse graph
    print("Graph traversal from user_auth:")
    result = api.traverse(user_auth.id, max_depth=2)
    print(f"  Found {len(result.nodes)} connected nodes")
    for node in result.nodes:
        if node.id != user_auth.id:
            print(f"    - {node.content}")
    print()

    # Show graph statistics
    print("Graph statistics:")
    stats = api.get_stats()
    print(f"  Nodes: {stats['node_count']}")
    print(f"  Edges: {stats['edge_count']}")
    print(f"  Node types: {stats['node_types']}")
    print(f"  Edge types: {stats['edge_types']}")
    print()

    # Export graph
    from pathlib import Path
    export_path = Path("example_graph.json")
    api.export_graph(export_path, format="json")
    print(f"✓ Exported graph to {export_path}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
