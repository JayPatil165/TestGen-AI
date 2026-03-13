# Command Reference Overview

TestGen-AI provides a comprehensive suite of commands designed to handle every stage of the testing lifecycle. This reference provides a technical comparison and detailed specifications for each operation.

## Command Comparison Matrix

| Command | Primary Function | Primary Use Case | Output Artifacts |
|---------|------------------|------------------|------------------|
| `setup` | System configuration | One-time post-install setup | PATH environment variable |
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

## Quick Setup

After installing testgen-ai with pip, run this once:

```bash
testgen setup
```

This ensures the `testgen` command works from any terminal on your system (especially important on Windows).

## Command Details

For in-depth technical specifications, including individual flags and execution parameters, refer to the specific command pages:

- [**setup**](#setup): One-time post-installation configuration.
- [**auto**](auto.md): The full autonomous testing workflow.
- [**generate**](generate.md): Source code analysis and test generation.
- [**test**](test.md): Multi-language execution and discovery.
- [**report**](report.md): Analytical reporting and visualization.
- [**config**](config.md): Global configuration and API key management.

## setup

```bash
testgen setup
```

**Purpose:** Configures your system to recognize the `testgen` command globally.

**What it does:**
- **Windows:** Automatically adds Python's Scripts folder to your system PATH (requires Administrator)
- **macOS/Linux:** Verifies the command is accessible and provides troubleshooting if needed
- **All platforms:** Helps you set up `python -m testgen` as a fallback if needed

**When to run:** Once, immediately after `pip install testgen-ai`

**Example:**
```bash
$ pip install testgen-ai
$ testgen setup

╭───── 🔧 Setup ─────╮
│ TestGen AI — Setup │
│ Platform: Windows  │
╰────────────────────╯

Windows Detected — Adding Python Scripts folder to PATH...

Scripts folder found at: C:\Python313\Scripts

✅ SUCCESS — Added to PATH

⚠️  Please restart your terminal for changes to take effect.

Then verify with:
  testgen --version
```

**Troubleshooting:**
- If you get a permission error on Windows, run your terminal as Administrator and try again.
- If you can't get it to work, use `python -m testgen` instead (it always works without any setup).

