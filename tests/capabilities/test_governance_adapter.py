"""Tests for governance_adapter module."""
import os
from src.capabilities.governance_adapter import (
    GovernanceViolation,
    GovernanceAdapter,
    _extract_imports,
    _resolve_root,
    _collect_python_files,
    LAYER_MAP,
)


class TestGovernanceViolation:
    def test_code_property(self):
        v = GovernanceViolation(
            file_path="test.py", line_no=1,
            source_layer="surfaces", target_layer="infrastructure",
            module_path="src.infrastructure", description="test"
        )
        assert v.code == "AT001"

    def test_severity_property(self):
        v = GovernanceViolation(
            file_path="test.py", line_no=1,
            source_layer="surfaces", target_layer="infrastructure",
            module_path="src.infrastructure", description="test"
        )
        assert v.severity == "CRITICAL"

    def test_message_property(self):
        v = GovernanceViolation(
            file_path="test.py", line_no=5,
            source_layer="surfaces", target_layer="capabilities",
            module_path="src.capabilities.test_actions", description="Surfaces cannot import capabilities"
        )
        msg = v.message
        assert "AES Layer Violation" in msg
        assert "surfaces" in msg
        assert "capabilities" in msg


class TestExtractImports:
    def test_extract_imports_valid_file(self, tmp_path):
        py_file = tmp_path / "sample.py"
        py_file.write_text(
            "import os\n"
            "from pathlib import Path\n"
            "from src.capabilities import test_actions\n"
        )
        imports = _extract_imports(str(py_file))
        assert len(imports) == 3
        assert (1, "os") in imports
        assert (2, "pathlib") in imports
        assert (3, "src.capabilities") in imports

    def test_extract_imports_syntax_error(self, tmp_path):
        py_file = tmp_path / "bad.py"
        py_file.write_text("def foo(:\n")
        imports = _extract_imports(str(py_file))
        assert imports == []

    def test_extract_imports_nonexistent(self):
        imports = _extract_imports("/nonexistent/file.py")
        assert imports == []


