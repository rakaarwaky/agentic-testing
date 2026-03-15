import pytest
from src.core.capabilities.code_analysis.actions import AstAnalyzer
import os


@pytest.mark.asyncio
async def test_ast_analyzer_basic():
    analyzer = AstAnalyzer()
    # Create a dummy file for analysis
    dummy_file = "dummy_test.py"
    with open(dummy_file, "w") as f:
        f.write(
            "class TestClass:\n    def method(self):\n        pass\n\ndef function():\n    pass"
        )

    try:
        result = await analyzer.analyze_file(dummy_file)
        assert result["classes"] == ["TestClass"]
        assert "function" in result["functions"]
        assert result["complexity_score"] > 0
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


@pytest.mark.asyncio
async def test_ast_analyzer_error():
    analyzer = AstAnalyzer()
    result = await analyzer.analyze_file("non_existent.py")
    assert "error" in result
