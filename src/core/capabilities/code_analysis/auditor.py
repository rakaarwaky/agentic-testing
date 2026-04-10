import asyncio
import json
import os
import tempfile
import subprocess
from ..._taxonomy.models import IQualityAuditor


class CoverageAuditor(IQualityAuditor):
    """Quality gateway via coverage analysis (Capability)."""

    async def check_coverage(self, target_dir: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            report_file = tmp.name

        try:
            # Use Python's sys.executable for better portability across environments
            import sys
            cmd = f"{sys.executable} -m pytest --cov={target_dir} --cov-report=json:{report_file}"

            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            await proc.communicate()

            if os.path.exists(report_file):
                with open(report_file, "r") as f:
                    try:
                        data = json.load(f)
                        return {
                            "total_pct": data.get("totals", {}).get(
                                "percent_covered", 0
                            ),
                            "summary": "Coverage report generated successfully.",
                        }
                    except json.JSONDecodeError:
                        return {"error": "Invalid coverage report format."}
            return {"error": "Failed to generate coverage report."}
        except Exception as e:
            return {"error": f"Coverage analysis failed: {str(e)}"}
        finally:
            if os.path.exists(report_file):
                os.remove(report_file)
