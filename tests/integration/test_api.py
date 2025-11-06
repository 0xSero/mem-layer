"""Integration tests for Memory API."""

from mem_layer.core.edge import EdgeType
from mem_layer.core.node import NodeType


def test_create_and_retrieve_node(memory_api):
    """Test creating and retrieving a node."""
    node = memory_api.create_node(
        type=NodeType.ENTITY,
        content="Test entity",
        tags=["test"],
    )

    retrieved = memory_api.get_node(node.id)

    assert retrieved.id == node.id
    assert retrieved.content == "Test entity"
    assert "test" in retrieved.tags


def test_create_relationship(memory_api):
    """Test creating a relationship between nodes."""
    node1 = memory_api.add_entity("Entity 1")
    node2 = memory_api.add_entity("Entity 2")

    edge = memory_api.create_edge(
        source_id=node1.id,
        target_id=node2.id,
        type=EdgeType.RELATES_TO,
    )

    edges = memory_api.get_edges(node1.id)

    assert len(edges) == 1
    assert edges[0].id == edge.id


def test_query(memory_api):
    """Test querying nodes."""
    memory_api.add_entity("First entity", tags=["important"])
    memory_api.add_entity("Second entity", tags=["test"])
    memory_api.add_note("A note")

    # Query all
    result = memory_api.query("*")
    assert result.total_count == 3

    # Query by type
    result = memory_api.query("type:entity")
    assert result.total_count == 2

    # Query by tag
    result = memory_api.query("tags:important")
    assert result.total_count == 1


def test_search(memory_api):
    """Test full-text search."""
    memory_api.add_entity("Python programming language")
    memory_api.add_entity("Java programming language")
    memory_api.add_note("Learn Python")

    result = memory_api.search("Python")

    assert result.total_count >= 2


def test_traverse(memory_api):
    """Test graph traversal."""
    node1 = memory_api.add_entity("Node 1")
    node2 = memory_api.add_entity("Node 2")
    node3 = memory_api.add_entity("Node 3")

    memory_api.relate(node1.id, node2.id, "relates_to")
    memory_api.relate(node2.id, node3.id, "relates_to")

    result = memory_api.traverse(node1.id, max_depth=2)

    assert len(result.nodes) == 3


def test_export_import(memory_api, temp_dir):
    """Test exporting and importing graph."""
    # Create some data
    memory_api.add_entity("Test entity 1")
    memory_api.add_entity("Test entity 2")
    memory_api.add_note("Test note")

    # Export
    export_path = temp_dir / "export.json"
    memory_api.export_graph(export_path, format="json")

    assert export_path.exists()

    # Clear graph
    memory_api.graph_manager.clear()
    assert len(memory_api.graph_manager.nodes) == 0

    # Import
    memory_api.import_graph(export_path, format="json")

    assert len(memory_api.graph_manager.nodes) == 3
