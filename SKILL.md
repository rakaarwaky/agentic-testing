---
name: agentic-testing
description: Autonomous Unit Testing Agent that analyzes, generates, runs, and self-heals tests.
version: 1.0.0
architecture: AES (Agentic Enterprise System) - 5 Domain Structure
---

# MCP Agentic Testing Skill 🧪

> **"Tests that fix themselves."**

This skill transforms the unit testing process from a manual chore into an autonomous capability. It implements **rule-based self-healing** for common test failures.

## Capabilities

1.  **Deep Introspection**: Analyze code structure (AST) to identify testable units.
2.  **Autonomous Execution**: Run `pytest` in isolation via subprocess.
3.  **Self-Healing**: Analyze failure logs (`ImportError`, `AttributeError`) and apply heuristic fixes automatically.
4.  **Synthetic Data**: Generate diverse edge cases instead of static fixtures.

## Theoretical Foundation 🧠

This skill implements the **Self-Healing Test Architecture** with deterministic healing strategies:

1.  **The Feedback Loop:** By coupling _Execution_ (pytest) with _Introspection_ (AST analysis), we reduce the "Feedback Lag" from minutes to seconds.
2.  **Performance First:** Tests are executed with `uv run` for environment isolation and fast startup.
3.  **Deterministic Healing:** We do not guess. We trace `ImportError` and `AttributeError` stacks to their source and apply semantic patches based on predefined rules.

## Architecture (AES 5-Domain Structure)

This MCP follows the **AES (Agentic Enterprise System)** architecture with 5 distinct domains:

```text
agentic-testing/
├── src/
│   ├── core/
│   │   ├── _taxonomy/           # Domain 1: Taxonomy (Entities & Interfaces)
│   │   │   ├── models.py        # TestResult, ITestRunner, ITestHealer, etc.
│   │   │   └── errors.py        # Domain-specific error types
│   │   └── capabilities/        # Domain 2: Capabilities (Business Logic)
│   │       ├── autonomous_testing/
│   │       │   ├── actions.py   # RunTestWithHealingUseCase
│   │       │   └── healer.py    # HeuristicHealer (rule-based fixes)
│   │       ├── code_analysis/
│   │       │   ├── actions.py   # AstAnalyzer
│   │       │   └── auditor.py   # CoverageAuditor
│   │       └── synthetic_data/
│   │           └── actions.py   # SimpleDataGenerator
│   ├── infrastructure/          # Domain 3: Infrastructure (Adapters)
│   │   └── shell_adapter.py     # PytestRunner (subprocess wrapper)
│   ├── bootstrap/               # Domain 4: Bootstrap (Wiring & Foundation)
│   │   ├── foundation/
│   │   │   └── logging_setup.py # Level 3a: System-wide logging
│   │   └── prod/
│   │       └── wiring.py        # Level 3b: Dependency injection
│   │   └── container.py         # Central orchestrator (DI container)
│   └── surfaces/                # Domain 5: Surface (MCP Interface)
│       └── mcp/
│           ├── server.py        # FastMCP entry point
│           └── tools.py         # Tool registrations (test_run, test_analyze, etc.)
└── tests/                       # Test suite (feature-first organization)
```

### Domain Responsibilities

| Domain       | Layer          | Component                               | Responsibility                            |
| ------------ | -------------- | --------------------------------------- | ----------------------------------------- |
| **Domain 1** | Taxonomy       | `models.py`, `errors.py`                | Pure entities & abstract interfaces (ABC) |
| **Domain 2** | Capabilities   | `actions.py`, `healer.py`, `auditor.py` | Business logic & use cases                |
| **Domain 3** | Infrastructure | `shell_adapter.py`                      | External system adapters (pytest CLI)     |
| **Domain 4** | Bootstrap      | `container.py`, `wiring.py`             | DI wiring & foundation setup              |
| **Domain 5** | Surface        | `server.py`, `tools.py`                 | MCP tool exposure to agents               |

### Data Flow (Request Lifecycle)

