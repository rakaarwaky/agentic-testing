"""Tests for DesktopCommander delegation clients."""

import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# ── desktop_commander_delegation_client tests ──


@pytest.mark.asyncio
async def test_delegation_blocks_dangerous_commands():
    """Blocked commands return blocked=True."""
    from src.infrastructure.desktop_commander_delegation_client import (
        execute_via_desktop_commander,
    )

    for dangerous_cmd in [["sudo", "ls"], ["kill", "-9", "1234"], ["chmod", "777", "/tmp"]]:
        result = await execute_via_desktop_commander(dangerous_cmd)
        assert result["returncode"] == 1
        assert result.get("blocked") is True
        assert "blocked" in result["stderr"]


@pytest.mark.asyncio
async def test_delegation_executes_safe_command():
    """Safe commands are executed via subprocess."""
    from src.infrastructure.desktop_commander_delegation_client import (
        execute_via_desktop_commander,
    )

    result = await execute_via_desktop_commander(["echo", "hello"])
    assert result["returncode"] == 0
    assert "hello" in result["stdout"]
    assert result["executed_by"] == "agentic-testing->desktop-commander-delegation"


@pytest.mark.asyncio
async def test_delegation_empty_command():
    """Empty command list returns error (no blocked key, just error)."""
    from src.infrastructure.desktop_commander_delegation_client import (
        execute_via_desktop_commander,
    )

    result = await execute_via_desktop_commander([])
    assert result["returncode"] == 1
    assert result["stderr"] != ""


@pytest.mark.asyncio
async def test_delegation_timeout():
    """Commands that exceed timeout return code 124."""
    from src.infrastructure.desktop_commander_delegation_client import (
        execute_via_desktop_commander,
    )

    result = await execute_via_desktop_commander(["sleep", "10"], timeout=1)
    assert result["returncode"] == 124
    assert "timed out" in result["stderr"]


@pytest.mark.asyncio
async def test_delegation_working_dir():
    """Commands respect working_dir parameter."""
    from src.infrastructure.desktop_commander_delegation_client import (
        execute_via_desktop_commander,
    )

    result = await execute_via_desktop_commander(["pwd"], working_dir="/tmp")
    assert result["returncode"] == 0
    assert "/tmp" in result["stdout"].strip()


@pytest.mark.asyncio
async def test_is_desktop_commander_available():
    """Check availability based on script path existence."""
    from src.infrastructure.desktop_commander_delegation_client import (
        is_desktop_commander_available,
    )

    # The script may or may not exist, but the function should not raise
    result = await is_desktop_commander_available()
    assert isinstance(result, bool)


# ── desktop_commander_mcp_client tests ──


@pytest.mark.asyncio
async def test_mcp_client_fallback_when_mcp_disabled():
    """When USE_DESKTOP_COMMANDER_MCP=false, falls back to secure adapter."""
    from src.infrastructure.desktop_commander_mcp_client import (
        execute_via_desktop_commander_mcp,
    )

    with patch.dict(os.environ, {"USE_DESKTOP_COMMANDER_MCP": "false"}, clear=False):
        result = await execute_via_desktop_commander_mcp(["echo", "fallback"])
        assert result["returncode"] == 0
        assert "fallback" in result["stdout"]


@pytest.mark.asyncio
async def test_mcp_client_blocked_command_via_fallback():
    """Blocked commands are rejected even in fallback mode."""
    from src.infrastructure.desktop_commander_mcp_client import (
        execute_via_desktop_commander_mcp,
    )

    with patch.dict(os.environ, {"USE_DESKTOP_COMMANDER_MCP": "false"}, clear=False):
        result = await execute_via_desktop_commander_mcp(["sudo", "ls"])
        assert result["returncode"] != 0


@pytest.mark.asyncio
async def test_mcp_client_http_success():
    """When MCP is enabled and server responds 200, return its result."""
    from src.infrastructure.desktop_commander_mcp_client import (
        execute_via_desktop_commander_mcp,
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "stdout": "from-mcp",
        "stderr": "",
        "returncode": 0,
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch.dict(os.environ, {"USE_DESKTOP_COMMANDER_MCP": "true"}, clear=False):
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await execute_via_desktop_commander_mcp(["echo", "test"])
            assert result["returncode"] == 0
            assert result["stdout"] == "from-mcp"
            assert result["executed_by"] == "agentic-testing-via-desktop-commander"


@pytest.mark.asyncio
async def test_mcp_client_http_error_fallback():
    """When MCP server returns non-200, falls back to secure adapter."""
    from src.infrastructure.desktop_commander_mcp_client import (
        execute_via_desktop_commander_mcp,
    )

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch.dict(os.environ, {"USE_DESKTOP_COMMANDER_MCP": "true"}, clear=False):
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await execute_via_desktop_commander_mcp(["echo", "fallback-test"])
            # Falls back to secure adapter which executes echo
            assert result["returncode"] == 0
            assert "fallback-test" in result["stdout"]


@pytest.mark.asyncio
async def test_mcp_client_exception_fallback():
    """When MCP call raises exception, falls back to secure adapter."""
    from src.infrastructure.desktop_commander_mcp_client import (
        execute_via_desktop_commander_mcp,
    )

    with patch.dict(os.environ, {"USE_DESKTOP_COMMANDER_MCP": "true"}, clear=False):
        with patch("httpx.AsyncClient", side_effect=ConnectionError("no server")):
            result = await execute_via_desktop_commander_mcp(["echo", "exc-fallback"])
            assert result["returncode"] == 0
            assert "exc-fallback" in result["stdout"]


@pytest.mark.asyncio
async def test_is_mcp_available_returns_bool():
    """is_desktop_commander_available returns bool without raising."""
    from src.infrastructure.desktop_commander_mcp_client import (
        is_desktop_commander_available,
    )

    result = await is_desktop_commander_available()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_is_mcp_available_success():
    """is_desktop_commander_available returns True when server responds 200 (line 81)."""
    from src.infrastructure.desktop_commander_mcp_client import (
        is_desktop_commander_available,
    )

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    mock_httpx = MagicMock()
    mock_httpx.AsyncClient = MagicMock(return_value=mock_client)

    with patch.dict("sys.modules", {"httpx": mock_httpx}):
        result = await is_desktop_commander_available()
        assert result is True
