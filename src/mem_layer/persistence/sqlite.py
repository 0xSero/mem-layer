"""SQLite persistence adapter."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.graph import GraphManager
from mem_layer.core.node import Node, NodeType
from mem_layer.exceptions import PersistenceException


class SQLiteAdapter:
    """Handles persistence to SQLite database."""

    def __init__(self, db_path: Path) -> None:
        """Initialize SQLite adapter.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Use WAL mode for better concurrency
        self.conn = sqlite3.connect(
            str(db_path), check_same_thread=False, isolation_level=None
        )
        self.conn.execute("PRAGMA journal_mode=WAL")

        # Initialize schema
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Nodes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                scope TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                importance REAL NOT NULL,
                access_count INTEGER NOT NULL,
                last_accessed TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        """
        )

        # Edges table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                type TEXT NOT NULL,
                weight REAL NOT NULL,
                confidence REAL NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
            )
        """
        )

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_scope ON nodes(scope)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_importance ON nodes(importance)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type)")

        # Full-text search for node content
        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts
            USING fts5(id, content, tags)
        """
        )

        # Scopes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scopes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                config TEXT NOT NULL,
                parent TEXT,
                metadata TEXT NOT NULL
            )
        """
        )

        # Sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                scope_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                summary TEXT,
                operations_count INTEGER DEFAULT 0,
                FOREIGN KEY (scope_id) REFERENCES scopes(id) ON DELETE CASCADE
            )
        """
        )

        self.conn.commit()

    def save_node(self, node: Node) -> None:
        """Save a node to database.

        Args:
            node: Node to save
        """
        try:
            cursor = self.conn.cursor()

            # Serialize complex fields
            metadata_json = json.dumps(node.metadata)
            tags_json = json.dumps(node.tags)

            cursor.execute(
                """
                INSERT OR REPLACE INTO nodes
                (id, type, scope, content, metadata, created_at, updated_at, created_by,
                 valid_from, valid_until, importance, access_count, last_accessed, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    node.id,
                    node.type.value,
                    node.scope,
                    node.content,
                    metadata_json,
                    node.created_at.isoformat(),
                    node.updated_at.isoformat(),
                    node.created_by,
                    node.valid_from.isoformat() if node.valid_from else None,
                    node.valid_until.isoformat() if node.valid_until else None,
                    node.importance,
                    node.access_count,
                    node.last_accessed.isoformat(),
                    tags_json,
                ),
            )

            # Update FTS index
            cursor.execute(
                """
                INSERT OR REPLACE INTO nodes_fts (id, content, tags)
                VALUES (?, ?, ?)
            """,
                (node.id, node.content, " ".join(node.tags)),
            )

            self.conn.commit()

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to save node: {e}") from e

    def load_node(self, node_id: str) -> Node | None:
        """Load a node from database.

        Args:
            node_id: Node ID to load

        Returns:
            Node object or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_node(row)

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to load node: {e}") from e

    def save_edge(self, edge: Edge) -> None:
        """Save an edge to database.

        Args:
            edge: Edge to save
        """
        try:
            cursor = self.conn.cursor()

            metadata_json = json.dumps(edge.metadata)

            cursor.execute(
                """
                INSERT OR REPLACE INTO edges
                (id, source_id, target_id, type, weight, confidence, metadata,
                 created_at, created_by, valid_from, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    edge.id,
                    edge.source_id,
                    edge.target_id,
                    edge.type.value,
                    edge.weight,
                    edge.confidence,
                    metadata_json,
                    edge.created_at.isoformat(),
                    edge.created_by,
                    edge.valid_from.isoformat() if edge.valid_from else None,
                    edge.valid_until.isoformat() if edge.valid_until else None,
                ),
            )

            self.conn.commit()

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to save edge: {e}") from e

    def load_edge(self, edge_id: str) -> Edge | None:
        """Load an edge from database.

        Args:
            edge_id: Edge ID to load

        Returns:
            Edge object or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM edges WHERE id = ?", (edge_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_edge(row)

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to load edge: {e}") from e

    def save_graph(self, graph: GraphManager, scope: str) -> None:
        """Save entire graph incrementally.

        Args:
            graph: Graph manager to save
            scope: Scope ID
        """
        try:
            # Save all nodes
            for node in graph.nodes.values():
                if node.scope == scope:
                    self.save_node(node)

            # Save all edges
            for edge in graph.edges.values():
                # Only save edges where both nodes are in this scope
                if (
                    edge.source_id in graph.nodes
                    and edge.target_id in graph.nodes
                    and graph.nodes[edge.source_id].scope == scope
                    and graph.nodes[edge.target_id].scope == scope
                ):
                    self.save_edge(edge)

        except Exception as e:
            raise PersistenceException(f"Failed to save graph: {e}") from e

    def load_graph(self, scope: str) -> GraphManager:
        """Load graph from database.

        Args:
            scope: Scope ID to load

        Returns:
            Loaded graph manager
        """
        try:
            graph = GraphManager()
            cursor = self.conn.cursor()

            # Load nodes for this scope
            cursor.execute("SELECT * FROM nodes WHERE scope = ?", (scope,))
            for row in cursor.fetchall():
                node = self._row_to_node(row)
                graph.add_node(node, track_temporal=False)

            # Load edges
            # Get all edges where both source and target are in this scope
            cursor.execute(
                """
                SELECT e.* FROM edges e
                JOIN nodes n1 ON e.source_id = n1.id
                JOIN nodes n2 ON e.target_id = n2.id
                WHERE n1.scope = ? AND n2.scope = ?
            """,
                (scope, scope),
            )
            for row in cursor.fetchall():
                edge = self._row_to_edge(row)
                if edge.source_id in graph.nodes and edge.target_id in graph.nodes:
                    graph.add_edge(edge, track_temporal=False)

            return graph

        except Exception as e:
            raise PersistenceException(f"Failed to load graph: {e}") from e

    def delete_node(self, node_id: str) -> bool:
        """Delete a node from database.

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            cursor.execute("DELETE FROM nodes_fts WHERE id = ?", (node_id,))
            self.conn.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to delete node: {e}") from e

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from database.

        Args:
            edge_id: Edge ID to delete

        Returns:
            True if deleted
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
            self.conn.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to delete edge: {e}") from e

    def search_nodes(self, query: str, scope: str | None = None, limit: int = 100) -> list[Node]:
        """Search nodes using full-text search.

        Args:
            query: Search query
            scope: Optional scope filter
            limit: Maximum results

        Returns:
            List of matching nodes
        """
        try:
            cursor = self.conn.cursor()

            if scope:
                cursor.execute(
                    """
                    SELECT n.* FROM nodes n
                    JOIN nodes_fts fts ON n.id = fts.id
                    WHERE fts.content MATCH ? AND n.scope = ?
                    LIMIT ?
                """,
                    (query, scope, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT n.* FROM nodes n
                    JOIN nodes_fts fts ON n.id = fts.id
                    WHERE fts.content MATCH ?
                    LIMIT ?
                """,
                    (query, limit),
                )

            return [self._row_to_node(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            raise PersistenceException(f"Failed to search nodes: {e}") from e

    def _row_to_node(self, row: tuple[Any, ...]) -> Node:
        """Convert database row to Node object."""
        return Node(
            id=row[0],
            type=NodeType(row[1]),
            scope=row[2],
            content=row[3],
            metadata=json.loads(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6]),
            created_by=row[7],
            valid_from=datetime.fromisoformat(row[8]) if row[8] else None,
            valid_until=datetime.fromisoformat(row[9]) if row[9] else None,
            importance=row[10],
            access_count=row[11],
            last_accessed=datetime.fromisoformat(row[12]),
            tags=json.loads(row[13]),
        )

    def _row_to_edge(self, row: tuple[Any, ...]) -> Edge:
        """Convert database row to Edge object."""
        return Edge(
            id=row[0],
            source_id=row[1],
            target_id=row[2],
            type=EdgeType(row[3]),
            weight=row[4],
            confidence=row[5],
            metadata=json.loads(row[6]),
            created_at=datetime.fromisoformat(row[7]),
            created_by=row[8],
            valid_from=datetime.fromisoformat(row[9]) if row[9] else None,
            valid_until=datetime.fromisoformat(row[10]) if row[10] else None,
        )

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self) -> "SQLiteAdapter":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
