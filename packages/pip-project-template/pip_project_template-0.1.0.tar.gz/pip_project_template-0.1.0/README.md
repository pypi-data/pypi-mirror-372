<!-- ---
!-- Timestamp: 2025-08-27 10:52:15
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/pip-project-template/README.md
!-- --- -->

# Pip Project Template

A Python project template for a pip package, featuring **FastMCP 2.0** servers for agentic coding workflows (planning + test-driven development).

[![CI](https://github.com/ywatanabe1989/pip-project-template/workflows/Validation/badge.svg)](https://github.com/ywatanabe1989/pip-project-template/actions)
[![codecov](https://codecov.io/gh/ywatanabe1989/pip-project-template/branch/develop/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/pip-project-template)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://gofastmcp.com)

## Quick Start

[Makefile](./Makefile), which defines commands, is the entry point.

```bash
# Installation
make install          # Install project dependencies (or pip install -e .)
                       
# Tests
make test-changed     # Run tests which affected by source code change (fast)
make test-full        # Run full tests with coverage
make coverage-html    # Generate HTML coverage report
make ci-act           # Run GitHub Actions locally with Act and Apptainer
make ci-container     # Run CI with containers (Apptainer -> Docker fallback)
make ci-local         # Run local CI emulator (Python-based)
make lint             # Run linting and formatting

# Publish as a pip package in PyPI repository
make build            # Build package for distribution
make upload-pypi-test # Upload to Test PyPI
make upload-pypi      # Upload to PyPI
make release          # Clean, build, and upload to PyPI

# Maintainance
make clean            # Remove cache files
```

## Python API

```bash
python -m pip_project_template calculate 10 5
python -m pip_project_template serve01
python -m pip_project_template info
```

## MCP Servers
<details>

``` json
{
  "mcpServers": {
    "calculator-basic": {
      "command": "python",
      "args": ["-m", "pip_project_template", "serve01", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    "calculator-enhanced": {
      "command": "python", 
      "args": ["-m", "pip_project_template", "serve02", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    "http-calculator": {
      "url": "http://localhost:8081/mcp",
      "transport": "http"
    },
    "sse-calculator": {
      "url": "http://localhost:8082",
      "transport": "sse"
    }
  },
  "defaults": {
    "timeout": 30,
    "retries": 3
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mcp.log"
  }
}
```

</details>
## Project Structure

```
src/pip_project_template/    # Source code
tests/custom                 # Custom Tests
tests/github_actions         # Scripts for running GitHub Actions locally
tests/pip_project_template/  # Tests for source code (1-on-1 relationship)
tests/reports                # Test results
data/                        # For persistent data
config/mcp_config.json       # MCP configuration
mgmt/                        # Project Management and Agent Definitions
```

## Requirements

Python 3.11+

## License

MIT

## Contact
Yusuke.Watanabe@scitex.ai

<!-- EOF -->