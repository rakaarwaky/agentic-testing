"""Tests for code analysis auditor."""
import pytest
from src.capabilities.code_analysis_auditor import CoverageAuditor


class TestCoverageAuditor:
    @pytest.mark.asyncio
    async def test_check_coverage(self):
        auditor = CoverageAuditor()
        result = await auditor.check_coverage(".")
        assert isinstance(result, dict)
        # Should return either coverage data or an error
        assert "total_pct" in result or "error" in result
