"""Tests for lint domain value objects (ScopeRef, Location)."""
import pytest
from src.taxonomy import ScopeRef, Location


class TestScopeRef:
    def test_str_with_file(self):
        sr = ScopeRef(name="my_func", kind="function", file="src/app.py")
        assert str(sr) == "function my_func in src/app.py"

    def test_str_without_file(self):
        sr = ScopeRef(name="MyClass", kind="class")
        assert str(sr) == "class MyClass"

    def test_str_no_kind(self):
        sr = ScopeRef(name="module_level", kind="")
        assert str(sr) == "module_level"

    def test_default_kind(self):
        sr = ScopeRef(name="test")
        assert sr.kind == "function"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            ScopeRef(name="")

    def test_has_range(self):
        sr = ScopeRef(name="func", start_line=1, end_line=10)
        assert sr.has_range is True

    def test_no_range(self):
        sr = ScopeRef(name="func")
        assert sr.has_range is False

    def test_partial_range(self):
        sr = ScopeRef(name="func", start_line=1)
        assert sr.has_range is False


class TestLocation:
    def test_str_full(self):
        loc = Location(file="src/app.py", line=10, column=5, description="issue here")
        result = str(loc)
        assert "src/app.py" in result
        assert "10:5" in result
        assert "issue here" in result

    def test_str_no_file(self):
        loc = Location(line=10, column=5)
        assert "10:5" in str(loc)

    def test_str_file_no_line(self):
        loc = Location(file="src/app.py")
        assert str(loc) == "src/app.py"

    def test_str_file_with_line_no_column(self):
        loc = Location(file="src/app.py", line=10)
        assert str(loc) == "src/app.py:10"

    def test_str_unknown(self):
        loc = Location()
        assert str(loc) == "unknown"

    def test_str_with_description(self):
        loc = Location(description="some problem")
        result = str(loc)
        assert "some problem" in result
