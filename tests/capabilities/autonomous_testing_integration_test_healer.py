import pytest
import os
import tempfile
from src.capabilities.autonomous_testing_healer import HeuristicHealer
from src.taxonomy.models import TestResult
from src.infrastructure.file_system import LocalFileSystem


@pytest.mark.asyncio
async def test_healer_assertion_patching():
    # Create a temporary test file with a failing assertion
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("def test_demo():\n    assert 'apple' == 'orange'\n")
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        # Simulate a pytest output for our file
        log = "E       AssertionError: assert 'apple' == 'orange'\n"
        result = TestResult(
            target=file_path, passed=False, output_log=log, error_type="AssertionError"
        )

        # Attempt to heal
        healed = await healer.attempt_fix(result)
        assert healed is True

        # Verify the file was patched
        with open(file_path, "r") as f:
            content = f.read()
            assert "assert 'apple' == 'apple'" in content
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.mark.asyncio
async def test_healer_import_patching():
    # Create a temporary test file missing sys.path
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write("import pytest\ndef test_import():\n    pass\n")
        file_path = f.name

    try:
        healer = HeuristicHealer(LocalFileSystem())
        # Simulate an ImportError
        result = TestResult(
            target=file_path,
            passed=False,
            output_log="module 'math' has no attribute 'sqrtt'",
            error_type="ImportError",
        )

        # Attempt to heal (sys.path fix)
        healed = await healer.attempt_fix(result)
        assert healed is True

        # Verify sys.path.insert was added
        with open(file_path, "r") as f:
            content = f.read()
            assert "sys.path.insert(0" in content
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
