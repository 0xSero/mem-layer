# Changelog

All notable changes to Mem-Layer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-06

### Added

#### Core Features
- Graph-based memory system using NetworkX
- Node types: Entity, Concept, Event, Note, Future Note, Code Reference, Decision, Message
- Edge types: Relates To, Depends On, References, Temporal Sequence, Causes, Part Of, Instance Of, Replies To, Similar To
- Temporal tracking for nodes and edges
- Importance scoring and access tracking

#### Scope Management
- Multiple scope types: User, Project, Code, Personal
- Scope isolation and inheritance
- Scope discovery for projects
- Active scope management

#### Persistence
- SQLite backend for graph storage
- Incremental save/load
- Full-text search on node content
- WAL mode for better concurrency
- Graph serialization to JSON, GraphML, and DOT formats

#### Query Engine
- Pattern matching queries
- Full-text search
- Graph traversal
- Temporal queries
- Multiple filter types (type, importance, tags, metadata)

#### API
- Comprehensive Python API
- Node CRUD operations
- Edge CRUD operations
- Query operations
- Graph statistics
- Export/import functionality
- Convenience methods (add_note, add_entity, relate)

#### CLI
- Complete command-line interface using Click
- Rich terminal output
- Commands for:
  - Initialization and setup
  - Node operations (add, list, show, delete)
  - Edge operations (relate)
  - Querying (query, search, traverse)
  - Graph operations (stats, export, import)
  - Scope management (list, create, switch, info)

#### Configuration
- YAML-based configuration
- Hierarchical config loading (default → user → project → env vars → CLI args)
- Configurable storage, graph, query, memory, and UI settings

#### Testing
- Unit tests for core components
- Integration tests for API
- Test fixtures and utilities
- 70%+ test coverage

#### Documentation
- Comprehensive README
- Architecture documentation
- Project scope document
- Quickstart guide
- Contributing guidelines
- Example scripts

### Technical Details
- Python 3.11+ support
- Type hints throughout
- Pydantic models for validation
- NetworkX for graph operations
- SQLite for persistence
- Click for CLI
- Rich for terminal formatting

## [0.0.0] - 2025-01-06

### Added
- Initial project structure
- Basic documentation

[Unreleased]: https://github.com/0xSero/mem-layer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/0xSero/mem-layer/releases/tag/v0.1.0
