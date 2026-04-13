"""Tests for code analysis auditor."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.capabilities.code_analysis_audit_analyzer import CoverageAuditor


class TestCoverageAuditor:
    @pytest.mark.asyncio
    async def test_check_coverage_with_report(self, tmp_path):
        """Test coverage with a mocked subprocess that produces a report."""
        import json
        report_file = tmp_path / "coverage.json"
        report_file.write_text(json.dumps({
            "totals": {"percent_covered": 85.5}
        }))

        auditor = CoverageAuditor()

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                mock_tmp.return_value.__enter__ = MagicMock()
                mock_tmp.return_value.__enter__.return_value.name = str(report_file)
                mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
                # Override to not delete the temp file
                with patch("src.capabilities.code_analysis_audit_analyzer.os.path.exists", return_value=True):
                    with patch("builtins.open", side_effect=lambda *a, **kw: open(str(report_file), *a[1:], **kw)):
                        with patch("src.capabilities.code_analysis_audit_analyzer.os.remove"):
                            result = await auditor.check_coverage(".")

        assert isinstance(result, dict)
        assert "total_pct" in result or "error" in result

    @pytest.mark.asyncio
    async def test_check_coverage_no_report(self):
        """Test coverage when report file is not created."""
        auditor = CoverageAuditor()

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with patch("src.capabilities.code_analysis_audit_analyzer.os.path.exists", return_value=False):
                result = await auditor.check_coverage("nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_check_coverage_invalid_json(self, tmp_path):
        """Test coverage when report file has invalid JSON."""
        report_file = tmp_path / "coverage_invalid.json"
        report_file.write_text("NOT VALID JSON {{{")

        auditor = CoverageAuditor()
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        # Save original open before patching
        import builtins
        real_open = builtins.open

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                mock_tmp.return_value.__enter__ = MagicMock()
                mock_tmp.return_value.__enter__.return_value.name = str(report_file)
                mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
                with patch("src.capabilities.code_analysis_audit_analyzer.os.path.exists", return_value=True):
                    with patch("builtins.open", side_effect=lambda *a, **kw: real_open(str(report_file), *a[1:], **kw)):
                        with patch("src.capabilities.code_analysis_audit_analyzer.os.remove"):
                            result = await auditor.check_coverage(".")

        assert "error" in result
        assert "Invalid coverage report" in result["error"]

    @pytest.mark.asyncio
    async def test_check_coverage_subprocess_error(self):
        """Test coverage when subprocess raises an exception."""
        auditor = CoverageAuditor()

        with patch("asyncio.create_subprocess_exec", side_effect=OSError("no such file")):
            result = await auditor.check_coverage(".")

        assert "error" in result
        assert "Coverage analysis failed" in result["error"]

    @pytest.mark.asyncio
    async def test_check_coverage_success_returns_pct(self, tmp_path):
        """Test coverage success path returns total_pct (line 32)."""
        import json as json_mod
        report_file = tmp_path / "cov.json"
        report_file.write_text(json_mod.dumps({
            "totals": {"percent_covered": 92.3}
        }))

        auditor = CoverageAuditor()
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                mock_tmp.return_value.__enter__ = MagicMock()
                mock_tmp.return_value.__enter__.return_value.name = str(report_file)
                mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
                with patch("src.capabilities.code_analysis_audit_analyzer.os.path.exists", return_value=True):
                    real_open = open
                    with patch("builtins.open", side_effect=lambda *a, **kw: real_open(str(report_file), *a[1:], **kw)):
                        with patch("src.capabilities.code_analysis_audit_analyzer.os.remove"):
                            result = await auditor.check_coverage(".")

        assert result.get("total_pct") == 92.3
        assert "summary" in result
