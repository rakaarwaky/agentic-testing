---
name: agentic-testing
description: Autonomous Unit Testing Skill with AST-based healing and synthetic data generation.
version: 1.0.0
standard: AES-2026-Skill
---

# Agentic Testing Skill 🧪

This skill equips you with autonomous testing capabilities. Use it to maintain a high-quality codebase with self-healing test execution.

## 🧭 Agentic Directives

### 1. The Coverage Gate
Use `execute_command` with action `audit` to check coverage. If coverage is below threshold, generate missing tests immediately.

### 2. Autonomous Healing Workflow
Do not stop at the first failure:
1. **Run**: Use `execute_command` with action `run` and `heal: true`
2. **Verify**: Run again with `heal: false` to confirm fix is permanent

### 3. Edge Case Synthesis
Use `execute_command` with action `generate-data` to stress-test logic with boundary values.

## 🛠 MCP Tools (5 Core)

### Core Tool 1: `execute_command`
Execute ANY agentic-test CLI command. Delegates to secure command runner.

**Parameters**:
- `action` (str): Command name (run, analyze, audit, generate, generate-data, migrate, find-slow, mock-generate, workflow, version, init)
- `args` (dict, optional): Command arguments
- `use_desktop_commander` (bool): Whether to use DesktopCommander (default: true)

**Example**:
```python
result = await execute_command("run", {"test_path": "tests/test_parser.py", "heal": True})
```

### Core Tool 2: `list_commands`
List all available CLI commands. Returns `agentic-test --help` output.

**Parameters**:
- `domain` (str, optional): Filter by domain (test, data, migration, performance, workflow, utility)

### Core Tool 3: `check_status`
Check server health, execution mode, and socket availability.

### Core Tool 4: `read_skill_context`
Read SKILL.md documentation sections.

**Sections**: directives, mcp-tools, cli-commands, workflows, architecture, token-efficiency

### Core Tool 5: `cancel_job`
Cancel a running test job (currently returns not_implemented).

## 💻 CLI Commands (11+ commands)

### Test Commands
- `agentic-test run <test_path>` — Run tests with self-healing
  - Options: `--heal`, `--max-retries N`, `--format json|text`
- `agentic-test analyze <target_file>` — AST analysis
  - Options: `--format json|text`
- `agentic-test audit <target_dir>` — Coverage audit
  - Options: `--threshold N`, `--format json|text`
- `agentic-test generate <source_file>` — Generate boilerplate tests
  - Options: `--output PATH`

### Test Data Commands
- `agentic-test generate-data <type>` — Generate synthetic test data
  - Types: strings, numbers, json, dates, emails, all
  - Options: `--count N`, `--format json|text`

### Migration Commands
- `agentic-test migrate <test_file>` — Migrate unittest to pytest
  - Converts: `assertEqual` → `assert a == b`, `assertTrue` → `assert`, `assertFalse` → `assert not`
  - Options: `--backup`

### Performance Commands
- `agentic-test find-slow <target_dir>` — Find slow tests
  - Options: `--threshold N`, `--top N`
- `agentic-test mock-generate "<signature>"` — Generate mock from signature
  - Options: `--output PATH`

### Workflow Commands
- `agentic-test workflow <workflow> <target>` — Run pre-defined workflows
  - Workflows: test-and-fix, coverage-gate, full-suite

### Utility Commands
- `agentic-test version` — Show version
- `agentic-test init <config_path>` — Initialize configuration

## 🔄 Common Workflows

### Pre-Commit Quality Gate
```bash
agentic-test run tests/ --heal --max-retries 3
agentic-test audit ./src --threshold 80
```

### Test-Driven Development (TDD)
```bash
agentic-test analyze src/new_feature.py
agentic-test generate src/new_feature.py
agentic-test run tests/test_new_feature.py --heal
```

### Legacy Test Migration
```bash
agentic-test migrate tests/old_test.py --backup
agentic-test run tests/old_test.py --heal
```

## ⚠️ Self-Healing Constraints

### Supported Fixes
- ✅ Import path fixes (`sys.path` injection)
- ✅ Basic attribute remapping (Levenshtein-like)
- ✅ Assertion value adjustments
- ✅ Missing import statements
- ✅ TypeError dummy argument injection

### Safety
- ✅ Backup created before every modification (`.healer.bak`)
- ❌ Logic flow changes NOT supported
- ❌ Complex dependency installs NOT supported
- ❌ Business logic corrections NOT supported

## 📐 Test Directory Standard

- `tests/[feature]/unit/`: Logic verification, mock-heavy
- `tests/[feature]/integration/`: Surface-to-Infrastructure verification
- `tests/fixtures/`: Shared state
