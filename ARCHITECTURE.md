# Mem-Layer Architecture

## Overview

Mem-Layer is designed as a layered architecture with clear separation of concerns. Each layer has specific responsibilities and communicates through well-defined interfaces.

## Architecture Layers

### Layer 1: User Interface Layer

**Responsibilities:**
- Accept user input from various interfaces (CLI, TUI, Web)
- Format and present data to users
- Route commands to the Core API layer

**Components:**
- **CLI** (`src/mem_layer/cli/`): Click-based command-line interface
- **TUI** (`src/mem_layer/tui/`): Textual-based terminal user interface
- **Web API** (`src/mem_layer/api/`): FastAPI-based REST API

### Layer 2: Core API Layer

**Responsibilities:**
- Provide a unified API for all memory operations
- Handle session management
- Coordinate between different subsystems
- Enforce business logic

**Key Classes:**
```python
class MemoryAPI:
    """Main API facade for all memory operations"""

    def __init__(self, scope_manager, graph_engine, query_engine):
        self.scope_manager = scope_manager
        self.graph_engine = graph_engine
        self.query_engine = query_engine

    # Node operations
    def create_node(self, type, content, scope, metadata) -> Node
    def get_node(self, node_id) -> Node
    def update_node(self, node_id, updates) -> Node
    def delete_node(self, node_id) -> bool

    # Edge operations
    def create_edge(self, source_id, target_id, type, metadata) -> Edge
    def get_edges(self, node_id, direction='both') -> List[Edge]

    # Query operations
    def query(self, pattern, scope=None) -> QueryResult
    def search(self, text, scope=None) -> List[Node]
    def traverse(self, start_id, max_depth=3) -> Graph

    # Session operations
    def start_session(self, scope) -> Session
    def end_session(self, session_id, save=True) -> SessionSummary
```

### Layer 3: Graph Engine Layer

**Responsibilities:**
- Manage the in-memory graph structure
- Provide graph operations (add, remove, query)
- Handle temporal metadata
- Maintain graph integrity

**Core Components:**

#### Graph Manager (`src/mem_layer/core/graph.py`)

```python
class GraphManager:
    """Manages the NetworkX graph and provides graph operations"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()  # Directed multigraph
        self.temporal_tracker = TemporalTracker()

    def add_node(self, node: Node) -> str:
        """Add a node to the graph"""

    def add_edge(self, edge: Edge) -> str:
        """Add an edge to the graph"""

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID"""

    def find_path(self, source: str, target: str) -> List[str]:
        """Find shortest path between two nodes"""

    def get_neighbors(self, node_id: str, depth: int = 1) -> Graph:
        """Get neighbors up to specified depth"""

    def get_subgraph(self, node_ids: List[str]) -> Graph:
        """Extract a subgraph"""
```

#### Node Types (`src/mem_layer/core/node.py`)

```python
class NodeType(Enum):
    ENTITY = "entity"      # Person, place, thing
    CONCEPT = "concept"    # Abstract idea
    EVENT = "event"        # Something that happened
    NOTE = "note"          # Annotation or comment
    FUTURE_NOTE = "future_note"  # Scheduled note
    CODE_REF = "code_ref"  # Reference to code element
    DECISION = "decision"  # Architectural decision

class Node:
    id: str
    type: NodeType
    scope: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str  # model context ID

    # Temporal fields
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]

    # Importance scoring
    importance: float  # 0.0 to 1.0
    access_count: int
    last_accessed: datetime
```

#### Edge Types (`src/mem_layer/core/edge.py`)

```python
class EdgeType(Enum):
    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    REFERENCES = "references"
    TEMPORAL_SEQUENCE = "temporal_sequence"  # A happened before B
    CAUSES = "causes"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"

class Edge:
    id: str
    source_id: str
    target_id: str
    type: EdgeType
    weight: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    created_at: datetime
    created_by: str
```

#### Temporal Tracking (`src/mem_layer/core/temporal.py`)

