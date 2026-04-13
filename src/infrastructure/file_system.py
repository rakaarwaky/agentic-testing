import os
from pathlib import Path
from ..taxonomy import IFileSystem


class PathValidationError(ValueError):
    """Raised when a path fails validation."""
    pass


class LocalFileSystem(IFileSystem):
    """Infrastructure adapter for local file system access."""

    def __init__(self, allowed_base: str | None = None):
        """Initialize with optional allowed base directory.

        Args:
            allowed_base: If set, all file operations are restricted to this directory.
                         Defaults to current working directory.
        """
        self.allowed_base = Path(allowed_base).resolve() if allowed_base else Path.cwd().resolve()

    def _validate_path(self, path: str) -> Path:
        """Validate that path is within allowed directory.

        Fix #8: Prevents path traversal attacks by resolving to absolute path
        and verifying it's within the allowed base directory.
        """
        p = Path(path)
        # Resolve relative paths relative to allowed_base, not CWD
        if not p.is_absolute():
            resolved = (self.allowed_base / p).resolve()
        else:
            resolved = p.resolve()
        try:
            resolved.relative_to(self.allowed_base)
        except ValueError:
            raise PathValidationError(
                f"Path '{path}' is outside allowed directory '{self.allowed_base}'"
            )
        return resolved

    def read_file(self, path: str) -> str:
        validated = self._validate_path(path)
        with open(validated, "r") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        validated = self._validate_path(path)
        validated.parent.mkdir(parents=True, exist_ok=True)
        with open(validated, "w") as f:
            f.write(content)

    def file_exists(self, path: str) -> bool:
        try:
            validated = self._validate_path(path)
            return validated.exists()
        except PathValidationError:
            return False

    def read_lines(self, path: str) -> list[str]:
        validated = self._validate_path(path)
        with open(validated, "r") as f:
            return f.readlines()

    def write_lines(self, path: str, lines: list[str]) -> None:
        validated = self._validate_path(path)
        validated.parent.mkdir(parents=True, exist_ok=True)
        with open(validated, "w") as f:
            f.writelines(lines)

    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        validated = self._validate_path(path)
        validated.mkdir(parents=True, exist_ok=exist_ok)
