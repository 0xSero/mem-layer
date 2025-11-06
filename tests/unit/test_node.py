"""Tests for node operations."""

from datetime import datetime

from mem_layer.core.node import Node, NodeType


def test_node_creation():
    """Test creating a node."""
    node = Node(
        type=NodeType.ENTITY,
        scope="test",
        content="Test entity",
        tags=["test"],
    )

    assert node.id is not None
    assert node.type == NodeType.ENTITY
    assert node.scope == "test"
    assert node.content == "Test entity"
    assert "test" in node.tags
    assert node.importance == 0.5
    assert node.access_count == 0


def test_node_access_tracking():
    """Test node access tracking."""
    node = Node(type=NodeType.NOTE, scope="test", content="Test note")

    initial_count = node.access_count
    initial_time = node.last_accessed

    node.increment_access()

    assert node.access_count == initial_count + 1
    assert node.last_accessed > initial_time


def test_node_temporal_validity():
    """Test temporal validity checking."""
    now = datetime.utcnow()
    node = Node(
        type=NodeType.ENTITY,
        scope="test",
        content="Test",
        valid_from=now,
    )

    assert node.is_valid_at(now)

    # Test past validity
    from datetime import timedelta

    past = now - timedelta(days=1)
    assert not node.is_valid_at(past)


def test_node_tags():
    """Test tag operations."""
    node = Node(type=NodeType.NOTE, scope="test", content="Test")

    node.add_tag("important")
    assert "important" in node.tags

    node.add_tag("review")
    assert "review" in node.tags
    assert len(node.tags) == 2

    node.remove_tag("important")
    assert "important" not in node.tags
    assert len(node.tags) == 1


def test_node_serialization():
    """Test node to/from dict."""
    original = Node(
        type=NodeType.ENTITY,
        scope="test",
        content="Test entity",
        tags=["tag1", "tag2"],
        importance=0.8,
    )

    # Convert to dict
    data = original.to_dict()
    assert data["type"] == "entity"
    assert data["content"] == "Test entity"
    assert data["importance"] == 0.8

    # Recreate from dict
    restored = Node.from_dict(data)
    assert restored.id == original.id
    assert restored.type == original.type
    assert restored.content == original.content
    assert restored.importance == original.importance
