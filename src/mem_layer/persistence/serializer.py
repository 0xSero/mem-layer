"""Graph serialization to various formats."""

import json
from typing import Any

from mem_layer.core.graph import GraphManager
from mem_layer.core.node import Node
from mem_layer.core.edge import Edge


class GraphSerializer:
    """Serializes graph to various formats."""

    @staticmethod
    def to_json(graph: GraphManager) -> str:
        """Serialize graph to JSON.

        Args:
            graph: Graph manager to serialize

        Returns:
            JSON string
        """
        data = {
            "nodes": [node.to_dict() for node in graph.nodes.values()],
            "edges": [edge.to_dict() for edge in graph.edges.values()],
            "stats": graph.get_stats(),
        }
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def from_json(json_str: str) -> GraphManager:
        """Deserialize graph from JSON.

        Args:
            json_str: JSON string

        Returns:
            Graph manager
        """
        data = json.loads(json_str)
        graph = GraphManager()

        # Load nodes
        for node_data in data.get("nodes", []):
            node = Node.from_dict(node_data)
            graph.add_node(node, track_temporal=False)

        # Load edges
        for edge_data in data.get("edges", []):
            edge = Edge.from_dict(edge_data)
            try:
                graph.add_edge(edge, track_temporal=False)
            except Exception:
                # Skip edges with missing nodes
                pass

        return graph

    @staticmethod
    def to_graphml(graph: GraphManager) -> str:
        """Export to GraphML format for visualization tools.

        Args:
            graph: Graph manager to export

        Returns:
            GraphML XML string
        """
        import networkx as nx

        # Export the NetworkX graph
        graphml_str = "\n".join(nx.generate_graphml(graph.graph))
        return graphml_str

    @staticmethod
    def to_dot(graph: GraphManager, include_metadata: bool = False) -> str:
        """Export to DOT format for Graphviz.

        Args:
            graph: Graph manager to export
            include_metadata: Include detailed metadata in labels

        Returns:
            DOT format string
        """
        lines = ["digraph G {"]
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=rounded];')

        # Add nodes
        for node_id, node in graph.nodes.items():
            label = node.content[:50].replace('"', '\\"')
            if include_metadata:
                label += f"\\nType: {node.type.value}"
                label += f"\\nImportance: {node.importance:.2f}"

            lines.append(f'  "{node_id}" [label="{label}"];')

        # Add edges
        for edge in graph.edges.values():
            label = edge.type.value
            if include_metadata:
                label += f" ({edge.weight:.2f})"

            lines.append(
                f'  "{edge.source_id}" -> "{edge.target_id}" [label="{label}"];'
            )

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def to_dict(graph: GraphManager) -> dict[str, Any]:
        """Convert graph to dictionary.

        Args:
            graph: Graph manager to convert

        Returns:
            Dictionary representation
        """
        return {
            "nodes": {nid: node.to_dict() for nid, node in graph.nodes.items()},
            "edges": {eid: edge.to_dict() for eid, edge in graph.edges.items()},
            "stats": graph.get_stats(),
        }
