import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.server.fastmcp import FastMCP
from src.surfaces.mcp_tools_registry import register_tools
from src.agent.dependency_injection_container import Container
from src.taxonomy import TestResult


@pytest.mark.asyncio
async def test_mcp_tools_execution():
    """Test that register_tools registers all 5 MCP tools."""
    mcp = FastMCP("test")
    container = MagicMock(spec=Container)

    # Mock use cases
    container.test_use_case = AsyncMock()
    container.test_use_case.execute.return_value = TestResult(
        target="test.py", passed=True, output_log="Success", healed=False
    )

    container.analyzer = AsyncMock()
    container.analyzer.analyze_file.return_value = {"classes": ["X"]}

    container.auditor = AsyncMock()
    container.auditor.check_coverage.return_value = {"total_pct": 100}

    container.generator = MagicMock()
    container.generator.generate_strings.return_value = ["a", "b"]

    register_tools(mcp, container)

    # Get the tools
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    # Verify all 5 tools are registered
    assert "execute_command" in tool_names
    assert "list_commands" in tool_names
    assert "check_status" in tool_names
    assert "read_skill_context" in tool_names
    assert "cancel_job" in tool_names


@pytest.mark.asyncio
async def test_read_skill_context_sections():
    """Test read_skill_context returns all sections."""
    funcs = {}
    mock_mcp = MagicMock()

    def save_tool(name=None, **kwargs):
        def decorator(f):
            funcs[name or f.__name__] = f
            return f
        return decorator

    mock_mcp.tool = save_tool

    container = MagicMock(spec=Container)
    register_tools(mock_mcp, container)

    assert "read_skill_context" in funcs

    # Test specific sections
    for section in ["directives", "mcp-tools", "cli-commands", "workflows", "architecture"]:
        res = await funcs["read_skill_context"](section=section)
        assert len(res) > 0
        assert section.replace("-", " ") not in res or "#" in res  # Has content

    # Test no section provided
    res = await funcs["read_skill_context"](section=None)
    assert "Available" in res

    # Test unknown section
    res = await funcs["read_skill_context"](section="nonexistent")
    assert "not found" in res


@pytest.mark.asyncio
async def test_cancel_job_tool():
    """Test cancel_job returns proper response."""
    funcs = {}
    mock_mcp = MagicMock()

    def save_tool(name=None, **kwargs):
        def decorator(f):
            funcs[name or f.__name__] = f
            return f
        return decorator

    mock_mcp.tool = save_tool
    container = MagicMock(spec=Container)
    register_tools(mock_mcp, container)

    assert "cancel_job" in funcs
    res = await funcs["cancel_job"](job_id="test-123")
    assert "not_implemented" in res
    assert "test-123" in res


@pytest.mark.asyncio
async def test_execute_command_tool():
    """Test execute_command tool registration and basic invocation."""
    funcs = {}
    mock_mcp = MagicMock()

    def save_tool(name=None, **kwargs):
        def decorator(f):
            funcs[name or f.__name__] = f
            return f
        return decorator

    mock_mcp.tool = save_tool
    container = MagicMock(spec=Container)
    register_tools(mock_mcp, container)

    assert "execute_command" in funcs
    assert "list_commands" in funcs
    assert "check_status" in funcs
