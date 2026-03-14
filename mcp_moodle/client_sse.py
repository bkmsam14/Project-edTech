"""
MCP Client — SSE (HTTP) transport
Requires the server to be running separately:
    python server.py sse

Then run this client in a second terminal:
    python client_sse.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client


SERVER_URL = "http://127.0.0.1:8000/sse"


async def main():
    print("=" * 50)
    print("MCP Client (SSE/HTTP transport)")
    print(f"Connecting to: {SERVER_URL}")
    print("=" * 50)

    async with sse_client(SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()
            print("\n[Connected to MCP Server]\n")

            # --- List available tools ---
            tools_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")

            # --- List available resources ---
            resources_response = await session.list_resources()
            print("\nAvailable resources:")
            for resource in resources_response.resources:
                print(f"  - {resource.uri}: {resource.description}")

            print("\n" + "-" * 50)
            print("Calling tools...\n")

            # --- Call tool: hello ---
            result = await session.call_tool("hello", {"name": "Bob"})
            print(f"hello('Bob')   => {result.content[0].text}")

            # --- Call tool: add ---
            result = await session.call_tool("add", {"a": 42, "b": 8})
            print(f"add(42, 8)     => {result.content[0].text}")

            # --- Call tool: reverse_string ---
            result = await session.call_tool("reverse_string", {"text": "Hello MCP"})
            print(f"reverse_string => {result.content[0].text}")

            print("\n" + "=" * 50)
            print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
