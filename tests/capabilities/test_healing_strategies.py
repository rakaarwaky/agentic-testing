"""Tests for healing strategies."""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.capabilities.healing_strategies import (
    ImportErrorStrategy,
    AttributeErrorStrategy,
    TypeErrorStrategy,
    NameErrorStrategy,
    AssertionErrorStrategy,
)
from src.taxonomy.models import TestResult, FailureMetadata
from src.infrastructure.file_system import LocalFileSystem


def _make_fs():
    return LocalFileSystem(allowed_base=tempfile.gettempdir())


class TestImportErrorStrategy:
    def test_can_fix(self):
        s = ImportErrorStrategy(_make_fs())
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="ImportError"))
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="ModuleNotFoundError"))
        assert not s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="TypeError"))

    def test_fix_already_present(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import sys\nsys.path.insert(0, 'x')\n")
            fp = f.name
        try:
            s = ImportErrorStrategy(_make_fs())
            result = TestResult(target=fp, passed=False, output_log="", error_type="ImportError")
            assert s.apply_fix(result) is False
        finally:
            os.remove(fp)

    def test_fix_no_pytest_trigger(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("no pytest here\n")
            fp = f.name
        try:
            s = ImportErrorStrategy(_make_fs())
            result = TestResult(target=fp, passed=False, output_log="", error_type="ImportError")
            assert s.apply_fix(result) is False
        finally:
            os.remove(fp)

    def test_fix_os_error(self):
        s = ImportErrorStrategy(_make_fs())
        result = TestResult(target="/tmp/nonexistent_xyz/test.py", passed=False, output_log="", error_type="ImportError")
        assert s.apply_fix(result) is False


class TestAttributeErrorStrategy:
    def test_can_fix(self):
        s = AttributeErrorStrategy(_make_fs())
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="AttributeError"))
        assert not s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="TypeError"))

    
    def test_fix_no_match(self):
        s = AttributeErrorStrategy(_make_fs())
        result = TestResult(target="t.py", passed=False, output_log="random error", error_type="AttributeError")
        assert s.apply_fix(result) is False

    
    def test_fix_with_hint(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import math\n")
            fp = f.name
        try:
            s = AttributeErrorStrategy(_make_fs())
            log = "module 'math' has no attribute 'sqrtt'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AttributeError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            assert "HEALER" in content
        finally:
            os.remove(fp)

    
    def test_fix_exception(self):
        fs = MagicMock()
        fs.read_file.side_effect = Exception("read error")
        s = AttributeErrorStrategy(fs)
        result = TestResult(target="t.py", passed=False, output_log="module 'x' has no attribute 'y'", error_type="AttributeError")
        assert s.apply_fix(result) is False


class TestTypeErrorStrategy:
    def test_can_fix(self):
        s = TypeErrorStrategy(_make_fs())
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="TypeError"))
        assert not s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="NameError"))

    
    def test_fix_no_match(self):
        s = TypeErrorStrategy(_make_fs())
        result = TestResult(target="t.py", passed=False, output_log="some other error", error_type="TypeError")
        assert s.apply_fix(result) is False

    
    def test_fix_success(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("func()\n")
            fp = f.name
        try:
            s = TypeErrorStrategy(_make_fs())
            log = "func() missing 1 required positional argument: 'x'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="TypeError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            assert "func(None)" in content
        finally:
            os.remove(fp)


class TestNameErrorStrategy:
    def test_can_fix(self):
        s = NameErrorStrategy(_make_fs())
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="NameError"))
        assert not s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="TypeError"))

    
    def test_fix_no_match(self):
        s = NameErrorStrategy(_make_fs())
        result = TestResult(target="t.py", passed=False, output_log="name 'weird' is not defined", error_type="NameError")
        assert s.apply_fix(result) is False

    
    def test_fix_success(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("print(os.getcwd())\n")
            fp = f.name
        try:
            s = NameErrorStrategy(_make_fs())
            log = "name 'os' is not defined"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="NameError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            assert "import os" in content
        finally:
            os.remove(fp)

    
    def test_fix_already_present(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import os\nprint(os.getcwd())\n")
            fp = f.name
        try:
            s = NameErrorStrategy(_make_fs())
            log = "name 'os' is not defined"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="NameError")
            assert s.apply_fix(result) is False
        finally:
            os.remove(fp)


class TestAssertionErrorStrategy:
    def test_can_fix(self):
        s = AssertionErrorStrategy(_make_fs())
        assert s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="AssertionError"))
        assert not s.can_fix(TestResult(target="t.py", passed=False, output_log="", error_type="TypeError"))

    def test_parse_assertion_literal(self):
        s = AssertionErrorStrategy(_make_fs())
        result = s._parse_assertion("assert 'a' == 'b'")
        assert result == ("a", "b")

    def test_parse_assertion_number(self):
        s = AssertionErrorStrategy(_make_fs())
        result = s._parse_assertion("assert 10 == 20")
        assert result == ("10", "20")

    def test_parse_assertion_no_match(self):
        s = AssertionErrorStrategy(_make_fs())
        result = s._parse_assertion("some random message")
        assert result is None
