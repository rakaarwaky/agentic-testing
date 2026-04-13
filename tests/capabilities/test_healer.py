"""Tests for HeuristicHealer with strategy pattern."""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.capabilities.autonomous_testing_healer import HeuristicHealer
from src.taxonomy.models import TestResult, FailureMetadata
from src.infrastructure.file_system import LocalFileSystem


def _make_fs(allowed_base=None):
    """Create LocalFileSystem scoped to /tmp or custom base."""
    return LocalFileSystem(allowed_base=allowed_base or tempfile.gettempdir())


@pytest.mark.asyncio
async def test_healer_no_error_type():
    healer = HeuristicHealer(_make_fs())
    result = TestResult(target="test.py", passed=False, output_log="Error", error_type=None)
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_unknown_error_type():
    healer = HeuristicHealer(_make_fs())
    result = TestResult(target="test.py", passed=False, output_log="Error", error_type="UnknownExtraError")
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_already_present():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("import sys\nsys.path.insert(0, ...)\ndef test_x(): pass")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        result = TestResult(target=file_path, passed=False, output_log="ImportError", error_type="ImportError")
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_os_error():
    healer = HeuristicHealer(_make_fs())
    # Use a path within /tmp that doesn't exist
    result = TestResult(
        target="/tmp/non_existent_folder_xyz/test.py", passed=False,
        output_log="import pytest", error_type="ImportError",
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_import_no_match():
    healer = HeuristicHealer(_make_fs())
    result = TestResult(target="test.py", passed=False, output_log="Some other error", error_type="AttributeError")
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_not_in_content():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("no trigger here")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        result = TestResult(target=file_path, passed=False, output_log="ImportError", error_type="ImportError")
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_missing_import_already_present():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("# HEALER: Detected missing attribute 'sqrtt' in module 'math'\nimport math")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = "module 'math' has no attribute 'sqrtt'"
        result = TestResult(target=file_path, passed=False, output_log=log, error_type="AttributeError")
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_assertion_no_match():
    healer = HeuristicHealer(_make_fs())
    log = "AssertionError: some other message"
    result = TestResult(target="test.py", passed=False, output_log=log, error_type="AssertionError")
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_assertion_not_modified():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("assert 1 == 2")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(target=file_path, passed=False, output_log=log, error_type="AssertionError")
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_literal():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("def test_foo():\n")
        f.write("    assert 'actual' == 'expected'\n")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path, line_number=2,
                exception_type="AssertionError", message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = _make_fs().read_file(file_path)
        assert "assert 'actual' == 'actual'" in content
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_literal_double_quotes():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write('def test_foo():\n')
        f.write('    assert "actual" == "expected"\n')
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = 'AssertionError: assert "actual" == "expected"'
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path, line_number=2,
                exception_type="AssertionError", message='assert "actual" == "expected"'
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = _make_fs().read_file(file_path)
        assert 'assert "actual" == "actual"' in content
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_variable():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("def test_foo():\n")
        f.write("    exp = 'expected'\n")
        f.write("    act = 'actual'\n")
        f.write("    assert act == exp\n")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path, line_number=4,
                exception_type="AssertionError", message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = _make_fs().read_file(file_path)
        assert "exp = 'actual'" in content
        assert "assert act == exp" in content
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_variable_not_found():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("def test_foo():\n")
        f.write("    # No definition of exp close enough\n")
        for _ in range(12):
            f.write("    pass\n")
        f.write("    assert act == exp\n")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path, line_number=15,
                exception_type="AssertionError", message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_out_of_bounds():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("def test_foo():\n")
        f.write("    assert 1 == 1\n")
        file_path = f.name
    try:
        healer = HeuristicHealer(_make_fs())
        result = TestResult(
            target=file_path, passed=False,
            output_log="AssertionError: assert 'actual' == 'expected'",
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path, line_number=50,
                exception_type="AssertionError", message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_assertion_no_regex_match():
    healer = HeuristicHealer(_make_fs())
    result = TestResult(
        target="test.py", passed=False, output_log="",
        error_type="AssertionError",
        failure=FailureMetadata(file_path="test.py", line_number=1, message="No match")
    )
    healed = await healer.attempt_fix(result)
    assert healed is False
