"""Scope types and definitions."""

from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ScopeType(str, Enum):
    """Types of memory scopes."""

    USER = "user"  # User-level memories
    PROJECT = "project"  # Project-specific memories
    CODE = "code"  # Code-level memories
    PERSONAL = "personal"  # Private memories


class ScopeConfig(BaseModel):
    """Configuration for a scope."""

    max_nodes: int = 10000
    max_edges: int = 50000
    enable_temporal: bool = True
    enable_consolidation: bool = True
    auto_save: bool = True
    save_interval: int = 300  # seconds


class Scope(BaseModel):
    """A memory scope."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: ScopeType
    path: Path
    config: ScopeConfig = Field(default_factory=ScopeConfig)
    parent: str | None = None  # Parent scope ID for inheritance
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    def get_db_path(self) -> Path:
        """Get the database file path for this scope."""
        return self.path / "memory.db"

    def get_config_path(self) -> Path:
        """Get the config file path for this scope."""
        return self.path / "config.yaml"

    def ensure_directory(self) -> None:
        """Ensure the scope directory exists."""
        self.path.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump()
        data["path"] = str(self.path)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scope":
        """Create from dictionary."""
        data["path"] = Path(data["path"])
        return cls(**data)
