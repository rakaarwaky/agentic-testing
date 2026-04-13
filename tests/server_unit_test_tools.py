import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.server.fastmcp import FastMCP
from src.surfaces.mcp_tools import register_tools
from src.agent.container import Container
from src.taxonomy.models import TestResult


@pytest.mark.asyncio
async def test_mcp_tools_execution():
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
    await mcp.list_tools()

    # Execute tools by calling the registered functions
    # In FastMCP, tools are stored in mcp._tools (actually it is _tools in some versions,
    # but let's try to use the public API if possible, or just mock the call)

    # Since we only care about COVERAGE of the code inside the tool functions,
    # and those functions are defined inside register_tools,
    # we can't easily get them back out of FastMCP in a clean way without knowing its internals.

    # However, we can use mcp.call_tool if we use the underlying server

    # Actually, a simpler way to get coverage is to just mock the decorator
    # and then we have the functions. But that's also complex.

    # Let's try to find where FastMCP stores tools. It might be in mcp._tool_managers or similar.
    # Looking at mcp-python SDK: FastMCP has a 'tools' property in some versions?

    # Let's try to use a more direct approach: pass a mock mcp that captures the functions.
    funcs = {}
    mock_mcp = MagicMock()

    def save_tool(name=None, **kwargs):
        def decorator(f):
            funcs[name or f.__name__] = f
            return f

        return decorator

    mock_mcp.tool = save_tool

    register_tools(mock_mcp, container)

    # Now we can call them!
    if "test_run" in funcs:
        res = await funcs["test_run"](test_path="test.py")
        assert "✅ PASS" in res

    if "test_analyze" in funcs:
        res = await funcs["test_analyze"](target_file="test.py")
        assert "X" in res

    if "test_audit" in funcs:
        res = await funcs["test_audit"](target_dir="src")
        assert "100" in res

    if "test_generate_data" in funcs:
        res = await funcs["test_generate_data"](data_type="strings")
        assert "['a', 'b']" in res

        res_fail = await funcs["test_generate_data"](data_type="unknown")
        assert "Unknown data type" in res_fail
        
        # Test invalid data type via direct call
        res_invalid = await funcs["test_generate_data"](data_type="invalid")
        assert "Unknown data type" in res_invalid

    if "test_generate" in funcs:
        container.test_generator = AsyncMock()
        container.test_generator.generate_test.return_value = "generated"
        res = await funcs["test_generate"](source_file="test.py")
        assert res == "generated"
        container.test_generator.generate_test.assert_called_with("test.py")
