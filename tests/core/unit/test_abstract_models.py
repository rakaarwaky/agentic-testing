import pytest
from src.core._taxonomy.models import (
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

    runner = MockRunner()
    healer = MockHealer()
    analyzer = MockAnalyzer()
    auditor = MockAuditor()

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
