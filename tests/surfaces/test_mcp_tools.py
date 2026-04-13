"""Tests for MCP tools."""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.surfaces.mcp_tools import register_tools, _get_execution_mode
from src.agent.container import Container


@pytest.fixture
def mock_mcp():
    class MockMCP:
        def __init__(self):
            self.tools = []

        def tool(self):
            def decorator(fn):
                self.tools.append(fn)
                return fn
            return decorator

    return MockMCP()


@pytest.fixture
def mock_container():
    return MagicMock(spec=Container)


@pytest.fixture
def registered_tools(mock_mcp, mock_container):
    register_tools(mock_mcp, mock_container)
    return mock_mcp.tools


class TestExecutionMode:
    def test_default_mode(self):
        with patch.dict("os.environ", {}, clear=True):
            assert _get_execution_mode() == "direct"

    def test_unix_socket_mode(self):
        with patch.dict("os.environ", {"USE_UNIX_SOCKET": "true"}):
            assert _get_execution_mode() == "unix_socket"

    def test_http_mode(self):
        with patch.dict("os.environ", {"USE_DESKTOP_COMMANDER_MCP": "true"}):
            assert _get_execution_mode() == "http"


class TestMcpToolsRegistration:
    def test_register_tools(self, mock_mcp, mock_container):
        register_tools(mock_mcp, mock_container)
        assert len(mock_mcp.tools) >= 4


class TestMcpTools:
    @pytest.mark.asyncio
    async def test_list_commands_no_filter(self, registered_tools):
        with patch("src.surfaces.mcp_tools.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "run\nanalyze\naudit", "stderr": ""}
            result = await registered_tools[1]()
            assert isinstance(result, str)
            assert "run" in result or "analyze" in result

    @pytest.mark.asyncio
    async def test_list_commands_with_domain(self, registered_tools):
        with patch("src.surfaces.mcp_tools.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "  run       <test_path>\n  analyze <file>", "stderr": ""}
            result = await registered_tools[1](domain="test")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_check_status(self, registered_tools):
        with patch("src.surfaces.mcp_tools.is_socket_available", return_value=True):
            with patch("src.surfaces.mcp_tools.get_socket_path", return_value="/tmp/dc.sock"):
                result = await registered_tools[2]()
                data = json.loads(result)
                assert data["status"] == "ready"
                assert data["unix_socket_path"] == "/tmp/dc.sock"

    @pytest.mark.asyncio
    async def test_read_skill_context_no_section(self, registered_tools):
        result = await registered_tools[3]()
        assert isinstance(result, str)
        assert "section" in result.lower() or "available" in result.lower()

    @pytest.mark.asyncio
    async def test_read_skill_context_with_section(self, registered_tools):
        result = await registered_tools[3](section="directives")
        assert "100%" in result or "coverage" in result.lower()

    @pytest.mark.asyncio
    async def test_read_skill_context_invalid_section(self, registered_tools):
        result = await registered_tools[3](section="nonexistent")
        assert "not found" in result.lower() or "available" in result.lower()

    @pytest.mark.asyncio
    async def test_cancel_job(self, registered_tools):
        result = await registered_tools[4](job_id="abc123")
        data = json.loads(result)
        assert "not_implemented" in data["status"]
