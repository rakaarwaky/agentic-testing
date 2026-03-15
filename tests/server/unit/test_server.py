import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_mcp_initialization():
    """Test that the FastMCP server can be initialized."""
    mcp = FastMCP("agentic-testing-test")
    assert mcp.name == "agentic-testing-test"


@pytest.mark.asyncio
async def test_tool_registration():
    """Test that tools are registered correctly."""
    from src.surfaces.mcp.tools import register_tools
    from src.bootstrap.container import Container

    mcp = FastMCP("agentic-testing-test")

    # Use real container or mock
    container = Container()

    register_tools(mcp, container)
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "test_run" in tool_names
    assert "test_analyze" in tool_names
    assert "test_audit" in tool_names
    assert "test_generate_data" in tool_names
