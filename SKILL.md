---
name: agentic-testing
description: Autonomous Unit Testing Skill with AST-based healing and synthetic data generation.
version: 1.0.0
standard: AES-2026-Skill
---

# Agentic Testing Skill 🧪

This skill equips you with autonomous testing capabilities. Use it to maintain a high-quality, 100% covered codebase without manual intervention.

## 🧭 Agentic Directives

### 1. The 100% Coverage Gate
Every piece of code in `src/` is a cost center unless verified. You MUST achieve 100% coverage for all "Living Stock" (reachable code).
- **Tool**: Use `test_audit` to identify gaps.
- **Action**: If coverage < 100%, generate missing tests immediately.

### 2. Autonomous Healing Workflow
Do not stop at the first failure. Follow the recovery loop:
1. **Analyze**: Use `test_analyze` to understand why the code failed.
2. **Heal**: Run `test_run` with `max_retries=3`. The heuristic healer handles `ImportError`, `AttributeError`, and `AssertionError`.
3. **Verify**: Run `test_run` again with 0 retries to confirm the fix is permanent.

### 3. Edge Case Synthesis
Never rely solely on static fixtures. 
- Use `test_generate_data` to stress-test your logic with emails, empty strings, and boundary numbers.

## 🛠 Tool Protocols

### `test_analyze`
**When to use**: Before creating any test file or modifying existing logic.
- **Agent Instruction**: Extract class and function signatures to ensure your `pytest` mocks are high-fidelity.

### `test_run`
**When to use**: After every code change.
- **Agent Instruction**: Always prioritize `max_retries >= 1`. If the healer applies a patch, read the updated file to confirm it aligns with the architectural intent.

### `test_generate`
**When to use**: When creating a new component.
- **Agent Instruction**: Use this to scaffold the `tests/[feature]/unit/` directory. Refine the generated tests to improve semantic depth.

### `test_audit`
**When to use**: Before finalize/submit.
- **Agent Instruction**: This is your quality gate. Report any file that falls below 100% as a "Quality Breach".

## 📐 Test Directory Standard (AES-2026)

Ensure your test structures follow the vertical slicing pattern:
- `tests/[feature]/unit/`: Logic verification, mock-heavy.
- `tests/[feature]/integration/`: Surface-to-Infrastructure verification.
- `tests/fixtures/`: Shared state.

## ⚠️ Self-Healing Constraints
- **Supported**: Import path fixes, basic attribute remapping, and literal comparison adjustments in assertions.
- **Unsupported**: Logic flow changes, complex library dependency installs, and type-system violations.

> [!IMPORTANT]
> When healing fails, do not loop indefinitely. Switch to `PLANNING` mode, analyze the failure log, and perform a manual "Vibe Check" with the Human Architect.
