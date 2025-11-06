"""Graph manager using NetworkX."""

from datetime import datetime
from typing import Any

import networkx as nx

from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.node import Node, NodeType
from mem_layer.core.temporal import TemporalTracker
from mem_layer.exceptions import EdgeNotFoundException, NodeNotFoundException


class GraphManager:
    """Manages the NetworkX graph and provides graph operations."""

    def __init__(self) -> None:
        # Use MultiDiGraph to allow multiple edges between nodes
        self.graph = nx.MultiDiGraph()
        self.temporal_tracker = TemporalTracker()

        # In-memory stores for full node and edge objects
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}

    def add_node(self, node: Node, track_temporal: bool = True) -> str:
        """Add a node to the graph."""
        # Store the full node object
        self.nodes[node.id] = node

        # Add to NetworkX graph with basic attributes for querying
        self.graph.add_node(
            node.id,
            type=node.type.value,
            scope=node.scope,
            importance=node.importance,
            created_at=node.created_at,
        )

        # Track temporal state
        if track_temporal:
            self.temporal_tracker.track_node(node)

        return node.id

    def get_node(self, node_id: str) -> Node:
        """Retrieve a node by ID."""
        node = self.nodes.get(node_id)
        if not node:
            raise NodeNotFoundException(node_id)

        # Update access tracking
        node.increment_access()
        return node

    def update_node(self, node_id: str, updates: dict[str, Any]) -> Node:
        """Update a node's attributes."""
        node = self.get_node(node_id)

        # Update fields
        for key, value in updates.items():
            if hasattr(node, key):
                setattr(node, key, value)

        node.updated_at = datetime.utcnow()

        # Track temporal change
        self.temporal_tracker.track_node(node)

        return node

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its edges."""
        if node_id not in self.nodes:
            raise NodeNotFoundException(node_id)

        # Remove all connected edges
        edges_to_remove = []
        for edge_id, edge in self.edges.items():
            if edge.source_id == node_id or edge.target_id == node_id:
                edges_to_remove.append(edge_id)

        for edge_id in edges_to_remove:
            self.delete_edge(edge_id)

        # Remove from graph and store
        self.graph.remove_node(node_id)
        del self.nodes[node_id]

        return True

    def add_edge(self, edge: Edge, track_temporal: bool = True) -> str:
        """Add an edge to the graph."""
        # Verify nodes exist
        if edge.source_id not in self.nodes:
            raise NodeNotFoundException(edge.source_id)
        if edge.target_id not in self.nodes:
            raise NodeNotFoundException(edge.target_id)

        # Store the full edge object
        self.edges[edge.id] = edge

        # Add to NetworkX graph
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            key=edge.id,
            type=edge.type.value,
            weight=edge.weight,
            created_at=edge.created_at,
        )

        # Track temporal state
        if track_temporal:
            self.temporal_tracker.track_edge(edge)

        return edge.id

    def get_edge(self, edge_id: str) -> Edge:
        """Retrieve an edge by ID."""
        edge = self.edges.get(edge_id)
        if not edge:
            raise EdgeNotFoundException(edge_id)
        return edge

    def get_edges(
        self, node_id: str, direction: str = "both", edge_type: EdgeType | None = None
    ) -> list[Edge]:
        """Get edges connected to a node."""
        if node_id not in self.nodes:
            raise NodeNotFoundException(node_id)

        result = []

        for edge_id, edge in self.edges.items():
            # Check direction
            if direction == "out" and edge.source_id != node_id:
                continue
            if direction == "in" and edge.target_id != node_id:
                continue
            if direction == "both" and edge.source_id != node_id and edge.target_id != node_id:
                continue

            # Check edge type
            if edge_type and edge.type != edge_type:
                continue

            result.append(edge)

        return result

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge."""
        if edge_id not in self.edges:
            raise EdgeNotFoundException(edge_id)

        edge = self.edges[edge_id]

        # Remove from NetworkX graph
        if self.graph.has_edge(edge.source_id, edge.target_id, key=edge_id):
            self.graph.remove_edge(edge.source_id, edge.target_id, key=edge_id)

        # Remove from store
        del self.edges[edge_id]

        return True

    def find_path(self, source_id: str, target_id: str) -> list[str]:
        """Find shortest path between two nodes."""
        if source_id not in self.nodes:
            raise NodeNotFoundException(source_id)
        if target_id not in self.nodes:
            raise NodeNotFoundException(target_id)

        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return []

    def get_neighbors(
        self, node_id: str, depth: int = 1, direction: str = "both"
    ) -> list[Node]:
        """Get neighbors up to specified depth."""
        if node_id not in self.nodes:
            raise NodeNotFoundException(node_id)

        neighbors_ids = set()

        if direction in ("out", "both"):
            # Get successors (outgoing edges)
            for d in range(1, depth + 1):
                if d == 1:
                    neighbors_ids.update(self.graph.successors(node_id))
                else:
                    # Get neighbors at this depth
                    current_level = list(neighbors_ids)
                    for neighbor_id in current_level:
                        if neighbor_id in self.graph:
                            neighbors_ids.update(self.graph.successors(neighbor_id))

        if direction in ("in", "both"):
            # Get predecessors (incoming edges)
            for d in range(1, depth + 1):
                if d == 1:
                    neighbors_ids.update(self.graph.predecessors(node_id))
                else:
                    current_level = list(neighbors_ids)
                    for neighbor_id in current_level:
                        if neighbor_id in self.graph:
                            neighbors_ids.update(self.graph.predecessors(neighbor_id))

        # Remove the source node itself
        neighbors_ids.discard(node_id)

        # Return full node objects
        return [self.nodes[nid] for nid in neighbors_ids if nid in self.nodes]

    def get_subgraph(self, node_ids: list[str]) -> "GraphManager":
        """Extract a subgraph containing specified nodes."""
        subgraph_manager = GraphManager()

        # Add nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                subgraph_manager.add_node(node, track_temporal=False)

        # Add edges between the nodes
        for edge_id, edge in self.edges.items():
            if edge.source_id in node_ids and edge.target_id in node_ids:
                subgraph_manager.add_edge(edge, track_temporal=False)

        return subgraph_manager

    def get_all_nodes(
        self, node_type: NodeType | None = None, scope: str | None = None
    ) -> list[Node]:
        """Get all nodes, optionally filtered by type and scope."""
        result = []

        for node in self.nodes.values():
            if node_type and node.type != node_type:
                continue
            if scope and node.scope != scope:
                continue
            result.append(node)

        return result

    def get_all_edges(self, edge_type: EdgeType | None = None) -> list[Edge]:
        """Get all edges, optionally filtered by type."""
        result = []

        for edge in self.edges.values():
            if edge_type and edge.type != edge_type:
                continue
            result.append(edge)

        return result

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        node_types: dict[str, int] = {}
        for node in self.nodes.values():
            node_types[node.type.value] = node_types.get(node.type.value, 0) + 1

        edge_types: dict[str, int] = {}
        for edge in self.edges.values():
            edge_types[edge.type.value] = edge_types.get(edge.type.value, 0) + 1

        # Calculate degree statistics
        degrees = [self.graph.degree(node_id) for node_id in self.nodes]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        # Find most connected nodes
        most_connected = sorted(
            [(node_id, self.graph.degree(node_id)) for node_id in self.nodes],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "average_degree": avg_degree,
            "most_connected": [
                {"node_id": nid, "degree": deg, "content": self.nodes[nid].content[:50]}
                for nid, deg in most_connected
            ],
            "is_connected": nx.is_weakly_connected(self.graph) if len(self.nodes) > 0 else False,
        }

    def clear(self) -> None:
        """Clear all nodes and edges."""
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.temporal_tracker.clear_history()
