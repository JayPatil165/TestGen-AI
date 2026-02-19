"""
TestGen AI - Main CLI Entry Point

This module provides the command-line interface for TestGen AI using Typer.
All commands are defined here: generate, test, report, auto, and version.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from testgen import __version__, config

# Initialize Typer app
app = typer.Typer(
    name="testgen",
    help="🚀 TestGen AI - The Autonomous QA Agent from Your CLI",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Rich console for beautiful output
console = Console()

# Global state for options
class GlobalState:
    """Global state to share across commands."""
    verbose: bool = False
    debug: bool = False

state = GlobalState()


def version_callback(value: bool):
    """Callback hook to display the application version information.

    Args:
        value (bool): If True, prints the version and exits.

    Raises:
        typer.Exit: Terminates the CLI after displaying version info.
    """
    if value:
        console.print(Panel.fit(
            f"[bold cyan]TestGen AI[/bold cyan]\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Python: [yellow]{sys.version.split()[0]}[/yellow]",
            title="📦 Version Info",
            border_style="cyan"
        ))
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with detailed logs"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode with full stack traces"
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version information and exit"
    ),
):
    """🚀 TestGen AI - The Autonomous, AI-Powered QA Agent from Your CLI.

    TestGen AI automates the entire testing lifecycle: scanning your source
    code, generating robust unit tests using state-of-the-art LLMs, executing
    them across 14+ languages, and producing beautiful analytics reports.

    🎯 Quick Start:
    - [bold green]testgen generate ./src[/bold green] : Generate tests
    - [bold blue]testgen test[/bold blue]            : Execute tests
    - [bold yellow]testgen report[/bold yellow]          : Create interactive report
    - [bold magenta]testgen auto ./src[/bold magenta]      : Full autonomous workflow

    📚 Documentation: [link=https://github.com/JayPatil165/TestGen-AI]https://github.com/JayPatil165/TestGen-AI[/link]
    """
    # Store global options
    state.verbose = verbose
    state.debug = debug
    
    # Configure logging based on flags
    if verbose:
        config.verbose = True
        config.log_level = "DEBUG" if debug else "INFO"


@app.command()
def version():
    """
    Display version information.
    
    Shows TestGen AI version and Python version.
    """
    console.print(Panel.fit(
        f"[bold cyan]TestGen AI[/bold cyan]\n"
        f"Version: [green]{__version__}[/green]\n"
        f"Python: [yellow]{sys.version.split()[0]}[/yellow]\n"
        f"Platform: [magenta]{sys.platform}[/magenta]",
        title="📦 Version Information",
        border_style="cyan"
    ))


@app.command()
def generate(
    target_directory: Path = typer.Argument(
        ...,
        help="Directory containing source code to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for generated tests (default: ./tests)",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Enable watch mode for real-time test generation",
    ),
):
    """
    Generate test files for your code using AI.
    
    Analyzes source code and generates comprehensive test suites using LLMs.
    
    Examples:
        testgen generate ./src
        testgen generate ./src --output ./tests
        testgen generate ./src --watch
    """
    try:
        # Set output directory
        output_dir = output or Path(config.test_output_dir)
        
        # Validate target directory
        if not target_directory.exists():
            console.print(f"[red]❌ Error: Directory '{target_directory}' does not exist[/red]")
            raise typer.Exit(1)
        
        if not any(target_directory.iterdir()):
            console.print(f"[yellow]⚠️  Warning: Directory '{target_directory}' is empty[/yellow]")
        
        # Display start message
        console.print(Panel.fit(
            f"[bold cyan]Test Generation Started[/bold cyan]\n\n"
            f"📁 Source: [green]{target_directory}[/green]\n"
            f"📝 Output: [green]{output_dir}[/green]\n"
            f"👀 Watch Mode: [yellow]{'Enabled' if watch else 'Disabled'}[/yellow]",
            title="🚀 TestGen AI",
            border_style="cyan"
        ))
        
        if state.verbose:
            console.print(f"[dim]Target directory: {target_directory.absolute()}[/dim]")
            console.print(f"[dim]Output directory: {output_dir.absolute()}[/dim]")
        
        # Import and initialize WorkflowManager
        from testgen.manager import WorkflowManager
        
        # Use target_directory as project_path
        # Outputs will go to: target_directory/TestGen-AI/tests/ and target_directory/TestGen-AI/reports/
        workflow_config = {
            'language': 'python',  # TODO: Auto-detect from files
            'verbose': state.verbose
        }
        
        # Pass target_directory as project_path
        manager = WorkflowManager(project_path=str(target_directory), config=workflow_config)
        
        # Execute generate workflow
        console.print("\n[yellow]📊 Analyzing code and generating tests...[/yellow]")
        
        result = manager.execute_generate(
            source_files=[str(target_directory)],
            language='python'
        )
        
        # Success message
        console.print("\n[green]✅ Test generation completed![/green]")
        console.print(f"[green]Generated {result.get('tests_generated', 0)} test files[/green]")
        console.print(f"[dim]Output directory: {output_dir}[/dim]")

        
        # TODO: Watch mode integration
        if watch:
            # ── Real watch mode using UniversalFileWatcher ─────────────────
            try:
                from testgen.core.watcher import UniversalFileWatcher, WATCHDOG_AVAILABLE, FileChangeType
                from testgen.core.language_config import Language
            except ImportError:
                WATCHDOG_AVAILABLE = False

            if not WATCHDOG_AVAILABLE:
                console.print("[red]❌ Watch mode dependency unavailable. Try: pip install --upgrade testgen-ai[/red]")
                raise typer.Exit(1)

            import threading

            console.print(Panel.fit(
                f"[bold cyan]Watch Mode Active[/bold cyan]\n\n"
                f"👀 Watching: [green]{target_directory}[/green]\n"
                f"⏱️  Debounce: [yellow]2.0s[/yellow]\n"
                f"⌨️  Press [bold]Ctrl+C[/bold] to stop",
                title="🔄 TestGen AI — Watch Mode",
                border_style="yellow"
            ))

            # Lock to prevent concurrent generate calls
            _gen_lock = threading.Lock()

            def on_file_changed(event):
                """Called whenever a watched source file changes."""
                if event.is_test_file:
                    return  # Ignore changes to generated test files

                changed_path = str(event.path)
                change_label = event.change_type.value.upper()

                console.print(
                    f"\n[yellow]🔄 [{change_label}] {event.path.name}[/yellow] "
                    f"[dim]({changed_path})[/dim]"
                )

                # Skip deletions — nothing to regenerate
                if event.change_type == FileChangeType.DELETED:
                    console.print("[dim]   ↳ File deleted — skipping regeneration[/dim]")
                    return

                if not _gen_lock.acquire(blocking=False):
                    console.print("[dim]   ↳ Already regenerating — change queued[/dim]")
                    return

                try:
                    console.print("[cyan]   ↳ Regenerating tests...[/cyan]")
                    gen_result = manager.execute_generate(
                        source_files=[changed_path],
                        language='python'
                    )
                    tests_made = gen_result.get('tests_generated', 0)
                    console.print(f"[green]   ✅ Done — {tests_made} test file(s) updated[/green]")
                except Exception as exc:
                    console.print(f"[red]   ❌ Regeneration failed: {exc}[/red]")
                    if state.debug:
                        console.print_exception()
                finally:
                    _gen_lock.release()

            watcher = UniversalFileWatcher(
                watch_paths=[str(target_directory)],
                languages=[Language.PYTHON],
                debounce_seconds=2.0,
                ignore_patterns=[
                    '*.pyc', '__pycache__', 'TestGen-AI',
                    '.git', 'node_modules', '*.pyo'
                ]
            )
            watcher.on_change(on_file_changed)

            try:
                watcher.start()
                console.print("[green]✅ Watching for file changes... (Ctrl+C to stop)[/green]\n")
                while True:
                    import time as _time
                    _time.sleep(0.5)
            except KeyboardInterrupt:
                watcher.stop()
                console.print("\n[yellow]👋 Watch mode stopped[/yellow]")

        
    except Exception as e:
        console.print(f"[red]❌ Error during test generation: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def test(
    project_dir: Optional[Path] = typer.Argument(
        None,
        help="Project directory whose generated tests to run (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    test_directory: Optional[Path] = typer.Option(
        None,
        "--tests",
        "-t",
        help="Explicit test directory (overrides auto-discovery inside project_dir)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    pattern: str = typer.Option(
        "test_*.py",
        "--pattern",
        "-p",
        help="Test file pattern to match",
    ),
    verbose_tests: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed test output",
    ),
):
    """
    Run generated tests and display results.
    
    Auto-discovers the most recent test run inside <project_dir>/TestGen-AI/tests/.
    Results are cached so 'testgen report <project_dir>' can build a report.
    
    Examples:
        testgen test ./my-project
        testgen test ./my-project --tests ./custom-tests
        testgen test ./my-project --pattern "test_*.py" --verbose
    """
    try:
        resolved_project_dir = project_dir or Path.cwd()
        
        # Auto-discover test directory if not explicitly provided
        if test_directory:
            test_dir = test_directory
        else:
            # Look inside <project>/TestGen-AI/tests/ and pick the most recent run
            tests_base = resolved_project_dir / "TestGen-AI" / "tests"
            if tests_base.exists():
                # Find the latest timestamped run folder
                run_dirs = sorted(
                    [d for d in tests_base.iterdir() if d.is_dir()],
                    reverse=True
                )
                if run_dirs:
                    test_dir = run_dirs[0]
                else:
                    test_dir = tests_base  # fallback: run on the base
            else:
                # Fallback to legacy default
                test_dir = resolved_project_dir / "tests"
        
        # Validate test directory
        if not test_dir.exists():
            console.print(f"[red]❌ Error: Test directory '{test_dir}' does not exist[/red]")
            console.print("[yellow]💡 Hint: Run 'testgen generate <project_dir>' first to create tests[/yellow]")
            raise typer.Exit(1)
        
        # Display start message
        console.print(Panel.fit(
            f"[bold cyan]Test Execution Started[/bold cyan]\n\n"
            f"📁 Project:   [green]{resolved_project_dir}[/green]\n"
            f"🧪 Tests dir: [green]{test_dir}[/green]\n"
            f"🔍 Pattern:   [yellow]{pattern}[/yellow]\n"
            f"📊 Verbose:   [yellow]{'Yes' if verbose_tests or state.verbose else 'No'}[/yellow]",
            title="🧪 TestGen AI",
            border_style="cyan"
        ))
        
        if state.verbose:
            console.print(f"[dim]Project dir: {resolved_project_dir.absolute()}[/dim]")
            console.print(f"[dim]Test directory: {test_dir.absolute()}[/dim]")
            console.print(f"[dim]Test pattern: {pattern}[/dim]")
        
        # Initialize WorkflowManager anchored to the project directory
        from testgen.manager import WorkflowManager
        
        workflow_config = {
            'language': 'python',
            'output_dir': str(test_dir),
            'verbose': state.verbose or verbose_tests
        }
        
        manager = WorkflowManager(
            project_path=str(resolved_project_dir),
            config=workflow_config,
            use_timestamp_folders=False
        )
        
        # Execute test workflow
        console.print("\n[yellow]🧪 Running tests...[/yellow]")
        
        result = manager.execute_test(
            test_files=None,  # Auto-discover inside test_dir
            language='python'
        )
        
        # Cache results for report generation (stored in <project>/TestGen-AI/.cache/)
        manager.cache_test_results(result, 'python')
        
        # Display results
        console.print("\n[bold cyan]═══ Test Results ═══[/bold cyan]\n")
        console.print(f"  [bold]Total:[/bold]   {result.get('total', 0)}")
        console.print(f"  [green]Passed:[/green]  {result.get('passed', 0)}")
        console.print(f"  [red]Failed:[/red]  {result.get('failed', 0)}")
        console.print(f"  [yellow]Skipped:[/yellow] {result.get('skipped', 0)}")
        console.print(f"  [magenta]Errors:[/magenta]  {result.get('errors', 0)}")
        console.print(f"  [blue]Duration:[/blue] {result.get('duration', 0):.2f}s")
        
        # Success message
        console.print("\n[green]✅ Test execution completed![/green]")
        console.print(f"[dim]💡 Run 'testgen report {resolved_project_dir}' to generate a report[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during test execution: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def report(
    project_dir: Optional[Path] = typer.Argument(
        None,
        help="Project directory to generate report for (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for report (default: <project_dir>/TestGen-AI/reports/report_<timestamp>.html)",
    ),
    pdf: bool = typer.Option(
        False,
        "--pdf",
        help="Generate PDF report instead of HTML",
    ),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open report in browser after generation",
    ),
):
    """
    Generate professional test reports from cached results.

    Transforms raw JSON test execution data into beautiful, interactive HTML
    reports for developer review. Reports include success charts, timing
    analysis, and detailed test tables.
    
    Creates beautiful HTML reports with test results, coverage, and charts.
    Reports are saved inside the project directory for easy access.
    
    Examples:
        testgen report ./my-project
        testgen report ./my-project --no-open
        testgen report ./my-project --output ./my-report.html
    """
    from datetime import datetime

    try:
        # Resolve project directory (default: CWD)
        resolved_project_dir = project_dir or Path.cwd()
        
        # Determine output path: <project>/TestGen-AI/reports/ with timestamped name
        if not output_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            ext = "pdf" if pdf else "html"
            report_dir = resolved_project_dir / "TestGen-AI" / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            output_path = report_dir / f"report_{timestamp}.{ext}"

        format_type = "PDF" if pdf else "HTML"
        
        # Display start message
        console.print(Panel.fit(
            f"[bold cyan]Report Generation Started[/bold cyan]\n\n"
            f"📁 Project:  [green]{resolved_project_dir}[/green]\n"
            f"📊 Format:   [yellow]{format_type}[/yellow]\n"
            f"📝 Output:   [green]{output_path}[/green]\n"
            f"🌐 Browser:  [yellow]{'Yes' if open_browser and not pdf else 'No'}[/yellow]",
            title="📈 TestGen AI",
            border_style="cyan"
        ))
        
        if state.verbose:
            console.print(f"[dim]Project dir: {resolved_project_dir.absolute()}[/dim]")
            console.print(f"[dim]Output path: {output_path.absolute()}[/dim]")
        
        # Initialize WorkflowManager anchored to the project directory
        from testgen.manager import WorkflowManager
        
        workflow_config = {
            'language': 'python',
            'report_dir': str(output_path.parent),
            'verbose': state.verbose
        }
        
        manager = WorkflowManager(
            project_path=str(resolved_project_dir),
            config=workflow_config,
            use_timestamp_folders=False
        )
        
        # Load cached test results
        console.print("\n[yellow]📂 Loading test results...[/yellow]")
        state_info = manager.get_state()
        
        if not state_info.get('test_results'):
            console.print("[yellow]⚠️  No test results found in cache[/yellow]")
            console.print("[dim]💡 Hint: Run 'testgen test <project_dir>' first[/dim]")
            test_results = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration': 0.0,
                'results': []
            }
        else:
            test_results = state_info['test_results']
        
        # Generate report
        console.print(f"\n[yellow]📊 Generating {format_type} report...[/yellow]")
        
        report_format = 'pdf' if pdf else 'html'
        report_path = manager.execute_report(
            results=test_results,
            format=report_format
        )
        
        # Success message
        console.print(f"\n[green]✅ Report generated successfully![/green]")
        console.print(f"[green]📄 Report: {report_path}[/green]")
        
        # Open in browser if requested
        if open_browser and not pdf and report_path:
            import webbrowser
            webbrowser.open(f"file://{Path(report_path).absolute()}")
            console.print("[cyan]🌐 Opened report in browser[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during report generation: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def auto(
    target_directory: Path = typer.Argument(
        ...,
        help="Directory containing source code to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for generated tests (default: ./tests)",
    ),
    skip_report: bool = typer.Option(
        False,
        "--skip-report",
        help="Skip report generation at the end",
    ),
):
    """
    Run the complete autonomous workflow: Analyze → Generate → Test → Report.

    The 'God Mode' command provides a true one-click solution for AI-powered
    quality assurance. It automates the entire lifecycle from code analysis
    to visual reporting.

    [bold]Steps Performed:[/bold]
    1. [bold blue]Analyze:[/bold blue] Scans code for eligible source files.
    2. [bold blue]Generate:[/bold blue] Creates comprehensive tests with AI.
    3. [bold blue]Execute:[/bold blue] Runs the newly created tests.
    4. [bold blue]Report:[/bold blue] Produces a visual analysis of the results.

    [bold]Examples:[/bold]
    - testgen auto ./src
    - testgen auto ./src --output ./my-tests
    - testgen auto ./src --skip-report
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    
    try:
        output_dir = output or Path(config.test_output_dir)
        
        # Display start message
        console.print("\n")
        console.print(Panel.fit(
            f"[bold cyan]🚀 TestGen AI - God Mode Activated[/bold cyan]\n\n"
            f"[bold]Complete Workflow:[/bold]\n"
            f"1️⃣  Analyze code\n"
            f"2️⃣  Generate tests with AI\n"
            f"3️⃣  Run test suite\n"
            f"4️⃣  {'Create report' if not skip_report else '[dim]Skip report[/dim]'}\n\n"
            f"📁 Source: [green]{target_directory}[/green]\n"
            f"📝 Tests: [green]{output_dir}[/green]",
            title="🎯 Auto Mode",
            border_style="cyan"
        ))
        
        console.print("\n")
        
        # Initialize WorkflowManager
        from testgen.manager import WorkflowManager
        
        # Use target_directory as project_path
        # Outputs will go to: target_directory/TestGen-AI/tests/ and target_directory/TestGen-AI/reports/
        workflow_config = {
            'language': 'python',  # TODO: Auto-detect
            'verbose': state.verbose
        }
        
        # Pass target_directory as project_path
        manager = WorkflowManager(project_path=str(target_directory), config=workflow_config)
        
        # Execute auto workflow
        console.print("[bold cyan]═══ Executing Auto Workflow ═══[/bold cyan]\n")
        
        result = manager.execute_auto(
            source_files=[str(target_directory)],
            language='python',
            report_format='both' if not skip_report else 'json'
        )
        
        # Final Summary
        state_info = manager.get_state()
        console.print(Panel.fit(
            f"[bold green]✅ All Phases Complete![/bold green]\n\n"
            f"[bold]Summary:[/bold]\n"
            f"  • Files Scanned: [yellow]{result.get('generate', {}).get('files_scanned', 0)}[/yellow]\n"
            f"  • Tests Generated: [green]{result.get('generate', {}).get('tests_generated', 0)}[/green]\n"
            f"  • Total Duration: [cyan]{result.get('total_duration', 0):.2f}s[/cyan]\n"
            f"  • Report: [cyan]{'Generated' if not skip_report else 'Skipped'}[/cyan]",
            title="🎉 Workflow Complete",
            border_style="green"
        ))
        
        console.print("\n[bold green]Success![/bold green] Your autonomous QA agent has completed all tasks.")
        console.print("[dim]💡 Tip: Use individual commands (generate, test, report) for more control[/dim]\n")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error during auto workflow: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


# ── Config subcommand group ──────────────────────────────────────────────────

config_app = typer.Typer(
    help="Manage global TestGen AI configuration (API keys, model, provider).",
    no_args_is_help=True,
)
app.add_typer(config_app, name="config")


def _write_global_env(key: str, value: str) -> None:
    """Write or update a single KEY=VALUE entry in ~/.testgen/.env."""
    from testgen.config import GLOBAL_CONFIG_DIR, GLOBAL_ENV_FILE

    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Read existing lines (if the file already exists)
    existing: dict[str, str] = {}
    if GLOBAL_ENV_FILE.exists():
        for line in GLOBAL_ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                existing[k.strip().upper()] = v.strip()

    existing[key.upper()] = value

    lines = [f"{k}={v}" for k, v in existing.items()]
    GLOBAL_ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key, e.g. GEMINI_API_KEY or LLM_PROVIDER"),
    value: str = typer.Argument(..., help="Value to store"),
):
    """
    Save a configuration value globally (works from any directory).

    Writes to [bold]~/.testgen/.env[/bold] so the setting persists across all projects.
    A local [bold].env[/bold] file in your project directory always overrides the global value.

    [bold]Common keys:[/bold]
    - GEMINI_API_KEY      — Google Gemini API key
    - OPENAI_API_KEY      — OpenAI API key
    - ANTHROPIC_API_KEY   — Anthropic / Claude API key
    - LLM_PROVIDER        — openai | anthropic | gemini | ollama
    - LLM_MODEL           — model name, e.g. gpt-4o or gemini-2.0-flash

    [bold]Examples:[/bold]
        testgen config set GEMINI_API_KEY AIza...
        testgen config set LLM_PROVIDER openai
        testgen config set LLM_MODEL gpt-4o
    """
    from testgen.config import GLOBAL_ENV_FILE

    _write_global_env(key, value)

    # Mask the value in output so secrets aren't shown in full
    display = value if len(value) <= 6 else value[:4] + "****" + value[-2:]
    console.print(
        f"[green]✅ Saved[/green] [bold]{key.upper()}[/bold] = [dim]{display}[/dim]\n"
        f"[dim]Stored in: {GLOBAL_ENV_FILE}[/dim]"
    )


