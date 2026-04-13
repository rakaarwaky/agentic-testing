"""Tests for healing strategies."""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.capabilities.test_healing_actions import (
    FixStrategy,
    ImportErrorStrategy,
    AttributeErrorStrategy,
    TypeErrorStrategy,
    NameErrorStrategy,
    AssertionErrorStrategy,
)
from src.taxonomy import TestResult, FailureMetadata
from src.infrastructure.file_system_provider import LocalFileSystem


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

    def test_fix_legacy_success(self):
        """Test legacy assertion fix path."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("def test_foo():\n    assert 'hello' == 'world'\n")
            fp = f.name
        try:
            s = AssertionErrorStrategy(_make_fs())
            log = "AssertionError: assert 'hello' == 'world'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AssertionError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            assert "'hello'" in content
        finally:
            os.remove(fp)

    def test_fix_with_line_exception(self):
        """Test _fix_with_line exception handling (lines 227-229)."""
        fs = MagicMock()
        fs.read_lines.side_effect = Exception("read error")
        s = AssertionErrorStrategy(fs)
        failure = FailureMetadata(line_number=5, message="assert 'a' == 'b'")
        result = TestResult(target="t.py", passed=False, output_log="", error_type="AssertionError", failure=failure)
        assert s.apply_fix(result) is False

    def test_fix_with_line_no_failure(self):
        """Test _fix_with_line returns False when failure is None (line 193)."""
        fs = MagicMock()
        s = AssertionErrorStrategy(fs)
        result = TestResult(target="t.py", passed=False, output_log="")
        assert s._fix_with_line(result) is False

    def test_fix_legacy_exception(self):
        """Test _fix_legacy exception handling (lines 246-248)."""
        fs = MagicMock()
        fs.read_lines.side_effect = Exception("read error")
        s = AssertionErrorStrategy(fs)
        result = TestResult(target="t.py", passed=False, output_log="AssertionError: assert 'a' == 'b'", error_type="AssertionError")
        assert s.apply_fix(result) is False


class TestAttributeErrorStrategyExtra:
    def test_fix_object_attribute_match(self):
        """Test the 'object has no attribute' branch (line 89-90)."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import math\nresult = math.sqrtt(4)\n")
            fp = f.name
        try:
            s = AttributeErrorStrategy(_make_fs())
            log = "'module' object has no attribute 'sqrtt'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AttributeError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            assert "HEALER" in content
        finally:
            os.remove(fp)

    def test_fix_with_typo_replacement(self):
        """Test the typo fix path (lines 102-104): typo NOT in file, close match IS."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            # sqrt is in the file, sqrtr (typo) is NOT
            f.write("import math\nresult = math.sqrt(4)\n")
            fp = f.name
        try:
            s = AttributeErrorStrategy(_make_fs())
            # Error references sqrtr which doesn't exist in file, but sqrt does
            log = "module 'math' has no attribute 'sqrtr'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AttributeError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            # sqrtr should have been replaced with sqrt (close match)
            assert "math.sqrt(4)" in content
        finally:
            os.remove(fp)

    def test_fix_close_match_replacement(self):
        """Test actual replacement when close match differs from typo (lines 102-104)."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            # sqrts is in the file; error references sqrtr (typo not in file)
            # difflib should match sqrtr -> sqrts (close match != typo)
            f.write("import math\nresult = math.sqrts(4)\n")
            fp = f.name
        try:
            s = AttributeErrorStrategy(_make_fs())
            log = "module 'math' has no attribute 'sqrtr'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AttributeError")
            assert s.apply_fix(result) is True
            content = _make_fs().read_file(fp)
            # sqrtr was not in file, so .sqrtr -> .sqrts replacement is no-op
            # fallback hint should be added
            assert "HEALER" in content
        finally:
            os.remove(fp)

    def test_fix_typo_in_content_with_close_match(self):
        """Test lines 102-104: difflib finds close match, replacement changes content."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import os\nresult = os.path.islinkk('/tmp')\n")
            fp = f.name
        try:
            s = AttributeErrorStrategy(_make_fs())
            log = "module 'os.path' has no attribute 'islinkk'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="AttributeError")
            # Mock difflib to return a DIFFERENT word as close match
            with patch("src.capabilities.test_healing_actions.difflib.get_close_matches", return_value=["islink"]):
                ret = s.apply_fix(result)
            content = _make_fs().read_file(fp)
            # .replace('.islinkk', '.islink') should have changed content
            assert ret is True
            assert "islink" in content
        finally:
            os.remove(fp)


class TestTypeErrorStrategyExtra:
    def test_fix_exception(self):
        """Test exception handling branch (lines 137-139)."""
        fs = MagicMock()
        fs.read_file.side_effect = Exception("read error")
        s = TypeErrorStrategy(fs)
        log = "func() missing 1 required positional argument: 'x'"
        result = TestResult(target="t.py", passed=False, output_log=log, error_type="TypeError")
        assert s.apply_fix(result) is False


class TestNameErrorStrategyExtra:
    def test_fix_no_regex_match(self):
        """Test when regex doesn't match (line 164)."""
        s = NameErrorStrategy(_make_fs())
        result = TestResult(target="t.py", passed=False, output_log="some other error", error_type="NameError")
        assert s.apply_fix(result) is False

    def test_fix_exception(self):
        """Test exception handling branch (lines 174-176)."""
        fs = MagicMock()
        fs.read_file.side_effect = Exception("read error")
        s = NameErrorStrategy(fs)
        result = TestResult(target="t.py", passed=False, output_log="name 'os' is not defined", error_type="NameError")
        assert s.apply_fix(result) is False


