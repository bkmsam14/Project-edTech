"""
MCP Client with Local LLM (Ollama)
------------------------------------
Flow:
  1. Connect to MCP server (stdio subprocess)
  2. Load available tools from the server
  3. User types a prompt
  4. Send prompt + tools to Ollama (llama3.2)
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
from moodle_login import get_session_cookie

# ── Config ────────────────────────────────────────────────────────────────────
SERVER_SCRIPT    = os.path.join(os.path.dirname(__file__), "server.py")
PYTHON_EXECUTABLE = sys.executable
OLLAMA_MODEL     = "qwen2.5:3b"   # change to e.g. "qwen2.5:3b" if preferred
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
    moodle_token: str,
):
    """Interactive loop: user prompt → LLM → (optional tool call) → answer."""

    print("\nType your prompt and press Enter. Type 'quit' to exit.")
    print("Example: 'What are my grades?' or 'Show my enrolled courses'\n")

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
        # Token injected into system prompt so LLM passes it to every moodle_* call.
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to tools.\n\n"
                    f"The user's Moodle session cookie is: {moodle_token}\n\n"
                    "Rules:\n"
                    "- Always pass this exact token to every moodle_* tool call.\n"
                    "- To show grades for all courses: first call moodle_get_courses to "
                    "get course IDs, then call moodle_get_grades for each course ID.\n"
                    "- When the user asks about the date or time, use get_current_date.\n"
                    "- Present grades clearly and in a readable format."
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

    # ── Ask for credentials and auto-login ─────────────────────────────────
    print("-" * 60)
    print("  Enter your Moodle credentials")
    print("-" * 60)
    moodle_email    = input("  Email   : ").strip()
    moodle_password = input("  Password: ").strip()

    if not moodle_email or not moodle_password:
        print("\n[ERROR] Email and password cannot be empty.")
        return

    print("\n[Logging in to Moodle...] A browser window will open briefly.")
    try:
        moodle_token = get_session_cookie(moodle_email, moodle_password)
        print("[Login successful]\n")
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
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

            # Start the interactive loop with the user's credentials
            await run_agent_loop(
                session,
                tools_list,
                ollama_tools,
                moodle_token,
            )


if __name__ == "__main__":
    asyncio.run(main())
