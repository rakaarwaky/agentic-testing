# Contributing to Agentic Testing

First off, thank you for considering contributing to `agentic-testing`! It's people like you that make testing autonomous and self-healing.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentic-testing.git
   ```
3. **Set up the development environment**. We use `uv` for dependency management:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

## Development Workflow

Before submitting a Pull Request, please ensure your code passes all quality gates.

1. **Linting:** We enforce strict type checking and linting.
   ```bash
   ruff check .
   mypy src/
   pyre check
   ```

2. **Testing:** Run the full test suite and ensure coverage remains above the 80% threshold.
   ```bash
   pytest --cov=src tests/
   ```

## Pull Request Process

1. Create a descriptive branch name (e.g., `feature/self-healing-ast` or `fix/import-error-regex`).
2. Include clear commit messages detailing *why* the change was made, not just what files were changed.
3. If your PR introduces a new capability, please add corresponding unit tests.
4. Update the `README.md` with details of any changes to the MCP interface.
5. Submit the PR against the `main` branch.

## Bug Reports and Feature Requests

Please use the GitHub Issue Tracker:
- For **bugs**, include steps to reproduce, the expected outcome, and the actual outcome.
- For **features**, describe the problem you are trying to solve and propose an API or implementation strategy.