class TestCreateBackup:
    """Tests for _create_backup error handling (lines 34-41)."""

    def test_backup_os_error(self):
        """Test _create_backup returns None on OSError (e.g., permission denied)."""
        s = ImportErrorStrategy(_make_fs())
        with patch("shutil.copy2", side_effect=OSError("Permission denied")):
            result = s._create_backup("/nonexistent/path/test.py")
            assert result is None

    def test_backup_success(self):
        """Test _create_backup returns backup path on success."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("import sys\n")
            fp = f.name
        try:
            s = ImportErrorStrategy(_make_fs())
            backup = s._create_backup(fp)
            assert backup is not None
            assert backup.endswith(".healer.bak")
            assert os.path.exists(backup)
            os.remove(backup)
        finally:
            os.remove(fp)


class TestParseAssertionGeneral:
    """Tests for _parse_assertion general regex pattern (line 259)."""

    def test_parse_assertion_general_pattern(self):
        """Test the catch-all regex: assert X == Y with variable names."""
        s = AssertionErrorStrategy(_make_fs())
        result = s._parse_assertion("assert some_var == other_var")
        assert result is not None
        # Regex captures with possible trailing whitespace
        assert "some_var" in result[0]
        assert "other_var" in result[1]


class TestFixStrategyAbstract:
    """Test that FixStrategy abstract methods raise NotImplementedError."""

    def test_can_fix_raises(self):
        """Test abstract can_fix raises NotImplementedError (line 25)."""

        class ConcreteStrategy(FixStrategy):
            pass

        # Can't instantiate directly, test via __init_subclass__
        with pytest.raises(TypeError):
            ConcreteStrategy(_make_fs())


class TestTypeErrorNoChangeBranch:
    """Branch 133->139: TypeErrorStrategy where replacement doesn't change content."""

    def test_fix_no_content_change(self):
        """Test when regex matches but replacement produces same content."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            # func() is NOT in the file, so .replace is a no-op
            f.write("print('hello')\n")
            fp = f.name
        try:
            s = TypeErrorStrategy(_make_fs())
            log = "func() missing 1 required positional argument: 'x'"
            result = TestResult(target=fp, passed=False, output_log=log, error_type="TypeError")
            # func() not in file → new_content == content → returns False
            assert s.apply_fix(result) is False
        finally:
            os.remove(fp)


class TestAssertionNonMatchingLine:
    """Branch 210->229: AssertionErrorStrategy with line that doesn't match regex."""

    def test_fix_with_line_no_literal_no_var_match(self):
        """Test _fix_with_line when expected not in line AND assert_var regex fails."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            # Line contains 'assert' but not 'assert X == Y' pattern
            f.write("def test_foo():\n    assert something_complicated()\n")
            fp = f.name
        try:
            s = AssertionErrorStrategy(_make_fs())
            failure = FailureMetadata(line_number=2, message="assert 'a' == 'b'")
            result = TestResult(target=fp, passed=False, output_log="", error_type="AssertionError", failure=failure)
            # 'a' not in the line, and 'assert something_complicated()' doesn't match 'assert \w+ == \w+'
            assert s.apply_fix(result) is False
        finally:
            os.remove(fp)
