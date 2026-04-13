"""Tests for lint value objects (Severity, ErrorCode, Position, Score)."""
from src.taxonomy import Severity, ErrorCode, Position, Score


class TestSeverity:
    def test_values(self):
        assert Severity.INFO.value == "info"
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"

    def test_score_impact(self):
        assert Severity.INFO.score_impact == 0
        assert Severity.LOW.score_impact == 0
        assert Severity.MEDIUM.score_impact == 2
        assert Severity.HIGH.score_impact == 10
        assert Severity.CRITICAL.score_impact == 50


class TestErrorCode:
    def test_str(self):
        ec = ErrorCode(code="E001")
        assert str(ec) == "E001"

    def test_is_test_error(self):
        assert ErrorCode(code="E001").is_test_error is True
        assert ErrorCode(code="F001").is_test_error is True
        assert ErrorCode(code="W001").is_test_error is False
        assert ErrorCode(code="I001").is_test_error is False

    def test_is_import_error(self):
        assert ErrorCode(code="I001").is_import_error is True
        assert ErrorCode(code="M001").is_import_error is True
        assert ErrorCode(code="E001").is_import_error is False


class TestPosition:
    def test_str_with_column(self):
        p = Position(line=10, column=5)
        assert str(p) == "10:5"

    def test_str_without_column(self):
        p = Position(line=10, column=0)
        assert str(p) == "10"

    def test_default_column(self):
        p = Position(line=5)
        assert p.column == 0
        assert str(p) == "5"


class TestScore:
    def test_str(self):
        s = Score(value=85.5)
        assert str(s) == "85.5"

    def test_is_passing(self):
        assert Score(value=80.0).is_passing is True
        assert Score(value=90.0).is_passing is True
        assert Score(value=79.9).is_passing is False

    def test_is_perfect(self):
        assert Score(value=100.0).is_perfect is True
        assert Score(value=99.9).is_perfect is False
