"""Scope manager for managing memory scopes."""

import json
from pathlib import Path
from typing import Any

from mem_layer.core.node import Node
from mem_layer.exceptions import ScopeNotFoundException
from mem_layer.scope.types import Scope, ScopeType


class ScopeManager:
    """Manages memory scopes."""

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize scope manager.

        Args:
            base_path: Base directory for scopes. Defaults to ~/.mem-layer
        """
        if base_path is None:
            base_path = Path.home() / ".mem-layer"

        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.scopes: dict[str, Scope] = {}
        self.active_scope: str | None = None

        # Registry file for tracking scopes
        self.registry_path = self.base_path / "scopes.json"

        # Load existing scopes
        self._load_registry()

    def create_scope(
        self,
        name: str,
        scope_type: ScopeType,
        path: Path | None = None,
        parent: str | None = None,
    ) -> Scope:
        """Create a new scope.

        Args:
            name: Scope name
            scope_type: Type of scope
            path: Optional custom path. If None, uses default location
            parent: Optional parent scope ID for inheritance

        Returns:
            Created scope
        """
        # Determine path
        if path is None:
            if scope_type == ScopeType.USER:
                path = self.base_path / "user" / name
            elif scope_type == ScopeType.PROJECT:
                path = Path.cwd() / ".mem-layer"
            elif scope_type == ScopeType.CODE:
                path = Path.cwd() / ".mem-layer" / "code"
            elif scope_type == ScopeType.PERSONAL:
                path = self.base_path / "personal" / name

        # Create scope
        scope = Scope(name=name, type=scope_type, path=path, parent=parent)

        # Ensure directory exists
        scope.ensure_directory()

        # Register scope
        self.scopes[scope.id] = scope
        self._save_registry()

        return scope

    def get_scope(self, scope_id: str) -> Scope:
        """Get scope by ID.

        Args:
            scope_id: Scope ID

        Returns:
            Scope object

        Raises:
            ScopeNotFoundException: If scope not found
        """
        scope = self.scopes.get(scope_id)
        if not scope:
            raise ScopeNotFoundException(scope_id)
        return scope

    def get_scope_by_name(self, name: str) -> Scope | None:
        """Get scope by name.

        Args:
            name: Scope name

        Returns:
            Scope object or None if not found
        """
        for scope in self.scopes.values():
            if scope.name == name:
                return scope
        return None

    def list_scopes(self, scope_type: ScopeType | None = None) -> list[Scope]:
        """List all scopes.

        Args:
            scope_type: Optional filter by scope type

        Returns:
            List of scopes
        """
        scopes = list(self.scopes.values())
        if scope_type:
            scopes = [s for s in scopes if s.type == scope_type]
        return scopes

    def delete_scope(self, scope_id: str) -> bool:
        """Delete a scope.

        Args:
            scope_id: Scope ID to delete

        Returns:
            True if deleted

        Raises:
            ScopeNotFoundException: If scope not found
        """
        scope = self.get_scope(scope_id)

        # Remove from registry
        del self.scopes[scope_id]
        self._save_registry()

        # If this was the active scope, clear it
        if self.active_scope == scope_id:
            self.active_scope = None

        return True

    def set_active_scope(self, scope_id: str) -> None:
        """Set the active scope for operations.

        Args:
            scope_id: Scope ID to activate

        Raises:
            ScopeNotFoundException: If scope not found
        """
        if scope_id not in self.scopes:
            raise ScopeNotFoundException(scope_id)
        self.active_scope = scope_id

    def get_active_scope(self) -> Scope | None:
        """Get the currently active scope.

        Returns:
            Active scope or None
        """
        if self.active_scope:
            return self.scopes.get(self.active_scope)
        return None

    def resolve_inheritance(self, scope_id: str) -> list[Scope]:
        """Get scope and all parent scopes in order.

        Args:
            scope_id: Scope ID

        Returns:
            List of scopes from child to root
        """
        result = []
        current_id: str | None = scope_id

        while current_id:
            scope = self.scopes.get(current_id)
            if not scope:
                break
            result.append(scope)
            current_id = scope.parent

        return result

    def can_access(self, scope_id: str, node: Node) -> bool:
        """Check if scope can access a node.

        Args:
            scope_id: Scope ID requesting access
            node: Node to access

        Returns:
            True if access is allowed
        """
        # Get scope hierarchy
        scopes = self.resolve_inheritance(scope_id)

        # Check if node belongs to any scope in the hierarchy
        for scope in scopes:
            if node.scope == scope.id:
                return True

        # Check by scope name (for convenience)
        for scope in scopes:
            if node.scope == scope.name:
                return True

        return False

    def _load_registry(self) -> None:
        """Load scope registry from disk."""
        if not self.registry_path.exists():
            return

        try:
            with open(self.registry_path, "r") as f:
                data = json.load(f)

            for scope_data in data.get("scopes", []):
                scope = Scope.from_dict(scope_data)
                self.scopes[scope.id] = scope

            self.active_scope = data.get("active_scope")

        except Exception:
            # If registry is corrupted, start fresh
            pass

    def _save_registry(self) -> None:
        """Save scope registry to disk."""
        data = {
            "scopes": [scope.to_dict() for scope in self.scopes.values()],
            "active_scope": self.active_scope,
        }

        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def discover_project_scope(self) -> Scope | None:
        """Discover project scope in current directory.

        Looks for .mem-layer directory in current or parent directories.

        Returns:
            Discovered scope or None
        """
        current = Path.cwd()

        # Search up to 5 levels
        for _ in range(5):
            mem_layer_dir = current / ".mem-layer"
            if mem_layer_dir.exists() and mem_layer_dir.is_dir():
                # Check if scope exists in registry
                for scope in self.scopes.values():
                    if scope.path == mem_layer_dir and scope.type == ScopeType.PROJECT:
                        return scope

                # Create new scope for this project
                return self.create_scope(
                    name=current.name, scope_type=ScopeType.PROJECT, path=mem_layer_dir
                )

            # Move up one directory
            if current.parent == current:
                break
            current = current.parent

        return None
