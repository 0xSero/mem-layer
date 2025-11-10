# MCP Server for Mem-Layer

Mem-Layer provides an MCP (Model Context Protocol) server that allows AI assistants like Claude Desktop to use graph-based persistent memory.

## What is MCP?

Model Context Protocol (MCP) is Anthropic's standard for connecting AI assistants to external data sources and tools. The mem-layer MCP server exposes memory operations as tools that AI models can call.

## Installation

```bash
# Install mem-layer with MCP support
pip install mem-layer

# Or from source
cd mem-layer
pip install -e .
```

## Configuration for Claude Desktop

### macOS

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mem-layer": {
      "command": "mem-layer-mcp"
    }
  }
}
```

### Windows

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mem-layer": {
      "command": "mem-layer-mcp"
    }
  }
}
```

### Linux

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mem-layer": {
      "command": "mem-layer-mcp"
    }
  }
}
```

## Available Tools

The MCP server provides the following tools to AI models:

### 1. `add_memory`

Store a new memory (entity, note, event, decision, etc.)

**Parameters:**
- `type` (required): "entity", "note", "event", "decision", "concept", or "code_ref"
- `content` (required): The memory content
- `tags` (optional): Array of tags
- `importance` (optional): 0.0 to 1.0
- `metadata` (optional): Additional key-value data
- `scope` (optional): Memory scope

**Example:**
```
add_memory({
  "type": "decision",
  "content": "Use PostgreSQL for primary database",
  "tags": ["database", "architecture"],
  "importance": 0.9
})
```

### 2. `query_memory`

Query memories using pattern matching.

**Parameters:**
- `pattern` (required): Query pattern (e.g., "type:entity AND tags:important")
- `scope` (optional): Scope to query
- `limit` (optional): Maximum results

**Example:**
```
query_memory({
  "pattern": "type:decision AND importance:>0.8"
})
```

**Pattern Syntax:**
- `type:entity` - Filter by type
- `tags:security` - Filter by tag
- `importance:>0.8` - Filter by importance
- `type:entity AND tags:auth` - Combine conditions

### 3. `search_memory`

Full-text search across all memory content.

**Parameters:**
- `text` (required): Search text
- `scope` (optional): Scope to search
- `limit` (optional): Maximum results

**Example:**
```
search_memory({
  "text": "authentication system"
})
```

### 4. `get_memory`

Retrieve a specific memory by ID.

**Parameters:**
- `node_id` (required): Memory ID
- `scope` (optional): Scope

**Example:**
```
get_memory({
  "node_id": "abc123..."
})
```

### 5. `relate_memories`

Create a relationship between two memories.

**Parameters:**
- `source_id` (required): Source memory ID
- `target_id` (required): Target memory ID
- `relation_type` (required): "relates_to", "depends_on", "references", "causes", "part_of", or "uses"
- `scope` (optional): Scope

**Example:**
```
relate_memories({
  "source_id": "abc123...",
  "target_id": "def456...",
  "relation_type": "depends_on"
})
```

### 6. `traverse_memory`

Traverse the memory graph from a starting point.

**Parameters:**
- `start_id` (required): Starting memory ID
- `max_depth` (optional): Maximum depth (default: 2)
- `scope` (optional): Scope

**Example:**
```
traverse_memory({
  "start_id": "abc123...",
  "max_depth": 3
})
```

### 7. `get_memory_stats`

Get statistics about the memory graph.

**Parameters:**
- `scope` (optional): Scope

**Example:**
```
get_memory_stats({})
```

### 8. `list_scopes`

List all available memory scopes.

**Example:**
```
list_scopes({})
```

### 9. `create_scope`

Create a new memory scope.

**Parameters:**
- `name` (required): Scope name
- `scope_type` (required): "user", "project", "code", or "personal"

**Example:**
```
create_scope({
  "name": "my-project",
  "scope_type": "project"
})
```

## Usage Examples

### Example 1: AI Remembering a Decision

```
User: "We decided to use PostgreSQL for the database"

AI uses: add_memory({
  "type": "decision",
  "content": "Use PostgreSQL for primary database - chosen for ACID compliance and JSON support",
  "tags": ["database", "architecture", "postgresql"],
  "importance": 0.9,
  "metadata": {
    "alternatives_considered": ["MySQL", "MongoDB"],
    "decision_date": "2025-01-06"
  }
})

Response: "I've stored that architectural decision in my memory."
```

### Example 2: AI Recalling Past Work

```
User: "What database are we using?"

AI uses: search_memory({
  "text": "database"
})

Finds: "Use PostgreSQL for primary database..."

