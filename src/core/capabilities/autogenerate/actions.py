import os
import logging
from ..._taxonomy.models import ITestGenerator, ICodeAnalyzer, IFileSystem

logger = logging.getLogger(__name__)

class AutogenerateTestUseCase(ITestGenerator):
    """Capability to generate boilerplate tests for code (Domain 4)."""

    def __init__(self, analyzer: ICodeAnalyzer, file_system: IFileSystem):
        self.analyzer = analyzer
        self.file_system = file_system

    async def generate_test(self, source_file: str) -> str:
        analysis = await self.analyzer.analyze_file(source_file)
        if "error" in analysis:
            logger.error(f"Failed to generate tests. Analyzer error: {analysis['error']}")
            return f"Error analyzing file: {analysis['error']}"

        base_name = os.path.basename(source_file).replace(".py", "")
        module_path = source_file.replace("/", ".").strip(".")
        # Handle cases where source_file starts with /
        if source_file.startswith("/"):
             # Try to find a relative path or just use the basename if complex
             import_path = base_name 
        else:
             import_path = module_path.replace(".py", "")

        test_content = [
            "import pytest",
            f"from {import_path} import *",
            "",
            f"# Auto-generated tests for {source_file}",
            ""
        ]

        for func in analysis.get("functions", []):
            if func.startswith("_"):
                continue
            test_content.append(f"def test_{func}():")
            test_content.append(f"    # TODO: Implement test for {func}")
            test_content.append("    assert True")
            test_content.append("")

        for cls in analysis.get("classes", []):
            test_content.append(f"class Test{cls}:")
            test_content.append("    def test_instantiation(self):")
            test_content.append(f"        # TODO: Test {cls}")
            test_content.append("        assert True")
            test_content.append("")

        # Save to tests directory
        test_dir = os.path.join(os.getcwd(), "tests")
        if not self.file_system.file_exists(test_dir):
            self.file_system.makedirs(test_dir)
        
        test_file_path = os.path.join(test_dir, f"test_{base_name}.py")
        
        # Avoid overwriting existing tests unless forced? 
        # For now, let's just write and return the path.
        self.file_system.write_file(test_file_path, "\n".join(test_content))

        logger.info(f"Generated boilerplate test at {test_file_path}")
        return f"Generated boilerplate test at {test_file_path}"