```
Agent Call → MCP Surface (Domain 5)
          ↓
     Container (Domain 4) - resolves dependencies
          ↓
     Use Case / Capability (Domain 2) - business logic
          ↓
     Infrastructure Adapter (Domain 3) - executes pytest
          ↓
     TestResult (Domain 1) - returned through layers
```

## Available Tools

| Tool                     | Description                                                | Input Params                                             |
| :----------------------- | :--------------------------------------------------------- | :------------------------------------------------------- |
| **`test_analyze`**       | Scan a file to identify functions, classes, and complexity | `target_file: str`                                       |
| **`test_run`**           | Run tests for a specific target with auto-healing enabled  | `test_path: str`, `max_retries: int`                     |
| **`test_generate_data`** | Create synthetic datasets for edge cases                   | `data_type: str` (strings/numbers/json/dates/emails/all) |
| **`test_audit`**         | Verify coverage and quality gates                          | `target_dir: str`                                        |

## Self-Healing Limitations

> [!NOTE]
> The current healer is **rule-based** (not AI-driven). It handles:
>
> | Error Type                            | Healing Strategy                                      |
> | ------------------------------------- | ----------------------------------------------------- |
> | `ImportError` / `ModuleNotFoundError` | Injects `sys.path.insert(0, ...)` after pytest import |
> | `AttributeError`                      | Adds TODO comment to check import statement           |
> | `AssertionError`                      | Adds TODO comment to review expected values           |
>
> **Not supported:** Complex refactoring, missing dependencies, logic bugs, type errors.

## Test Directory Structure (2026 Standard)

All tests follow the **Feature-First** organization:

```text
tests/
├── [feature_name]/                 # 🎯 Per-feature folder
│   ├── unit/                       # L1: Fast, mock-heavy, no I/O
│   ├── integration/                # L2: Real MCP, real DB
│   ├── agentic/                    # L3: LLM Evals & Semantic Tests
│   ├── e2e/                        # L4: Full Browser/System flows
│   ├── fixtures/                   # Shared data for THIS feature
│   │   ├── samples/
│   │   └── mocks/
│   └── conftest.py                 # Feature-specific fixtures
```

**Test Level Classification:**

| Level | Name        | Purpose                    | Actuator Policy (Mocking)  |
| :---- | :---------- | :------------------------- | :------------------------- |
| L1    | Unit        | Pure logic, mocked, no I/O | ✅ Mocks Allowed           |
| L2    | Integration | Real MCP, real DB          | ⚠️ External APIs Only      |
| L3    | Agentic     | LLM Evals, semantic tests  | ✅ Input Mocks Allowed     |
| L4    | E2E         | Full browser/system flows  | ❌ **REAL ACTUATORS ONLY** |

> [!CRITICAL]
> **L4 E2E Rule**: You MUST use the real `browser_subagent` or `selenium`.
> Logging "I would have clicked" is a **L1 Unit Test**, NOT an E2E test.

## Usage Guide

### 1. Analysis Phase

```bash
# MCP tool call - analyze a Python file
test_analyze(target_file="src/parser.py")
# Returns: {file, classes: [...], functions: [...], complexity_score}
```

### 2. Execution & Healing Loop

```bash
# MCP tool call - run tests with self-healing
test_run(test_path="tests/parser/unit/test_parser.py", max_retries=2)
# Returns: Status (PASS/FAIL), healing attempts count, output log
```

### 3. Coverage Audit

```bash
# MCP tool call - check coverage for a directory
test_audit(target_dir="src/")
# Returns: {total_pct, summary} or {error}
```

### 4. Synthetic Data Generation

```bash
# Generate all edge case types
test_generate_data(data_type="all")

# Generate specific types
test_generate_data(data_type="strings")  # ["", None, "   ", "🔥", ...]
test_generate_data(data_type="numbers")  # [0, -1, INT_MIN, INT_MAX, inf, ...]
test_generate_data(data_type="emails")   # ["", "invalid", "@nodomain", ...]
```

## Installation

```bash
# Install dependencies (requires uv)
uv pip install -e .

# Or via pip
pip install -e .
```

### MCP Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "agentic-testing": {
      "command": "uv",
      "args": ["run", "agentic-testing"]
    }
  }
}
```