```python
class TemporalTracker:
    """Tracks temporal validity of nodes and edges"""

    def is_valid_at(self, element: Union[Node, Edge], timestamp: datetime) -> bool:
        """Check if element was valid at given time"""

    def get_history(self, element_id: str) -> List[TemporalSnapshot]:
        """Get complete history of an element"""

    def update_validity(self, element_id: str, valid_until: datetime):
        """Mark element as no longer valid after timestamp"""

    def query_at_time(self, graph: Graph, timestamp: datetime) -> Graph:
        """Get graph state at specific time"""
```

### Layer 4: Scope Management Layer

**Responsibilities:**
- Manage different memory scopes (user, project, code, personal)
- Handle scope isolation and inheritance
- Resolve conflicts between scopes
- Provide scope-aware queries

**Components:**

#### Scope Manager (`src/mem_layer/scope/manager.py`)

```python
class ScopeType(Enum):
    USER = "user"
    PROJECT = "project"
    CODE = "code"
    PERSONAL = "personal"

class Scope:
    id: str
    name: str
    type: ScopeType
    path: Path
    config: ScopeConfig
    parent: Optional[str]  # For inheritance

class ScopeManager:
    """Manages memory scopes"""

    def __init__(self):
        self.scopes: Dict[str, Scope] = {}
        self.active_scope: Optional[str] = None

    def create_scope(self, name: str, type: ScopeType, path: Path) -> Scope:
        """Create a new scope"""

    def get_scope(self, scope_id: str) -> Scope:
        """Get scope by ID"""

    def set_active_scope(self, scope_id: str):
        """Set the active scope for operations"""

    def resolve_inheritance(self, scope_id: str) -> List[Scope]:
        """Get scope and all parent scopes in order"""

    def can_access(self, scope_id: str, node: Node) -> bool:
        """Check if scope can access a node"""
```

#### Scope Resolution (`src/mem_layer/scope/resolver.py`)

```python
class ScopeResolver:
    """Resolves queries across multiple scopes"""

    def query_with_inheritance(self, query: Query, scope: Scope) -> QueryResult:
        """Execute query across scope hierarchy"""

    def merge_results(self, results: List[QueryResult], strategy: MergeStrategy) -> QueryResult:
        """Merge results from multiple scopes"""
```

### Layer 5: Query Engine Layer

**Responsibilities:**
- Parse and execute queries
- Provide various query types (pattern matching, full-text, graph traversal)
- Optimize query execution
- Return structured results

**Components:**

#### Query Engine (`src/mem_layer/query/engine.py`)

```python
class QueryType(Enum):
    PATTERN = "pattern"        # Pattern matching on graph
    FULL_TEXT = "full_text"    # Text search on content
    TRAVERSAL = "traversal"    # Graph traversal
    TEMPORAL = "temporal"      # Time-based queries
    HYBRID = "hybrid"          # Combination

class Query:
    type: QueryType
    pattern: Optional[str]
    text: Optional[str]
    start_nodes: Optional[List[str]]
    filters: Dict[str, Any]
    scope: Optional[str]
    temporal: Optional[datetime]
    limit: int = 100

class QueryEngine:
    """Executes queries against the graph"""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager

    def execute(self, query: Query) -> QueryResult:
        """Execute a query"""

    def pattern_match(self, pattern: str, scope: str) -> List[Node]:
        """Match nodes by pattern"""

    def full_text_search(self, text: str, scope: str) -> List[Node]:
        """Search node content"""

    def traverse(self, start_id: str, max_depth: int, filters: Dict) -> Graph:
        """Traverse graph from starting node"""

    def temporal_query(self, timestamp: datetime, filters: Dict) -> Graph:
        """Query graph state at specific time"""
```

### Layer 6: Persistence Layer

**Responsibilities:**
- Persist graph to SQLite database
- Serialize/deserialize graph structures
- Handle migrations
- Export/import to various formats

**Components:**

#### SQLite Adapter (`src/mem_layer/persistence/sqlite.py`)

