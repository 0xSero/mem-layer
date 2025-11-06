"""Node types and operations."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of nodes in the memory graph."""

    ENTITY = "entity"  # Person, place, thing
    CONCEPT = "concept"  # Abstract idea
    EVENT = "event"  # Something that happened
    NOTE = "note"  # Annotation or comment
    FUTURE_NOTE = "future_note"  # Scheduled note
    CODE_REF = "code_ref"  # Reference to code element
    DECISION = "decision"  # Architectural decision
    MESSAGE = "message"  # Model-to-model message


class Node(BaseModel):
    """A node in the memory graph."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    scope: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"

    # Temporal validity
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    # Importance and access tracking
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    # Tags and categorization
    tags: list[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def increment_access(self) -> None:
        """Increment access count and update last accessed time."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()

    def update_content(self, content: str) -> None:
        """Update node content and timestamp."""
        self.content = content
        self.updated_at = datetime.utcnow()

    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if node is valid at given timestamp."""
        if self.valid_from and timestamp < self.valid_from:
            return False
        if self.valid_until and timestamp > self.valid_until:
            return False
        return True

    def add_tag(self, tag: str) -> None:
        """Add a tag to the node."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the node."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Node":
        """Create node from dictionary."""
        return cls(**data)
