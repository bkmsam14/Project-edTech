"""
MCP Client — stdio transport
The client spawns server.py as a subprocess and communicates via stdin/stdout.
"""

import asyncio
import sys
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")

# Use the venv Python so that 'mcp' package is available
PYTHON_EXECUTABLE = sys.executable  # same Python running this client


async def main():
    print("=" * 50)
    print("MCP Client (stdio transport)")
    print("=" * 50)

    # Define how to launch the server as a subprocess
    server_params = StdioServerParameters(
        command=PYTHON_EXECUTABLE,
        args=[SERVER_SCRIPT, "stdio"],
        env=None,  # inherit current environment
    )

    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # Initialize the connection
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
            result = await session.call_tool("hello", {"name": "Alice"})
            print(f"hello('Alice') => {result.content[0].text}")

            # --- Call tool: add ---
            result = await session.call_tool("add", {"a": 7, "b": 3})
            print(f"add(7, 3)      => {result.content[0].text}")

            # --- Call tool: reverse_string ---
            result = await session.call_tool("reverse_string", {"text": "MCP is awesome"})
            print(f"reverse_string => {result.content[0].text}")

            # --- Read a resource ---
            print("\n" + "-" * 50)
            print("Reading resource...\n")
            resource_result = await session.read_resource("info://server")
            print(f"info://server  => {resource_result.contents[0].text}")

            print("\n" + "=" * 50)
            print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
