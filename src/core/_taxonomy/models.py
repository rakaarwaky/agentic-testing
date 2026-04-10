from dataclasses import dataclass
from typing import Optional, Any
from abc import ABC, abstractmethod


@dataclass
class FailureMetadata:
    """Detailed metadata for a test failure (Taxonomy)."""
    file_path: str
    line_number: Optional[int] = None
    exception_type: Optional[str] = None
    message: Optional[str] = None


@dataclass
class TestResult:
    """Core entity representing the outcome of a test execution (Taxonomy)."""

    target: str
    passed: bool
    output_log: str
    error_type: Optional[str] = None
    failure: Optional[FailureMetadata] = None
    coverage_pct: float = 0.0
    duration: float = 0.0
    healed: bool = False
    healing_attempts: int = 0

    # Ensure pytest doesn't collect this as a test class
    __test__ = False


class ITestRunner(ABC):
    @abstractmethod
    async def run_test(self, test_path: str) -> TestResult:
        """Executes a pytest run for a specific file."""
        raise NotImplementedError()


class ITestHealer(ABC):
    @abstractmethod
    async def attempt_fix(self, result: TestResult) -> bool:
        """Tries to fix the code based on the TestResult error."""
        raise NotImplementedError()


class ICodeAnalyzer(ABC):
    @abstractmethod
    async def analyze_file(self, file_path: str) -> dict[str, Any]:
        raise NotImplementedError()


class IQualityAuditor(ABC):
    @abstractmethod
    async def check_coverage(self, target_dir: str) -> dict[str, Any]:
        raise NotImplementedError()
class ITestGenerator(ABC):
    @abstractmethod
    async def generate_test(self, source_file: str) -> str:
        """Generates a unit test file for a given source file."""
        raise NotImplementedError()


class IFileSystem(ABC):
    @abstractmethod
    def read_file(self, path: str) -> str:
        """Reads content from a file."""
        raise NotImplementedError()

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """Writes content to a file."""
        raise NotImplementedError()

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Checks if a file exists."""
        raise NotImplementedError()
        
    @abstractmethod
    def read_lines(self, path: str) -> list[str]:
        """Reads content as lines."""
        raise NotImplementedError()
        
    @abstractmethod
    def write_lines(self, path: str, lines: list[str]) -> None:
        """Writes lines to a file."""
        raise NotImplementedError()
        
    @abstractmethod
    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        """Creates a directory and all parent directories."""
        raise NotImplementedError()
