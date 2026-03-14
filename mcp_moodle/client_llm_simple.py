"""
Simple MCP Client with Local LLM (Ollama) - No Moodle login required
--------------------------------------------------------------------
Flow:
  1. Connect to MCP server (stdio subprocess)
  2. Load available tools from the server
  3. User types a prompt
  4. Send prompt + tools to Ollama
  5. If LLM wants to call a tool → execute it on the MCP server
  6. Send tool result back to LLM → get final answer
  7. Print the answer, repeat

Requirements:
  - Ollama installed and running  (https://ollama.com/download)
  - Model pulled: ollama pull llama3.2
"""

import asyncio
import json
import sys
import os

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Config ────────────────────────────────────────────────────────────────────
SERVER_SCRIPT    = os.path.join(os.path.dirname(__file__), "server.py")
PYTHON_EXECUTABLE = sys.executable
OLLAMA_MODEL     = "llama3.2"   # change to e.g. "qwen2.5:3b" if preferred
# ──────────────────────────────────────────────────────────────────────────────


def mcp_tools_to_ollama_format(mcp_tools) -> list[dict]:
    """Convert MCP tool definitions to the format Ollama expects."""
    ollama_tools = []
    for tool in mcp_tools:
        ollama_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema if tool.inputSchema else {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        })
    return ollama_tools


async def run_agent_loop(
    session: ClientSession,
    tools_list,
    ollama_tools: list[dict],
):
    """Interactive loop: user prompt → LLM → (optional tool call) → answer."""

    print("\nType your prompt and press Enter. Type 'quit' to exit.")
    print("Example: 'What is 5 + 3?' or 'What's the date today?'\n")

    while True:
        # ── Get user input ──────────────────────────────────────────────────
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # ── Build conversation messages ─────────────────────────────────────
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to tools.\n"
                    "Use the available tools to answer user questions.\n"
                    "When the user asks about the date or time, use get_current_date.\n"
                    "Present answers clearly and in a readable format."
                ),
            },
            {"role": "user", "content": user_input},
        ]

        print(f"\n[Thinking...]\n")

        # ── Agentic tool-calling loop ───────────────────────────────────────
        while True:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=ollama_tools,
            )

            assistant_message = response.message

            # Add assistant reply to conversation history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in (assistant_message.tool_calls or [])
                ],
            })

            # If no tool calls → final answer, break
            if not assistant_message.tool_calls:
                break

            # ── Execute each requested tool call via MCP server ────────────
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments  # already a dict

                print(f"[Tool call] {tool_name}({json.dumps(tool_args)})")

                # Call the tool on the MCP server
                tool_result = await session.call_tool(tool_name, tool_args)
                result_text = tool_result.content[0].text if tool_result.content else ""

                print(f"[Tool result] {result_text}\n")

                # Add tool result to conversation so LLM can use it
                messages.append({
                    "role": "tool",
                    "content": result_text,
                })

        # ── Print final LLM answer ──────────────────────────────────────────
        final_answer = assistant_message.content or "(no response)"
        print(f"Assistant: {final_answer}\n")
        print("-" * 60)


async def main():
    print("=" * 60)
    print(f"  MCP + Ollama Client  |  model: {OLLAMA_MODEL}")
    print("=" * 60)

    # ── Verify Ollama is reachable ──────────────────────────────────────────
    try:
        models = ollama.list()
        available = [m.model for m in models.models]
        if not any(OLLAMA_MODEL in m for m in available):
            print(f"\n[WARNING] Model '{OLLAMA_MODEL}' not found locally.")
            print(f"  Run:  ollama pull {OLLAMA_MODEL}\n")
        else:
            print(f"\n[OK] Model '{OLLAMA_MODEL}' is available.\n")
    except Exception:
        print("\n[ERROR] Cannot reach Ollama. Is it running?")
        print("  Start it with:  ollama serve\n")
        return

    print("-" * 60)

    # ── Connect to MCP server ───────────────────────────────────────────────
    server_params = StdioServerParameters(
        command=PYTHON_EXECUTABLE,
        args=[SERVER_SCRIPT, "stdio"],
        env=None,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            # Load tools from MCP server
            tools_response = await session.list_tools()
            tools_list     = tools_response.tools
            ollama_tools   = mcp_tools_to_ollama_format(tools_list)

            print(f"\n[MCP Server connected]  Tools: {[t.name for t in tools_list]}\n")

            # Start the interactive loop
            await run_agent_loop(
                session,
                tools_list,
                ollama_tools,
            )


if __name__ == "__main__":
    asyncio.run(main())
