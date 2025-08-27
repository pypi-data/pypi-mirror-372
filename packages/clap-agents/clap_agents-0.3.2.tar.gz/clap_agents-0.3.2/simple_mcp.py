

from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers."""
    print(f"[MCP Server] Received add request: {a} + {b}")
    result = a + b
    print(f"[MCP Server] Returning result: {result}")
    return result

if __name__ == "__main__":
    print("Starting minimal MCP server on http://localhost:8000/sse")
    
    mcp.run(transport='sse')

