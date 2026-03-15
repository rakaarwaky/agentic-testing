import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.capabilities.code_analysis.auditor import CoverageAuditor


@pytest.mark.asyncio
async def test_check_coverage_success():
    auditor = CoverageAuditor()

    # Mock data to be written to the temp file
    mock_data = {"totals": {"percent_covered": 85.5}}

    # We need to mock asyncio.create_subprocess_shell
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        # We also need to mock the json file creation and reading
        # Instead of mocking tempfile, let's just ensure we handle the file path

        # We'll use a real temp file but mock the subprocess that WOULD have written to it
        # Actually, let's mock 'open' to return our json data when the report_file is read

        # A better way: patch CoverageAuditor.check_coverage to use a predictable file
        # or just mock the file system

        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                json.dumps(mock_data)
            )
            with patch("os.path.exists", return_value=True):
                result = await auditor.check_coverage("src")

                assert result["total_pct"] == 85.5
                assert "generated successfully" in result["summary"]


@pytest.mark.asyncio
async def test_check_coverage_failure():
    auditor = CoverageAuditor()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"error")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        with patch("os.path.exists", return_value=False):
            result = await auditor.check_coverage("src")
            assert "error" in result
            assert "Failed to generate" in result["error"]


@pytest.mark.asyncio
async def test_check_coverage_invalid_json():
    auditor = CoverageAuditor()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                "invalid json"
            )
            with patch("os.path.exists", return_value=True):
                result = await auditor.check_coverage("src")
                assert "error" in result
                assert "Invalid coverage report format" in result["error"]


@pytest.mark.asyncio
async def test_check_coverage_exception():
    auditor = CoverageAuditor()

    with patch("asyncio.create_subprocess_shell", side_effect=Exception("Test Error")):
        result = await auditor.check_coverage("src")
        assert "error" in result
        assert "Coverage analysis failed: Test Error" in result["error"]
