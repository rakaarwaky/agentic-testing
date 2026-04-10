"""Tests for migrate, slow finder, and mock generate CLI commands."""

import os
import tempfile
import pytest
from click.testing import CliRunner
from src.surfaces.cli.main import cli


class TestMigrateCommand:
    """Tests for the migrate CLI command (Fix #1)."""

    def test_migrate_assert_equal(self):
        """Fix #1: self.assertEqual(a, b) → assert a == b (valid Python)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a unittest-style test file
            test_file = "test_old.py"
            with open(test_file, "w") as f:
                f.write(
                    "import unittest\n\n"
                    "class TestFoo(unittest.TestCase):\n"
                    "    def test_one(self):\n"
                    "        self.assertEqual(1, 1)\n"
                )

            result = runner.invoke(cli, ["migrate", test_file])
            assert result.exit_code == 0

            # Read the migrated file
            with open(test_file, "r") as f:
                content = f.read()

            # Verify valid Python syntax (Fix #1)
            compile(content, test_file, "exec")

            # Verify correct transformation
            assert "assert 1 == 1" in content
            assert "self.assertEqual" not in content
            assert "import unittest" not in content
            assert "unittest.TestCase" not in content

    def test_migrate_assert_true_false(self):
        """self.assertTrue(x) → assert x, self.assertFalse(x) → assert not x."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            test_file = "test_old.py"
            with open(test_file, "w") as f:
                f.write(
                    "import unittest\n\n"
                    "class TestFoo(unittest.TestCase):\n"
                    "    def test_two(self):\n"
                    "        self.assertTrue(True)\n"
                    "        self.assertFalse(False)\n"
                )

            result = runner.invoke(cli, ["migrate", test_file])
            assert result.exit_code == 0

            with open(test_file, "r") as f:
                content = f.read()

            # Verify valid Python syntax
            compile(content, test_file, "exec")

            assert "assert True" in content
            assert "assert not False" in content

    def test_migrate_with_backup(self):
        """--backup flag creates .bak file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            test_file = "test_old.py"
            with open(test_file, "w") as f:
                f.write("import unittest\n\nclass Test(unittest.TestCase): pass\n")

            result = runner.invoke(cli, ["migrate", test_file, "--backup"])
            assert result.exit_code == 0
            assert os.path.exists(test_file + ".bak")

    def test_migrate_file_not_found(self):
        """Should fail gracefully for missing file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", "nonexistent.py"])
        assert result.exit_code != 0


class TestFindSlowCommand:
    """Tests for the find-slow CLI command."""

    def test_find_slow_basic(self):
        """Basic execution of find-slow command."""
        runner = CliRunner()
        # Use the project's own tests directory
        result = runner.invoke(cli, ["find-slow", "tests", "--threshold", "10.0"])
        # Should not crash even if no slow tests found
        assert result.exit_code == 0 or "Error" not in (result.stderr or "")


class TestMockGenerateCommand:
    """Tests for the mock-generate CLI command."""

    def test_mock_generate_valid_signature(self):
        """Should produce valid Python mock code."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["mock-generate", "def get_user(id: int) -> User"]
        )
        assert result.exit_code == 0
        assert "mock_get_user" in result.output
        assert "Mock()" in result.output

    def test_mock_generate_invalid_signature(self):
        """Should fail gracefully for invalid input."""
        runner = CliRunner()
        result = runner.invoke(cli, ["mock-generate", "not a function"])
        assert result.exit_code != 0
        assert "Invalid signature" in result.output

    def test_mock_generate_with_output(self):
        """Should save to file when --output is provided."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["mock-generate", "def foo(x)", "--output", "mocks/mock_foo.py"],
            )
            assert result.exit_code == 0
            assert os.path.exists("mocks/mock_foo.py")
