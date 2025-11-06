# Mem-Layer: Graph Database Memory System for AI Models

## Executive Summary

Mem-Layer is a graph-based memory management system designed to provide AI models with persistent, scoped, and temporally-aware memory. The system enables long-standing operations, cross-session context retention, and structured knowledge management through a lightweight yet powerful architecture.

## Research Findings

### Industry Landscape (2025)

**Leading Solutions:**
- **Mem0**: Production-ready memory system with 91% lower p95 latency, 90% token cost savings
- **Graphiti (Zep)**: Temporal knowledge graphs with 14K GitHub stars, 25K weekly PyPI downloads
- **Neo4j**: Industry standard graph database for AI products
- **NetworkX**: Lightweight Python library for in-memory graph operations

**Key Patterns Identified:**
1. **Hierarchical Memory**: Working memory (session) + Episodic memory (long-term)
2. **Temporal Tracking**: Time-aware relationships with validity periods
3. **Entity-Relationship Model**: Nodes (entities) + Edges (relationships) + Properties
4. **Hybrid Retrieval**: Combining graph traversal with semantic search
5. **Consolidation**: Periodic summarization and deduplication of memory

### Technology Stack Decision

After deep research, the optimal stack for a reasonable, non-overly ambitious implementation:

- **Language**: Python 3.11+ (best ecosystem for AI/ML)
- **Graph Engine**: NetworkX (lightweight, no server required, excellent for prototyping)
- **Persistence**: SQLite (file-based, zero-config, ACID compliant)
- **CLI Framework**: Click (simple, powerful, widely adopted)
- **Terminal UI**: Rich (beautiful terminal output)
- **Optional Web UI**: FastAPI + lightweight frontend
- **Serialization**: JSON + pickle for graph persistence

## Project Scope

### Phase 1: Core Memory System (MVP) - 2-3 Weeks

**Goal**: Build a functional graph-based memory system with basic persistence and CLI

#### 1.1 Core Graph Memory Engine

**Features:**
- Entity-Relationship graph model using NetworkX
- Node types: Entity, Concept, Event, Note
- Edge types: RELATES_TO, DEPENDS_ON, REFERENCES, TEMPORAL_SEQUENCE
- Temporal metadata: created_at, updated_at, valid_from, valid_until
- Node properties: id, type, scope, content, metadata, timestamps
- Edge properties: type, weight, confidence, timestamps

**Memory Types:**
- **Working Memory**: Current session context (in-memory, ephemeral)
- **Episodic Memory**: Historical interactions and events (persisted)
- **Semantic Memory**: Facts and knowledge (persisted)

#### 1.2 Scoping System

**Scope Levels:**
1. **User Scope**: Personal memories tied to user identity
   - Location: `~/.mem-layer/user/<user_id>/`
   - Use case: User preferences, personal context

2. **Project Scope**: Project-specific memories
   - Location: `<project_dir>/.mem-layer/`
   - Use case: Project context, architecture decisions, patterns

3. **Code Scope**: Code-specific memories (functions, classes, modules)
   - Location: Embedded in project scope with code references
   - Use case: Function purposes, refactoring notes, code relationships

4. **Personal Scope**: Private, unshared memories
   - Location: `~/.mem-layer/personal/`
   - Use case: Private notes, learning journal

**Scope Properties:**
- Inheritance: Project scope can access user scope (read-only)
- Isolation: Personal scope is fully isolated
- Merging: Query across multiple scopes with priority rules

#### 1.3 Persistence Layer

**Database Schema:**
```
Tables:
- nodes (id, type, scope, content, metadata, created_at, updated_at)
- edges (id, source_id, target_id, type, weight, metadata, created_at)
- scopes (id, name, type, path, config)
- sessions (id, scope_id, started_at, ended_at, summary)
```

**Operations:**
- Graph serialization to SQLite
- Incremental updates (not full graph replacement)
- Transaction support for atomic operations
- Export/import to JSON for portability

#### 1.4 CLI Interface

