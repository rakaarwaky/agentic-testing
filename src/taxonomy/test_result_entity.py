"""test_result_entity — Test domain entities and interfaces."""

from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod


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
        if self.failure and self.failure.line_number:
            return f"{self.target}:{self.failure.line_number}"
        return self.target

    @property
    def error_code(self) -> str:
        return self.error_type or "UNKNOWN"

    @property
    def identity(self) -> str:
        return f"{self.target}:{self.error_type or 'pass'}"

    def mark_healed(self, attempts: int):
        """Mark this result as healed after retry."""
        self.healed = True
        self.healing_attempts = attempts


class ITestRunner(ABC):
    """Interface for test execution."""

    @abstractmethod
    async def run_test(self, test_path: str) -> TestResult:
        ...


class ITestHealer(ABC):
    """Interface for test healing."""

    @abstractmethod
    async def attempt_fix(self, result: TestResult) -> bool:
        ...


class ICodeAnalyzer(ABC):
    """Interface for code analysis."""

    @abstractmethod
    async def analyze_file(self, file_path: str) -> dict:
        ...


class IQualityAuditor(ABC):
    """Interface for coverage auditing."""

    @abstractmethod
    async def check_coverage(self, target_dir: str) -> dict:
        ...


class ITestGenerator(ABC):
    """Interface for test generation."""

    @abstractmethod
    async def generate_test(self, source_file: str) -> str:
        ...


class IFileSystem(ABC):
    """Interface for file system operations."""

    @abstractmethod
    def read_file(self, path: str) -> str:
        ...

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        ...

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        ...

    @abstractmethod
    def read_lines(self, path: str) -> list[str]:
        ...

    @abstractmethod
    def write_lines(self, path: str, lines: list[str]) -> None:
        ...

    @abstractmethod
    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        ...
