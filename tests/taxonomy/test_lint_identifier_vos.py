"""Tests for lint identifier value objects."""
import pytest
from src.taxonomy import TestName, FilePath, SymbolName, DirectoryPath


class TestTestName:
    def test_creation(self):
        tn = TestName(value="test_something")
        assert tn.value == "test_something"

    def test_str(self):
        tn = TestName(value="test_something")
        assert str(tn) == "test_something"

    def test_strips_whitespace(self):
        tn = TestName(value="  test_something  ")
        assert tn.value == "test_something"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            TestName(value="")
        with pytest.raises(ValueError):
            TestName(value="   ")

    def test_eq_with_string(self):
        tn = TestName(value="test_something")
        assert tn == "test_something"
        assert tn != "other"

    def test_hash(self):
        tn1 = TestName(value="test_something")
        tn2 = TestName(value="test_something")
        assert hash(tn1) == hash(tn2)

    def test_eq_with_testname(self):
        """Cover isinstance(other, TestName) branch."""
        tn1 = TestName(value="foo")
        tn2 = TestName(value="foo")
        tn3 = TestName(value="bar")
        assert tn1 == tn2
        assert tn1 != tn3

    def test_eq_with_other_type(self):
        """Cover NotImplemented return for other types."""
        tn = TestName(value="foo")
        assert tn.__eq__(42) is NotImplemented


class TestFilePath:
    def test_creation(self):
        fp = FilePath(value="/some/path/file.py")
        assert fp.value == "/some/path/file.py"

    def test_extension(self):
        fp = FilePath(value="/some/path/file.py")
        assert fp.extension == "py"

    def test_no_extension(self):
        fp = FilePath(value="/some/path/Makefile")
        assert fp.extension == ""

    def test_has_extension(self):
        fp = FilePath(value="/some/path/file.py")
        assert fp.has_extension("py") is True
        assert fp.has_extension("PY") is True
        assert fp.has_extension("js") is False

    def test_normalizes_backslash(self):
        fp = FilePath(value="C:\\Users\\file.py")
        assert fp.value == "C:/Users/file.py"

    def test_strips_trailing_slash(self):
        fp = FilePath(value="/some/path/")
        assert fp.value == "/some/path"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            FilePath(value="")

    def test_eq_with_string(self):
        fp = FilePath(value="/some/path/file.py")
        assert fp == "/some/path/file.py"

    def test_str(self):
        fp = FilePath(value="/some/path/file.py")
        assert str(fp) == "/some/path/file.py"

    def test_hash(self):
        fp1 = FilePath(value="/a/b.py")
        fp2 = FilePath(value="/a/b.py")
        assert hash(fp1) == hash(fp2)

    def test_eq_with_filepath(self):
        fp1 = FilePath(value="/a/b.py")
        fp2 = FilePath(value="/a/b.py")
        fp3 = FilePath(value="/a/c.py")
        assert fp1 == fp2
        assert fp1 != fp3

    def test_eq_with_other_type(self):
        fp = FilePath(value="/a/b.py")
        assert fp.__eq__(123) is NotImplemented


class TestSymbolName:
    def test_creation(self):
        sn = SymbolName(value="my_function")
        assert sn.value == "my_function"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            SymbolName(value="")

    def test_eq_with_string(self):
        sn = SymbolName(value="my_function")
        assert sn == "my_function"

    def test_str(self):
        sn = SymbolName(value="my_function")
        assert str(sn) == "my_function"

    def test_hash(self):
        sn1 = SymbolName(value="fn")
        sn2 = SymbolName(value="fn")
        assert hash(sn1) == hash(sn2)

    def test_eq_with_symbolname(self):
        sn1 = SymbolName(value="fn")
        sn2 = SymbolName(value="fn")
        sn3 = SymbolName(value="gn")
        assert sn1 == sn2
        assert sn1 != sn3

    def test_eq_with_other_type(self):
        sn = SymbolName(value="fn")
        assert sn.__eq__(None) is NotImplemented


class TestDirectoryPath:
    def test_creation(self):
        dp = DirectoryPath(value="/some/dir")
        assert dp.value == "/some/dir"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            DirectoryPath(value="")

    def test_normalizes_backslash(self):
        dp = DirectoryPath(value="C:\\Users\\dir")
        assert dp.value == "C:/Users/dir"

    def test_str(self):
        dp = DirectoryPath(value="/some/dir")
        assert str(dp) == "/some/dir"

    def test_hash(self):
        dp1 = DirectoryPath(value="/a/b")
        dp2 = DirectoryPath(value="/a/b")
        assert hash(dp1) == hash(dp2)

    def test_eq_with_directorypath(self):
        dp1 = DirectoryPath(value="/a/b")
        dp2 = DirectoryPath(value="/a/b")
        dp3 = DirectoryPath(value="/a/c")
        assert dp1 == dp2
        assert dp1 != dp3

    def test_eq_with_string(self):
        dp = DirectoryPath(value="/a/b")
        assert dp == "/a/b"

    def test_eq_with_other_type(self):
        dp = DirectoryPath(value="/a/b")
        assert dp.__eq__(3.14) is NotImplemented

    def test_strips_trailing_slash(self):
        dp = DirectoryPath(value="/some/path/")
        assert dp.value == "/some/path"
