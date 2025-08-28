# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp>=3.12.15",
#     "dateparser>=1.2.2",
#     "fastmcp>=2.11.1",
#     "ujson>=5.10.0",
#     "rock-solid-base>=0.1.11",
# ]
# ///
import inspect
from os import getenv

from fastmcp import FastMCP
import siga_mcp._start
import siga_mcp.tools
from siga_mcp.constants import MCP_TRANSPORT
from siga_mcp.decorators import tool


mcp = FastMCP("My MCP Server", host=getenv("HOST"), port=getenv("PORT"), instructions="Responda sempre em CAPS LOCK")

tools = [
    func
    for name, func in inspect.getmembers(siga_mcp.tools, inspect.isfunction)
    if func.__module__ == siga_mcp.tools.__name__
]

for mcp_tool in tools:
    tool(server=mcp, transport=MCP_TRANSPORT)(mcp_tool)


def main():
    mcp.run(transport=MCP_TRANSPORT)


if __name__ == "__main__":
    main()
