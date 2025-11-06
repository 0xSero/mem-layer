"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from mem_layer.api import MemoryAPI
from mem_layer.core.graph import GraphManager
from mem_layer.scope.manager import ScopeManager
from mem_layer.scope.types import ScopeType


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def graph_manager():
    """Create a graph manager instance."""
    return GraphManager()


@pytest.fixture
def scope_manager(temp_dir):
    """Create a scope manager with temp directory."""
    return ScopeManager(base_path=temp_dir)


@pytest.fixture
def test_scope(scope_manager, temp_dir):
    """Create a test scope."""
    return scope_manager.create_scope(
        name="test",
        scope_type=ScopeType.PROJECT,
        path=temp_dir / "test-scope",
    )


@pytest.fixture
def memory_api(temp_dir):
    """Create a MemoryAPI instance with temp directory."""
    scope_manager = ScopeManager(base_path=temp_dir)
    scope = scope_manager.create_scope(
        name="test",
        scope_type=ScopeType.PROJECT,
        path=temp_dir / "test-scope",
    )
    scope_manager.set_active_scope(scope.id)

    api = MemoryAPI(scope="test", base_path=temp_dir)
    return api
