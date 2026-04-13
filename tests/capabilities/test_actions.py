import pytest
from unittest.mock import AsyncMock
from src.capabilities.autonomous_testing_actions import RunTestWithHealingUseCase
from src.taxonomy import TestResult


@pytest.mark.asyncio
async def test_execute_passed_first_time():
    runner = AsyncMock()
    healer = AsyncMock()

    expected_result = TestResult(target="test.py", passed=True, output_log="Success")
    runner.run_test.return_value = expected_result

    use_case = RunTestWithHealingUseCase(runner, healer)
    result = await use_case.execute("test.py")

    assert result.passed is True
    assert runner.run_test.call_count == 1
    assert healer.attempt_fix.call_count == 0


@pytest.mark.asyncio
async def test_execute_fails_then_heals():
    runner = AsyncMock()
    healer = AsyncMock()

    fail_result = TestResult(target="test.py", passed=False, output_log="Error")
    pass_result = TestResult(target="test.py", passed=True, output_log="Fixed")

    runner.run_test.side_effect = [fail_result, pass_result]
    healer.attempt_fix.return_value = True

    use_case = RunTestWithHealingUseCase(runner, healer)
    result = await use_case.execute("test.py", max_retries=1)

    assert result.passed is True
    assert result.healed is True
    assert result.healing_attempts == 1
    assert runner.run_test.call_count == 2
    assert healer.attempt_fix.call_count == 1


@pytest.mark.asyncio
async def test_execute_fails_no_healing():
    runner = AsyncMock()
    healer = AsyncMock()

    fail_result = TestResult(target="test.py", passed=False, output_log="Fatal")
    runner.run_test.return_value = fail_result
    healer.attempt_fix.return_value = False

    use_case = RunTestWithHealingUseCase(runner, healer)
    result = await use_case.execute("test.py", max_retries=5)

    assert result.passed is False
    assert runner.run_test.call_count == 1
    assert healer.attempt_fix.call_count == 1
