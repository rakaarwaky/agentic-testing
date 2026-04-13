"""test_result_entity — Test domain entities and interfaces."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FailureMetadata:
    """Detailed metadata for a test failure."""
    file_path: str = ""
    line_number: Optional[int] = None
    exception_type: Optional[str] = None
    message: Optional[str] = None


@dataclass
class TestResult:
    """Core entity representing test execution outcome."""

    target: str
    passed: bool
    output_log: str
    error_type: Optional[str] = None
    failure: Optional[FailureMetadata] = None
    coverage_pct: float = 0.0
    duration: float = 0.0
    healed: bool = False
    healing_attempts: int = 0

    __test__ = False

    @property
    def position(self) -> str:
        """Return target:line if failure has line number, else just target."""
        if self.failure and self.failure.line_number:
            return f"{self.target}:{self.failure.line_number}"
        return self.target

    @property
    def error_code(self) -> str:
        """Return error type or 'UNKNOWN' as string identifier."""
        return self.error_type or "UNKNOWN"

    @property
    def identity(self) -> str:
        """Return unique identity string: target:error_type or target:pass."""
        return f"{self.target}:{self.error_type or 'pass'}"

    def mark_healed(self, attempts: int):
        """Mark this result as healed after retry."""
        self.healed = True
        self.healing_attempts = attempts
