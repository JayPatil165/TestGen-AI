# Command Reference Overview

TestGen-AI provides a comprehensive suite of commands designed to handle every stage of the testing lifecycle. This reference provides a technical comparison and detailed specifications for each operation.

## Command Comparison Matrix

| Command | Primary Function | Primary Use Case | Output Artifacts |
|---------|------------------|------------------|------------------|
| `auto` | End-to-End Orchestration | CI/CD, Rapid Development | Tests, Reports, Logs |
| `generate` | AI-Driven Test Creation | Initializing test suites | Source code test files |
| `test` | Automated Execution | Verification of local code | Terminal results matrix |
| `report` | Visual Analytics | Stakeholder reviews | HTML/JSON Dashboards |
| `config` | Global Configuration | API key setup, provider config | `~/.testgen/.env` |

## Universal Flags

The following flags are applicable to all commands within the TestGen-AI ecosystem:

| Flag | Description | Default |
|------|-------------|---------|
| `--verbose` | Enables detailed logging and internal trace monitoring. | `False` |
| `--debug` | Provides full stack traces and debug-level execution logs. | `False` |
| `--version` | Displays the current build version and system metadata. | N/A |
| `--help` | Renders the command-line help interface for the specific scope. | N/A |

## Command Details

For in-depth technical specifications, including individual flags and execution parameters, refer to the specific command pages:

- [**auto**](auto.md): The full autonomous testing workflow.
- [**generate**](generate.md): Source code analysis and test generation.
- [**test**](test.md): Multi-language execution and discovery.
- [**report**](report.md): Analytical reporting and visualization.
- [**config**](config.md): Global configuration and API key management.
