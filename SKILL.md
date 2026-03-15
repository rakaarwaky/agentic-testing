---
name: agentic-testing
description: Autonomous Unit Testing Agent that analyzes, generates, runs, and self-heals tests.
version: 1.0.0
---

# Agentic Testing Skill 🧪

This skill enables autonomous testing capabilities including AST analysis, recursive test execution, rule-based self-healing, and synthetic data generation. It is designed to be used by AI agents to maintain high-quality codebases with 100% test coverage.

## Core Directives for Agents
1. **Target 100% Coverage**: All new features must be accompanied by tests that achieve full coverage.
2. **Autonomous Healing**: When a test fails, always use `test_run` with `max_retries > 0` to attempt automatic recovery.
3. **Data Diversity**: Use `test_generate_data` to ensure logic is resilient against edge cases.

## Available Tools

### `test_analyze`
Introspects a Python file to extract its semantic structure. Use this before writing tests to understand the available classes, functions, and their complexity.
- **Param**: `target_file` (str) - Absolute path to the Python file.

### `test_run`
Executes tests for a specific path with optional autonomous self-healing.
- **Param**: `test_path` (str) - Path to the test file or directory.
- **Param**: `max_retries` (int, default=1) - Number of healing attempts to perform on failure.
- **Healing Capabilities**:
  - Fixes `ImportError` by adjusting `sys.path`.
  - Fixes simple `AssertionError` by parsing error messages and updating code.
  - Automatically retries execution after applying fixes.

### `test_audit`
Performs a quality and coverage check for a directory. Use this to verify that the 100% coverage gate is met.
- **Param**: `target_dir` (str) - Absolute path to the source directory.

### `test_generate`
Generates boilerplate unit tests for a given source file based on its AST analysis.
- **Param**: `source_file` (str) - Absolute path to the component to be tested.

### `test_generate_data`
Generates diverse synthetic data for edge-case testing.
- **Param**: `data_type` (str) - One of `strings`, `numbers`, `json`, `dates`, `emails`, or `all`.

## Standard Test Patterns

### Unit Testing (L1)
Focus on pure logic with mocked infrastructure.
- Location: `tests/[feature]/unit/`
- Mocking: Mandatory for I/O and external services.

### Integration Testing (L2)
Verify interaction between components and real adapters.
- Location: `tests/[feature]/integration/`
- Mocking: External APIs only.

### Self-Healing Loop
1. Analyze code structure via `test_analyze`.
2. Generate base tests via `test_generate`.
3. Run with healing: `test_run(test_path="...", max_retries=3)`.
4. Finalize with `test_audit` to ensure 100% coverage.
