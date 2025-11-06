"""Main Memory API for interacting with the memory system."""

from datetime import datetime
from pathlib import Path
from typing import Any

from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.graph import GraphManager
from mem_layer.core.node import Node, NodeType
from mem_layer.persistence.sqlite import SQLiteAdapter
from mem_layer.persistence.serializer import GraphSerializer
from mem_layer.query.engine import Query, QueryEngine, QueryResult, QueryType
from mem_layer.scope.manager import ScopeManager
from mem_layer.scope.resolver import ScopeResolver
from mem_layer.scope.types import Scope, ScopeType
from mem_layer.utils.config import Config
from mem_layer.utils.logger import setup_logger


class MemoryAPI:
    """Main API facade for all memory operations."""

    def __init__(
        self,
        scope: str | None = None,
        config: Config | None = None,
        base_path: Path | None = None,
    ) -> None:
        """Initialize Memory API.

        Args:
            scope: Scope name or ID to use. If None, tries to discover project scope
            config: Configuration object. If None, loads from files
            base_path: Base path for scopes. If None, uses ~/.mem-layer
        """
        self.config = config or Config.load()
        self.logger = setup_logger("mem_layer")

        # Initialize scope manager
        self.scope_manager = ScopeManager(base_path)

        # Initialize scope resolver
        self.scope_resolver = ScopeResolver(self.scope_manager)

        # Set or discover active scope
        if scope:
            # Try to find scope by name or ID
            scope_obj = self.scope_manager.get_scope_by_name(scope)
            if not scope_obj:
                # Try as ID
                try:
                    scope_obj = self.scope_manager.get_scope(scope)
                except Exception:
                    # Create new project scope
                    scope_obj = self.scope_manager.create_scope(
                        name=scope, scope_type=ScopeType.PROJECT
                    )
            self.scope_manager.set_active_scope(scope_obj.id)
        else:
            # Try to discover project scope
            discovered = self.scope_manager.discover_project_scope()
            if discovered:
                self.scope_manager.set_active_scope(discovered.id)

        # Initialize graph manager
        self.graph_manager = GraphManager()

        # Initialize query engine
        self.query_engine = QueryEngine(self.graph_manager)

        # Load graph if scope is set
        if self.scope_manager.get_active_scope():
            self._load_graph()

    def _get_db_adapter(self) -> SQLiteAdapter:
        """Get SQLite adapter for current scope."""
        active_scope = self.scope_manager.get_active_scope()
        if not active_scope:
            raise ValueError("No active scope set")

        db_path = active_scope.get_db_path()
        return SQLiteAdapter(db_path)

    def _load_graph(self) -> None:
        """Load graph from database."""
        try:
            active_scope = self.scope_manager.get_active_scope()
            if not active_scope:
                return

            adapter = self._get_db_adapter()
            self.graph_manager = adapter.load_graph(active_scope.id)
            self.query_engine = QueryEngine(self.graph_manager)
            self.logger.info(f"Loaded graph for scope {active_scope.name}")

        except Exception as e:
            self.logger.warning(f"Could not load graph: {e}")

    def _save_graph(self) -> None:
        """Save graph to database."""
        try:
            active_scope = self.scope_manager.get_active_scope()
            if not active_scope:
                return

            adapter = self._get_db_adapter()
            adapter.save_graph(self.graph_manager, active_scope.id)
            self.logger.debug(f"Saved graph for scope {active_scope.name}")

        except Exception as e:
            self.logger.error(f"Could not save graph: {e}")

    # Node operations

    def create_node(
        self,
        type: NodeType,
        content: str,
        scope: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        importance: float = 0.5,
        created_by: str = "system",
    ) -> Node:
        """Create a new node.

        Args:
            type: Node type
            content: Node content
            scope: Scope name. If None, uses active scope
            metadata: Optional metadata dictionary
            tags: Optional list of tags
            importance: Importance score (0.0 to 1.0)
            created_by: Creator identifier

        Returns:
            Created node
        """
        if scope is None:
            active_scope = self.scope_manager.get_active_scope()
            if not active_scope:
                raise ValueError("No active scope and no scope specified")
            scope = active_scope.id

        node = Node(
            type=type,
            scope=scope,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            importance=importance,
            created_by=created_by,
        )

        self.graph_manager.add_node(node)

        # Save to database
        if self.config.storage.auto_save:
            adapter = self._get_db_adapter()
            adapter.save_node(node)

        return node

    def get_node(self, node_id: str) -> Node:
        """Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node object
        """
        return self.graph_manager.get_node(node_id)

    def update_node(self, node_id: str, **updates: Any) -> Node:
        """Update a node's attributes.

        Args:
            node_id: Node ID
            **updates: Fields to update

        Returns:
            Updated node
        """
        node = self.graph_manager.update_node(node_id, updates)

        # Save to database
        if self.config.storage.auto_save:
            adapter = self._get_db_adapter()
            adapter.save_node(node)

        return node

    def delete_node(self, node_id: str) -> bool:
        """Delete a node.

        Args:
            node_id: Node ID

        Returns:
            True if deleted
        """
        result = self.graph_manager.delete_node(node_id)

        # Delete from database
        if self.config.storage.auto_save:
            adapter = self._get_db_adapter()
            adapter.delete_node(node_id)

        return result

    # Edge operations

    def create_edge(
        self,
        source_id: str,
        target_id: str,
        type: EdgeType,
        weight: float = 1.0,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
        created_by: str = "system",
    ) -> Edge:
        """Create a new edge.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            type: Edge type
            weight: Edge weight (0.0 to 1.0)
            confidence: Confidence score (0.0 to 1.0)
            metadata: Optional metadata
            created_by: Creator identifier

        Returns:
            Created edge
        """
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            type=type,
            weight=weight,
            confidence=confidence,
            metadata=metadata or {},
            created_by=created_by,
        )

        self.graph_manager.add_edge(edge)

        # Save to database
        if self.config.storage.auto_save:
            adapter = self._get_db_adapter()
            adapter.save_edge(edge)

        return edge

    def get_edges(
        self, node_id: str, direction: str = "both", edge_type: EdgeType | None = None
    ) -> list[Edge]:
        """Get edges connected to a node.

        Args:
            node_id: Node ID
            direction: Direction ("in", "out", "both")
            edge_type: Optional edge type filter

        Returns:
            List of edges
        """
        return self.graph_manager.get_edges(node_id, direction, edge_type)

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge.

        Args:
            edge_id: Edge ID

        Returns:
            True if deleted
        """
        result = self.graph_manager.delete_edge(edge_id)

        # Delete from database
        if self.config.storage.auto_save:
            adapter = self._get_db_adapter()
            adapter.delete_edge(edge_id)

        return result

    # Query operations

    def query(
        self,
        pattern: str | None = None,
        scope: str | None = None,
        limit: int = 100,
        **filters: Any,
    ) -> QueryResult:
        """Query the graph with pattern matching.

        Args:
            pattern: Query pattern
            scope: Scope to query
            limit: Maximum results
            **filters: Additional filters

        Returns:
            Query results
        """
        query = Query(
            type=QueryType.PATTERN,
            pattern=pattern,
            scope=scope,
            limit=limit,
            filters=filters,
        )
        return self.query_engine.execute(query)

    def search(self, text: str, scope: str | None = None, limit: int = 100) -> QueryResult:
        """Full-text search.

        Args:
            text: Search text
            scope: Scope to search
            limit: Maximum results

        Returns:
            Query results
        """
        query = Query(type=QueryType.FULL_TEXT, text=text, scope=scope, limit=limit)
        return self.query_engine.execute(query)

    def traverse(
        self, start_id: str, max_depth: int = 3, direction: str = "both"
    ) -> QueryResult:
        """Traverse graph from starting node.

        Args:
            start_id: Starting node ID
            max_depth: Maximum depth
            direction: Traversal direction

        Returns:
            Query results
        """
        query = Query(
            type=QueryType.TRAVERSAL,
            start_nodes=[start_id],
            filters={"max_depth": max_depth, "direction": direction},
        )
        return self.query_engine.execute(query)

    def query_at_time(self, timestamp: datetime, **filters: Any) -> QueryResult:
        """Query graph state at specific time.

        Args:
            timestamp: Query timestamp
            **filters: Additional filters

        Returns:
            Query results
        """
        query = Query(type=QueryType.TEMPORAL, temporal=timestamp, filters=filters)
        return self.query_engine.execute(query)

    # Convenience methods

    def add_note(
        self, content: str, tags: list[str] | None = None, priority: str = "normal"
    ) -> Node:
        """Add a note.

        Args:
            content: Note content
            tags: Optional tags
            priority: Priority ("low", "normal", "high")

        Returns:
            Created note node
        """
        importance_map = {"low": 0.3, "normal": 0.5, "high": 0.8}
        importance = importance_map.get(priority, 0.5)

        return self.create_node(
            type=NodeType.NOTE,
            content=content,
            tags=tags or [],
            importance=importance,
        )

    def add_entity(
        self, content: str, tags: list[str] | None = None, importance: float = 0.5
    ) -> Node:
        """Add an entity.

        Args:
            content: Entity description
            tags: Optional tags
            importance: Importance score

        Returns:
            Created entity node
        """
        return self.create_node(
            type=NodeType.ENTITY, content=content, tags=tags or [], importance=importance
        )

    def relate(self, source_id: str, target_id: str, relation_type: str = "relates_to") -> Edge:
        """Create a relationship between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Relation type

        Returns:
            Created edge
        """
        edge_type = EdgeType(relation_type)
        return self.create_edge(source_id, target_id, edge_type)

    # Graph operations

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics.

        Returns:
            Statistics dictionary
        """
        return self.graph_manager.get_stats()

    def export_graph(self, file_path: Path, format: str = "json") -> None:
        """Export graph to file.

        Args:
            file_path: Output file path
            format: Export format ("json", "graphml", "dot")
        """
        if format == "json":
            content = GraphSerializer.to_json(self.graph_manager)
        elif format == "graphml":
            content = GraphSerializer.to_graphml(self.graph_manager)
        elif format == "dot":
            content = GraphSerializer.to_dot(self.graph_manager)
        else:
            raise ValueError(f"Unsupported format: {format}")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

        self.logger.info(f"Exported graph to {file_path}")

    def import_graph(self, file_path: Path, format: str = "json") -> None:
        """Import graph from file.

        Args:
            file_path: Input file path
            format: Import format ("json")
        """
        if format != "json":
            raise ValueError(f"Unsupported import format: {format}")

        with open(file_path) as f:
            content = f.read()

        imported_graph = GraphSerializer.from_json(content)

        # Merge into current graph
        for node in imported_graph.nodes.values():
            if node.id not in self.graph_manager.nodes:
                self.graph_manager.add_node(node)

        for edge in imported_graph.edges.values():
            if edge.id not in self.graph_manager.edges:
                try:
                    self.graph_manager.add_edge(edge)
                except Exception:
                    pass

        # Save
        self._save_graph()
        self.logger.info(f"Imported graph from {file_path}")

    # Scope operations

    def create_scope(self, name: str, scope_type: str, path: Path | None = None) -> Scope:
        """Create a new scope.

        Args:
            name: Scope name
            scope_type: Scope type
            path: Optional custom path

        Returns:
            Created scope
        """
        stype = ScopeType(scope_type)
        return self.scope_manager.create_scope(name, stype, path)

    def list_scopes(self) -> list[Scope]:
        """List all scopes.

        Returns:
            List of scopes
        """
        return self.scope_manager.list_scopes()

    def switch_scope(self, scope_name: str) -> None:
        """Switch to a different scope.

        Args:
            scope_name: Scope name to switch to
        """
        scope = self.scope_manager.get_scope_by_name(scope_name)
        if not scope:
            raise ValueError(f"Scope not found: {scope_name}")

        self.scope_manager.set_active_scope(scope.id)
        self._load_graph()

    def get_active_scope(self) -> Scope | None:
        """Get the active scope.

        Returns:
            Active scope or None
        """
        return self.scope_manager.get_active_scope()

    # Persistence

    def save(self) -> None:
        """Save current graph to database."""
        self._save_graph()

    def reload(self) -> None:
        """Reload graph from database."""
        self._load_graph()
