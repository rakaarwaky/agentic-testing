# Agentic Testing MCP Server

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**"The Self-Healing Unit Tester"**

The Agentic Testing MCP server fundamentally shifts how developers interact with unit tests. Built for integration with Claude Desktop and other coding agents, this server provides deep AST introspection, self-healing test execution, and autonomous coverage auditing. It does not just run tests; it actively understands failures and patches syntax or import errors on the fly.

---

## 🚀 Key Capabilities

- **Self-Healing Execution:** Intelligently analyzes `ImportError`, `NameError`, and basic syntax faults, applying patches and retrying without blocking the developer loop.
- **Deep Introspection:** Leverages python AST parsing to map class structures, function dependencies, and code complexity before testing begins.
- **Quality Auditing:** Enforces test coverage gates (default >80%), refusing to pass incomplete testing suites.
- **Synthetic Data Generation:** Generates comprehensive fuzzing inputs (strings, dates, edge-case numbers) for robust test coverage.

---

## 🛠️ MCP Tools

This server exposes the following tools directly to your agentic coding assistant:

| Tool Name | Description |
| :--- | :--- |
| `test_run` | Executes a specific Python test file. If the test fails, the server uses autonomous self-healing capabilities up to a defined `max_retries` limit. |
| `test_analyze` | Performs static AST analysis on a Python source file, returning classes, functions, docstrings, and cyclomatic complexity. |
| `test_audit` | Scans a target directory, runs coverage analysis, and generates an audit report verifying coverage minimums. |
| `test_generate` | Automatically scaffolds boilerplate `pytest` unit tests for a given source file based on its AST structure. |
| `test_generate_data` | Generates synthetic edge-case data for testing (types: `strings`, `numbers`, `json`, `dates`, `emails`, `all`). |

---

## 🏗️ Architecture

This repository is strictly structured using the **Enterprise 4-Layer Clean Architecture**, ensuring high cohesion and loose coupling.

1.  **Domain:** Core logic, entities, and protocols (`TestResult`, interfaces).
2.  **Application:** Business use cases (`RunTestWithHealing` workflow orchestrator).
3.  **Infrastructure:** Concrete implementations and adapters (`PytestAdapter`, `AstAnalyzer`).
4.  **Interface:** Surface area for MCP communication (`server.py`).

*(See `SKILL.md` for extended architectural guidelines and developer instructions).*

---

## 📦 Installation & Setup

We recommend managing the environment with [`uv`](https://github.com/astral-sh/uv) for highly optimized dependency resolution.

### 1. Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/agentic-testing.git
cd agentic-testing

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 2. Registering with MCP Clients (Claude Desktop)

To use this server with Claude Desktop or similar MCP clients, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agentic-testing": {
      "command": "/absolute/path/to/agentic-testing/.venv/bin/python",
      "args": [
        "-m",
        "src.surfaces.mcp.server"
      ]
    }
  }
}
```

*Note: You can also use the provided `wrapper.sh` script to streamline startup if you prefer a bash wrapper.*

---

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, development environment setup, and the process for submitting Pull Requests to us.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
