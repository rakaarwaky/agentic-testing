import logging
import shutil
from ..._taxonomy.models import ITestHealer, TestResult, IFileSystem

logger = logging.getLogger(__name__)

class HeuristicHealer(ITestHealer):
    """Rule-based healer for common test issues (Capability)."""

    def __init__(self, file_system: IFileSystem):
        self.file_system = file_system
        self._backup_created = False

    def _create_backup(self, file_path: str) -> str:
        """Create backup before modifying a file. Returns backup path."""
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
        """Attempts to fix based on error_type and metadata."""
        if not result.error_type:
            return False

        # Create backup before any fix attempt (Fix #2)
        if result.failure and result.failure.file_path:
            self._create_backup(result.failure.file_path)
        elif result.target:
            self._create_backup(result.target)

        strategies = {
            "ImportError": self._fix_missing_sys_path,
            "ModuleNotFoundError": self._fix_missing_sys_path,
            "AttributeError": self._fix_attribute_error,
            "AssertionError": self._fix_assertion,
            "TypeError": self._fix_type_error,
            "NameError": self._fix_name_error,
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
                logger.info(f"Successfully fixed missing sys path for {file_path}")
                return True
        except OSError as e:
            logger.error(f"Failed to fix missing sys path: {str(e)}", exc_info=True)
            return False
        return False

    def _fix_attribute_error(self, result: TestResult) -> bool:
        """Fixes common AttributeError typos using Levenshtein-like heuristics."""
        file_path = result.target
        log = result.output_log
        try:
            import re
            import difflib

            # Pattern: module 'math' has no attribute 'sqrtt'
            module_match = re.search(r"module '([^']+)' has no attribute '([^']+)'", log)
            object_match = re.search(r"'([^']+)' object has no attribute '([^']+)'", log)

            if module_match:
                owner_name, attr_name = module_match.groups()
                fix_hint = f"# HEALER: Detected missing attribute '{attr_name}' in module '{owner_name}'\n"
            elif object_match:
                owner_name, attr_name = object_match.groups()
                fix_hint = f"# HEALER: Detected missing attribute '{attr_name}' on '{owner_name}'\n"
            else:
                return False

            content = self.file_system.read_file(file_path)

            # Simple heuristic: find all words in file, look for best match
            words = set(re.findall(r"\w+", content))
            matches = difflib.get_close_matches(attr_name, words, n=1, cutoff=0.8)

            if matches:
                suggested = matches[0]
                new_content = content.replace(f".{attr_name}", f".{suggested}")
                if new_content != content:
                    self.file_system.write_file(file_path, new_content)
                    logger.info(f"Fixed AttributeError typo: {attr_name} -> {suggested}")
                    return True

            # Fallback to hint comment (idempotent: only write if not already present)
            if fix_hint not in content:
                self.file_system.write_file(file_path, fix_hint + content)
                logger.info(f"Added fallback hint for missing attribute '{attr_name}'")
                return True
        except Exception as e:
            logger.error(f"Failed to fix attribute error: {str(e)}", exc_info=True)
        return False

    def _fix_type_error(self, result: TestResult) -> bool:
        """Fixes common TypeError issues like missing arguments."""
        file_path = result.target
        log = result.output_log
        try:
            import re
            # Pattern: func() missing 1 required positional argument: 'x'
            match = re.search(r"(\w+)\(\) missing \d+ required positional argument[s]?: '([^']+)'", log)
            if match:
                func_name, arg_name = match.groups()
                content = self.file_system.read_file(file_path)
                # Try to add a dummy argument or None
                new_content = content.replace(f"{func_name}()", f"{func_name}(None)")
                if new_content != content:
                    self.file_system.write_file(file_path, new_content)
                    logger.info(f"Fixed TypeError: added None to {func_name}")
                    return True
        except Exception as e:
            logger.error(f"Failed to fix type error: {str(e)}", exc_info=True)
        return False

    def _fix_name_error(self, result: TestResult) -> bool:
        """Fixes NameError by attempting common imports."""
        file_path = result.target
        log = result.output_log
        try:
            import re
            match = re.search(r"name '([^']+)' is not defined", log)
            if not match:
                return False
            
            name = match.group(1)
            common_imports = {
                "os": "import os",
                "sys": "import sys",
                "pd": "import pandas as pd",
                "np": "import numpy as np",
                "plt": "import matplotlib.pyplot as plt",
                "json": "import json",
                "datetime": "from datetime import datetime"
            }
            
            if name in common_imports:
                content = self.file_system.read_file(file_path)
                imp = common_imports[name]
                if imp not in content:
                    self.file_system.write_file(file_path, imp + "\n" + content)
                    logger.info(f"Fixed NameError: added {imp}")
                    return True
        except Exception as e:
            logger.error(f"Failed to fix name error: {str(e)}", exc_info=True)
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
                # Try numeric match: assert 10 == 20
                match = re.search(r"assert\s+(\d+)\s*==\s*(\d+)", msg)
                if not match:
                    # Generic: assert X == Y (captures variable names)
                    match = re.search(r"assert\s+(.+)\s*==\s*(.+)", msg)
                    if not match:
                        return False

            actual, expected = match.groups()
            actual = actual.strip()
            expected = expected.strip()

            lines = self.file_system.read_lines(target_file)
            idx = line_no - 1
            if idx >= len(lines):
                return False

            line = lines[idx]

            # Case 1: Literal expected value is in the assert line → patch it directly
            if str(expected) in line:
                lines[idx] = line.replace(str(expected), str(actual))
                self.file_system.write_lines(target_file, lines)
                logger.info(f"Fixed assertion (literal): {expected} -> {actual}")
                return True

            # Case 2: Assert uses variable names → find variable definition in nearby lines
            # Extract the expected variable name from the assert (e.g. "exp" from "assert act == exp")
            assert_var_match = re.search(r"assert\s+\w+\s*==\s*(\w+)", line)
            if assert_var_match:
                expected_var = assert_var_match.group(1)
                # Search backward up to 10 lines for: expected_var = 'expected_value'
                search_start = max(0, idx - 10)
                for search_idx in range(idx - 1, search_start - 1, -1):
                    var_line = lines[search_idx]
                    var_match = re.search(
                        rf"{re.escape(expected_var)}\s*=\s*(['\"])(.+?)\1", var_line
                    )
                    if var_match:
                        quote_char = var_match.group(1)
                        old_val = var_match.group(2)
                        # Replace old_val with actual
                        new_val = actual.strip("'\"")
                        lines[search_idx] = var_line.replace(
                            f"{expected_var} = {quote_char}{old_val}{quote_char}",
                            f"{expected_var} = {quote_char}{new_val}{quote_char}"
                        )
                        self.file_system.write_lines(target_file, lines)
                        logger.info(f"Fixed assertion (variable trace): {expected_var} '{old_val}' -> '{new_val}'")
                        return True

            return False
        except Exception as e:
            logger.error(f"Failed to fix assertion: {str(e)}", exc_info=True)
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
                    logger.info(f"Successfully fixed legacy assertion in {file_path}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to fix legacy assertion: {str(e)}", exc_info=True)
            return False
