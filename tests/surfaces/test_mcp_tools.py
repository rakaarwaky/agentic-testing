"""Tests for MCP tools."""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.surfaces.mcp_tools_registry import register_tools, _get_execution_mode
from src.agent.dependency_injection_container import Container


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
        with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "run\nanalyze\naudit", "stderr": ""}
            result = await registered_tools[1]()
            assert isinstance(result, str)
            assert "run" in result or "analyze" in result

    @pytest.mark.asyncio
    async def test_list_commands_with_domain(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "  run       <test_path>\n  analyze <file>", "stderr": ""}
            result = await registered_tools[1](domain="test")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_check_status(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_socket_available", return_value=True):
            with patch("src.surfaces.mcp_tools_registry.get_socket_path", return_value="/tmp/dc.sock"):
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


class TestExecuteCommand:
    """Tests for the execute_command MCP tool — covers all action branches."""

    @pytest.mark.asyncio
    async def test_execute_run_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="run",
                    args={"test_path": "tests/test_foo.py", "heal": True, "max_retries": 3, "format": "json"},
                )
                data = json.loads(result)
                assert data["returncode"] == 0
                cmd = data["command"]
                assert "agentic-test" in cmd
                assert "run" in cmd
                assert "--heal" in cmd
                assert "--max-retries" in cmd
                assert "--format" in cmd

    @pytest.mark.asyncio
    async def test_execute_run_no_args(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="run", args=None)
                data = json.loads(result)
                assert data["returncode"] == 0

    @pytest.mark.asyncio
    async def test_execute_analyze_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "analysis", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="analyze",
                    args={"target_file": "src/foo.py", "format": "text"},
                )
                data = json.loads(result)
                assert "analyze" in data["command"]
                assert "--format" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_audit_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "audit", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="audit",
                    args={"target_dir": "src/", "threshold": 80, "format": "json"},
                )
                data = json.loads(result)
                assert "audit" in data["command"]
                assert "--threshold" in data["command"]
                assert "--format" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_generate_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "generated", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="generate",
                    args={"source_file": "src/foo.py", "output": "tests/test_foo.py"},
                )
                data = json.loads(result)
                assert "generate" in data["command"]
                assert "--output" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_generate_data_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "data", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="generate-data",
                    args={"data_type": "emails", "count": 10, "format": "json"},
                )
                data = json.loads(result)
                assert "generate-data" in data["command"]
                assert "--count" in data["command"]
                assert "--format" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_migrate_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "migrated", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="migrate",
                    args={"test_path": "tests/old.py", "backup": True},
                )
                data = json.loads(result)
                assert "migrate" in data["command"]
                assert "--backup" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_find_slow_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "slow tests", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="find-slow",
                    args={"target_dir": "tests/", "threshold": 2.0, "top": 5},
                )
                data = json.loads(result)
                assert "find-slow" in data["command"]
                assert "--threshold" in data["command"]
                assert "--top" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_mock_generate_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "mock", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="mock-generate",
                    args={"function_signature": "def foo(x: int) -> str", "output": "mock.py"},
                )
                data = json.loads(result)
                assert "mock-generate" in data["command"]
                assert "--output" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_workflow_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "done", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="workflow",
                    args={"workflow": "test-and-fix", "target": "tests/", "threshold": 80, "max_retries": 3},
                )
                data = json.loads(result)
                assert "workflow" in data["command"]
                assert "--threshold" in data["command"]
                assert "--max-retries" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_init_action(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "initialized", "stderr": "", "returncode": 0}
                result = await registered_tools[0](
                    action="init",
                    args={"config_path": "/tmp/config.yaml"},
                )
                data = json.loads(result)
                assert "init" in data["command"]

    @pytest.mark.asyncio
    async def test_execute_security_blocked(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(False, "dangerous command")):
            result = await registered_tools[0](action="run", args=None)
            data = json.loads(result)
            assert data["blocked"] is True
            assert "Security blocked" in data["stderr"]
            assert data["returncode"] == 1

    @pytest.mark.asyncio
    async def test_execute_returns_error_result(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "", "stderr": "error occurred", "returncode": 1}
                result = await registered_tools[0](action="run", args={"test_path": "missing.py"})
                data = json.loads(result)
                assert data["returncode"] == 1
                assert "error occurred" in data["stderr"]

    @pytest.mark.asyncio
    async def test_execute_missing_returncode_defaults(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "out", "stderr": ""}
                result = await registered_tools[0](action="version")
                data = json.loads(result)
                # Default returncode should be 1 when not provided
                assert data["returncode"] == 1


