"""test_event — Domain event types for agentic-testing."""

from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class TestRunStarted:
    """Test run began."""
    path: str
    heal_enabled: bool = False
    max_retries: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class TestRunCompleted:
    """Test run finished."""
    path: str
    passed: bool
    healed: bool = False
    healing_attempts: int = 0
    coverage_pct: float = 0.0
    duration_ms: float = 0.0
    timestamp: str = ""

    @property
    def is_passing(self) -> bool:
        return self.passed or self.coverage_pct >= 80.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class TestRunFailed:
    """Test run failed."""
    path: str
    error_type: str
    error_message: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class HealApplied:
    """Fix applied to a test file."""
    path: str
    error_type: str
    success: bool
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
