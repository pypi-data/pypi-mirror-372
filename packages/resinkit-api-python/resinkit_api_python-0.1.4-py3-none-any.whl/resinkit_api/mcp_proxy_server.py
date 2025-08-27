"""
uv run mcp_proxy_server.py
"""

from fastmcp import FastMCP

# Create a proxy to a remote server
server = FastMCP.as_proxy("http://localhost:8603/mcp-server/mcp", name="Resinkit Agent MCP")

if __name__ == "__main__":
    server.run()  # Runs via STDIO for Claude Desktop
