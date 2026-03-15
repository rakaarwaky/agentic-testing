import os
from ..core._taxonomy.models import IFileSystem

class LocalFileSystem(IFileSystem):
    """Infrastructure adapter for local file system access."""
    
    def read_file(self, path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        with open(path, "w") as f:
            f.write(content)

    def file_exists(self, path: str) -> bool:
        return os.path.exists(path)
        
    def read_lines(self, path: str) -> list[str]:
        with open(path, "r") as f:
            return f.readlines()
            
    def write_lines(self, path: str, lines: list[str]) -> None:
        with open(path, "w") as f:
            f.writelines(lines)
            
    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        os.makedirs(path, exist_ok=exist_ok)