**Core Commands:**
```bash
# Initialization
mem-layer init [--scope user|project|personal]

# Memory operations
mem-layer add <entity|relation|note> [--scope SCOPE]
mem-layer query <pattern> [--scope SCOPE]
mem-layer search <text> [--scope SCOPE]
mem-layer list [--type TYPE] [--scope SCOPE]
mem-layer show <id>
mem-layer delete <id>

# Graph operations
mem-layer graph stats [--scope SCOPE]
mem-layer graph export <file> [--scope SCOPE]
mem-layer graph import <file> [--scope SCOPE]
mem-layer graph visualize [--scope SCOPE] [--output FILE]

# Scope management
mem-layer scope list
mem-layer scope create <name> --type <TYPE>
mem-layer scope switch <name>
mem-layer scope info [<name>]

# Session management
mem-layer session start [--scope SCOPE]
mem-layer session end [--save]
mem-layer session list
mem-layer session show <id>
```

#### 1.5 Basic Query Engine

**Query Capabilities:**
- Find nodes by type, scope, or property
- Graph traversal: neighbors, paths, subgraphs
- Temporal queries: "What was true at time T?"
- Pattern matching: Find entities matching a pattern
- Full-text search on node content

**NOT Included in Phase 1:**
- Vector embeddings / semantic search
- Advanced graph algorithms (centrality, communities)
- Natural language queries

### Phase 2: Model Communication & Rules - 2 Weeks

**Goal**: Enable model-to-model communication and access control

#### 2.1 Model-to-Model Communication

**Features:**
- Message queue system for async model communication
- Inbox/outbox pattern for each model context
- Message types: REQUEST, RESPONSE, NOTIFICATION, NOTE
- Message routing based on scope and permissions

**Message Schema:**
```python
{
  "id": "msg_uuid",
  "from": "model_context_id",
  "to": "model_context_id",  # or "broadcast"
  "type": "REQUEST|RESPONSE|NOTIFICATION|NOTE",
  "subject": "Short description",
  "content": "Detailed message",
  "reply_to": "parent_msg_id",
  "scope": "project|user|code",
  "created_at": "timestamp",
  "read_at": "timestamp|null"
}
```

#### 2.2 Access Control & Rules

**Rule System:**
- Define what each model context can read/write
- Scope-based permissions (read, write, delete)
- Entity-level permissions
- Audit log for all modifications

**Rule Examples:**
```yaml
rules:
  - context: "code_agent"
    scope: "code"
    permissions: [read, write]
    constraints:
      - type: "only_own_entities"
      - type: "no_delete_older_than_7d"

  - context: "review_agent"
    scope: "code"
    permissions: [read]

  - context: "user_agent"
    scope: "user"
    permissions: [read, write, delete]
```

#### 2.3 Notes for Future Self

**Features:**
- Special node type: FutureNote
- Scheduling: deliver note at specific time or trigger condition
- Priorities: CRITICAL, HIGH, NORMAL, LOW
- Categorization: tags, topics, related entities

**Example:**
```python
mem_layer.add_future_note(
    content="Review the refactoring of module X",
    trigger="on_next_session",  # or specific datetime
    priority="HIGH",
    tags=["refactoring", "module-x"],
    scope="project"
)
```

### Phase 3: Advanced UI - 1-2 Weeks

**Goal**: Provide visual interfaces for exploration and management

#### 3.1 Terminal UI (TUI)

**Technology**: Textual (Python TUI framework)

**Features:**
- Interactive graph visualization (ASCII art)
- Split-pane layout: graph view + detail view
- Keyboard navigation
- Search and filter
- Real-time updates

**Screens:**
1. Dashboard: Stats, recent activity, notifications
2. Graph Explorer: Visual graph navigation
3. Search: Full-text and pattern search
4. Messages: Model-to-model communication inbox
5. Settings: Scope and rule configuration

#### 3.2 Web UI

**Technology**: FastAPI + vanilla JS or minimal React

**Features:**
- Interactive graph visualization (vis.js or cytoscape.js)
- REST API for all operations
- WebSocket for real-time updates
- Export to various formats (JSON, GraphML, DOT)