```python
class SQLiteAdapter:
    """Handles persistence to SQLite database"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def save_node(self, node: Node):
        """Save a node to database"""

    def load_node(self, node_id: str) -> Node:
        """Load a node from database"""

    def save_edge(self, edge: Edge):
        """Save an edge to database"""

    def save_graph(self, graph: GraphManager, scope: str):
        """Save entire graph (incremental)"""

    def load_graph(self, scope: str) -> GraphManager:
        """Load graph from database"""
```

#### Serializer (`src/mem_layer/persistence/serializer.py`)

```python
class GraphSerializer:
    """Serializes graph to various formats"""

    def to_json(self, graph: GraphManager) -> str:
        """Serialize to JSON"""

    def from_json(self, json_str: str) -> GraphManager:
        """Deserialize from JSON"""

    def to_graphml(self, graph: GraphManager) -> str:
        """Export to GraphML format"""

    def to_dot(self, graph: GraphManager) -> str:
        """Export to DOT format for Graphviz"""
```

### Layer 7: Communication Layer (Phase 2)

**Responsibilities:**
- Enable model-to-model messaging
- Route messages based on context and permissions
- Maintain message history
- Handle async communication

**Components:**

```python
class Message:
    id: str
    from_context: str
    to_context: str  # or "broadcast"
    type: MessageType
    subject: str
    content: str
    reply_to: Optional[str]
    scope: str
    created_at: datetime
    read_at: Optional[datetime]

class MessageRouter:
    """Routes messages between model contexts"""

    def send(self, message: Message):
        """Send a message"""

    def receive(self, context: str) -> List[Message]:
        """Get messages for a context"""

    def broadcast(self, message: Message, scope: str):
        """Broadcast to all contexts in scope"""
```

### Layer 8: Rules Engine (Phase 2)

**Responsibilities:**
- Define and enforce access control rules
- Validate operations against rules
- Audit rule violations
- Provide rule management

**Components:**

```python
class Rule:
    id: str
    context: str  # Which model context
    scope: str
    permissions: List[Permission]
    constraints: List[Constraint]

class RulesEngine:
    """Enforces access control rules"""

    def can_read(self, context: str, node: Node) -> bool:
        """Check if context can read node"""

    def can_write(self, context: str, node: Node) -> bool:
        """Check if context can modify node"""

    def can_delete(self, context: str, node: Node) -> bool:
        """Check if context can delete node"""

    def validate_operation(self, context: str, operation: Operation) -> ValidationResult:
        """Validate operation against rules"""
```

## Data Flow

### Creating a Node

```
User -> CLI -> MemoryAPI.create_node()
                    |
                    v
            ScopeManager.get_active_scope()
                    |
                    v
            RulesEngine.can_write() [Phase 2]
                    |
                    v
            GraphManager.add_node()
                    |
                    v
            TemporalTracker.track()
                    |
                    v
            SQLiteAdapter.save_node()
                    |
                    v
            Return Node
```

### Querying the Graph

```
User -> CLI -> MemoryAPI.query()
                    |
                    v
            ScopeResolver.query_with_inheritance()
                    |
                    v
            QueryEngine.execute()
                    |
                    +-> pattern_match()
                    |-> full_text_search()
                    |-> traverse()
                    +-> temporal_query()
                    |
                    v
            Filter by permissions [Phase 2]
                    |
                    v
            Return QueryResult
```

### Session Management

```
User -> CLI -> MemoryAPI.start_session()
                    |
                    v
            Create Session object
            Set as active session
                    |
                    v
            [User performs operations]
            All operations tagged with session_id
                    |
                    v
            MemoryAPI.end_session()
                    |
                    v
            Summarize session activity
            Save session to database
            Merge working memory to episodic memory
                    |
                    v
            Return SessionSummary
```

## Configuration Management

Configuration is managed through a hierarchical system:

1. **Default Config** (`src/mem_layer/config/default.yaml`)
2. **User Config** (`~/.mem-layer/config.yaml`)
3. **Project Config** (`<project>/.mem-layer/config.yaml`)
4. **Environment Variables** (`MEM_LAYER_*`)
5. **CLI Arguments**

Priority: CLI Args > Env Vars > Project Config > User Config > Default Config

