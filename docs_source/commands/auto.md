# Command: auto

The `auto` command executes the full autonomous testing lifecycle in a single atomic operation. It is the primary command for end-to-end verification and CI/CD integration.

## Technical Execution Flow

When invoked, the `auto` command orchestrates the following internal phases:

1. **Source Discovery**: Recursively scans the target directory for supported source files.
2. **Context Analysis**: Extracts AST metadata and identifies code blocks requiring tests.
3. **AI Generation**: Interfaces with the configured LLM to generate test suites.
4. **Environment Setup**: Initializes temporary test directories and captures environment state.
5. **Multi-Language Execution**: Triggers native test runners for each identified language.
6. **Result Aggregation**: Collects execution data and generates a unified reporting artifact.

## Usage Specification

```bash
testgen auto [TARGET_DIRECTORY] [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `TARGET_DIRECTORY` | The path to the source code root directory for analysis. | Yes |

### Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--output` | `-o` | Specifies the directory for generated tests and reports. | `./tests` |
| `--verbose` | `-v` | Enables detailed step-by-step execution logs. | `False` |
| `--debug` | | Enables full stack traces and debug logging. | `False` |

## Execution Example

```text
[bold cyan]TestGen-AI: Autonomous Workflow Initiated[/bold cyan]
--------------------------------------------------
[blue]Phase 1[/blue]: Scanning directory: ./src
[green]Found[/green]: 12 Python files, 4 Javascript files.

[blue]Phase 2[/blue]: Generating test suites...
[green]Generated[/green]: test_auth.py, test_db.py, api.test.js

[blue]Phase 3[/blue]: Executing tests...
[dim]Running pytest...[/dim] ✅ 85% coverage
[dim]Running jest...[/dim]   ✅ 92% coverage

[blue]Phase 4[/blue]: Finalizing Report...
[bold green]Success[/bold green]: Report generated at ./docs/report_2026-02-19.html
```