**Routes:**
```
GET  /api/v1/graph          - Get full graph or filtered subgraph
GET  /api/v1/nodes          - List nodes with filtering
GET  /api/v1/nodes/{id}     - Get node details
POST /api/v1/nodes          - Create node
PUT  /api/v1/nodes/{id}     - Update node
GET  /api/v1/search         - Search nodes
GET  /api/v1/query          - Complex graph queries
WS   /api/v1/ws             - WebSocket for real-time updates
```

### Phase 4: Production Features - 1-2 Weeks

**Goal**: Make system production-ready

#### 4.1 Advanced Features

- **Graph Algorithms**: Centrality, shortest paths, community detection
- **Consolidation**: Periodic summarization of old memories
- **Importance Scoring**: Rank memories by relevance
- **Decay Mechanism**: Fade old, unused memories
- **Conflict Resolution**: Handle contradictory information
- **Migration to Neo4j**: Optional upgrade path for large-scale deployment

#### 4.2 Developer Experience

- Comprehensive documentation
- Example integrations (LangChain, LlamaIndex)
- Plugin system for custom node/edge types
- Configuration file support (YAML/TOML)
- Logging and debugging tools

#### 4.3 Testing & Quality

- Unit tests (90%+ coverage)
- Integration tests
- Performance benchmarks
- Example datasets and demos

## Non-Goals (Out of Scope)

To keep this project reasonable, the following are explicitly OUT of scope:

1. **Vector Embeddings**: Not in initial version (can add later)
2. **Multi-tenancy**: Single user focus initially
3. **Distributed Systems**: No clustering, sharding, or replication
4. **Real-time Collaboration**: No multi-user editing
5. **LLM Integration**: No built-in LLM calls (integration points only)
6. **Cloud Deployment**: Local-first, self-hosted only
7. **Complex Security**: Basic auth only, no OAuth/SSO
8. **Mobile Apps**: Desktop/server only
9. **Graph ML**: No graph neural networks or complex analytics

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interfaces                       │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │     CLI      │     TUI      │       Web UI (localhost)  │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Core API Layer                          │
│  - Memory Operations  - Query Engine  - Session Management   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Graph Memory Engine                        │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │   NetworkX   │  Scope Mgmt  │   Temporal Tracking      │ │
│  │  Graph Core  │  & Isolation │   & Versioning           │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Persistence Layer                           │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │    SQLite    │  Graph       │   Export/Import          │ │
│  │    Storage   │  Serializer  │   (JSON, GraphML)        │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
mem-layer/
├── README.md
├── PROJECT_SCOPE.md (this file)
├── pyproject.toml
├── setup.py
├── requirements.txt
├── requirements-dev.txt
│
├── src/
│   └── mem_layer/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       │
│       ├── core/                # Core graph engine
│       │   ├── __init__.py
│       │   ├── graph.py         # NetworkX graph wrapper
│       │   ├── node.py          # Node types and operations
│       │   ├── edge.py          # Edge types and operations
│       │   ├── memory.py        # Memory types (working, episodic, semantic)
│       │   └── temporal.py      # Temporal tracking logic
│       │
│       ├── scope/               # Scoping system
│       │   ├── __init__.py
│       │   ├── manager.py       # Scope management
│       │   ├── types.py         # Scope types (user, project, code, personal)
│       │   └── resolver.py      # Scope resolution and inheritance
│       │
│       ├── persistence/         # Database layer
│       │   ├── __init__.py
│       │   ├── sqlite.py        # SQLite adapter
│       │   ├── serializer.py    # Graph serialization
│       │   └── migrations/      # DB migrations
│       │
│       ├── query/               # Query engine
│       │   ├── __init__.py
│       │   ├── engine.py        # Query execution
│       │   ├── builder.py       # Query builder
│       │   └── parser.py        # Query parsing
│       │
│       ├── communication/       # Model-to-model messaging
│       │   ├── __init__.py
│       │   ├── message.py       # Message types
│       │   └── router.py        # Message routing
│       │
│       ├── rules/               # Access control
│       │   ├── __init__.py
│       │   ├── engine.py        # Rule engine
│       │   └── definitions.py   # Rule definitions
│       │
│       ├── cli/                 # Command-line interface
│       │   ├── __init__.py
│       │   ├── main.py          # CLI app
│       │   ├── commands/        # Command implementations
│       │   └── formatting.py    # Output formatting with Rich
│       │
│       ├── tui/                 # Terminal UI (Phase 3)
│       │   ├── __init__.py
│       │   ├── app.py           # Textual app
│       │   └── screens/         # TUI screens
│       │
│       ├── api/                 # Web API (Phase 3)
│       │   ├── __init__.py
│       │   ├── server.py        # FastAPI app
│       │   ├── routes/          # API routes
│       │   └── websocket.py     # WebSocket handler
│       │
│       ├── utils/               # Utilities
│       │   ├── __init__.py
│       │   ├── config.py        # Configuration management
│       │   ├── logger.py        # Logging setup
│       │   └── validation.py    # Data validation
│       │
│       └── config/              # Default configs
│           ├── default.yaml
│           └── schema.json
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── examples/                    # Usage examples
│   ├── basic_usage.py
│   ├── model_communication.py
│   └── custom_integration.py
│
├── docs/                        # Documentation
│   ├── index.md
│   ├── quickstart.md
│   ├── architecture.md
│   ├── api_reference.md
│   └── examples.md
│
└── scripts/                     # Development scripts
    ├── setup_dev.sh
    ├── run_tests.sh
    └── benchmark.py
