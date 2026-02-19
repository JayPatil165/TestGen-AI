# Command: report

The `report` command transforms raw execution data into comprehensive visual artifacts. It is designed to provide high-level insights for developers and stakeholders through interactive dashboards.

## Technical Specifications

- **Input Formats**: Consumes `.testgen_state.json` or native runner artifacts (e.g., `.report.json`).
- **Engines**: Utilizes Jinja2 for HTML templating and TailwindCSS for responsive visualization.
- **Visual Analytics**: Includes distribution charts for test duration, success rates, and language breakdown.

## Usage Specification

```bash
testgen report [INPUT_DIR] [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `INPUT_DIR` | The directory containing the test results to visualize. | No (Defaults to `./tests`) |

### Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--output` | `-o` | Directory where the HTML report will be saved. | `./reports` |
| `--open` | | Automatically opens the report in the default system browser. | `True` |

## Execution Example

```text
[bold cyan]TestGen-AI: Reporting Engine[/bold cyan]
--------------------------------------------------
[blue]Extracting[/blue]: Processing 45 test results...
[blue]Rendering[/blue]: Generating interactive dashboard...

[bold green]Success[/bold green]: HTML Report available at:
[link=file:///D:/Projects/TestGen-AI/reports/index.html]reports/index.html[/link]

[dim]Statistics:[/dim]
- 100% Pass Rate
- 12.4s Total Execution Time
- 14 Languages Covered
```