@config_app.command("show")
def config_show():
    """
    Display the current active configuration.

    Shows which API keys are set (masked), the active provider and model,
    and where each value is coming from.
    """
    from testgen.config import GLOBAL_ENV_FILE, Config

    # Re-instantiate to pick up any recent writes
    active = Config()

    def mask(v: Optional[str]) -> str:
        if not v:
            return "[dim]not set[/dim]"
        if len(v) <= 8:
            return "[yellow]****[/yellow]"
        return f"[yellow]{v[:4]}****{v[-2:]}[/yellow]"

    console.print(Panel.fit(
        f"[bold]Provider:[/bold]    [cyan]{active.llm_provider.value}[/cyan]\n"
        f"[bold]Model:[/bold]       [cyan]{active.llm_model}[/cyan]\n\n"
        f"[bold]GEMINI_API_KEY:[/bold]    {mask(active.gemini_api_key)}\n"
        f"[bold]OPENAI_API_KEY:[/bold]    {mask(active.openai_api_key)}\n"
        f"[bold]ANTHROPIC_API_KEY:[/bold] {mask(active.anthropic_api_key)}\n\n"
        f"[dim]Global config: {GLOBAL_ENV_FILE}[/dim]\n"
        f"[dim]Local override: .env  (in current directory)[/dim]",
        title="⚙️  TestGen AI — Active Configuration",
        border_style="cyan"
    ))


# ── CLI entry point ───────────────────────────────────────────────────────────


def cli():
    """Universal entry point for the TestGen AI command-line interface.

    This function handles high-level exception management (e.g., KeyboardInterrupt)
    and routes the execution to the Typer application.
    """
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        if state.debug:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {e}[/red]")
            console.print("[dim]Run with --debug for full traceback[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
