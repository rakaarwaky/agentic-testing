"""
MCP Surface — Agentic Testing (Hybrid Architecture).

Layer 1 Discovery: Every tool description lists available CLI actions.
Layer 3 Discovery: `list_commands` runs `--help` on-demand for dynamic enumeration.
Full CLI reference lives in SKILL.md (Layer 2).
"""

import re
import subprocess
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from ...bootstrap.container import Container


def register_tools(mcp: FastMCP, container: Container):
    """Bridges Capabilities to the MCP Surface (Domain 5)."""

    # ─── Layer 3: Dynamic CLI Discovery ─────────────────────────────────────

    @mcp.tool()
    async def list_commands() -> str:
        """
        List ALL available CLI commands for the `agentic-test` tool.

        Returns the full --help output so the agent can discover commands
        without consuming extra MCP tool slots.

        CLI entry: `agentic-test --help`
        """
        result = subprocess.run(
            ["agentic-test", "--help"],
            capture_output=True,
            text=True,
        )
        output = result.stdout or result.stderr
        if not output.strip():
            # Fallback: enumerate from this module's knowledge
            return (
                "Available `agentic-test` commands:\n"
                "  run       <test_path> [--max-retries N]\n"
                "  analyze   <target_file>\n"
                "  audit     <target_dir> [--threshold N]\n"
                "  generate  <source_file>\n"
                "  migrate   <test_file>\n"
                "  data      <data_type: strings|numbers|json|dates|emails|all>\n"
                "  mock      <function_signature>\n\n"
                "Tip: Run `agentic-test <command> --help` for details on each command."
            )
        return output

    # ─── Core Test Execution ─────────────────────────────────────────────────

    @mcp.tool()
    async def test_run(
        test_path: str = Field(
            ...,
            description="Path to the test file to run (e.g., 'tests/test_parser.py')",
        ),
        max_retries: int = Field(
            2, description="Maximum number of self-healing attempts"
        ),
    ) -> str:
        """
        Runs a unit test with autonomous self-healing capabilities.

        CLI equivalent: `agentic-test run <test_path> [--max-retries N]`

        Self-healing order:
          1. ImportError  → auto-fixes import paths.
          2. AttributeError → remaps attribute access.
          3. AssertionError → adjusts literal comparisons.

        If healing fails after `max_retries`, switch to PLANNING mode
        and consult the Human Architect.
        """
        result = await container.test_use_case.execute(test_path, max_retries)

        status = "✅ PASS" if result.passed else "❌ FAIL"
        healing_info = (
            f"(Healed after {result.healing_attempts} attempts)"
            if result.healed
            else ""
        )

        return (
            f"Status: {status} {healing_info}\n"
            f"Target: {result.target}\n"
            f"\nOutput:\n{result.output_log}"
        )

    # ─── Analysis ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def test_analyze(
        target_file: str = Field(..., description="Path to the python file to analyze"),
    ) -> str:
        """
        Analyzes a Python file to extract functions, classes, and complexity.

        CLI equivalent: `agentic-test analyze <target_file>`

        Use BEFORE creating any test file. Extract class/function signatures
        to ensure your pytest mocks are high-fidelity.
        """
        return str(await container.analyzer.analyze_file(target_file))

    # ─── Quality Audit ───────────────────────────────────────────────────────

    @mcp.tool()
    async def test_audit(
        target_dir: str = Field(..., description="Directory to check coverage for"),
    ) -> str:
        """
        Audits the quality of tests in a directory (Coverage %).

        CLI equivalent: `agentic-test audit <target_dir> [--threshold N]`

        This is your quality gate. Report any file below 100% as a
        "Quality Breach" and generate missing tests immediately.
        """
        return str(await container.auditor.check_coverage(target_dir))

    # ─── Synthetic Data ──────────────────────────────────────────────────────

    @mcp.tool()
    async def test_generate_data(
        data_type: str = Field(
            ...,
            description="Type of data: 'strings', 'numbers', 'json', 'dates', 'emails', 'all'",
        ),
    ) -> str:
        """
        Generates synthetic edge-case data for testing.

        CLI equivalent: `agentic-test data <data_type>`

        Never rely solely on static fixtures. Use this to stress-test logic
        with boundary values, empty strings, and malformed inputs.
        """
        generators = {
            "strings": container.generator.generate_strings,
            "numbers": container.generator.generate_numbers,
            "json": container.generator.generate_json,
            "dates": container.generator.generate_dates,
            "emails": container.generator.generate_emails,
            "all": container.generator.generate_all,
        }

        if gen_func := generators.get(data_type):
            return str(gen_func())

        return f"Unknown data type. Available: {list(generators.keys())}"

    # ─── Test Scaffolding ─────────────────────────────────────────────────────

    @mcp.tool()
    async def test_generate(
        source_file: str = Field(
            ..., description="Path to the Python file to generate tests for"
        ),
    ) -> str:
        """
        Automatically generates boilerplate unit tests for a source file.

        CLI equivalent: `agentic-test generate <source_file>`

        Use when creating a new component to scaffold the
        `tests/[feature]/unit/` directory. Refine generated tests for
        semantic depth after scaffolding.
        """
        return await container.test_generator.generate_test(source_file)

    # ─── Migration ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def test_migrate(
        test_path: str = Field(
            ..., description="Path to a unittest-style file to migrate to pytest"
        ),
    ) -> str:
        """
        Converts unittest-style tests to pytest-style.

        CLI equivalent: `agentic-test migrate <test_file>`

        Handles: TestCase removal, assertEqual → assert, assertTrue → assert,
        assertFalse → assert not, and unused unittest imports.
        """
        try:
            content = container.file_system.read_file(test_path)
            new_content = content.replace("unittest.TestCase", "")
            new_content = new_content.replace("self.assertEqual(", "assert ")
            new_content = new_content.replace("self.assertTrue(", "assert ")
            new_content = new_content.replace("self.assertFalse(", "assert not ")
            new_content = new_content.replace("import unittest\n", "")
            container.file_system.write_file(test_path, new_content)
            return f"Migrated {test_path} to pytest-style (basic assertions converted)."
        except Exception as e:
            return f"Migration failed: {str(e)}"

    # ─── Slow Test Finder ────────────────────────────────────────────────────

    @mcp.tool()
    async def test_slow_finder(
        target_dir: str = Field(..., description="Directory to scan for slow tests"),
        threshold: float = Field(1.0, description="Seconds threshold for 'slow'"),
    ) -> str:
        """
        Identifies slow-running tests in a project.

        CLI equivalent: `agentic-test slow <target_dir> [--threshold N]`

        Tests exceeding `threshold` seconds are reported as bottlenecks.
        Uses pytest --durations internally.
        """
        result = subprocess.run(
            ["python", "-m", "pytest", target_dir, f"--durations=0", "-q", "--tb=no"],
            capture_output=True,
            text=True,
            cwd=target_dir,
        )
        output = result.stdout or result.stderr
        # Filter lines over threshold
        slow_lines = []
        for line in output.splitlines():
            match = re.match(r"^\s*([\d.]+)s\s+(.+)", line)
            if match and float(match.group(1)) >= threshold:
                slow_lines.append(line.strip())
        if slow_lines:
            return f"Slow tests (>{threshold}s):\n" + "\n".join(slow_lines)
        return f"✅ No tests exceed {threshold}s threshold.\nFull output:\n{output}"

    # ─── Mock Generator ──────────────────────────────────────────────────────

    @mcp.tool()
    async def test_mock_generate(
        function_signature: str = Field(
            ...,
            description="Signature of function to mock (e.g., 'def get_user(id: int)')",
        ),
    ) -> str:
        """
        Generates a mock template from a function signature.

        CLI equivalent: `agentic-test mock "<function_signature>"`

        Use this to scaffold high-fidelity mocks before writing assertions.
        """
        match = re.search(r"def\s+(\w+)\((.*)\)", function_signature)
        if not match:
            return "Invalid signature. Example: 'def my_func(a, b)'"

        name, args = match.groups()
        return (
            f"from unittest.mock import Mock\n\n"
            f"mock_{name} = Mock()\n"
            f"mock_{name}.return_value = None\n"
            f"# Args: {args}"
        )
