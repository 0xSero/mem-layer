# Mem-Layer

> A graph-based memory management system for AI models with scoped persistence, temporal awareness, and cross-model communication.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Mem-Layer provides AI models with persistent, structured memory using graph databases. It enables:

- 🧠 **Persistent Memory**: Keep context across sessions
- 🎯 **Scoped Isolation**: Separate memories for user, project, and code contexts
- ⏰ **Temporal Awareness**: Track how knowledge changes over time
- 🤝 **Model Communication**: Enable models to leave notes for each other
- 🔒 **Access Control**: Define what models can read and modify
- 🖥️ **Multiple Interfaces**: CLI, Terminal UI, Web UI, and MCP Server
- 🔌 **MCP Integration**: Works with Claude Desktop and other MCP clients

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/0xSero/mem-layer.git
cd mem-layer

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install mem-layer
```

### Basic Usage

```bash
# Initialize a project scope
mem-layer init --scope project

# Add an entity to memory
mem-layer add entity "User authentication module" \
    --tags auth,security \
    --importance 0.9

# Add a note
mem-layer add note "Remember to refactor the login handler" \
    --priority high

# Search memory
mem-layer search "authentication"

# Query the graph
mem-layer query "type:entity AND tags:security"

# Visualize the memory graph
mem-layer graph visualize --output graph.png

# View statistics
mem-layer graph stats
```

### MCP Server (For Claude Desktop & AI Assistants)

Mem-Layer includes an MCP server that lets AI assistants access persistent memory:

```bash
# Add to Claude Desktop configuration:
# ~/.config/Claude/claude_desktop_config.json (Linux)
# ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
{
  "mcpServers": {
    "mem-layer": {
      "command": "mem-layer-mcp"
    }
  }
}
```

Now Claude Desktop can use tools like:
- `add_memory` - Store persistent memories
- `query_memory` - Query with patterns
- `search_memory` - Full-text search
- `traverse_memory` - Follow relationship graphs

See [MCP Server Documentation](docs/mcp-server.md) for details.

## Key Features

### 🎯 Multiple Memory Scopes

Organize memories into different contexts:

- **User Scope**: Personal preferences and context across projects
- **Project Scope**: Project-specific knowledge and architecture decisions
- **Code Scope**: Code-level memories (functions, classes, modules)
- **Personal Scope**: Private notes and learning journal

```bash
# Create a project scope
mem-layer scope create my-project --type project

# Switch to project scope
mem-layer scope switch my-project

# Query across scopes
mem-layer query "refactoring" --scope user,project
```

### ⏰ Temporal Knowledge Tracking

Track how facts and relationships change over time:

```python
from mem_layer import MemoryAPI

api = MemoryAPI()

# Add a fact with validity period
api.create_node(
    type="entity",
    content="API endpoint: /api/v1/users",
    valid_from="2024-01-01",
    valid_until="2024-06-01"  # Deprecated after this
)

# Query what was true at a specific time
result = api.query_at_time("2024-03-15")
```

### 🤝 Model-to-Model Communication

Enable AI models to communicate asynchronously:

```python
# Model A leaves a note for Model B
api.send_message(
    from_context="code_reviewer",
    to_context="test_generator",
    subject="Need tests for auth module",
    content="The authentication module was refactored. Please generate new tests.",
    priority="HIGH"
)

# Model B receives messages
messages = api.receive_messages(context="test_generator")
```

### 🔒 Rule-Based Access Control

Define what each model context can access:

```yaml
# rules.yaml
rules:
  - context: "code_agent"
    scope: "code"
    permissions: [read, write]
    constraints:
      - only_own_entities
      - no_delete_older_than_7d

  - context: "review_agent"
    scope: "code"
    permissions: [read]
```

### 📊 Rich Querying

Multiple query types for different use cases:

```bash
# Pattern matching
mem-layer query "type:entity AND importance:>0.8"

# Full-text search
mem-layer search "refactoring authentication"

# Graph traversal
mem-layer traverse <node-id> --depth 3

