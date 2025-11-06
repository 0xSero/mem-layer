"""Scope resolver for querying across multiple scopes."""

from typing import Any

from mem_layer.core.node import Node
from mem_layer.scope.manager import ScopeManager
from mem_layer.scope.types import Scope


class MergeStrategy:
    """Strategy for merging results from multiple scopes."""

    UNION = "union"  # Include all results
    INTERSECTION = "intersection"  # Only include common results
    PRIORITY = "priority"  # Use scope priority order


class ScopeResolver:
    """Resolves queries across multiple scopes."""

    def __init__(self, scope_manager: ScopeManager) -> None:
        """Initialize resolver.

        Args:
            scope_manager: Scope manager instance
        """
        self.scope_manager = scope_manager

    def get_query_scopes(self, scope_ids: list[str] | None = None) -> list[Scope]:
        """Get scopes to query.

        Args:
            scope_ids: Optional list of scope IDs. If None, uses active scope with inheritance

        Returns:
            List of scopes to query
        """
        if scope_ids:
            return [self.scope_manager.get_scope(sid) for sid in scope_ids]

        # Use active scope with inheritance
        active = self.scope_manager.get_active_scope()
        if not active:
            return []

        return self.scope_manager.resolve_inheritance(active.id)

    def filter_by_scope_access(self, nodes: list[Node], scope_id: str) -> list[Node]:
        """Filter nodes by scope access.

        Args:
            nodes: List of nodes
            scope_id: Scope requesting access

        Returns:
            Filtered list of nodes
        """
        return [node for node in nodes if self.scope_manager.can_access(scope_id, node)]

    def merge_results(
        self, results: list[list[Node]], strategy: str = MergeStrategy.UNION
    ) -> list[Node]:
        """Merge results from multiple scopes.

        Args:
            results: List of node lists from different scopes
            strategy: Merge strategy to use

        Returns:
            Merged list of nodes
        """
        if not results:
            return []

        if strategy == MergeStrategy.UNION:
            # Combine all results, removing duplicates by ID
            seen_ids = set()
            merged = []
            for result_list in results:
                for node in result_list:
                    if node.id not in seen_ids:
                        seen_ids.add(node.id)
                        merged.append(node)
            return merged

        elif strategy == MergeStrategy.INTERSECTION:
            # Only include nodes present in all result sets
            if not results:
                return []

            # Get IDs from first result
            common_ids = {node.id for node in results[0]}

            # Intersect with other results
            for result_list in results[1:]:
                result_ids = {node.id for node in result_list}
                common_ids &= result_ids

            # Build result from first list
            return [node for node in results[0] if node.id in common_ids]

        elif strategy == MergeStrategy.PRIORITY:
            # Use first non-empty result (higher priority scopes first)
            for result_list in results:
                if result_list:
                    return result_list
            return []

        else:
            # Default to union
            return self.merge_results(results, MergeStrategy.UNION)

    def resolve_scope_path(self, scope_name: str) -> Scope | None:
        """Resolve a scope by name.

        Args:
            scope_name: Scope name to resolve

        Returns:
            Resolved scope or None
        """
        return self.scope_manager.get_scope_by_name(scope_name)