```yaml
# Example config.yaml
version: "1.0"

storage:
  backend: sqlite
  path: "{scope_path}/memory.db"
  auto_save: true
  save_interval: 300  # seconds

graph:
  default_scope: project
  max_nodes: 10000
  enable_temporal: true

query:
  default_limit: 100
  max_depth: 5
  enable_full_text: true

memory:
  consolidation:
    enabled: true
    interval: "daily"
    keep_important: true
    threshold: 0.7

  decay:
    enabled: true
    half_life: 30  # days
    min_importance: 0.1

ui:
  cli:
    output_format: table
    color_scheme: auto

  tui:
    theme: dark

  web:
    host: localhost
    port: 8080
    cors_origins: ["http://localhost:3000"]
```

## Performance Considerations

### In-Memory Graph Size

- **Target**: Support graphs up to 10,000 nodes comfortably
- **Strategy**: Lazy loading of scopes, only active scope in memory
- **Fallback**: If graph > 10K nodes, recommend migration to Neo4j

### Query Performance

- **Indexing**: SQLite indexes on node type, scope, content (FTS)
- **Caching**: LRU cache for frequently accessed nodes
- **Optimization**: Query planner for complex queries

### Persistence Performance

- **Incremental Saves**: Only save changed nodes/edges
- **Batching**: Batch database operations
- **Write-Ahead Log**: Use SQLite WAL mode for concurrency

### Memory Usage

- **Target**: < 500MB for typical workloads
- **Strategy**:
  - Serialize large content to disk
  - Implement node eviction for large graphs
  - Use generators for large result sets

## Error Handling

```python
class MemLayerException(Exception):
    """Base exception for all mem-layer errors"""

class NodeNotFoundException(MemLayerException):
    """Node not found in graph"""

class ScopeNotFoundException(MemLayerException):
    """Scope not found"""

class PermissionDeniedException(MemLayerException):
    """Operation not permitted by rules"""

class ValidationException(MemLayerException):
    """Data validation failed"""

class PersistenceException(MemLayerException):
    """Database operation failed"""
```

## Security Considerations

### Phase 1 (MVP)
- Basic validation of inputs
- No authentication (local-only)
- File permission checks

### Phase 2
- Rule-based access control
- Audit logging
- Input sanitization

### Future
- Encryption at rest
- Encryption in transit (for web API)
- API key authentication
- Rate limiting

## Testing Strategy

### Unit Tests
- Each class tested independently
- Mock dependencies
- Test edge cases and error conditions

### Integration Tests
- Test full data flow
- Test scope inheritance
- Test query across multiple scopes

### Performance Tests
- Benchmark graph operations
- Load testing with large graphs
- Memory profiling

### End-to-End Tests
- CLI command tests
- Full workflow tests
- Multi-session tests

## Migration Path

### From NetworkX to Neo4j

When graph size exceeds NetworkX capabilities:

1. Export graph to GraphML format
2. Install Neo4j
3. Import GraphML into Neo4j
4. Update config to use Neo4j backend
5. Restart with Neo4j adapter

```python
# Future: Neo4j adapter with same interface
class Neo4jAdapter(GraphBackend):
    """Neo4j implementation of GraphBackend interface"""
    def add_node(self, node: Node) -> str:
        # Use Neo4j Python driver
        pass
```

## Extensibility Points

### Custom Node Types
```python
# users can define custom node types
class CustomNode(Node):
    type = "my_custom_type"
    custom_field: str
```

### Custom Edge Types
```python
class CustomEdge(Edge):
    type = "my_custom_relation"
```

### Custom Query Types
```python
class CustomQuery(Query):
    type = "my_custom_query"
```

### Plugins
```python
# Future plugin system
class MemLayerPlugin:
    def on_node_created(self, node: Node):
        pass

    def on_query_executed(self, query: Query, result: QueryResult):
        pass
```

## Conclusion

This architecture provides:

- ✅ Clear separation of concerns
- ✅ Testable components
- ✅ Extensibility points
- ✅ Performance optimization opportunities
- ✅ Migration path for scaling
- ✅ Multiple interface support

The design is intentionally simple for Phase 1, with clear paths to add complexity in later phases.
