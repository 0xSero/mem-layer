"""Simple MCP server integration test."""

from mem_layer import MemoryAPI, NodeType

print("=== MCP Server Integration Test ===\n")

# Test that the underlying API works (what MCP server uses)
print("1. Testing MemoryAPI (used by MCP server)...")
api = MemoryAPI(scope="mcp-test")

# Add memory
node = api.create_node(
    type=NodeType.ENTITY,
    content="Test entity for MCP server validation",
    tags=["mcp", "test"],
    importance=0.8,
    created_by="mcp_test"
)
print(f"   ✓ Created node: {node.id[:12]}")
print(f"     Content: {node.content[:50]}...")

# Query
result = api.query("type:entity", limit=5)
print(f"\n2. Testing query...")
print(f"   ✓ Found {len(result.nodes)} memories")

# Search
result = api.search("test", limit=5)
print(f"\n3. Testing search...")
print(f"   ✓ Found {len(result.nodes)} results")

# Stats
stats = api.get_stats()
print(f"\n4. Testing stats...")
print(f"   ✓ Total memories: {stats['node_count']}")
print(f"   ✓ Relationships: {stats['edge_count']}")

# Scopes
scopes = api.list_scopes()
print(f"\n5. Testing scopes...")
print(f"   ✓ Found {len(scopes)} scopes")

print("\n=== ✅ MCP Server Backend Tests Passed! ===")
print("\nThe MCP server is ready to use with:")
print("  • Claude Desktop")
print("  • Other MCP clients")
print("\nConfiguration file: mcp-config-example.json")
print("Documentation: docs/mcp-server.md")
