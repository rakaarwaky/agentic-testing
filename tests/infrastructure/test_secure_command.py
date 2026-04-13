"""Tests for secure command execution."""
import pytest
from src.infrastructure.secure_command import is_command_safe, is_server_healthy


class TestCommandSafety:
    def test_safe_command(self):
        safe, reason = is_command_safe(["pytest", "tests/"])
        assert safe is True
        assert reason == ""

    def test_empty_command(self):
        safe, reason = is_command_safe([])
        assert safe is False
        assert "Empty" in reason

    def test_blocked_sudo(self):
        safe, reason = is_command_safe(["sudo", "ls"])
        assert safe is False
        assert "blocked" in reason

    def test_blocked_rm(self):
        safe, reason = is_command_safe(["rm", "-rf", "/"])
        assert safe is False
        assert "blocked" in reason

    def test_blocked_chmod(self):
        safe, reason = is_command_safe(["chmod", "777", "/"])
        assert safe is False
        assert "blocked" in reason

    def test_blocked_kill(self):
        safe, reason = is_command_safe(["kill", "-9", "1"])
        assert safe is False
        assert "blocked" in reason


class TestServerHealth:
    @pytest.mark.asyncio
    async def test_is_server_healthy(self):
        result = await is_server_healthy()
        assert result["status"] == "ready"
        assert result["installed"] is True
        assert result["security_enabled"] is True
