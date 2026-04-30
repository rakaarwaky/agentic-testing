import pytest
import uuid
from pathlib import Path
from src.capabilities.autonomous_testing_healing_adapter import HeuristicHealer
from src.contract import TestResult
from src.infrastructure.file_system_provider import LocalFileSystem


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_healer_assertion_patching():
    # Create a unique temp dir within the project root to satisfy path validation
    tmp_dir = PROJECT_ROOT / f"_test_tmp_{uuid.uuid4().hex[:8]}"
    tmp_dir.mkdir(exist_ok=True)
    file_path = tmp_dir / "test_heal_assertion.py"
    file_path.write_text("def test_demo():\n    assert 'apple' == 'orange'\n")

    try:
        healer = HeuristicHealer(LocalFileSystem(str(PROJECT_ROOT)))
        log = "E       AssertionError: assert 'apple' == 'orange'\n"
        result = TestResult(
            target=str(file_path), passed=False, output_log=log, error_type="AssertionError"
        )

        healed = await healer.attempt_fix(result)
        assert healed is True

        content = file_path.read_text()
        assert "assert 'apple' == 'apple'" in content
    finally:
        import shutil
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_healer_import_patching():
    tmp_dir = PROJECT_ROOT / f"_test_tmp_{uuid.uuid4().hex[:8]}"
    tmp_dir.mkdir(exist_ok=True)
    file_path = tmp_dir / "test_heal_import.py"
    file_path.write_text("import pytest\ndef test_import():\n    pass\n")

    try:
        healer = HeuristicHealer(LocalFileSystem(str(PROJECT_ROOT)))
        result = TestResult(
            target=str(file_path),
            passed=False,
            output_log="module 'math' has no attribute 'sqrtt'",
            error_type="ImportError",
        )

        healed = await healer.attempt_fix(result)
        assert healed is True

        content = file_path.read_text()
        assert "sys.path.insert(0" in content
    finally:
        import shutil
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
