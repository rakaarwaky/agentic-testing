import asyncio
import subprocess
from ..taxonomy import ITestRunner, TestResult


class PytestRunner(ITestRunner):
    """Infrastructure adapter for running pytest (Domain 2)."""

    def __init__(self):
        # Environment handled by 'uv run'
        pass

    async def run_test(self, test_path: str) -> TestResult:
        import sys

        # Fix #3: Use create_subprocess_exec instead of create_subprocess_shell
        # to prevent shell injection vulnerabilities
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pytest", test_path, "-v", "--tb=short",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() + stderr.decode()
        exit_code = proc.returncode

        error_type = None
        failure_meta = None

        if exit_code != 0:
            import re
            from ..taxonomy import FailureMetadata

            # Extraction logic (Heuristic)
            # Pattern: tests/test_failing_sample.py:4: in test_typo
            # Pattern: E   AssertionError: assert 'helo' == 'hello'

            import os
            base_name = os.path.basename(test_path)
            # Use re.escape to handle special regex characters in filenames
            line_match = re.search(rf"{re.escape(base_name)}:(\d+):", output)
            line_number = int(line_match.group(1)) if line_match else None
            
            # Extract error type and message
            # Matches E       AssertionError: ... or E  ImportError: ...
            error_match = re.search(r"E\s+([a-zA-Z]+Error):?\s+(.*)", output)
            if error_match:
                error_type = error_match.group(1)
                message = error_match.group(2).strip()

                # Improve regex robustness for AssertionError messages, specifically string comparisons
                if error_type == "AssertionError":
                    # Use flexible whitespace and handle both ' and "
                    match = re.search(r"assert\s+['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]", message)
                    if match:
                        actual, expected = match.groups()
                        message = f"AssertionError: Expected '{expected}', got '{actual}'"

                failure_meta = FailureMetadata(
                    file_path=test_path,
                    line_number=line_number,
                    exception_type=error_type,
                    message=message
                )
            else:
                # Fallback for old markers
                if "ModuleNotFoundError" in output:
                    error_type = "ModuleNotFoundError"
                elif "ImportError" in output:
                    error_type = "ImportError"
                elif "AssertionError" in output:
                    error_type = "AssertionError"
                else:
                    error_type = "UnknownError"

        return TestResult(
            target=test_path,
            passed=(exit_code == 0),
            output_log=output,
            error_type=error_type,
            failure=failure_meta
        )