class TestListCommandsEdgeCases:
    """Tests for list_commands empty-output fallback (line 216)."""

    @pytest.mark.asyncio
    async def test_list_commands_empty_output_shows_fallback(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "", "stderr": ""}
            result = await registered_tools[1]()
            assert "run" in result
            assert "analyze" in result
            assert "audit" in result
            assert "generate-data" in result

    @pytest.mark.asyncio
    async def test_list_commands_unknown_domain(self, registered_tools):
        with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "run\nanalyze\naudit", "stderr": ""}
            result = await registered_tools[1](domain="nonexistent")
            assert "run" in result or "analyze" in result


class TestReadSkillContextEdgeCases:
    """Tests for read_skill_context no-section case (line 388)."""

    @pytest.mark.asyncio
    async def test_read_skill_context_none_section(self, registered_tools):
        result = await registered_tools[3](section=None)
        assert "section" in result.lower() or "available" in result.lower()

    @pytest.mark.asyncio
    async def test_read_skill_context_all_sections(self, registered_tools):
        for section_name in ["directives", "mcp-tools", "cli-commands", "workflows", "architecture"]:
            result = await registered_tools[3](section=section_name)
            assert isinstance(result, str)
            assert len(result) > 10


class TestExecuteCommandMinimalArgs:
    """Tests for execute_command with minimal/missing args — covers falsy branch paths.

    IMPORTANT: args={} is falsy in Python, so `if args:` skips the entire block.
    We must pass a truthy dict (with at least one key) to enter the block,
    then individual get() checks will be falsy for missing keys.
    """

    @pytest.mark.asyncio
    async def test_run_missing_optional_keys(self, registered_tools):
        """Run with truthy args but missing keys — all get() branches go falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                # Use a dummy key to make args truthy, but missing run-specific keys
                result = await registered_tools[0](action="run", args={"_truthy": True})
                data = json.loads(result)
                assert data["returncode"] == 0
                assert "agentic-test run" in data["command"]
                assert "--heal" not in data["command"]
                assert "--max-retries" not in data["command"]
                assert "--format" not in data["command"]

    @pytest.mark.asyncio
    async def test_run_partial_heal_only(self, registered_tools):
        """Run with only heal=True — test_path falsy, max_retries falsy, format falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="run", args={"heal": True})
                data = json.loads(result)
                assert "--heal" in data["command"]
                assert "--max-retries" not in data["command"]

    @pytest.mark.asyncio
    async def test_analyze_missing_target_file(self, registered_tools):
        """Analyze with truthy args but no target_file — falsy branch."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="analyze", args={"_truthy": True})
                data = json.loads(result)
                assert "analyze" in data["command"]
                assert "--format" not in data["command"]

    @pytest.mark.asyncio
    async def test_analyze_format_only(self, registered_tools):
        """Analyze with format only — target_file falsy, format truthy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="analyze", args={"format": "text"})
                data = json.loads(result)
                assert "--format" in data["command"]

    @pytest.mark.asyncio
    async def test_audit_missing_optional_keys(self, registered_tools):
        """Audit with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="audit", args={"_truthy": True})
                data = json.loads(result)
                assert "audit" in data["command"]
                assert "--threshold" not in data["command"]
                assert "--format" not in data["command"]

    @pytest.mark.asyncio
    async def test_audit_target_dir_only(self, registered_tools):
        """Audit with target_dir only — threshold and format falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="audit", args={"target_dir": "src/"})
                data = json.loads(result)
                assert "src/" in data["command"]
                assert "--threshold" not in data["command"]

    @pytest.mark.asyncio
    async def test_generate_missing_optional_keys(self, registered_tools):
        """Generate with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="generate", args={"_truthy": True})
                data = json.loads(result)
                assert "generate" in data["command"]
                assert "--output" not in data["command"]

    @pytest.mark.asyncio
    async def test_generate_data_missing_optional_keys(self, registered_tools):
        """Generate-data with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="generate-data", args={"_truthy": True})
                data = json.loads(result)
                assert "generate-data" in data["command"]
                assert "--count" not in data["command"]
                assert "--format" not in data["command"]

    @pytest.mark.asyncio
    async def test_generate_data_data_type_only(self, registered_tools):
        """Generate-data with data_type only — count and format falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="generate-data", args={"data_type": "strings"})
                data = json.loads(result)
                assert "strings" in data["command"]
                assert "--count" not in data["command"]

    @pytest.mark.asyncio
    async def test_migrate_missing_optional_keys(self, registered_tools):
        """Migrate with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="migrate", args={"_truthy": True})
                data = json.loads(result)
                assert "migrate" in data["command"]
                assert "--backup" not in data["command"]

    @pytest.mark.asyncio
    async def test_find_slow_missing_optional_keys(self, registered_tools):
        """Find-slow with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="find-slow", args={"_truthy": True})
                data = json.loads(result)
                assert "find-slow" in data["command"]
                assert "--threshold" not in data["command"]
                assert "--top" not in data["command"]

    @pytest.mark.asyncio
    async def test_find_slow_target_dir_only(self, registered_tools):
        """Find-slow with target_dir only — threshold and top falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="find-slow", args={"target_dir": "tests/"})
                data = json.loads(result)
                assert "tests/" in data["command"]
                assert "--top" not in data["command"]

    @pytest.mark.asyncio
    async def test_mock_generate_missing_optional_keys(self, registered_tools):
        """Mock-generate with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="mock-generate", args={"_truthy": True})
                data = json.loads(result)
                assert "mock-generate" in data["command"]
                assert "--output" not in data["command"]

    @pytest.mark.asyncio
    async def test_workflow_missing_optional_keys(self, registered_tools):
        """Workflow with truthy args but missing keys — all falsy branches."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="workflow", args={"_truthy": True})
                data = json.loads(result)
                assert "workflow" in data["command"]
                assert "--threshold" not in data["command"]
                assert "--max-retries" not in data["command"]

    @pytest.mark.asyncio
    async def test_workflow_workflow_only(self, registered_tools):
        """Workflow with workflow name only — target, threshold, max_retries falsy."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="workflow", args={"workflow": "test-and-fix"})
                data = json.loads(result)
                assert "test-and-fix" in data["command"]

    @pytest.mark.asyncio
    async def test_init_missing_config_path(self, registered_tools):
        """Init with truthy args but missing config_path — falsy branch."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="init", args={"_truthy": True})
                data = json.loads(result)
                assert "init" in data["command"]

    @pytest.mark.asyncio
    async def test_unknown_action_with_args(self, registered_tools):
        """Unknown action with args — falls through to no elif match."""
        with patch("src.surfaces.mcp_tools_registry.is_command_safe", return_value=(True, "ok")):
            with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
                mock_exec.return_value = {"stdout": "ok", "stderr": "", "returncode": 0}
                result = await registered_tools[0](action="unknown", args={"key": "val"})
                data = json.loads(result)
                assert "unknown" in data["command"]

    @pytest.mark.asyncio
    async def test_list_commands_domain_filter_no_match(self, registered_tools):
        """List commands with valid domain but output has no matching keywords."""
        with patch("src.surfaces.mcp_tools_registry.execute_via_unix_socket") as mock_exec:
            mock_exec.return_value = {"stdout": "no relevant commands here", "stderr": ""}
            result = await registered_tools[1](domain="migration")
            assert "No commands found" in result or "no relevant" in result
