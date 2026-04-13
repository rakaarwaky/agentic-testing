import logging
from src.taxonomy import ITestHealer, TestResult, IFileSystem
from .test_healing_actions import (
    FixStrategy,
    ImportErrorStrategy,
    AttributeErrorStrategy,
    TypeErrorStrategy,
    NameErrorStrategy,
    AssertionErrorStrategy,
)

logger = logging.getLogger(__name__)


class HeuristicHealer(ITestHealer):
    """Rule-based healer for common test issues (Capability).

    Uses the Strategy Pattern to delegate fixes to specialized strategies.
    """

    def __init__(self, file_system: IFileSystem):
        self.file_system = file_system
        self._backup_created = False
        self._strategies: list[FixStrategy] = [
            ImportErrorStrategy(file_system),
            AttributeErrorStrategy(file_system),
            AssertionErrorStrategy(file_system),
            TypeErrorStrategy(file_system),
            NameErrorStrategy(file_system),
        ]

    def _create_backup(self, file_path: str) -> str | None:
        """Create backup before modifying a file. Returns backup path."""
        import shutil
        backup_path = file_path + '.healer.bak'
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            self._backup_created = True
            return backup_path
        except OSError as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    async def attempt_fix(self, result: TestResult) -> bool:
        """Attempts to fix based on error_type using strategy pattern."""
        if not result.error_type:
            return False

        # Create backup before any fix attempt
        file_path = (
            result.failure.file_path
            if result.failure and result.failure.file_path
            else result.target
        )
        if file_path:
            self._create_backup(file_path)

        # Find and apply the first matching strategy
        for strategy in self._strategies:
            if strategy.can_fix(result):
                return strategy.apply_fix(result)

        return False
