# Command: generate

The `generate` command focuses exclusively on the analysis of source code and the AI-driven creation of test suites. It is used to initialize or update test coverage for existing codebases.

## Technical Details

The generation process utilizes semantic analysis to ensure that generated tests are not only syntactically correct but also contextually relevant. It supports incremental generation, allowing users to update specific modules without regenerating the entire suite.

## Usage Specification

```bash
testgen generate [TARGET_DIRECTORY] [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `TARGET_DIRECTORY` | The directory containing source code to be analyzed. | Yes |

### Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--output` | `-o` | Target directory for generated test files. | `./tests` |
| `--watch` | `-w` | Enables real-time monitoring and incremental generation on file save. | `False` |
| `--verbose` | `-v` | Enables detailed generation logs. | `False` |

## Execution Example

```text
[bold cyan]TestGen-AI: Generation Phase[/bold cyan]
--------------------------------------------------
[blue]Action[/blue]: Analyzing src/manager.py
[dim]Extracting classes: WorkflowManager, SessionManager[/dim]
[dim]Sending context to LLM (Model: gpt-4-turbo)[/dim]

[bold green]Result[/bold green]: Created tests/test_manager.py
[bold green]Result[/bold green]: Updated tests/test_session.py

[yellow]Summary[/yellow]: 2 files processed, 15 new test cases generated.
```

## Watch Mode Specification

When the `--watch` flag is enabled, TestGen-AI initializes a file system observer. Upon detection of a `WRITE` event on a supported source file, the system automatically triggers a targeted generation cycle for that specific file, ensuring tests remain synchronized with code changes.