# Temporal queries
mem-layer query --at-time "2024-01-15"
```

## Architecture

Mem-Layer uses a layered architecture:

```
┌─────────────────────────────────────────┐
│  User Interfaces (CLI / TUI / Web)      │
├─────────────────────────────────────────┤
│  Core API Layer                          │
├─────────────────────────────────────────┤
│  Graph Engine (NetworkX)                 │
├─────────────────────────────────────────┤
│  Scope Management & Rules                │
├─────────────────────────────────────────┤
│  Persistence Layer (SQLite)              │
└─────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

## Python API

### Basic Operations

```python
from mem_layer import MemoryAPI, NodeType, EdgeType

# Initialize API
api = MemoryAPI(scope="project")

# Create nodes
user_node = api.create_node(
    type=NodeType.ENTITY,
    content="User authentication system",
    metadata={"module": "auth", "version": "2.0"},
    importance=0.9
)

db_node = api.create_node(
    type=NodeType.ENTITY,
    content="PostgreSQL database",
    metadata={"host": "localhost", "port": 5432}
)

# Create relationship
api.create_edge(
    source_id=user_node.id,
    target_id=db_node.id,
    type=EdgeType.DEPENDS_ON,
    weight=0.95
)

# Query
results = api.query(
    pattern="type:entity AND metadata.module:auth"
)

# Search
results = api.search("authentication database")

# Get node with neighbors
subgraph = api.get_with_neighbors(user_node.id, depth=2)
```

### Session Management

```python
# Start a session
session = api.start_session(scope="project")

# Perform operations (all tagged with session ID)
api.create_node(...)
api.create_edge(...)

# End session and save
summary = api.end_session(session.id, save=True)
print(f"Session summary: {summary.operations_count} operations")
```

### Advanced Usage

```python
# Future notes (reminders)
api.add_future_note(
    content="Review the caching strategy",
    trigger="on_next_session",
    priority="HIGH",
    tags=["performance", "caching"]
)

# Importance scoring (auto-calculated but can be adjusted)
api.update_importance(node_id, importance=0.95)

# Graph analysis
stats = api.get_graph_stats()
print(f"Nodes: {stats.node_count}, Edges: {stats.edge_count}")
print(f"Most connected: {stats.most_connected_nodes}")

# Export
api.export_graph("backup.json", format="json")
api.export_graph("graph.graphml", format="graphml")
```

## CLI Reference

### Initialization

```bash
mem-layer init [--scope user|project|personal]
mem-layer config show
mem-layer config set <key> <value>
```

### Memory Operations

```bash
# Add nodes
mem-layer add entity <content> [--tags TAGS] [--importance FLOAT]
mem-layer add note <content> [--priority high|normal|low]
mem-layer add event <content> [--timestamp TIMESTAMP]

# Add relationships
mem-layer relate <source-id> <target-id> --type <TYPE>

# Query and search
mem-layer query <pattern> [--scope SCOPE] [--limit N]
mem-layer search <text> [--scope SCOPE]
mem-layer list [--type TYPE] [--scope SCOPE]
mem-layer show <node-id>

# Update and delete
mem-layer update <node-id> [--content TEXT] [--importance FLOAT]
mem-layer delete <node-id>
```

### Graph Operations

```bash
mem-layer graph stats [--scope SCOPE]
mem-layer graph visualize [--output FILE] [--format png|svg|dot]
mem-layer graph export <file> [--format json|graphml]
mem-layer graph import <file>
mem-layer traverse <node-id> [--depth N]
```

### Scope Management

```bash
mem-layer scope list
mem-layer scope create <name> --type <TYPE>
mem-layer scope switch <name>
mem-layer scope info [<name>]
mem-layer scope delete <name>
```

### Sessions

```bash
mem-layer session start [--scope SCOPE]
mem-layer session end [--save]
mem-layer session list
mem-layer session show <session-id>
```

## Configuration

Configuration files are loaded in order of priority:

1. CLI arguments (highest priority)
2. Environment variables (`MEM_LAYER_*`)
3. Project config (`.mem-layer/config.yaml`)
4. User config (`~/.mem-layer/config.yaml`)
5. Default config (lowest priority)

