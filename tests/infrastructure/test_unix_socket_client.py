"""Tests for Unix socket client."""
import os
import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.unix_socket_client import (
    execute_via_unix_socket,
    is_socket_available,
    get_socket_path,
)


class TestSocketHelpers:
    def test_get_socket_path_default(self):
        with patch.dict("os.environ", {}, clear=True):
            path = get_socket_path()
            assert path == "/tmp/dc.sock"

    def test_get_socket_path_env_override(self):
        with patch.dict("os.environ", {"DC_SOCKET_PATH": "/custom.sock"}):
            path = get_socket_path()
            assert path == "/custom.sock"

    @pytest.mark.asyncio
    async def test_socket_not_available(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("os.path.exists", return_value=False):
                available = await is_socket_available()
                assert available is False

    @pytest.mark.asyncio
    async def test_socket_available(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("os.path.exists", return_value=True):
                available = await is_socket_available()
                assert available is True


class TestExecuteViaUnixSocket:
    @pytest.mark.asyncio
    async def test_socket_not_found(self):
        with patch("os.path.exists", return_value=False):
            result = await execute_via_unix_socket(["echo", "test"])
            assert result["returncode"] == 1
            assert "not found" in result["stderr"].lower()

    @pytest.mark.asyncio
    async def test_command_timeout(self):
        with patch("os.path.exists", return_value=True):
            with patch("asyncio.wait_for", side_effect=TimeoutError("timeout")):
                result = await execute_via_unix_socket(["echo", "test"], timeout=1)
                assert result["returncode"] == 124
                assert "timed out" in result["stderr"]

    @pytest.mark.asyncio
    async def test_socket_error(self):
        with patch("os.path.exists", return_value=True):
            with patch("asyncio.wait_for", side_effect=Exception("connection error")):
                result = await execute_via_unix_socket(["echo", "test"])
                assert result["returncode"] == 1
                assert "error" in result["stderr"].lower()
