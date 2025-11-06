"""Memory types and management."""

from enum import Enum


class MemoryType(str, Enum):
    """Types of memory in the system."""

    WORKING = "working"  # Current session, ephemeral
    EPISODIC = "episodic"  # Historical interactions, persisted
    SEMANTIC = "semantic"  # Facts and knowledge, persisted
