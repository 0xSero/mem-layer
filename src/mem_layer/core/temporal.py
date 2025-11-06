"""Temporal tracking for nodes and edges."""

from datetime import datetime
from typing import Any

from mem_layer.core.node import Node
from mem_layer.core.edge import Edge


class TemporalSnapshot(dict[str, Any]):
    """A snapshot of an element at a specific time."""

    def __init__(
        self,
        element_id: str,
        timestamp: datetime,
        element_type: str,
        data: dict[str, Any],
    ) -> None:
        super().__init__(
            element_id=element_id,
            timestamp=timestamp,
            element_type=element_type,
            data=data,
        )


class TemporalTracker:
    """Tracks temporal validity of nodes and edges."""

    def __init__(self) -> None:
        self.history: dict[str, list[TemporalSnapshot]] = {}

    def track_node(self, node: Node) -> None:
        """Record a node's state."""
        snapshot = TemporalSnapshot(
            element_id=node.id,
            timestamp=datetime.utcnow(),
            element_type="node",
            data=node.to_dict(),
        )

        if node.id not in self.history:
            self.history[node.id] = []

        self.history[node.id].append(snapshot)

    def track_edge(self, edge: Edge) -> None:
        """Record an edge's state."""
        snapshot = TemporalSnapshot(
            element_id=edge.id,
            timestamp=datetime.utcnow(),
            element_type="edge",
            data=edge.to_dict(),
        )

        if edge.id not in self.history:
            self.history[edge.id] = []

        self.history[edge.id].append(snapshot)

    def get_history(self, element_id: str) -> list[TemporalSnapshot]:
        """Get complete history of an element."""
        return self.history.get(element_id, [])

    def get_at_time(self, element_id: str, timestamp: datetime) -> TemporalSnapshot | None:
        """Get element state at specific time."""
        snapshots = self.history.get(element_id, [])
        if not snapshots:
            return None

        # Find the most recent snapshot before or at the given timestamp
        valid_snapshots = [s for s in snapshots if s["timestamp"] <= timestamp]
        if not valid_snapshots:
            return None

        return max(valid_snapshots, key=lambda s: s["timestamp"])

    def is_valid_at(self, element: Node | Edge, timestamp: datetime) -> bool:
        """Check if element was valid at given time."""
        return element.is_valid_at(timestamp)

    def update_validity(self, element_id: str, valid_until: datetime) -> None:
        """Mark element as no longer valid after timestamp."""
        # This would be implemented when we update the actual element
        pass

    def clear_history(self, element_id: str | None = None) -> None:
        """Clear history for specific element or all elements."""
        if element_id:
            self.history.pop(element_id, None)
        else:
            self.history.clear()
