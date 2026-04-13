import os
import tempfile
import shutil
from src.infrastructure.file_system import LocalFileSystem

def test_file_exists():
    fs = LocalFileSystem()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_path = f.name
    try:
        assert fs.file_exists(file_path) is True
        assert fs.file_exists("/this_path_really_should_not_exist_xyz123") is False
    finally:
        os.remove(file_path)

def test_makedirs():
    fs = LocalFileSystem()
    test_dir = tempfile.mkdtemp()
    sub_dir = os.path.join(test_dir, "new_folder", "nested")
    
    try:
        assert os.path.exists(sub_dir) is False
        fs.makedirs(sub_dir, exist_ok=True)
        assert os.path.exists(sub_dir) is True
        
        # Calling again with exist_ok=True should not raise an exception
        fs.makedirs(sub_dir, exist_ok=True)
    finally:
        shutil.rmtree(test_dir)
def test_read_write_file():
    fs = LocalFileSystem()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        path = tf.name
    
    try:
        content = "hello world"
        fs.write_file(path, content)
        assert fs.read_file(path) == content
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_read_write_lines():
    fs = LocalFileSystem()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        path = tf.name
    
    try:
        lines = ["line1\n", "line2\n"]
        fs.write_lines(path, lines)
        assert fs.read_lines(path) == lines
    finally:
        if os.path.exists(path):
            os.remove(path)
