from pydantic import Field
from mcp.server.fastmcp import FastMCP
from ...bootstrap.container import Container


def register_tools(mcp: FastMCP, container: Container):
    """Bridges Capabilities to the MCP Surface (Domain 5)."""

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
        """Runs a unit test with autonomous self-healing capabilities."""
        result = await container.test_use_case.execute(test_path, max_retries)

        status = "✅ PASS" if result.passed else "❌ FAIL"
        healing_info = (
            f"(Healed after {result.healing_attempts} attempts)"
            if result.healed
            else ""
        )

        return f"""
        Status: {status} {healing_info}
        Target: {result.target}
        Output:
        {result.output_log}
        """

    @mcp.tool()
    async def test_analyze(
        target_file: str = Field(..., description="Path to the python file to analyze"),
    ) -> str:
        """Analyzes a Python file to extract functions, classes, and complexity."""
        return str(await container.analyzer.analyze_file(target_file))

    @mcp.tool()
    async def test_audit(
        target_dir: str = Field(..., description="Directory to check coverage for"),
    ) -> str:
        """Audits the quality of tests in a directory (Coverage %)."""
        return str(await container.auditor.check_coverage(target_dir))

    @mcp.tool()
    async def test_generate_data(
        data_type: str = Field(
            ...,
            description="Type of data: 'strings', 'numbers', 'json', 'dates', 'emails', 'all'",
        ),
    ) -> str:
        """Generates synthetic edge-case data for testing."""
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
    @mcp.tool()
    async def test_generate(
        source_file: str = Field(..., description="Path to the Python file to generate tests for"),
    ) -> str:
        """Automatically generates boilerplate unit tests for a source file."""
        return await container.test_generator.generate_test(source_file)
