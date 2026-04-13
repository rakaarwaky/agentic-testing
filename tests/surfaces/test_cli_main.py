"""Tests for CLI main entry."""
from click.testing import CliRunner
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.surfaces.cli_main import cli, run_test


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_container():
    with patch("src.surfaces.cli_main.get_container") as mock:
        container = MagicMock()
        mock_report = MagicMock()
        container.test_use_case.execute = AsyncMock(return_value=MagicMock(
            passed=True, target="test.py", healed=False, healing_attempts=0, output_log="OK"
        ))
        container.analyzer.analyze_file = AsyncMock(return_value={
            "file": "test.py", "classes": [], "functions": ["foo"], "complexity_score": 5.0
        })
        container.auditor.check_coverage = AsyncMock(return_value={
            "total_pct": 85.0, "summary": "OK"
        })
        container.test_generator.generate_test = AsyncMock(return_value="Generated test")
        container.generator.generate_strings = MagicMock(return_value=["a", "b"])
        container.generator.generate_numbers = MagicMock(return_value=[1, 2])
        container.generator.generate_json = MagicMock(return_value=[{}])
        container.generator.generate_dates = MagicMock(return_value=["2024-01-01"])
        container.generator.generate_emails = MagicMock(return_value=["a@b.com"])
        container.generator.generate_all = MagicMock(return_value={"strings": []})
        mock.return_value = container
        yield container


class TestCliRun:
    def test_run_test_text(self, runner, mock_container, tmp_path):
        f = tmp_path / "test_sample.py"
        f.write_text("def test_ok(): pass\n")
        result = runner.invoke(cli, ["run", str(f)])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_run_test_json(self, runner, mock_container, tmp_path):
        f = tmp_path / "test_sample.py"
        f.write_text("def test_ok(): pass\n")
        result = runner.invoke(cli, ["run", str(f), "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "passed" in data

    def test_run_with_heal(self, runner, mock_container, tmp_path):
        f = tmp_path / "test_sample.py"
        f.write_text("def test_ok(): pass\n")
        result = runner.invoke(cli, ["run", str(f), "--heal", "--max-retries", "5"])
        assert result.exit_code == 0


class TestCliAnalyze:
    def test_analyze_text(self, runner, mock_container, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def foo(): pass\n")
        result = runner.invoke(cli, ["analyze", str(f)])
        assert result.exit_code == 0
        assert "foo" in result.output

    def test_analyze_json(self, runner, mock_container, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def foo(): pass\n")
        result = runner.invoke(cli, ["analyze", str(f), "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "functions" in data


class TestCliAudit:
    def test_audit_pass(self, runner, mock_container):
        result = runner.invoke(cli, ["audit", ".", "--threshold", "80"])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_audit_fail(self, runner, mock_container):
        mock_container.auditor.check_coverage = AsyncMock(return_value={
            "total_pct": 50.0, "summary": "Low"
        })
        result = runner.invoke(cli, ["audit", ".", "--threshold", "80"])
        assert result.exit_code == 1
        assert "FAIL" in result.output

    def test_audit_json(self, runner, mock_container):
        result = runner.invoke(cli, ["audit", ".", "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "total_pct" in data

    def test_audit_error(self, runner, mock_container):
        mock_container.auditor.check_coverage = AsyncMock(return_value={
            "error": "coverage failed"
        })
        result = runner.invoke(cli, ["audit", "."])
        assert result.exit_code == 0
        assert "Error" in result.output


class TestCliGenerate:
    def test_generate(self, runner, mock_container, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def foo(): pass\n")
        result = runner.invoke(cli, ["generate", str(f)])
        assert result.exit_code == 0


class TestCliGenerateData:
    def test_generate_strings(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "strings"])
        assert result.exit_code == 0

    def test_generate_numbers(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "numbers"])
        assert result.exit_code == 0

    def test_generate_json(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "json"])
        assert result.exit_code == 0

    def test_generate_dates(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "dates"])
        assert result.exit_code == 0

    def test_generate_emails(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "emails"])
        assert result.exit_code == 0

    def test_generate_all(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "all"])
        assert result.exit_code == 0

    def test_generate_data_json_format(self, runner, mock_container):
        result = runner.invoke(cli, ["generate-data", "strings", "--format", "text"])
        assert result.exit_code == 0


class TestCliVersion:
    def test_version(self, runner):
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestCliInit:
    def test_init(self, runner, tmp_path):
        config = tmp_path / "config.json"
        result = runner.invoke(cli, ["init", str(config)])
        assert result.exit_code == 0
        assert "initialized" in result.output.lower()
        assert config.exists()
