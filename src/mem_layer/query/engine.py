"""Query engine for executing queries against the graph."""

import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.graph import GraphManager
from mem_layer.core.node import Node, NodeType
from mem_layer.exceptions import QueryException


class QueryType(str, Enum):
    """Types of queries."""

    PATTERN = "pattern"  # Pattern matching on graph
    FULL_TEXT = "full_text"  # Text search on content
    TRAVERSAL = "traversal"  # Graph traversal
    TEMPORAL = "temporal"  # Time-based queries
    HYBRID = "hybrid"  # Combination


class Query(BaseModel):
    """A query specification."""

    type: QueryType = QueryType.PATTERN
    pattern: str | None = None
    text: str | None = None
    start_nodes: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    scope: str | None = None
    temporal: datetime | None = None
    limit: int = 100
    offset: int = 0


class QueryResult(BaseModel):
    """Query result."""

    nodes: list[Node] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)
    total_count: int = 0
    query_time_ms: float = 0.0

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class QueryEngine:
    """Executes queries against the graph."""

    def __init__(self, graph_manager: GraphManager) -> None:
        """Initialize query engine.

        Args:
            graph_manager: Graph manager instance
        """
        self.graph_manager = graph_manager

    def execute(self, query: Query) -> QueryResult:
        """Execute a query.

        Args:
            query: Query specification

        Returns:
            Query results
        """
        start_time = datetime.utcnow()

        try:
            if query.type == QueryType.PATTERN:
                nodes = self.pattern_match(query.pattern or "", query.filters)
            elif query.type == QueryType.FULL_TEXT:
                nodes = self.full_text_search(query.text or "", query.filters)
            elif query.type == QueryType.TRAVERSAL:
                nodes = self.traverse(
                    query.start_nodes, query.filters.get("max_depth", 3), query.filters
                )
            elif query.type == QueryType.TEMPORAL:
                nodes = self.temporal_query(query.temporal, query.filters)
            else:
                nodes = self.pattern_match("*", query.filters)

            # Apply scope filter
            if query.scope:
                nodes = [n for n in nodes if n.scope == query.scope]

            # Apply pagination
            total_count = len(nodes)
            nodes = nodes[query.offset : query.offset + query.limit]

            # Get relevant edges
            node_ids = {n.id for n in nodes}
            edges = [
                e
                for e in self.graph_manager.edges.values()
                if e.source_id in node_ids and e.target_id in node_ids
            ]

            # Calculate query time
            end_time = datetime.utcnow()
            query_time_ms = (end_time - start_time).total_seconds() * 1000

            return QueryResult(
                nodes=nodes,
                edges=edges,
                total_count=total_count,
                query_time_ms=query_time_ms,
            )

        except Exception as e:
            raise QueryException(f"Query execution failed: {e}") from e

    def pattern_match(self, pattern: str, filters: dict[str, Any]) -> list[Node]:
        """Match nodes by pattern.

        Pattern syntax:
        - type:entity - Match by type
        - importance:>0.8 - Match by importance
        - tags:auth - Match by tag
        - * - Match all

        Args:
            pattern: Pattern string
            filters: Additional filters

        Returns:
            List of matching nodes
        """
        nodes = list(self.graph_manager.nodes.values())

        # Parse pattern
        if pattern and pattern != "*":
            conditions = pattern.split(" AND ")
            for condition in conditions:
                condition = condition.strip()
                if ":" in condition:
                    key, value = condition.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "type":
                        try:
                            node_type = NodeType(value)
                            nodes = [n for n in nodes if n.type == node_type]
                        except ValueError:
                            pass

                    elif key == "importance":
                        # Handle comparisons
                        if value.startswith(">"):
                            threshold = float(value[1:])
                            nodes = [n for n in nodes if n.importance > threshold]
                        elif value.startswith("<"):
                            threshold = float(value[1:])
                            nodes = [n for n in nodes if n.importance < threshold]
                        elif value.startswith(">="):
                            threshold = float(value[2:])
                            nodes = [n for n in nodes if n.importance >= threshold]
                        elif value.startswith("<="):
                            threshold = float(value[2:])
                            nodes = [n for n in nodes if n.importance <= threshold]
                        else:
                            threshold = float(value)
                            nodes = [n for n in nodes if abs(n.importance - threshold) < 0.01]

                    elif key == "tags":
                        nodes = [n for n in nodes if value in n.tags]

                    elif key == "scope":
                        nodes = [n for n in nodes if n.scope == value]

                    elif key.startswith("metadata."):
                        meta_key = key[9:]  # Remove "metadata."
                        nodes = [
                            n
                            for n in nodes
                            if meta_key in n.metadata and str(n.metadata[meta_key]) == value
                        ]

        # Apply additional filters
        if "node_type" in filters:
            node_type = filters["node_type"]
            if isinstance(node_type, str):
                node_type = NodeType(node_type)
            nodes = [n for n in nodes if n.type == node_type]

        if "min_importance" in filters:
            min_imp = filters["min_importance"]
            nodes = [n for n in nodes if n.importance >= min_imp]

        if "tags" in filters:
            required_tags = filters["tags"]
            if isinstance(required_tags, str):
                required_tags = [required_tags]
            nodes = [n for n in nodes if any(tag in n.tags for tag in required_tags)]

        return nodes

    def full_text_search(self, text: str, filters: dict[str, Any]) -> list[Node]:
        """Search node content using full-text search.

        Args:
            text: Search text
            filters: Additional filters

        Returns:
            List of matching nodes
        """
        nodes = list(self.graph_manager.nodes.values())

        # Simple case-insensitive search
        text_lower = text.lower()
        matching_nodes = []

        for node in nodes:
            content_lower = node.content.lower()
            tags_lower = " ".join(node.tags).lower()

            if text_lower in content_lower or text_lower in tags_lower:
                matching_nodes.append(node)

        # Apply additional filters
        if "node_type" in filters:
            node_type = filters["node_type"]
            if isinstance(node_type, str):
                node_type = NodeType(node_type)
            matching_nodes = [n for n in matching_nodes if n.type == node_type]

        # Sort by relevance (simple: prefer matches in content over tags)
        def relevance_score(node: Node) -> float:
            score = 0.0
            if text_lower in node.content.lower():
                score += 1.0
            if text_lower in " ".join(node.tags).lower():
                score += 0.5
            # Boost by importance
            score += node.importance * 0.2
            return score

        matching_nodes.sort(key=relevance_score, reverse=True)

        return matching_nodes

    def traverse(
        self, start_node_ids: list[str], max_depth: int, filters: dict[str, Any]
    ) -> list[Node]:
        """Traverse graph from starting nodes.

        Args:
            start_node_ids: Starting node IDs
            max_depth: Maximum traversal depth
            filters: Additional filters

        Returns:
            List of reached nodes
        """
        if not start_node_ids:
            return []

        visited = set()
        result = []

        for start_id in start_node_ids:
            if start_id not in self.graph_manager.nodes:
                continue

            # Get start node
            start_node = self.graph_manager.nodes[start_id]
            visited.add(start_id)
            result.append(start_node)

            # Get neighbors
            neighbors = self.graph_manager.get_neighbors(
                start_id, depth=max_depth, direction=filters.get("direction", "both")
            )

            for neighbor in neighbors:
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    result.append(neighbor)

        return result

    def temporal_query(self, timestamp: datetime | None, filters: dict[str, Any]) -> list[Node]:
        """Query graph state at specific time.

        Args:
            timestamp: Query timestamp
            filters: Additional filters

        Returns:
            List of nodes valid at timestamp
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        nodes = list(self.graph_manager.nodes.values())

        # Filter by temporal validity
        valid_nodes = [n for n in nodes if n.is_valid_at(timestamp)]

        # Apply additional filters
        if "node_type" in filters:
            node_type = filters["node_type"]
            if isinstance(node_type, str):
                node_type = NodeType(node_type)
            valid_nodes = [n for n in valid_nodes if n.type == node_type]

        return valid_nodes
