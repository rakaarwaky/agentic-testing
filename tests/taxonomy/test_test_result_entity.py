"""Tests for TestResult entity — covering uncovered branches."""

from src.contract import TestResult, FailureMetadata


class TestTestResultPosition:
    """position property fallback branches."""

    def test_position_with_line_number(self):
        meta = FailureMetadata(line_number=42)
        tr = TestResult(target="test_foo.py", passed=False, output_log="", failure=meta)
        assert tr.position == "test_foo.py:42"

    def test_position_without_failure(self):
        tr = TestResult(target="test_foo.py", passed=True, output_log="")
        assert tr.position == "test_foo.py"

    def test_position_with_failure_no_line(self):
        meta = FailureMetadata(line_number=None)
        tr = TestResult(target="test_foo.py", passed=False, output_log="", failure=meta)
        assert tr.position == "test_foo.py"


class TestTestResultErrorCode:
    """error_code property fallback branches."""

    def test_error_code_with_type(self):
        tr = TestResult(target="t.py", passed=False, output_log="", error_type="AssertionError")
        assert tr.error_code == "AssertionError"

    def test_error_code_without_type(self):
        tr = TestResult(target="t.py", passed=False, output_log="")
        assert tr.error_code == "UNKNOWN"


class TestTestResultIdentity:
    """identity property fallback branches."""

    def test_identity_with_error_type(self):
        tr = TestResult(target="t.py", passed=False, output_log="", error_type="ImportError")
        assert tr.identity == "t.py:ImportError"

    def test_identity_passing(self):
        tr = TestResult(target="t.py", passed=True, output_log="")
        assert tr.identity == "t.py:pass"


class TestTestResultMarkHealed:
    """mark_healed method."""

    def test_mark_healed(self):
        tr = TestResult(target="t.py", passed=False, output_log="")
        assert tr.healed is False
        assert tr.healing_attempts == 0
        tr.mark_healed(3)
        assert tr.healed is True
        assert tr.healing_attempts == 3


class TestFailureMetadata:
    """FailureMetadata defaults."""

    def test_defaults(self):
        fm = FailureMetadata()
        assert fm.file_path == ""
        assert fm.line_number is None
        assert fm.exception_type is None
        assert fm.message is None

    def test_full_construction(self):
        fm = FailureMetadata(
            file_path="test.py", line_number=5, exception_type="AssertionError", message="x != y"
        )
        assert fm.file_path == "test.py"
        assert fm.line_number == 5