Example configuration:

```yaml
# ~/.mem-layer/config.yaml
version: "1.0"

storage:
  backend: sqlite
  auto_save: true
  save_interval: 300

graph:
  default_scope: project
  max_nodes: 10000

memory:
  consolidation:
    enabled: true
    interval: daily
  decay:
    enabled: true
    half_life: 30

ui:
  cli:
    output_format: table
    color_scheme: auto
```

## Development Roadmap

### Phase 1: Core Memory System (MVP) ✅ Current
- [x] Graph engine with NetworkX
- [x] SQLite persistence
- [x] Basic scoping (user, project, code, personal)
- [x] Temporal tracking
- [ ] CLI with core commands
- [ ] Query engine (pattern, full-text, traversal)
- [ ] Documentation and examples

### Phase 2: Model Communication
- [ ] Message queue system
- [ ] Rule-based access control
- [ ] Audit logging
- [ ] Future notes with triggers

### Phase 3: Advanced UI
- [ ] Terminal UI (Textual)
- [ ] Web UI (FastAPI + React)
- [ ] Interactive graph visualization
- [ ] Real-time updates

### Phase 4: Production Features
- [ ] Graph algorithms (centrality, communities)
- [ ] Memory consolidation
- [ ] Importance scoring and decay
- [ ] Migration path to Neo4j
- [ ] Performance optimizations

## Use Cases

### 1. Long-Running Development Projects

Track architectural decisions, refactoring notes, and code relationships across multiple sessions:

```bash
# Day 1: Document decision
mem-layer add decision "Use PostgreSQL for persistent storage" \
    --tags architecture,database \
    --importance 0.9

# Day 7: Add related note
mem-layer add note "Consider adding Redis cache layer" \
    --relates-to <decision-id>

# Day 30: Review decisions
mem-layer query "type:decision AND age:<30days" \
    --sort-by importance
```

### 2. AI Agent Collaboration

Multiple AI agents working on the same project can share context:

```python
# Agent 1: Code reviewer
api.create_node(
    type=NodeType.NOTE,
    content="Found potential memory leak in request handler",
    metadata={"severity": "high", "file": "api.py", "line": 145}
)
api.send_message(
    to_context="code_fixer",
    subject="Memory leak detected",
    priority="HIGH"
)

# Agent 2: Code fixer
messages = api.receive_messages(context="code_fixer")
# Fix the issue...
api.add_note("Memory leak fixed by using context managers")
```

### 3. Learning and Research

Build a personal knowledge graph:

```bash
mem-layer scope create ml-research --type personal
mem-layer scope switch ml-research

mem-layer add concept "Transformer architecture" \
    --tags deep-learning,nlp

mem-layer add concept "Attention mechanism" \
    --tags deep-learning

mem-layer relate <transformer-id> <attention-id> \
    --type part_of
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/0xSero/mem-layer.git
cd mem-layer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
mypy src/
ruff check src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use Mem-Layer in your research, please cite:

```bibtex
@software{mem_layer_2025,
  title = {Mem-Layer: Graph-Based Memory Management for AI Models},
  author = {0xSero},
  year = {2025},
  url = {https://github.com/0xSero/mem-layer}
}
```

## Acknowledgments

Inspired by:
- [Mem0](https://github.com/mem0ai/mem0) - Memory management for AI agents
- [Graphiti](https://github.com/getzep/graphiti) - Temporal knowledge graphs
- [Neo4j](https://neo4j.com/) - Graph database platform
- [NetworkX](https://networkx.org/) - Python graph library

## Links

- **Documentation**: [docs/](docs/)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Scope**: [PROJECT_SCOPE.md](PROJECT_SCOPE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Issues**: [GitHub Issues](https://github.com/0xSero/mem-layer/issues)

## Support

- 📖 [Documentation](docs/)
- 💬 [Discussions](https://github.com/0xSero/mem-layer/discussions)
- 🐛 [Issue Tracker](https://github.com/0xSero/mem-layer/issues)

---

**Status**: 🚧 Under active development (Phase 1 - MVP)

Built with ❤️ by the open source community.
