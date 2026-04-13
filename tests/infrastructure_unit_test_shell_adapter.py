import pytest
from unittest.mock import AsyncMock, patch
from src.infrastructure.shell_adapter import PytestRunner


@pytest.mark.asyncio
async def test_pytest_runner_success():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"PASSED", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is True
        assert "PASSED" in result.output_log
        assert result.error_type is None


@pytest.mark.asyncio
async def test_pytest_runner_assertion_error():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"AssertionError: assert 1 == 2", b"")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "AssertionError"


@pytest.mark.asyncio
async def test_pytest_runner_import_error():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"ImportError: No module named x", b"")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "ImportError"


@pytest.mark.asyncio
async def test_pytest_runner_module_not_found_error():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (
        b"ModuleNotFoundError: No module named y",
        b"",
    )
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "ModuleNotFoundError"


@pytest.mark.asyncio
async def test_pytest_runner_unknown_error():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"Some weird error", b"")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "UnknownError"

@pytest.mark.asyncio
async def test_pytest_runner_assertion_error_parsing_single_quotes():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    output = b"test_file.py:42: in test_foo\nE       AssertionError: assert 'actual' == 'expected'\n"
    mock_proc.communicate.return_value = (output, b"")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "AssertionError"
        assert result.failure is not None
        assert result.failure.line_number == 42
        assert result.failure.message == "AssertionError: Expected 'expected', got 'actual'"

@pytest.mark.asyncio
async def test_pytest_runner_assertion_error_parsing_double_quotes():
    runner = PytestRunner()

    mock_proc = AsyncMock()
    output = b'test_file.py:10: in test_bar\nE  AssertionError: assert "actual" == "expected"\n'
    mock_proc.communicate.return_value = (output, b"")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
        result = await runner.run_test("test_file.py")

        assert result.passed is False
        assert result.error_type == "AssertionError"
        assert result.failure is not None
        assert result.failure.line_number == 10
        assert result.failure.message == "AssertionError: Expected 'expected', got 'actual'"

