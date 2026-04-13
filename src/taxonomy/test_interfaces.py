"""test_interfaces — Interface definitions (moved from test_result_entity for clarity)."""

from abc import ABC, abstractmethod
from .test_result_entity import TestResult


class ITestRunner(ABC):
    """Interface for test execution."""

    @abstractmethod
    async def run_test(self, test_path: str) -> TestResult:
        """Executes a test run for a specific file."""
        ...


class ITestHealer(ABC):
    """Interface for test healing."""

    @abstractmethod
    async def attempt_fix(self, result: TestResult) -> bool:
        """Tries to fix the code based on the TestResult error."""
        ...


class ICodeAnalyzer(ABC):
    """Interface for code analysis."""

    @abstractmethod
    async def analyze_file(self, file_path: str) -> dict:
        """Analyze a source file and return structured data."""
        ...


class IQualityAuditor(ABC):
    """Interface for coverage auditing."""

    @abstractmethod
    async def check_coverage(self, target_dir: str) -> dict:
        """Check coverage for a directory and return metrics."""
        ...


class ITestGenerator(ABC):
    """Interface for test generation."""

    @abstractmethod
    async def generate_test(self, source_file: str) -> str:
        """Generates a test file for a given source file."""
        ...


class IFileSystem(ABC):
    """Interface for file system operations."""

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Reads content from a file."""
        ...

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """Writes content to a file."""
        ...

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Checks if a file exists."""
        ...

    @abstractmethod
    def read_lines(self, path: str) -> list[str]:
        """Reads content as lines."""
        ...

    @abstractmethod
    def write_lines(self, path: str, lines: list[str]) -> None:
        """Writes lines to a file."""
        ...

    @abstractmethod
    def makedirs(self, path: str, exist_ok: bool = True) -> None:
        """Creates a directory and all parent directories."""
        ...
