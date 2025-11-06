"""Tests for graph manager."""

import pytest

from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.graph import GraphManager
from mem_layer.core.node import Node, NodeType
from mem_layer.exceptions import EdgeNotFoundException, NodeNotFoundException


def test_add_node(graph_manager):
    """Test adding a node to the graph."""
    node = Node(type=NodeType.ENTITY, scope="test", content="Test node")

    node_id = graph_manager.add_node(node)

    assert node_id == node.id
    assert node_id in graph_manager.nodes
    assert node_id in graph_manager.graph


def test_get_node(graph_manager):
    """Test retrieving a node."""
    node = Node(type=NodeType.ENTITY, scope="test", content="Test node")
    graph_manager.add_node(node)

    retrieved = graph_manager.get_node(node.id)

    assert retrieved.id == node.id
    assert retrieved.content == node.content


def test_get_nonexistent_node(graph_manager):
    """Test getting a node that doesn't exist."""
    with pytest.raises(NodeNotFoundException):
        graph_manager.get_node("nonexistent-id")


def test_add_edge(graph_manager):
    """Test adding an edge."""
    node1 = Node(type=NodeType.ENTITY, scope="test", content="Node 1")
    node2 = Node(type=NodeType.ENTITY, scope="test", content="Node 2")

    graph_manager.add_node(node1)
    graph_manager.add_node(node2)

    edge = Edge(
        source_id=node1.id,
        target_id=node2.id,
        type=EdgeType.RELATES_TO,
    )

    edge_id = graph_manager.add_edge(edge)

    assert edge_id == edge.id
    assert edge_id in graph_manager.edges


def test_get_edges(graph_manager):
    """Test getting edges for a node."""
    node1 = Node(type=NodeType.ENTITY, scope="test", content="Node 1")
    node2 = Node(type=NodeType.ENTITY, scope="test", content="Node 2")
    node3 = Node(type=NodeType.ENTITY, scope="test", content="Node 3")

    graph_manager.add_node(node1)
    graph_manager.add_node(node2)
    graph_manager.add_node(node3)

    edge1 = Edge(source_id=node1.id, target_id=node2.id, type=EdgeType.RELATES_TO)
    edge2 = Edge(source_id=node1.id, target_id=node3.id, type=EdgeType.DEPENDS_ON)

    graph_manager.add_edge(edge1)
    graph_manager.add_edge(edge2)

    # Get outgoing edges
    out_edges = graph_manager.get_edges(node1.id, direction="out")
    assert len(out_edges) == 2

    # Get by type
    relates_edges = graph_manager.get_edges(node1.id, edge_type=EdgeType.RELATES_TO)
    assert len(relates_edges) == 1


def test_delete_node(graph_manager):
    """Test deleting a node."""
    node = Node(type=NodeType.ENTITY, scope="test", content="Test node")
    graph_manager.add_node(node)

    result = graph_manager.delete_node(node.id)

    assert result is True
    assert node.id not in graph_manager.nodes
    assert node.id not in graph_manager.graph


def test_find_path(graph_manager):
    """Test finding path between nodes."""
    node1 = Node(type=NodeType.ENTITY, scope="test", content="Node 1")
    node2 = Node(type=NodeType.ENTITY, scope="test", content="Node 2")
    node3 = Node(type=NodeType.ENTITY, scope="test", content="Node 3")

    graph_manager.add_node(node1)
    graph_manager.add_node(node2)
    graph_manager.add_node(node3)

    edge1 = Edge(source_id=node1.id, target_id=node2.id, type=EdgeType.RELATES_TO)
    edge2 = Edge(source_id=node2.id, target_id=node3.id, type=EdgeType.RELATES_TO)

    graph_manager.add_edge(edge1)
    graph_manager.add_edge(edge2)

    path = graph_manager.find_path(node1.id, node3.id)

    assert len(path) == 3
    assert path[0] == node1.id
    assert path[1] == node2.id
    assert path[2] == node3.id


def test_get_neighbors(graph_manager):
    """Test getting neighbors."""
    node1 = Node(type=NodeType.ENTITY, scope="test", content="Node 1")
    node2 = Node(type=NodeType.ENTITY, scope="test", content="Node 2")
    node3 = Node(type=NodeType.ENTITY, scope="test", content="Node 3")

    graph_manager.add_node(node1)
    graph_manager.add_node(node2)
    graph_manager.add_node(node3)

    edge1 = Edge(source_id=node1.id, target_id=node2.id, type=EdgeType.RELATES_TO)
    edge2 = Edge(source_id=node2.id, target_id=node3.id, type=EdgeType.RELATES_TO)

    graph_manager.add_edge(edge1)
    graph_manager.add_edge(edge2)

    # Get depth 1 neighbors
    neighbors1 = graph_manager.get_neighbors(node1.id, depth=1)
    assert len(neighbors1) == 1
    assert neighbors1[0].id == node2.id

    # Get depth 2 neighbors
    neighbors2 = graph_manager.get_neighbors(node1.id, depth=2)
    assert len(neighbors2) == 2


def test_graph_stats(graph_manager):
    """Test getting graph statistics."""
    node1 = Node(type=NodeType.ENTITY, scope="test", content="Node 1")
    node2 = Node(type=NodeType.NOTE, scope="test", content="Node 2")

    graph_manager.add_node(node1)
    graph_manager.add_node(node2)

    edge = Edge(source_id=node1.id, target_id=node2.id, type=EdgeType.RELATES_TO)
    graph_manager.add_edge(edge)

    stats = graph_manager.get_stats()

    assert stats["node_count"] == 2
    assert stats["edge_count"] == 1
    assert "entity" in stats["node_types"]
    assert "note" in stats["node_types"]
    assert "relates_to" in stats["edge_types"]
