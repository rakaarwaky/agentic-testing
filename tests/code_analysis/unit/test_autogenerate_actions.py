import pytest
from unittest.mock import MagicMock, AsyncMock
from src.core.capabilities.autogenerate.actions import AutogenerateTestUseCase
from src.infrastructure.file_system import LocalFileSystem

@pytest.fixture
def mock_analyzer():
    analyzer = MagicMock()
    analyzer.analyze_file = AsyncMock()
    return analyzer

@pytest.fixture
def mock_file_system():
    fs = MagicMock(spec=LocalFileSystem)
    fs.file_exists.return_value = False
    return fs

@pytest.mark.asyncio
async def test_generate_test_success(mock_analyzer, mock_file_system):
    mock_analyzer.analyze_file.return_value = {
        "functions": ["compute_value", "_private_func"],
        "classes": ["Calculator"]
    }
    
    use_case = AutogenerateTestUseCase(mock_analyzer, mock_file_system)
    
    result = await use_case.generate_test("src/math/calc.py")
    
    assert "Generated boilerplate test at" in result
    mock_file_system.makedirs.assert_called_once()
    mock_file_system.write_file.assert_called_once()
    
    # Check the content written
    args, kwargs = mock_file_system.write_file.call_args
    written_content = args[1]
    
    assert "import pytest" in written_content
    assert "import importlib.util" in written_content
    assert "import sys" in written_content
    assert f"spec = importlib.util.spec_from_file_location('calc', 'src/math/calc.py')" in written_content
    assert "from calc import *" in written_content
    assert "def test_compute_value():" in written_content
    assert "def test__private_func():" not in written_content
    assert "class TestCalculator:" in written_content
    assert "def test_instantiation(self):" in written_content

@pytest.mark.asyncio
async def test_generate_test_analyzer_error(mock_analyzer, mock_file_system):
    mock_analyzer.analyze_file.return_value = {
        "error": "SyntaxError: invalid syntax"
    }
    
    use_case = AutogenerateTestUseCase(mock_analyzer, mock_file_system)
    
    result = await use_case.generate_test("bad_file.py")
    
    assert "Error analyzing file: SyntaxError: invalid syntax" in result
    mock_file_system.write_file.assert_not_called()

@pytest.mark.asyncio
async def test_generate_test_absolute_path(mock_analyzer, mock_file_system):
    mock_analyzer.analyze_file.return_value = {
        "functions": ["do_something"],
    }
    
    use_case = AutogenerateTestUseCase(mock_analyzer, mock_file_system)
    
    result = await use_case.generate_test("/absolute/path/to/module.py")
    
    assert "Generated boilerplate test at" in result
    args, kwargs = mock_file_system.write_file.call_args
    written_content = args[1]
    
    # It should use importlib logic with the basename
    assert "import importlib.util" in written_content
    assert "spec = importlib.util.spec_from_file_location('module', '/absolute/path/to/module.py')" in written_content
    assert "from module import *" in written_content
