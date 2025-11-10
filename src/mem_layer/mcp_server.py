"""MCP server for Mem-Layer - Provides AI models with persistent graph-based memory."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pathlib import Path
from typing import Any
import json

from mem_layer import MemoryAPI, NodeType, EdgeType
from mem_layer.exceptions import MemLayerException

# Initialize MCP server
app = Server("mem-layer")

# Global API instance (will be initialized per scope)
_api_cache: dict[str, MemoryAPI] = {}


def get_api(scope: str | None = None) -> MemoryAPI:
    """Get or create MemoryAPI instance for scope."""
    scope_key = scope or "default"
    if scope_key not in _api_cache:
        _api_cache[scope_key] = MemoryAPI(scope=scope)
    return _api_cache[scope_key]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available memory tools."""
    return [
        Tool(
            name="add_memory",
            description="Store a new memory (entity, note, event, decision, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["entity", "note", "event", "decision", "concept", "code_ref"],
                        "description": "Type of memory to store"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content/description of the memory"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to categorize the memory"
                    },
                    "importance": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Importance score (0.0 to 1.0)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata as key-value pairs"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Memory scope (user, project, personal)"
                    }
                },
                "required": ["type", "content"]
            }
        ),
        Tool(
            name="query_memory",
            description="Query memories using pattern matching (e.g., 'type:entity AND tags:important')",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Query pattern (e.g., 'type:entity', 'tags:security', 'importance:>0.8')"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Scope to query"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="search_memory",
            description="Full-text search across all memory content",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to search for"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Scope to search in"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_memory",
            description="Retrieve a specific memory by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "ID of the memory to retrieve"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Scope containing the memory"
                    }
                },
                "required": ["node_id"]
            }
        ),
        Tool(
            name="relate_memories",
            description="Create a relationship between two memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Source memory ID"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target memory ID"
                    },
                    "relation_type": {
                        "type": "string",
                        "enum": ["relates_to", "depends_on", "references", "causes", "part_of", "uses"],
                        "description": "Type of relationship"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Memory scope"
                    }
                },
                "required": ["source_id", "target_id", "relation_type"]
            }
        ),
        Tool(
            name="traverse_memory",
            description="Traverse the memory graph from a starting point",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_id": {
                        "type": "string",
                        "description": "Starting memory ID"
                    },
                    "max_depth": {
                        "type": "number",
                        "description": "Maximum traversal depth"
                    },
                    "scope": {
                        "type": "string",
                        "description": "Memory scope"
                    }
                },
                "required": ["start_id"]
            }
        ),
        Tool(
            name="get_memory_stats",
            description="Get statistics about the memory graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "description": "Scope to get stats for"
                    }
                }
            }
        ),
        Tool(
            name="list_scopes",
            description="List all available memory scopes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_scope",
            description="Create a new memory scope",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Scope name"
                    },
                    "scope_type": {
                        "type": "string",
                        "enum": ["user", "project", "code", "personal"],
                        "description": "Type of scope"
                    }
                },
                "required": ["name", "scope_type"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI models."""

    try:
        scope = arguments.get("scope")
        api = get_api(scope)

        if name == "add_memory":
            # Add a new memory
            node_type = NodeType(arguments["type"])
            content = arguments["content"]
            tags = arguments.get("tags", [])
            importance = arguments.get("importance", 0.5)
            metadata = arguments.get("metadata", {})

            node = api.create_node(
                type=node_type,
                content=content,
                tags=tags,
                importance=importance,
                metadata=metadata,
                created_by="mcp_client"
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "node_id": node.id,
                    "type": node.type.value,
                    "content": node.content,
                    "tags": node.tags,
                    "importance": node.importance,
                    "message": f"Memory stored successfully: {node.id[:8]}"
                }, indent=2)
            )]

        elif name == "query_memory":
            # Query memories
            pattern = arguments["pattern"]
            limit = arguments.get("limit", 20)

            result = api.query(pattern, limit=limit)

            # Compact memory responses for efficiency (per CAMEL-AI best practices)
            memories = []
            for node in result.nodes:
                # Truncate content if too long to keep responses lean
                content = node.content
                if len(content) > 200:
                    content = content[:197] + "..."

                memories.append({
                    "id": node.id[:12],  # Shortened ID for efficiency
                    "type": node.type.value,
                    "content": content,
                    "tags": node.tags[:5],  # Limit tags to reduce noise
                    "importance": round(node.importance, 2)
                })

            # Summary-style response
            summary = f"Found {len(memories)} memories"
            if result.total_count > len(memories):
                summary += f" (showing {len(memories)} of {result.total_count} total)"

            return [TextContent(
                type="text",
                text=json.dumps({
                    "summary": summary,
                    "count": len(memories),
                    "memories": memories
                }, indent=2)
            )]

        elif name == "search_memory":
            # Full-text search
            text = arguments["text"]
            limit = arguments.get("limit", 20)

            result = api.search(text, limit=limit)

            # Compact search results
            memories = []
            for node in result.nodes:
                content = node.content[:200] if len(node.content) > 200 else node.content
                memories.append({
                    "id": node.id[:12],
                    "type": node.type.value,
                    "content": content,
                    "tags": node.tags[:3],
                    "importance": round(node.importance, 2)
                })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "summary": f"Found {len(memories)} results for '{text}'",
                    "count": len(memories),
                    "memories": memories
                }, indent=2)
            )]

        elif name == "get_memory":
            # Get specific memory
            node_id = arguments["node_id"]
            node = api.get_node(node_id)

            # Get relationships
            edges = api.get_edges(node_id)
            relationships = []
            for edge in edges:
                relationships.append({
                    "type": edge.type.value,
                    "direction": "outgoing" if edge.source_id == node_id else "incoming",
                    "other_id": edge.target_id if edge.source_id == node_id else edge.source_id,
                    "weight": edge.weight
                })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "memory": {
                        "id": node.id,
                        "type": node.type.value,
                        "content": node.content,
                        "tags": node.tags,
                        "importance": node.importance,
                        "metadata": node.metadata,
                        "created_at": node.created_at.isoformat(),
                        "updated_at": node.updated_at.isoformat(),
                        "created_by": node.created_by,
                        "access_count": node.access_count
                    },
                    "relationships": relationships
                }, indent=2)
            )]

        elif name == "relate_memories":
            # Create relationship
            source_id = arguments["source_id"]
            target_id = arguments["target_id"]
            relation_type = arguments["relation_type"]

            edge = api.relate(source_id, target_id, relation_type)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "edge_id": edge.id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "type": relation_type,
                    "message": f"Relationship created: {relation_type}"
                }, indent=2)
            )]

        elif name == "traverse_memory":
            # Traverse graph
            start_id = arguments["start_id"]
            max_depth = arguments.get("max_depth", 2)

            result = api.traverse(start_id, max_depth=max_depth)

            memories = []
            for node in result.nodes:
                memories.append({
                    "id": node.id,
                    "type": node.type.value,
                    "content": node.content,
                    "tags": node.tags
                })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "start_id": start_id,
                    "depth": max_depth,
                    "nodes_found": len(memories),
                    "memories": memories
                }, indent=2)
            )]

        elif name == "get_memory_stats":
            # Get statistics
            stats = api.get_stats()

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "stats": {
                        "total_memories": stats["node_count"],
                        "total_relationships": stats["edge_count"],
                        "average_connections": stats["average_degree"],
                        "memory_types": stats["node_types"],
                        "relationship_types": stats["edge_types"],
                        "most_connected": stats["most_connected"][:5]
                    }
                }, indent=2)
            )]

        elif name == "list_scopes":
            # List all scopes
            scopes = api.list_scopes()

            scope_list = []
            for scope_obj in scopes:
                scope_list.append({
                    "id": scope_obj.id,
                    "name": scope_obj.name,
                    "type": scope_obj.type.value,
                    "path": str(scope_obj.path)
                })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(scope_list),
                    "scopes": scope_list
                }, indent=2)
            )]

        elif name == "create_scope":
            # Create new scope
            name = arguments["name"]
            scope_type = arguments["scope_type"]

            new_scope = api.create_scope(name, scope_type)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "scope": {
                        "id": new_scope.id,
                        "name": new_scope.name,
                        "type": new_scope.type.value,
                        "path": str(new_scope.path)
                    },
                    "message": f"Scope '{name}' created successfully"
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }, indent=2)
            )]

    except MemLayerException as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "error_type": e.__class__.__name__
            }, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError"
            }, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