```

## Timeline Estimate

**Total: 6-9 weeks for full implementation**

- Phase 1 (MVP): 2-3 weeks
- Phase 2 (Communication & Rules): 2 weeks
- Phase 3 (UI): 1-2 weeks
- Phase 4 (Production): 1-2 weeks

**Recommended Approach**: Build Phase 1 completely, validate with users, then decide on Phase 2-4 based on feedback.

## Success Metrics

**Technical:**
- Graph operations < 100ms for graphs with <10K nodes
- Persistence operations < 500ms
- Memory usage < 500MB for typical workloads
- 90%+ test coverage

**Functional:**
- Support for 4 scope types
- 5+ node types, 5+ edge types
- Temporal queries working correctly
- Model-to-model messaging functional
- CLI with 20+ commands
- Export/import working for JSON and GraphML

**User Experience:**
- Documentation complete and clear
- 5+ working examples
- Installation in < 5 minutes
- First graph created in < 2 minutes

## Risk Assessment

**Low Risk:**
- Core graph operations (well-established with NetworkX)
- SQLite persistence (mature, stable)
- CLI development (straightforward with Click)

**Medium Risk:**
- Temporal query performance at scale
- Graph serialization efficiency
- Scope isolation complexity

**High Risk:**
- TUI complexity (Textual learning curve)
- Graph visualization performance
- Migration path to Neo4j if needed

**Mitigation:**
- Start simple, add complexity incrementally
- Extensive testing at each phase
- Performance benchmarking early
- Clear upgrade path documented

## Open Questions

1. **Vector Embeddings**: Add in Phase 1 or defer to Phase 4?
   - Recommendation: Defer to Phase 4, focus on core graph first

2. **Query Language**: Custom DSL or simple API?
   - Recommendation: Start with simple API, add DSL if needed

3. **Visualization**: ASCII art, or require graphviz?
   - Recommendation: ASCII for TUI, graphviz for CLI export

4. **Multi-user**: Support now or later?
   - Recommendation: Later (Phase 4 or beyond)

## Conclusion

This scope represents a **reasonable, achievable project** that delivers significant value while avoiding over-ambition. The phased approach allows for:

- **Early validation** with MVP (Phase 1)
- **Incremental complexity** in Phases 2-4
- **Flexibility** to adjust based on feedback
- **Clear upgrade paths** for production needs

The system will provide AI models with:
- ✅ Persistent, scoped memory
- ✅ Temporal awareness
- ✅ Model-to-model communication
- ✅ Access control
- ✅ Multiple interfaces (CLI, TUI, Web)
- ✅ Long-standing operation support

**Recommendation**: Start with Phase 1 implementation immediately. This is well-scoped, achievable, and provides a solid foundation for future expansion.
