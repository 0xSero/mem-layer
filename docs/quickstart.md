# Quickstart Guide

Get started with Mem-Layer in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/0xSero/mem-layer.git
cd mem-layer

# Install in development mode
pip install -e .

# Verify installation
mem-layer --version
```

## Initialize a Project

```bash
# Initialize a project scope in current directory
mem-layer init --scope project

# Or initialize a user scope
mem-layer init --scope user --name my-user

# Check scope info
mem-layer scope info
```

## Basic Operations

### Adding Memories

```bash
# Add an entity
mem-layer add entity "User authentication module" --tags auth,security --importance 0.9

# Add a note
mem-layer add note "Review the caching strategy" --priority high --tags performance

# Add a decision (architectural decision record)
mem-layer add entity "Use PostgreSQL for primary database" --tags database,decision
```

### Creating Relationships

First, add two entities and note their IDs:

```bash
# Add entities
mem-layer add entity "API Gateway"
# Output: Created entity: abc12345

mem-layer add entity "User Service"
# Output: Created entity: def67890

# Create a relationship
mem-layer relate abc12345 def67890 --type depends_on
```

### Querying

```bash
# Pattern matching
mem-layer query "type:entity"
mem-layer query "tags:security"
mem-layer query "importance:>0.8"

# Combine conditions with AND
mem-layer query "type:entity AND tags:auth"

# Full-text search
mem-layer search "authentication"
mem-layer search "database cache"

# List all nodes
mem-layer list

# List specific type
mem-layer list --type note

# Show node details
mem-layer show abc12345

# Traverse from a node
mem-layer traverse abc12345 --depth 2
```

### Graph Operations

```bash
# View statistics
mem-layer graph stats

# Export graph
mem-layer graph export backup.json --format json
mem-layer graph export diagram.dot --format dot

# Import graph
mem-layer graph import backup.json --format json
```

## Using the Python API

```python
from mem_layer import MemoryAPI, NodeType, EdgeType

# Initialize
api = MemoryAPI(scope="my-project")

# Create nodes
node1 = api.create_node(
    type=NodeType.ENTITY,
    content="FastAPI server",
    tags=["api", "backend"],
    importance=0.8
)

node2 = api.create_node(
    type=NodeType.ENTITY,
    content="PostgreSQL database",
    tags=["database"],
    importance=0.9
)

# Create relationship
edge = api.create_edge(
    source_id=node1.id,
    target_id=node2.id,
    type=EdgeType.DEPENDS_ON,
    weight=0.9
)

# Query
result = api.query("type:entity AND importance:>0.8")
for node in result.nodes:
    print(f"{node.content} - Importance: {node.importance}")

# Search
result = api.search("database")
for node in result.nodes:
    print(node.content)

# Traverse
result = api.traverse(node1.id, max_depth=2)
print(f"Found {len(result.nodes)} connected nodes")

# Save
api.save()
```

## Scope Management

```bash
# List all scopes
mem-layer scope list

# Create a new scope
mem-layer scope create my-feature --type project

# Switch to a scope
mem-layer scope switch my-feature

# View current scope
mem-layer scope info

# Create different scope types
mem-layer scope create personal-notes --type personal
mem-layer scope create user-prefs --type user
```

## Working with Multiple Scopes

```python
from mem_layer import MemoryAPI

# Work in project scope
api_project = MemoryAPI(scope="my-project")
api_project.add_entity("Project-specific knowledge")

# Work in personal scope
api_personal = MemoryAPI(scope="personal-notes")
api_personal.add_note("Personal learning note")

# Switch between scopes
api_project.switch_scope("another-project")
```

## Common Patterns

### Architecture Decision Records

```bash
# Document a decision
mem-layer add entity "Use Redis for session cache" \
    --tags decision,architecture,caching \
    --importance 0.9

# Link to related entities
mem-layer add entity "Session management system" --tags auth
# Get IDs from output, then relate them
mem-layer relate <decision-id> <session-system-id> --type influences
```

### Code Documentation

```python
api = MemoryAPI(scope="code-memory")

# Document a function
func_node = api.create_node(
    type=NodeType.CODE_REF,
    content="authenticate_user(username, password)",
    metadata={
        "file": "auth/handlers.py",
        "line": 45,
        "purpose": "Validates user credentials and returns JWT token"
    },
    tags=["function", "auth"]
)

# Add related notes
note = api.add_note(
    "This function should be refactored to use async/await",
    tags=["refactoring", "async"]
)

api.relate(note.id, func_node.id, "references")
```

### Temporal Queries

```python
from datetime import datetime, timedelta

api = MemoryAPI()

# Create a node with validity period
node = api.create_node(
    type=NodeType.ENTITY,
    content="API v1 endpoints",
    valid_from=datetime(2024, 1, 1),
    valid_until=datetime(2024, 12, 31)
)

# Query what was valid at a specific time
past = datetime(2024, 6, 1)
result = api.query_at_time(past)
```

## Tips

1. **Use Tags Liberally**: Tags make it easy to find related nodes later
2. **Set Importance**: Important nodes are easier to find and won't be consolidated
3. **Create Relationships**: Links between nodes make traversal powerful
4. **Use Scopes**: Separate concerns (project, personal, code) for better organization
5. **Export Regularly**: Backup your memory graphs
6. **Descriptive Content**: Make node content searchable and understandable

## Next Steps

- Read the full [Documentation](../README.md)
- Check out [Examples](../examples/)
- Learn about the [Architecture](../ARCHITECTURE.md)
- Explore [Advanced Features](advanced.md)

## Troubleshooting

### "No active scope" error

Make sure you've initialized a scope or specify one:

```bash
mem-layer init --scope project
# or
mem-layer add entity "..." --scope my-scope
```

### Can't find nodes after restart

Data is persisted in `.mem-layer/memory.db`. Make sure you're in the same directory or specify the scope.

### Performance issues with large graphs

Consider:
- Using more specific queries
- Limiting result counts
- Exporting old data and starting fresh
- Migrating to Neo4j for very large graphs (10K+ nodes)
