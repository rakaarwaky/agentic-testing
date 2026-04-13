"""Tests for LocalFileSystem adapter."""
import os
import tempfile
import shutil
from src.infrastructure.file_system import LocalFileSystem


def _make_fs():
    """Create LocalFileSystem scoped to a temp directory."""
    td = tempfile.mkdtemp()
    return LocalFileSystem(allowed_base=td), td


def test_file_exists():
    fs, td = _make_fs()
    file_path = os.path.join(td, "test.txt")
    try:
        with open(file_path, "w") as f:
            f.write("hello")
        assert fs.file_exists("test.txt") is True
        assert fs.file_exists("nonexistent.txt") is False
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_makedirs():
    fs, td = _make_fs()
    sub_dir = os.path.join(td, "new_folder", "nested")
    rel_sub = os.path.relpath(sub_dir, td)

    try:
        assert os.path.exists(sub_dir) is False
        fs.makedirs(rel_sub, exist_ok=True)
        assert os.path.exists(sub_dir) is True
        fs.makedirs(rel_sub, exist_ok=True)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_read_write_file():
    fs, td = _make_fs()
    try:
        content = "hello world"
        fs.write_file("test.txt", content)
        assert fs.read_file("test.txt") == content
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_read_write_lines():
    fs, td = _make_fs()
    try:
        lines = ["line1\n", "line2\n"]
        fs.write_lines("test.txt", lines)
        assert fs.read_lines("test.txt") == lines
    finally:
        shutil.rmtree(td, ignore_errors=True)
