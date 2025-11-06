"""Scope management system."""

from mem_layer.scope.types import Scope, ScopeConfig, ScopeType
from mem_layer.scope.manager import ScopeManager
from mem_layer.scope.resolver import ScopeResolver

__all__ = [
    "Scope",
    "ScopeConfig",
    "ScopeType",
    "ScopeManager",
    "ScopeResolver",
]
