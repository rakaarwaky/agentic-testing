"""Tests for mcp_tools_registry helpers."""
from unittest.mock import patch
from src.surfaces.mcp_tools_registry import _get_execution_mode


class TestExecutionModeHelpers:
    def test_get_execution_mode_direct(self):
        with patch.dict("os.environ", {}, clear=True):
            mode = _get_execution_mode()
            assert mode == "direct"

    def test_get_execution_mode_unix_socket(self):
        with patch.dict("os.environ", {"USE_UNIX_SOCKET": "true"}):
            mode = _get_execution_mode()
            assert mode == "unix_socket"

    def test_get_execution_mode_http(self):
        with patch.dict("os.environ", {"USE_DESKTOP_COMMANDER_MCP": "true"}):
            mode = _get_execution_mode()
            assert mode == "http"

    def test_get_execution_mode_unix_socket_case_insensitive(self):
        with patch.dict("os.environ", {"USE_UNIX_SOCKET": "TRUE"}):
            mode = _get_execution_mode()
            assert mode == "unix_socket"

    def test_get_execution_mode_empty_env(self):
        with patch.dict("os.environ", {"USE_UNIX_SOCKET": "", "USE_DESKTOP_COMMANDER_MCP": ""}):
            mode = _get_execution_mode()
            assert mode == "direct"
