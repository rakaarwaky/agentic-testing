# Product Requirements Document (PRD)

## Agentic Testing — Autonomous Test Engine v1.0.0

---

## 1. Product Overview

**Name**: Agentic Testing
**Type**: MCP Server + CLI Tool
**Version**: 1.0.0
**License**: MIT
**Language**: Python >= 3.12

Agentic Testing is an autonomous test engine with self-healing capabilities. It runs as both an MCP server for AI agents and a CLI tool for developers.

Uses `mcp.server.fastmcp.FastMCP` for the MCP server interface.
Connects to DesktopCommander via Unix socket for secure command execution.

---

## 2. Problem Statement

Writing and maintaining tests is tedious and error-prone. Developers and AI agents need:

- Automated test generation from source code
- Self-healing tests that fix themselves when they break
- Coverage auditing with configurable thresholds
- Synthetic test data generation for edge cases
- Migration tools for legacy test frameworks (unittest → pytest)

**The Real Cost of Inaction:**

| Issue                | Impact                                  |
| -------------------- | --------------------------------------- |
| Manual test writing  | 5+ hours/week per developer             |
| Brittle tests        | Tests break on minor refactors          |
| Low coverage         | Undetected bugs reach production        |
| Test data creation   | Manual edge case discovery is slow      |
| Framework migration  | Costly and risky to migrate by hand     |

---

## 3. AI Agent Value

In 2026, AI agents do the coding. Agentic Testing enables:

| Value Driver             | Description                                 |
| ------------------------ | ------------------------------------------- |
| **Agent Autonomy** | Agent generates and runs tests independently  |
| **Self-Healing**   | Agent auto-fixes broken tests automatically   |
| **Coverage Gates** | Agent enforces coverage thresholds in CI      |
| **Data Synthesis** | Agent generates edge-case test data           |

---

## 4. Target Users

| User           | Interface          | Use Case                                         |
| -------------- | ------------------ | ------------------------------------------------ |
| **AI Agents**  | MCP tools (5 tools) | Autonomous test generation and self-healing    |
| **Developers** | CLI (11+ commands)  | Run tests, generate tests, audit coverage       |
| **CI/CD**      | CLI + exit codes    | Coverage gates, quality metrics                |
| **Contributors** | GitHub + PRs     | Add capabilities, adapters, CLI commands        |

---

## 5. Functional Requirements

### 5.1 Test Execution

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-001 | Run pytest on individual test files            | Done   |
| FR-002 | Parse pytest output for failure metadata       | Done   |
| FR-003 | Self-healing retry loop (up to N attempts)     | Done   |
| FR-004 | Extract error type, line number, message       | Done   |
| FR-005 | Create backup before auto-fix                  | Done   |

### 5.2 Self-Healing

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-010 | Fix ImportError/ModuleNotFoundError            | Done   |
| FR-011 | Fix AttributeError typos (Levenshtein match)  | Done   |
| FR-012 | Fix AssertionError (literal + variable trace)  | Done   |
| FR-013 | Fix TypeError (missing arguments)              | Done   |
| FR-014 | Fix NameError (common imports)                 | Done   |

### 5.3 Code Analysis

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-020 | AST-based file analysis (classes, functions)  | Done   |
| FR-021 | Complexity scoring                           | Done   |
| FR-022 | Coverage auditing with threshold               | Done   |

### 5.4 Test Generation

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-030 | Generate boilerplate tests from AST           | Done   |
| FR-031 | Generate synthetic test data (strings, etc.)  | Done   |
| FR-032 | Migrate unittest → pytest                      | Done   |
| FR-033 | Generate mocks from function signatures        | Done   |

### 5.5 Integration

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-040 | MCP server via FastMCP                        | Done   |
| FR-041 | CLI via Click with command groups             | Done   |
| FR-042 | Unix socket communication                     | Done   |
| FR-043 | Secure command execution (blocked commands)   | Done   |

### 5.6 Report Formats

| ID     | Requirement                                    | Status |
| ------ | ---------------------------------------------- | ------ |
| FR-050 | Text output (human-readable)                   | Done   |
| FR-051 | JSON output (machine-readable)                 | Done   |

---

## 6. Non-Functional Requirements

| ID      | Requirement                | Target    | Current |
| ------- | -------------------------- | --------- | ------- |
| NFR-001 | Test coverage              | 100%      | TBD     |
| NFR-002 | All tests passing          | 100%      | TBD     |
| NFR-003 | Python version             | >= 3.12   | 3.12+   |
| NFR-004 | Self-healing success rate  | > 70%     | TBD     |
| NFR-005 | Startup time (MCP server)  | < 2s      | ~1s     |

---

## 7. Architecture

### 7.1 Domain Model (5 Domains)

```
src/
  agent/              -- Wiring layer: DI container, logging
  capabilities/       -- Thinking logic: test execution, healing, analysis, generation
  infrastructure/     -- Toolbox: pytest runner, file system, transports
  surfaces/           -- Interfaces: CLI (Click), MCP (FastMCP)
  taxonomy/           -- Shared language: interfaces, models, data classes
```

### 7.2 Dependency Rules

```
surfaces      → capabilities       OK
surfaces      → infrastructure     OK
capabilities  → infrastructure     OK (via taxonomy interfaces)
infrastructure → taxonomy          OK
agent         → everything         OK (wiring layer)
```

### 7.3 MCP Server Architecture

Uses `mcp.server.fastmcp.FastMCP` with decorator-based tool registration:

```
mcp_server.py       -- creates FastMCP, registers tools
mcp_tools.py        -- all 5 MCP tool definitions
```

---

## 8. MCP Interface (5 Tools)

| Tool                    | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `execute_command`     | Execute any CLI command with security check  |
| `list_commands`       | Discover available CLI commands              |
| `check_status`        | Check server health and socket availability  |
| `read_skill_context`  | Read SKILL.md documentation sections         |
| `cancel_job`          | Cancel a running test job                    |

---

## 9. CLI Interface (11 Commands)

| Category    | Commands                                                       |
| ----------- | -------------------------------------------------------------- |
| Test        | run, analyze, audit, generate                                  |
| Data        | generate-data                                                  |
| Migration   | migrate                                                        |
| Performance | find-slow, mock-generate                                       |
| Workflow    | workflow                                                       |
| Utility     | version, init                                                  |

---

## 10. Security

| Feature                  | Description                                       |
| ------------------------ | ------------------------------------------------- |
| Blocked commands list  | `sudo`, `rm -rf`, `dd`, `chmod`, etc.            |
| Path validation        | Prevents directory traversal attacks              |
| Unix socket only       | No network exposure, local IPC only              |
| Timeout enforcement    | 300s default timeout for all commands            |

---

## 11. Dependencies

| Package      | Type     | Purpose                        |
| ------------ | -------- | ------------------------------ |
| mcp[cli]     | Core     | MCP protocol library           |
| fastmcp      | Core     | FastMCP server framework       |
| pydantic     | Core     | Data validation                |
| click        | Core     | CLI framework                  |
| pytest       | Core     | Test runner                    |
| pytest-cov   | Optional | Coverage reporting             |

---

## 12. Constraints

- Python only (3.12+)
- Free models only (no paid API dependencies)
- Unix socket for DesktopCommander communication
- No database required (file-based operations only)
- Platform: Linux, macOS, Windows
