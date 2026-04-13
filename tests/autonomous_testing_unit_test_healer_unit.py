import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.capabilities.autonomous_testing_healer import HeuristicHealer
from src.taxonomy.models import TestResult, FailureMetadata
from src.infrastructure.file_system import LocalFileSystem


@pytest.mark.asyncio
async def test_healer_no_error_type():
    healer = HeuristicHealer(LocalFileSystem())
    result = TestResult(
        target="test.py", passed=False, output_log="Error", error_type=None
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_unknown_error_type():
    healer = HeuristicHealer(LocalFileSystem())
    result = TestResult(
        target="test.py",
        passed=False,
        output_log="Error",
        error_type="UnknownExtraError",
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_already_present():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("import sys\nsys.path.insert(0, ...)\ndef test_x(): pass")
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        result = TestResult(
            target=file_path,
            passed=False,
            output_log="ImportError",
            error_type="ImportError",
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_missing_import_attribute():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("import math\ndef test_math(): math.sqrtt(1)")
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        log = "module 'math' has no attribute 'sqrtt'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AttributeError"
        )
        healed = await healer.attempt_fix(result)
        assert healed is True

        with open(file_path, "r") as f:
            content = f.read()
            assert (
                "HEALER: Detected missing attribute 'sqrtt' in module 'math'" in content
            )
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_os_error():
    healer = HeuristicHealer(LocalFileSystem())
    # Path that should fail
    result = TestResult(
        target="/non_existent_folder/test.py",
        passed=False,
        output_log="import pytest",
        error_type="ImportError",
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_import_no_match():
    healer = HeuristicHealer(LocalFileSystem())
    # Log doesn't match re
    result = TestResult(
        target="test.py",
        passed=False,
        output_log="Some other error",
        error_type="AttributeError",
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_import_exception():
    with patch("builtins.open", side_effect=Exception("Read error")):
        healer = HeuristicHealer(LocalFileSystem())
        log = "module 'x' has no attribute 'y'"
        result = TestResult(
            target="test.py", passed=False, output_log=log, error_type="AttributeError"
        )
        healed = await healer.attempt_fix(result)
        assert healed is False


@pytest.mark.asyncio
async def test_healer_assertion_exception():
    with patch("builtins.open", side_effect=Exception("Read error")):
        healer = HeuristicHealer(LocalFileSystem())
        log = "AssertionError: assert 'a' == 'b'"
        result = TestResult(
            target="test.py", passed=False, output_log=log, error_type="AssertionError"
        )
        healed = await healer.attempt_fix(result)
        assert healed is False


@pytest.mark.asyncio
async def test_healer_fix_missing_sys_path_not_in_content():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("no trigger here")
        file_path = f.name
    try:
        healer = HeuristicHealer(LocalFileSystem())
        result = TestResult(
            target=file_path,
            passed=False,
            output_log="ImportError",
            error_type="ImportError",
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_missing_import_already_present():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        module_name, attr_name = "math", "sqrtt"
        fix_hint = f"# HEALER: Detected missing attribute '{attr_name}' in module '{module_name}'\n"
        f.write(fix_hint + "import math")
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        log = "module 'math' has no attribute 'sqrtt'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AttributeError"
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_assertion_no_match():
    healer = HeuristicHealer(LocalFileSystem())
    # Log doesn't match the specific regex
    log = "AssertionError: some other message"
    result = TestResult(
        target="test.py", passed=False, output_log=log, error_type="AssertionError"
    )
    healed = await healer.attempt_fix(result)
    assert healed is False


@pytest.mark.asyncio
async def test_healer_assertion_not_modified():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("assert 1 == 2")  # No 'expected' string in single quotes
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError"
        )
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
        healer = HeuristicHealer(LocalFileSystem())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path,
            passed=False,
            output_log=log,
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path,
                line_number=2,
                exception_type="AssertionError",
                message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = LocalFileSystem().read_file(file_path)
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
        healer = HeuristicHealer(LocalFileSystem())
        log = 'AssertionError: assert "actual" == "expected"'
        result = TestResult(
            target=file_path,
            passed=False,
            output_log=log,
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path,
                line_number=2,
                exception_type="AssertionError",
                message='assert "actual" == "expected"'
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = LocalFileSystem().read_file(file_path)
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
        healer = HeuristicHealer(LocalFileSystem())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path,
            passed=False,
            output_log=log,
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path,
                line_number=4,
                exception_type="AssertionError",
                message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is True
        content = LocalFileSystem().read_file(file_path)
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
        healer = HeuristicHealer(LocalFileSystem())
        log = "AssertionError: assert 'actual' == 'expected'"
        result = TestResult(
            target=file_path,
            passed=False,
            output_log=log,
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path,
                line_number=15,
                exception_type="AssertionError",
                message="assert 'actual' == 'expected'"
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
        healer = HeuristicHealer(LocalFileSystem())
        result = TestResult(
            target=file_path,
            passed=False,
            output_log="AssertionError: assert 'actual' == 'expected'",
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path=file_path,
                line_number=50, # Out of bounds
                exception_type="AssertionError",
                message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is False
    finally:
        os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_fix_assertion_read_exception():
    with patch("src.infrastructure.file_system.LocalFileSystem.read_lines", side_effect=Exception("Read error")):
        healer = HeuristicHealer(LocalFileSystem())
        result = TestResult(
            target="test.py",
            passed=False,
            output_log="AssertionError: assert 'actual' == 'expected'",
            error_type="AssertionError",
            failure=FailureMetadata(
                file_path="test.py",
                line_number=2,
                exception_type="AssertionError",
                message="assert 'actual' == 'expected'"
            )
        )
        healed = await healer.attempt_fix(result)
        assert healed is False


        assert healed is False


@pytest.mark.asyncio
async def test_healer_assertion_no_regex_match():
    healer = HeuristicHealer(LocalFileSystem())
    # Failure with line number but message doesn't match assert regex
    result = TestResult(
        target="test.py",
        passed=False,
        output_log="",
        error_type="AssertionError",
        failure=FailureMetadata(file_path="test.py", line_number=1, message="No match")
    )
    healed = await healer.attempt_fix(result)
    assert healed is False  # Hits line 93


@pytest.mark.asyncio
async def test_healer_assertion_exception_handling():
    fs = MagicMock()
    fs.read_lines.side_effect = Exception("error")
    healer = HeuristicHealer(fs)
    result = TestResult(
        target="test.py",
        passed=False,
        output_log="AssertionError: assert 'a' == 'b'",
        error_type="AssertionError",
        failure=FailureMetadata(file_path="test.py", line_number=1, message="assert 'a' == 'b'")
    )
    healed = await healer.attempt_fix(result)
    assert healed is False  # Hits line 125


@pytest.mark.asyncio
async def test_healer_legacy_assertion_exception_handling():
    fs = MagicMock()
    fs.read_lines.side_effect = Exception("error")
    healer = HeuristicHealer(fs)
    # No line number triggers legacy
    result = TestResult(
        target="test.py",
        passed=False,
        output_log="AssertionError: assert 'a' == 'b'",
        error_type="AssertionError"
    )
    healed = await healer.attempt_fix(result)
    assert healed is False  # Hits line 147/148
