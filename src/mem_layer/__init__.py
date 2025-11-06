"""
Mem-Layer: Graph-based memory management system for AI models.
"""

__version__ = "0.1.0"

from mem_layer.core.node import Node, NodeType
from mem_layer.core.edge import Edge, EdgeType
from mem_layer.core.graph import GraphManager
from mem_layer.core.memory import MemoryType
from mem_layer.scope.types import Scope, ScopeType
from mem_layer.api import MemoryAPI

__all__ = [
    "MemoryAPI",
    "Node",
    "NodeType",
    "Edge",
    "EdgeType",
    "GraphManager",
    "MemoryType",
    "Scope",
    "ScopeType",
]
