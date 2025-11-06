"""Edge types and operations."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EdgeType(str, Enum):
    """Types of edges (relationships) in the memory graph."""

    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    REFERENCES = "references"
    TEMPORAL_SEQUENCE = "temporal_sequence"  # A happened before B
    CAUSES = "causes"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"
    REPLIES_TO = "replies_to"  # For messages
    SIMILAR_TO = "similar_to"
    USES = "uses"  # Uses or employs


class Edge(BaseModel):
    """An edge (relationship) in the memory graph."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: EdgeType

    # Relationship strength
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"

    # Temporal validity
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if edge is valid at given timestamp."""
        if self.valid_from and timestamp < self.valid_from:
            return False
        if self.valid_until and timestamp > self.valid_until:
            return False
        return True

    def invalidate(self, timestamp: datetime | None = None) -> None:
        """Mark edge as invalid from given timestamp."""
        self.valid_until = timestamp or datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Edge":
        """Create edge from dictionary."""
        return cls(**data)

    def __repr__(self) -> str:
        """String representation of edge."""
        return (
            f"Edge({self.source_id} --[{self.type.value}]--> {self.target_id}, "
            f"weight={self.weight:.2f})"
        )
