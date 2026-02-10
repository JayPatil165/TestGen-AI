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
    """Callback for version flag."""
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
    """
    TestGen AI - AI-Powered Test Generation & Execution
    
    🎯 Quick Start:
        testgen generate ./src      # Generate tests
        testgen test                # Run tests
        testgen report              # Create report
        testgen auto ./src          # Do everything
    
    📚 Documentation: https://github.com/JayPatil165/TestGen-AI
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
            console.print("\n[yellow]👀 Watch mode...[/yellow]")
            console.print("[dim]⚠️  Watch mode will auto-regenerate tests when files change[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during test generation: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def test(
    test_directory: Optional[Path] = typer.Argument(
        None,
        help="Directory containing tests (default: ./tests)",
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
    Run existing tests and display results.
    
    Executes test suite and shows a beautiful terminal matrix with results.
    
    Examples:
        testgen test
        testgen test ./tests
        testgen test --pattern "test_*.py" --verbose
    """
    try:
        # Set test directory
        test_dir = test_directory or Path(config.test_output_dir)
        
        # Validate test directory
        if not test_dir.exists():
            console.print(f"[red]❌ Error: Test directory '{test_dir}' does not exist[/red]")
            console.print("[yellow]💡 Hint: Run 'testgen generate' first to create tests[/yellow]")
            raise typer.Exit(1)
        
        # Display start message
        console.print(Panel.fit(
            f"[bold cyan]Test Execution Started[/bold cyan]\n\n"
            f"📁 Test Directory: [green]{test_dir}[/green]\n"
            f"🔍 Pattern: [yellow]{pattern}[/yellow]\n"
            f"📊 Verbose: [yellow]{'Yes' if verbose_tests or state.verbose else 'No'}[/yellow]",
            title="🧪 TestGen AI",
            border_style="cyan"
        ))
        
        if state.verbose:
            console.print(f"[dim]Test directory: {test_dir.absolute()}[/dim]")
            console.print(f"[dim]Test pattern: {pattern}[/dim]")
        
        # Initialize WorkflowManager
        from testgen.manager import WorkflowManager
        
        workflow_config = {
            'language': 'python',  # TODO: Auto-detect
            'output_dir': str(test_dir),
            'verbose': state.verbose or verbose_tests
        }
        
        manager = WorkflowManager(
            config=workflow_config,
            use_timestamp_folders=False
        )
        
        # Execute test workflow
        console.print("\n[yellow]🧪 Running tests...[/yellow]")
        
        result = manager.execute_test(
            test_files=None,  # Auto-discover
            language='python'
        )
        
        # Cache results for report generation
        manager.cache_test_results(result, 'python')
        
        # Display results
        console.print("\n[bold cyan]═══ Test Results ═══[/bold cyan]\n")
        console.print(f"  [bold]Total:[/bold] {result.get('total', 0)}")
        console.print(f"  [green]Passed:[/green] {result.get('passed', 0)}")
        console.print(f"  [red]Failed:[/red] {result.get('failed', 0)}")
        console.print(f"  [yellow]Skipped:[/yellow] {result.get('skipped', 0)}")
        console.print(f"  [magenta]Errors:[/magenta] {result.get('errors', 0)}")
        console.print(f"  [blue]Duration:[/blue] {result.get('duration', 0):.2f}s")
        
        # Success message
        console.print("\n[green]✅ Test execution completed![/green]")

        
    except Exception as e:
        console.print(f"[red]❌ Error during test execution: {e}[/red]")
        if state.debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def report(
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for report (default: ./reports/testgen-report.html)",
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
    Generate a test report from cached results.
    
    Creates beautiful HTML or PDF reports with test results, coverage, and charts.
    
    Examples:
        testgen report
        testgen report --pdf
        testgen report --output ./my-report.html
    """
    try:
        # Determine output format and path
        if pdf and not output_path:
            output_path = Path(config.report_output_dir) / "testgen-report.pdf"
        elif not output_path:
            output_path = Path(config.report_output_dir) / "testgen-report.html"
        
        format_type = "PDF" if pdf else "HTML"
        
        # Display start message
        console.print(Panel.fit(
            f"[bold cyan]Report Generation Started[/bold cyan]\n\n"
            f"📊 Format: [yellow]{format_type}[/yellow]\n"
            f"📝 Output: [green]{output_path}[/green]\n"
            f"🌐 Open in Browser: [yellow]{'Yes' if open_browser and not pdf else 'No'}[/yellow]",
            title="📈 TestGen AI",
            border_style="cyan"
        ))
        
        if state.verbose:
            console.print(f"[dim]Output path: {output_path.absolute()}[/dim]")
            console.print(f"[dim]Format: {format_type}[/dim]")
        
        # Initialize WorkflowManager
        from testgen.manager import WorkflowManager
        
        workflow_config = {
            'language': 'python',
            'report_dir': str(output_path.parent),
            'verbose': state.verbose
        }
        
        manager = WorkflowManager(
            config=workflow_config,
            use_timestamp_folders=False
        )
        
        # Check if we have cached test results
        console.print("\n[yellow]📂 Loading test results...[/yellow]")
        
        # Get last execution state
        state_info = manager.get_state()
        
        if not state_info.get('test_results'):
            console.print("[yellow]⚠️  No test results found in cache[/yellow]")
            console.print("[dim]💡 Hint: Run 'testgen test' or 'testgen auto' first[/dim]")
            # Generate a report anyway with empty results
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
        
        if pdf:
            console.print("[yellow]⚠️  PDF generation not yet implemented[/yellow]")
            console.print("[dim]Falling back to HTML format[/dim]")
        
        report_format = 'html'  # TODO: Add PDF support
        report_path = manager.execute_report(
            results=test_results,
            format=report_format
        )
        
        # Success message
        console.print(f"\n[green]✅ Report generated successfully![/green]")
        console.print(f"[green]📄 Report saved to: {report_path}[/green]")
        
        # Open in browser if requested
        if open_browser and not pdf:
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
    Run the complete workflow: Generate → Test → Report (God Mode).
    
    This is the one-click solution that does everything:
    1. Analyzes your code
    2. Generates tests with AI
    3. Runs all tests
    4. Creates a beautiful HTML report
    
    Examples:
        testgen auto ./src
        testgen auto ./src --output ./my-tests
        testgen auto ./src --skip-report
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


# CLI entry point
def cli():
    """Main entry point for the CLI."""
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
