"""
Basic MCP Client — connects to server.py via stdio, then uses Azure OpenAI
to decide which tools to call based on a user query.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AzureOpenAI

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-5.4")


def mcp_tools_to_openai_schema(tools) -> list[dict]:
    """Convert MCP tool list to OpenAI function-calling schema."""
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        })
    return openai_tools


async def run(query: str):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "server.py")],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Discover available tools from the MCP server
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"\n[MCP] Tools available: {[t.name for t in tools]}")

            openai_tools = mcp_tools_to_openai_schema(tools)

            # 2. Send user query to Azure OpenAI with tools attached
            messages = [{"role": "user", "content": query}]
            print(f"[User] {query}")

            response = client.chat.completions.create(
                model=DEPLOYMENT,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            # 3. If the model wants to call a tool, execute it via MCP
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    tool_args = json.loads(tc.function.arguments)
                    print(f"[LLM] Calling tool '{tool_name}' with args {tool_args}")

                    result = await session.call_tool(tool_name, tool_args)
                    tool_output = result.content[0].text
                    print(f"[MCP] Tool result: {tool_output}")

                    # 4. Send tool result back to get final answer
                    messages.append(msg)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_output,
                    })

                final = client.chat.completions.create(
                    model=DEPLOYMENT,
                    messages=messages,
                )
                answer = final.choices[0].message.content
            else:
                answer = msg.content

            print(f"\n[Assistant] {answer}\n")


if __name__ == "__main__":
    print("MCP Client ready. Type your query (or 'exit' to quit).")
    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not query or query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print("=" * 60)
        asyncio.run(run(query))
