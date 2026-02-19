# Command: test

The `test` command provides a unified interface for executing heterogeneous test suites across multiple programming languages. It abstracts the complexity of native test runners and provides a single, consolidated results matrix.

## Technical Capabilities

- **Polyglot Execution**: Orchestrates multiple runners (pytest, jest, cargo, etc.) in parallel or sequence.
- **Result Capture**: Intercepts stdout/stderr and structured output (JSON/XML) from native runners to aggregate metrics.
- **Fail-Fast Logic**: Optional configuration to terminate execution upon the first detected failure.

## Usage Specification

```bash
testgen test [TARGET_DIRECTORY] [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `TARGET_DIRECTORY` | The directory containing the tests to be executed. | No (Defaults to `./tests`) |

### Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--verbose` | `-v` | Displays full output from native test runners. | `False` |
| `--fail-fast` | | Terminates execution immediately on first failure. | `False` |

## Execution Example

```text
[bold cyan]TestGen-AI: Execution Matrix[/bold cyan]
--------------------------------------------------
[bold]Running Python Tests[/bold] (pytest)
[green]PASS[/green] tests/test_auth.py (0.4s)
[red]FAIL[/red] tests/test_api.py (1.2s) - [dim]AssertionError: 404 != 200[/dim]

[bold]Running Javascript Tests[/bold] (jest)
[green]PASS[/green] tests/utils.test.js (0.8s)

[yellow]Final Results[/yellow]:
  Total: 3 | [green]Passed: 2[/green] | [red]Failed: 1[/red] | [dim]Skipped: 0[/dim]
```
