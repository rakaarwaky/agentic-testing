"""Tests for autogenerate test use case."""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.capabilities.autogenerate_actions import AutogenerateTestUseCase


@pytest.mark.asyncio
async def test_generate_test_success():
    mock_analyzer = AsyncMock()
    mock_analyzer.analyze_file.return_value = {
        "file": "sample.py",
        "classes": ["MyClass"],
        "functions": ["foo", "bar"],
    }
    mock_fs = MagicMock()
    mock_fs.file_exists.return_value = False
    mock_fs.makedirs.return_value = None
    mock_fs.write_file.return_value = None

    use_case = AutogenerateTestUseCase(mock_analyzer, mock_fs)
    result = await use_case.generate_test("sample.py")
    assert "Generated" in result
    mock_fs.write_file.assert_called_once()


@pytest.mark.asyncio
async def test_generate_test_analyzer_error():
    mock_analyzer = AsyncMock()
    mock_analyzer.analyze_file.return_value = {"error": "parse error"}
    mock_fs = MagicMock()

    use_case = AutogenerateTestUseCase(mock_analyzer, mock_fs)
    result = await use_case.generate_test("bad.py")
    assert "Error" in result


@pytest.mark.asyncio
async def test_generate_test_existing_test_dir():
    mock_analyzer = AsyncMock()
    mock_analyzer.analyze_file.return_value = {
        "file": "sample.py",
        "classes": [],
        "functions": ["foo"],
    }
    mock_fs = MagicMock()
    mock_fs.file_exists.return_value = True
    mock_fs.makedirs.return_value = None
    mock_fs.write_file.return_value = None

    use_case = AutogenerateTestUseCase(mock_analyzer, mock_fs)
    result = await use_case.generate_test("sample.py")
    assert "Generated" in result
    # Should not call makedirs if test dir exists
    mock_fs.makedirs.assert_not_called()
