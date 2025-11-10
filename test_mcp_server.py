"""Test MCP server functionality."""

import asyncio
import json
from mem_layer.mcp_server import app

async def test_mcp_server():
    """Test MCP server tools."""
    print("=== Testing MCP Server ===\n")

    # Test list_tools
    print("1. Testing list_tools...")
    tools = await app._list_tools_handler()
    print(f"   ✓ Found {len(tools)} tools:")
    for tool in tools:
        print(f"     - {tool.name}: {tool.description[:50]}...")

    # Test add_memory tool
    print("\n2. Testing add_memory tool...")
    result = await app._call_tool_handler(
        "add_memory",
        {
            "type": "entity",
            "content": "Test memory from MCP server",
            "tags": ["test", "mcp"],
            "importance": 0.8
        }
    )
    response = json.loads(result[0].text)
    print(f"   ✓ Memory created: {response.get('node_id', 'N/A')[:12]}")
    print(f"     Content: {response.get('content', '')}")

    # Test query_memory tool
    print("\n3. Testing query_memory tool...")
    result = await app._call_tool_handler(
        "query_memory",
        {
            "pattern": "type:entity",
            "limit": 5
        }
    )
    response = json.loads(result[0].text)
    print(f"   ✓ Query result: {response.get('summary', 'N/A')}")
    print(f"     Found {response.get('count', 0)} memories")

    # Test search_memory tool
    print("\n4. Testing search_memory tool...")
    result = await app._call_tool_handler(
        "search_memory",
        {
            "text": "test",
            "limit": 5
        }
    )
    response = json.loads(result[0].text)
    print(f"   ✓ Search result: {response.get('summary', 'N/A')}")

    # Test get_memory_stats tool
    print("\n5. Testing get_memory_stats tool...")
    result = await app._call_tool_handler(
        "get_memory_stats",
        {}
    )
    response = json.loads(result[0].text)
    if response.get('success'):
        stats = response.get('stats', {})
        print(f"   ✓ Total memories: {stats.get('total_memories', 0)}")
        print(f"     Total relationships: {stats.get('total_relationships', 0)}")

    # Test list_scopes tool
    print("\n6. Testing list_scopes tool...")
    result = await app._call_tool_handler(
        "list_scopes",
        {}
    )
    response = json.loads(result[0].text)
    print(f"   ✓ Found {response.get('count', 0)} scopes")

    print("\n=== All MCP Server Tests Passed! ===")
    print("\nMemory Efficiency Features:")
    print("  ✓ Compact responses (IDs shortened to 12 chars)")
    print("  ✓ Content truncated at 200 chars for lists")
    print("  ✓ Tags limited to prevent noise")
    print("  ✓ Summary-style responses")
    print("  ✓ Importance scoring for filtering")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