Response: "Based on our previous decision, we're using PostgreSQL as the primary database."
```

### Example 3: Building Knowledge Graph

```
# Store related memories
add_memory({
  "type": "entity",
  "content": "User Authentication System",
  "tags": ["auth", "security"]
})
→ Returns: node_id: "auth123"

add_memory({
  "type": "entity",
  "content": "PostgreSQL Database",
  "tags": ["database"]
})
→ Returns: node_id: "db456"

# Link them
relate_memories({
  "source_id": "auth123",
  "target_id": "db456",
  "relation_type": "depends_on"
})

# Later, traverse to understand dependencies
traverse_memory({
  "start_id": "auth123",
  "max_depth": 2
})
→ Returns: All connected memories including the database
```

## Memory Efficiency Considerations

To keep memory clean and efficient (as per [CAMEL-AI best practices](https://www.camel-ai.org/blogs/brainwash-your-agent-how-we-keep-the-memory-clean)):

### 1. Compact Responses

MCP tool responses are designed to be concise:
- Only essential information returned
- IDs shortened in summaries (first 8 chars)
- Large metadata not included in lists (only in get_memory)

### 2. Importance Scoring

Use importance to filter noise:
```
# High importance - architecture decisions, critical info
add_memory({..., "importance": 0.9})

# Medium importance - regular work items
add_memory({..., "importance": 0.5})

# Low importance - temporary notes
add_memory({..., "importance": 0.2})

# Query only important items
query_memory({"pattern": "importance:>0.7"})
```

### 3. Periodic Cleanup

```python
# Later feature: Auto-consolidation
# Old, low-importance memories are automatically summarized
# Reduces memory bloat while preserving key information
```

### 4. Scoped Memory

Use scopes to isolate concerns:
- Project scope: Project-specific context
- User scope: Cross-project patterns
- Personal scope: Temporary scratch space

### 5. Limit Result Sizes

Always use `limit` parameter:
```
query_memory({
  "pattern": "type:entity",
  "limit": 10  # Don't return thousands of results
})
```

## Running the MCP Server

### Automatic (via Claude Desktop)

When configured, Claude Desktop automatically starts the server.

### Manual (for testing)

```bash
# Run MCP server directly
mem-layer-mcp

# Or via Python
python -m mem_layer.mcp_server
```

### Testing with MCP Inspector

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector mem-layer-mcp
```

## Troubleshooting

### "Command not found: mem-layer-mcp"

Ensure mem-layer is installed and in your PATH:
```bash
pip install -e .
which mem-layer-mcp
```

### "Connection failed"

Check Claude Desktop logs:
- macOS: `~/Library/Logs/Claude/mcp*.log`
- Windows: `%APPDATA%\Claude\Logs\mcp*.log`

### Memory not persisting

Memories are stored in:
- Project scope: `<project>/.mem-layer/memory.db`
- User scope: `~/.mem-layer/user/<name>/memory.db`
- Personal scope: `~/.mem-layer/personal/<name>/memory.db`

Check these directories exist and are writable.

## Advanced Configuration

### Custom Scope Path

```json
{
  "mcpServers": {
    "mem-layer": {
      "command": "mem-layer-mcp",
      "env": {
        "MEM_LAYER_BASE_PATH": "/custom/path"
      }
    }
  }
}
```

### Multiple Scopes

```json
{
  "mcpServers": {
    "mem-layer-project": {
      "command": "mem-layer-mcp",
      "env": {
        "MEM_LAYER_DEFAULT_SCOPE": "my-project"
      }
    },
    "mem-layer-personal": {
      "command": "mem-layer-mcp",
      "env": {
        "MEM_LAYER_DEFAULT_SCOPE": "personal-notes"
      }
    }
  }
}
```

## Best Practices

1. **Use Descriptive Content**: Make memories searchable
2. **Tag Appropriately**: Use consistent tags across related memories
3. **Set Importance**: High for decisions, medium for regular work, low for temporary
4. **Link Relationships**: Connect related memories with relate_memories
5. **Regular Queries**: Periodically query to refresh context
6. **Scope Isolation**: Use project scope for work, personal for notes

## Security Considerations

- MCP server runs locally with stdio transport
- No network access required
- Memories stored in local SQLite files
- File permissions respect system settings
- No external API calls (unless adding vector embeddings)

## Next Steps

- See [examples/](../examples/) for more usage examples
- Read [Architecture](../ARCHITECTURE.md) for system design
- Check [Contributing](../CONTRIBUTING.md) to extend functionality

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [Memory Efficiency Best Practices](https://www.camel-ai.org/blogs/brainwash-your-agent-how-we-keep-the-memory-clean)
