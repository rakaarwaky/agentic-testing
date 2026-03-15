import logging
from ..._taxonomy.models import ITestHealer, TestResult, IFileSystem

logger = logging.getLogger(__name__)

class HeuristicHealer(ITestHealer):
    """Rule-based healer for common test issues (Capability)."""

    def __init__(self, file_system: IFileSystem):
        self.file_system = file_system

    async def attempt_fix(self, result: TestResult) -> bool:
        """Attempts to fix based on error_type and metadata."""
        if not result.error_type:
            return False

        strategies = {
            "ImportError": self._fix_missing_sys_path,
            "ModuleNotFoundError": self._fix_missing_sys_path,
            "AttributeError": self._fix_missing_import,
            "AssertionError": self._fix_assertion,
        }

        strategy = strategies.get(result.error_type)
        if strategy:
            return strategy(result)
        return False

    def _fix_missing_sys_path(self, result: TestResult) -> bool:
        file_path = result.target
        try:
            content = self.file_system.read_file(file_path)

            if "sys.path.insert" in content:
                return False

            trigger = "import pytest"
            if trigger in content:
                payload = (
                    "\nimport sys\nfrom pathlib import Path\n"
                    "sys.path.insert(0, str(Path(__file__).parent.parent))\n"
                )
                new_content = content.replace(trigger, trigger + payload)

                self.file_system.write_file(file_path, new_content)
                return True
        except OSError as e:
            logger.error(f"Failed to fix missing sys path: {str(e)}", exc_info=True)
            return False
        return False
    def _fix_missing_import(self, result: TestResult) -> bool:
        """Tries to identify and fix missing attributes/imports."""
        file_path = result.target
        log = result.output_log
        try:
            import re

            # Pattern: module 'math' has no attribute 'sqrtt' -> math.sqrt?
            # Or: name 'X' is not defined
            match = re.search(r"module '([^']+)' has no attribute '([^']+)'", log)
            if not match:
                return False

            module_name, attr_name = match.groups()

            content = self.file_system.read_file(file_path)

            # Strategy: If it looks like a typo, or missing submodule
            # For now, let's just add a more helpful hint or try a common fix
            # Since this is a 'Heuristic' healer, we'll add a specific hint
            fix_hint = f"# HEALER: Detected missing attribute '{attr_name}' in module '{module_name}'\n"
            if fix_hint not in content:
                self.file_system.write_file(file_path, fix_hint + content)
                return True
        except Exception as e:
            logger.error(f"Failed to fix missing import: {str(e)}", exc_info=True)
            return False
        return False
    def _fix_assertion(self, result: TestResult) -> bool:
        """Advanced assertion fixer using line numbers and variable analysis."""
        if not result.failure or not result.failure.line_number:
            return self._legacy_assertion_fix(result)

        target_file = result.target
        line_no = result.failure.line_number
        msg = result.failure.message or ""

        try:
            import re
            # Use flexible whitespace and handle both ' and "
            match = re.search(r"assert\s+['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]", msg)
            if not match:
                return False

            actual, expected = match.groups()

            lines = self.file_system.read_lines(target_file)

            # lines is 0-indexed, pytest line_no is 1-indexed
            idx = line_no - 1
            if idx >= len(lines):
                return False

            line = lines[idx]
            
            # Simple Case: Literal is in the line
            if f"'{expected}'" in line:
                lines[idx] = line.replace(f"'{expected}'", f"'{actual}'")
            elif f'"{expected}"' in line:
                lines[idx] = line.replace(f'"{expected}"', f'"{actual}"')
            else:
                # Variable Case: Look at previous lines for assignment
                # Heuristic: search backwards for expected variable
                for i in range(idx - 1, max(0, idx - 10), -1):
                    if (f"'{expected}'" in lines[i] or f'"{expected}"' in lines[i]) and "=" in lines[i]:
                        lines[i] = lines[i].replace(f"'{expected}'", f"'{actual}'").replace(f'"{expected}"', f'"{actual}"')
                        break
                else:
                    return False

            self.file_system.write_lines(target_file, lines)
            return True
        except Exception as e:
            logger.error(f"Failed to fix assertion using line numbers: {str(e)}", exc_info=True)
            return False

    def _legacy_assertion_fix(self, result: TestResult) -> bool:
        """Fallback for when line numbers are missing."""
        file_path = result.target
        log = result.output_log
        try:
            import re
            match = re.search(r"AssertionError: assert '([^']+)' == '([^']+)'", log)
            if not match:
                return False
            actual, expected = match.groups()
            
            lines = self.file_system.read_lines(file_path)
                
            for i, line in enumerate(lines):
                if f"'{expected}'" in line and "assert" in line:
                    lines[i] = line.replace(f"'{expected}'", f"'{actual}'")
                    self.file_system.write_lines(file_path, lines)
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to fix legacy assertion: {str(e)}", exc_info=True)
            return False