class TestResolveRoot:
    def test_resolve_root_with_src(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        result = _resolve_root(str(tmp_path / "src" / "some_file.py"))
        # Creates parent dir, but src is at tmp_path level
        # The function checks for src subdir in parent dirs
        (tmp_path / "src").mkdir(exist_ok=True)
        result = _resolve_root(str(tmp_path / "src" / "capabilities" / "test.py"))
        assert "src" in os.listdir(result)

    def test_resolve_root_returns_path(self, tmp_path):
        # When no src dir found, returns parent of path or path
        result = _resolve_root(str(tmp_path))
        assert isinstance(result, str)


class TestCollectPythonFiles:
    def test_collect_single_file(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("# test")
        files = _collect_python_files(str(py_file))
        assert len(files) == 1
        assert files[0].endswith("test.py")

    def test_collect_nonexistent_path(self):
        files = _collect_python_files("/nonexistent/path")
        assert files == []

    def test_collect_directory(self, tmp_path):
        (tmp_path / "a.py").write_text("# a")
        (tmp_path / "b.py").write_text("# b")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.py").write_text("# c")
        files = _collect_python_files(str(tmp_path))
        assert len(files) == 3

    def test_collect_skips_pycache(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "cached.py").write_text("# cached")
        (tmp_path / "real.py").write_text("# real")
        files = _collect_python_files(str(tmp_path))
        assert len(files) == 1
        assert "real.py" in files[0]

    def test_collect_skips_venv(self, tmp_path):
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "lib.py").write_text("# venv")
        (tmp_path / "main.py").write_text("# main")
        files = _collect_python_files(str(tmp_path))
        assert len(files) == 1
        assert "main.py" in files[0]


class TestGovernanceAdapter:
    def test_detect_layer(self):
        adapter = GovernanceAdapter()
        assert adapter._detect_layer("src.capabilities.test") == "capabilities"
        assert adapter._detect_layer("src.infrastructure.shell") == "infrastructure"
        assert adapter._detect_layer("random.module") is None

    def test_detect_file_layer(self):
        adapter = GovernanceAdapter()
        assert adapter._detect_file_layer("/project/src/capabilities/test.py", "/project") == "capabilities"
        assert adapter._detect_file_layer("/project/src/surfaces/cli.py", "/project") == "surfaces"

    def test_detect_file_layer_returns_none(self):
        """Test _detect_file_layer returns None when no layer matches (line 107)."""
        adapter = GovernanceAdapter()
        # Path with no recognizable layer directories
        result = adapter._detect_file_layer("/project/unknown/stuff/test.py", "/project")
        assert result is None

    def test_scan_no_violations(self, tmp_path):
        rules = [("capabilities", "surfaces", "Cannot import surfaces")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)
        
        py_file = tmp_path / "src" / "capabilities" / "test.py"
        py_file.parent.mkdir(parents=True)
        py_file.write_text("import os\n")
        
        violations = adapter.scan(str(py_file))
        assert len(violations) == 0

    def test_scan_with_violation(self, tmp_path):
        rules = [("capabilities", "surfaces", "Cannot import surfaces")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)
        
        # Create src directory structure for _resolve_root
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        cap_dir = src_dir / "capabilities"
        cap_dir.mkdir()
        py_file = cap_dir / "test.py"
        py_file.write_text("from src.surfaces import cli_main_entry\n")
        
        violations = adapter.scan(str(tmp_path))
        assert len(violations) == 1
        assert violations[0].source_layer == "capabilities"
        assert violations[0].target_layer == "surfaces"

    def test_scan_agent_skipped(self, tmp_path):
        rules = [("agent", "capabilities", "test")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)
        
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        agent_dir = src_dir / "agent"
        agent_dir.mkdir()
        py_file = agent_dir / "test.py"
        py_file.write_text("from src.capabilities import test_actions\n")
        
        violations = adapter.scan(str(tmp_path))
        assert len(violations) == 0  # agent is allowed to import anything

    def test_scan_unknown_layer_skipped(self, tmp_path):
        """Files with unrecognized layer (None) are skipped."""
        rules = [("capabilities", "surfaces", "Cannot import")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        unknown_dir = src_dir / "random"
        unknown_dir.mkdir()
        py_file = unknown_dir / "test.py"
        py_file.write_text("from src.surfaces import cli_main_entry\n")

        violations = adapter.scan(str(py_file))
        assert len(violations) == 0

    def test_scan_import_layer_unknown(self, tmp_path):
        """Import from unrecognized module — target_layer is None, skip (line 125->126)."""
        rules = [("capabilities", "surfaces", "Cannot import")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        cap_dir = src_dir / "capabilities"
        cap_dir.mkdir()
        py_file = cap_dir / "test.py"
        py_file.write_text("import os\nimport json\n")

        violations = adapter.scan(str(py_file))
        assert len(violations) == 0

    def test_scan_no_matching_rule(self, tmp_path):
        """Import target layer detected but no rule matches (line 128->123, 129->128)."""
        rules = [("surfaces", "capabilities", "Cannot import caps")]
        adapter = GovernanceAdapter(rules=rules, layer_map=LAYER_MAP)

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        cap_dir = src_dir / "capabilities"
        cap_dir.mkdir()
        py_file = cap_dir / "test.py"
        # capabilities importing infrastructure — no rule forbids this
        py_file.write_text("from src.infrastructure import shell_adapter\n")

        violations = adapter.scan(str(py_file))
        assert len(violations) == 0


class TestExtractImportsEdgeCases:
    def test_extract_imports_from_no_module(self, tmp_path):
        """Relative import like 'from . import foo' — node.module is None (line 76->71)."""
        py_file = tmp_path / "rel.py"
        py_file.write_text("from . import foo\n")
        imports = _extract_imports(str(py_file))
        # Relative import with no module path — module is None, skipped
        assert imports == []

    def test_collect_non_py_file(self, tmp_path):
        """Non-.py file in directory — skipped by _collect_python_files."""
        (tmp_path / "readme.txt").write_text("not python")
        (tmp_path / "main.py").write_text("# python")
        files = _collect_python_files(str(tmp_path))
        assert len(files) == 1
        assert files[0].endswith("main.py")
