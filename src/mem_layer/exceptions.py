"""Exception classes for Mem-Layer."""


class MemLayerException(Exception):
    """Base exception for all mem-layer errors."""

    pass


class NodeNotFoundException(MemLayerException):
    """Node not found in graph."""

    def __init__(self, node_id: str) -> None:
        super().__init__(f"Node not found: {node_id}")
        self.node_id = node_id


class EdgeNotFoundException(MemLayerException):
    """Edge not found in graph."""

    def __init__(self, edge_id: str) -> None:
        super().__init__(f"Edge not found: {edge_id}")
        self.edge_id = edge_id


class ScopeNotFoundException(MemLayerException):
    """Scope not found."""

    def __init__(self, scope_id: str) -> None:
        super().__init__(f"Scope not found: {scope_id}")
        self.scope_id = scope_id


class PermissionDeniedException(MemLayerException):
    """Operation not permitted by rules."""

    def __init__(self, operation: str, context: str) -> None:
        super().__init__(f"Permission denied for {operation} by context {context}")
        self.operation = operation
        self.context = context


class ValidationException(MemLayerException):
    """Data validation failed."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class PersistenceException(MemLayerException):
    """Database operation failed."""

    pass


class ConfigurationException(MemLayerException):
    """Configuration error."""

    pass


class QueryException(MemLayerException):
    """Query execution failed."""

    pass


class SessionException(MemLayerException):
    """Session management error."""

    pass
