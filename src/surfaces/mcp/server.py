from mcp.server.fastmcp import FastMCP
from .tools import register_tools
from ...bootstrap.container import get_container


def main():
    """Main entry point for Agentic Testing (AES Structure)."""
    mcp = FastMCP("Agentic Testing (AES)")
    container = get_container()

    # Register tools
    register_tools(mcp, container)

    # Run server
    mcp.run()


if __name__ == "__main__":
    main()
