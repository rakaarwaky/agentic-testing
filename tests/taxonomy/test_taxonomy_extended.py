"""Tests for taxonomy: agentic_error, test_event, lint_identifier uncovered lines."""

from src.taxonomy.agentic_error import (
    AgenticTestingError,
    InfrastructureError,
)
from src.taxonomy.test_event import (
    TestRunStarted,
    TestRunCompleted,
    TestRunFailed,
    HealApplied,
)


# ── agentic_error: __str__ with cause ──


def test_error_str_with_cause():
    """__str__ includes cause when provided."""
    err = AgenticTestingError("main msg", cause="root cause")
    assert "main msg" in str(err)
    assert "root cause" in str(err)
    assert "caused by" in str(err)


def test_error_str_without_cause():
    """__str__ returns just message when no cause."""
    err = AgenticTestingError("just message")
    assert str(err) == "just message"


def test_error_attributes():
    """Error stores message and cause."""
    err = InfrastructureError("infra fail", cause="disk full")
    assert err.message == "infra fail"
    assert err.cause == "disk full"


# ── test_event: TestRunStarted ──


def test_test_run_started_auto_timestamp():
    """Auto-generates timestamp when not provided."""
    event = TestRunStarted(path="/test.py")
    assert event.timestamp != ""
    assert event.path == "/test.py"
    assert event.heal_enabled is False
    assert event.max_retries == 0


def test_test_run_started_custom_timestamp():
    """Uses provided timestamp."""
    event = TestRunStarted(path="/test.py", timestamp="2025-01-01T00:00:00")
    assert event.timestamp == "2025-01-01T00:00:00"


def test_test_run_started_with_heal():
    """Heal options are stored."""
    event = TestRunStarted(path="/test.py", heal_enabled=True, max_retries=3)
    assert event.heal_enabled is True
    assert event.max_retries == 3


# ── test_event: TestRunCompleted ──


def test_test_run_completed_auto_timestamp():
    """Auto-generates timestamp."""
    event = TestRunCompleted(path="/test.py", passed=True)
    assert event.timestamp != ""


def test_test_run_completed_is_passing_passed():
    """is_passing is True when test passed."""
    event = TestRunCompleted(path="/test.py", passed=True, coverage_pct=50.0)
    assert event.is_passing is True


def test_test_run_completed_is_passing_high_coverage():
    """is_passing is True when coverage >= 80 even if not passed."""
    event = TestRunCompleted(path="/test.py", passed=False, coverage_pct=85.0)
    assert event.is_passing is True


def test_test_run_completed_is_passing_false():
    """is_passing is False when not passed and coverage < 80."""
    event = TestRunCompleted(path="/test.py", passed=False, coverage_pct=50.0)
    assert event.is_passing is False


def test_test_run_completed_healed():
    """Healing info stored."""
    event = TestRunCompleted(
        path="/test.py", passed=True, healed=True, healing_attempts=2, duration_ms=1500.0
    )
    assert event.healed is True
    assert event.healing_attempts == 2
    assert event.duration_ms == 1500.0


def test_test_run_completed_custom_timestamp():
    """Preserves custom timestamp (exits __post_init__ early)."""
    event = TestRunCompleted(path="/test.py", passed=True, timestamp="2025-01-01T00:00:00Z")
    assert event.timestamp == "2025-01-01T00:00:00Z"


# ── test_event: TestRunFailed ──


def test_test_run_failed_auto_timestamp():
    """Auto-generates timestamp."""
    event = TestRunFailed(path="/test.py", error_type="ImportError", error_message="no module")
    assert event.timestamp != ""
    assert event.error_type == "ImportError"


def test_test_run_failed_custom_timestamp():
    """Preserves custom timestamp (exits __post_init__ early)."""
    event = TestRunFailed(path="/test.py", error_type="IOError", error_message="fail", timestamp="2025-06-01T00:00:00Z")
    assert event.timestamp == "2025-06-01T00:00:00Z"


# ── test_event: HealApplied ──


def test_heal_applied_auto_timestamp():
    """Auto-generates timestamp."""
    event = HealApplied(path="/test.py", error_type="SyntaxError", success=True)
    assert event.timestamp != ""
    assert event.success is True


def test_heal_applied_failed():
    """Failed heal."""
    event = HealApplied(path="/test.py", error_type="TypeError", success=False)
    assert event.success is False


def test_heal_applied_custom_timestamp():
    """Preserves custom timestamp (exits __post_init__ early)."""
    event = HealApplied(path="/test.py", error_type="SyntaxError", success=True, timestamp="2025-03-15T12:00:00Z")
    assert event.timestamp == "2025-03-15T12:00:00Z"


def test_test_run_started_custom_timestamp():
    """Preserves custom timestamp for TestRunStarted (exits __post_init__ early)."""
    event = TestRunStarted(path="/test.py", timestamp="2025-04-20T10:00:00Z")
    assert event.timestamp == "2025-04-20T10:00:00Z"
