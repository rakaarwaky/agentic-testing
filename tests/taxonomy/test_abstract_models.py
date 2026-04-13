import pytest
from src.taxonomy.models import (
    ITestRunner,
    ITestHealer,
    ICodeAnalyzer,
    IQualityAuditor,
    TestResult,
)


def test_abstract_methods_raise_not_implemented():
    # We can't instantiate abstract classes directly with abstractmethods
    # But we can create a subclass that doesn't implement them and call them if they have a body

    class MockRunner(ITestRunner):
        async def run_test(self, test_path: str) -> TestResult:
            return await ITestRunner.run_test(self, test_path)

    class MockHealer(ITestHealer):
        async def attempt_fix(self, result: TestResult) -> bool:
            return await ITestHealer.attempt_fix(self, result)

    class MockAnalyzer(ICodeAnalyzer):
        async def analyze_file(self, file_path: str) -> dict:
            return await ICodeAnalyzer.analyze_file(self, file_path)

    class MockAuditor(IQualityAuditor):
        async def check_coverage(self, target_dir: str) -> dict:
            return await IQualityAuditor.check_coverage(self, target_dir)

    from src.taxonomy.models import ITestGenerator, IFileSystem

    class MockTestGenerator(ITestGenerator):
        async def generate_test(self, source_file: str) -> str:
            return await ITestGenerator.generate_test(self, source_file)

    class MockFileSystem(IFileSystem):
        def read_file(self, path: str) -> str:
            return IFileSystem.read_file(self, path)
        def write_file(self, path: str, content: str) -> None:
            return IFileSystem.write_file(self, path, content)
        def file_exists(self, path: str) -> bool:
            return IFileSystem.file_exists(self, path)
        def read_lines(self, path: str) -> list[str]:
            return IFileSystem.read_lines(self, path)
        def write_lines(self, path: str, lines: list[str]) -> None:
            return IFileSystem.write_lines(self, path, lines)
        def makedirs(self, path: str, exist_ok: bool = True) -> None:
            return IFileSystem.makedirs(self, path, exist_ok)

    runner = MockRunner()
    healer = MockHealer()
    analyzer = MockAnalyzer()
    auditor = MockAuditor()
    generator = MockTestGenerator()
    fs = MockFileSystem()

    import asyncio

    with pytest.raises(NotImplementedError):
        asyncio.run(runner.run_test("test"))

    with pytest.raises(NotImplementedError):
        asyncio.run(
            healer.attempt_fix(TestResult(target="t", passed=False, output_log=""))
        )

    with pytest.raises(NotImplementedError):
        asyncio.run(analyzer.analyze_file("test"))

    with pytest.raises(NotImplementedError):
        asyncio.run(auditor.check_coverage("dir"))

    with pytest.raises(NotImplementedError):
        asyncio.run(generator.generate_test("test"))
        
    with pytest.raises(NotImplementedError):
        fs.read_file("test")

    with pytest.raises(NotImplementedError):
        fs.write_file("test", "test")

    with pytest.raises(NotImplementedError):
        fs.file_exists("test")

    with pytest.raises(NotImplementedError):
        fs.read_lines("test")

    with pytest.raises(NotImplementedError):
        fs.write_lines("test", ["test"])

    with pytest.raises(NotImplementedError):
        fs.makedirs("test")

