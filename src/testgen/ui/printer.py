"""
Universal Terminal UI Printer for TestGen AI.

Beautiful terminal output using Rich library for ALL 14 programming languages.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Table = None
    Panel = None

from ..core.language_config import Language


class TerminalPrinter:
    """
    Universal terminal printer supporting ALL 14 programming languages.
    
    Provides beautiful, formatted output for test results, progress,
    and statistics using the Rich library.
    """
    
    def __init__(self, use_color: bool = True):
        """
        Initialize terminal printer.
        
        Args:
            use_color: Whether to use colored output
        """
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library not installed. Install with: pip install rich"
            )
        
        self.console = Console(color_system="auto" if use_color else None)
        self.use_color = use_color
    
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """
        Print a formatted header.
        
        Args:
            title: Main title
            subtitle: Optional subtitle
        """
        content = f"[bold cyan]{title}[/bold cyan]"
        if subtitle:
            content += f"\n[dim]{subtitle}[/dim]"
        
        panel = Panel(
            content,
            style="bold blue",
            border_style="blue"
        )
        self.console.print(panel)
    
    def print_test_result(
        self,
        test_name: str,
        status: str,
        duration: float,
        details: Optional[str] = None,
        language: Optional[Language] = None
    ) -> None:
        """
        Print a single test result.
        
        Args:
            test_name: Name of the test
            status: Test status (PASS, FAIL, SKIP)
            duration: Test duration in seconds
            details: Optional details message
            language: Programming language
        """
        # Status icon and color
        if status == "PASS":
            status_text = "[bold green]✔ PASS[/bold green]"
        elif status == "FAIL":
            status_text = "[bold red]✘ FAIL[/bold red]"
        elif status == "SKIP":
            status_text = "[yellow]⊘ SKIP[/yellow]"
        else:
            status_text = f"[dim]{status}[/dim]"
        
        # Duration color coding
        if duration < 1.0:
            duration_text = f"[green]{duration:.2f}s[/green]"
        elif duration < 5.0:
            duration_text = f"[yellow]{duration:.2f}s[/yellow]"
        else:
            duration_text = f"[red]{duration:.2f}s[/red]"
        
        # Language badge
        lang_text = ""
        if language:
            lang_text = f"[blue][[/blue][cyan]{language.value}[/cyan][blue]][/blue] "
        
        # Format output
        output = f"{lang_text}{status_text} {test_name} [dim]({duration_text})[/dim]"
        
        if details:
            output += f"\n    [dim]{details}[/dim]"
        
        self.console.print(output)
    
    def print_test_table(
        self,
        results: List[Dict[str, Any]],
        title: str = "Test Results"
    ) -> None:
        """
        Print test results in a formatted table.
        
        Args:
            results: List of test result dictionaries
            title: Table title
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        table.add_column("Language", style="cyan", width=12)
        table.add_column("Test Name", style="white", width=30)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Details", style="dim", width=40)
        
        for result in results:
            # Get values
            language = result.get('language', 'unknown')
            test_name = result.get('test_name', 'N/A')
            status = result.get('status', 'UNKNOWN')
            duration = result.get('duration', 0.0)
            details = result.get('details', '')
            
            # Format status
            if status == "PASS":
                status_cell = "[green]✔ PASS[/green]"
            elif status == "FAIL":
                status_cell = "[red]✘ FAIL[/red]"
            elif status == "SKIP":
                status_cell = "[yellow]⊘ SKIP[/yellow]"
            else:
                status_cell = status
            
            # Format duration
            if duration < 1.0:
                duration_cell = f"[green]{duration:.2f}s[/green]"
            elif duration < 5.0:
                duration_cell = f"[yellow]{duration:.2f}s[/yellow]"
            else:
                duration_cell = f"[red]{duration:.2f}s[/red]"
            
            table.add_row(
                language,
                test_name,
                status_cell,
                duration_cell,
                details[:40]  # Truncate long details
            )
        
        self.console.print(table)
    
    def render_test_result(
        self,
        result: Dict[str, Any],
        table: Optional[Table] = None
    ) -> str:
        """
        Dynamically render a single test result row.
        
        Creates a formatted row for a test result that can be added
        to a table or displayed standalone.
        
        Args:
            result: Test result dictionary with keys:
                   - language: str
                   - test_name: str
                   - status: str (PASS/FAIL/SKIP)
                   - duration: float
                   - details: str (optional)
            table: Optional existing table to add row to
            
        Returns:
            Formatted row string
        """
        # Extract values
        language = result.get('language', 'unknown').upper()
        test_name = result.get('test_name', 'N/A')
        status = result.get('status', 'UNKNOWN')
        duration = result.get('duration', 0.0)
        details = result.get('details', '')
        
        # Format duration to 2 decimal places
        duration_str = f"{duration:.2f}s"
        
        # Truncate long error messages with "..."
        max_details_length = 40
        if len(details) > max_details_length:
            details = details[:max_details_length - 3] + "..."
        
        # Format status with color
        if status == "PASS":
            status_cell = "[green]✔ PASS[/green]"
        elif status == "FAIL":
            status_cell = "[red]✘ FAIL[/red]"
        elif status == "SKIP":
            status_cell = "[yellow]⊘ SKIP[/yellow]"
        else:
            status_cell = status
        
        # Format duration with color
        if duration < 1.0:
            duration_cell = f"[green]{duration_str}[/green]"
        elif duration < 5.0:
            duration_cell = f"[yellow]{duration_str}[/yellow]"
        else:
            duration_cell = f"[red]{duration_str}[/red]"
        
        # If table provided, add row to it
        if table is not None:
            table.add_row(
                language,
                test_name,
                status_cell,
                duration_cell,
                details
            )
        
        # Return formatted string representation
        return f"{language:12} {test_name:30} {status:10} {duration_str:10} {details:40}"
    
    def print_summary(
        self,
        total: int,
        passed: int,
        failed: int,
        skipped: int,
        duration: float,
        language: Optional[Language] = None
    ) -> None:
        """
        Print test summary.
        
        Args:
            total: Total tests
            passed: Passed tests
            failed: Failed tests
            skipped: Skipped tests
            duration: Total duration
            language: Programming language
        """
        # Build summary text
        summary_lines = []
        
        if language:
            summary_lines.append(f"[bold]Language:[/bold] [cyan]{language.value.upper()}[/cyan]")
        
        summary_lines.append(f"[bold]Total Tests:[/bold] {total}")
        summary_lines.append(f"[green]Passed:[/green] {passed}")
        
        if failed > 0:
            summary_lines.append(f"[red]Failed:[/red] {failed}")
        
        if skipped > 0:
            summary_lines.append(f"[yellow]Skipped:[/yellow] {skipped}")
        
        summary_lines.append(f"[bold]Total Duration:[/bold] {duration:.2f}s")
        
        # Calculate and show average duration
        if total > 0:
            avg_duration = duration / total
            summary_lines.append(f"[bold]Average Duration:[/bold] {avg_duration:.2f}s")
        
        # Success rate
        if total > 0:
            success_rate = (passed / total) * 100
            if success_rate == 100:
                rate_text = f"[bold green]{success_rate:.1f}%[/bold green]"
            elif success_rate >= 80:
                rate_text = f"[green]{success_rate:.1f}%[/green]"
            elif success_rate >= 50:
                rate_text = f"[yellow]{success_rate:.1f}%[/yellow]"
            else:
                rate_text = f"[red]{success_rate:.1f}%[/red]"
            
            summary_lines.append(f"[bold]Success Rate:[/bold] {rate_text}")
        
        # Create panel
        summary_text = "\n".join(summary_lines)
        panel = Panel(
            summary_text,
            title="[bold]Test Summary[/bold]",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def print_multi_language_summary(
        self,
        results_by_language: Dict[str, Dict[str, int]]
    ) -> None:
        """
        Print summary for multiple languages.
        
        Args:
            results_by_language: Dictionary mapping language to stats
        """
        table = Table(
            title="Multi-Language Test Summary",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Language", style="cyan", width=15)
        table.add_column("Total", justify="right", width=8)
        table.add_column("Passed", justify="right", width=8)
        table.add_column("Failed", justify="right", width=8)
        table.add_column("Skipped", justify="right", width=8)
        table.add_column("Success Rate", justify="right", width=12)
        
        for language, stats in results_by_language.items():
            total = stats.get('total', 0)
            passed = stats.get('passed', 0)
            failed = stats.get('failed', 0)
            skipped = stats.get('skipped', 0)
            
            # Success rate
            if total > 0:
                rate = (passed / total) * 100
                if rate == 100:
                    rate_cell = f"[bold green]{rate:.1f}%[/bold green]"
                elif rate >= 80:
                    rate_cell = f"[green]{rate:.1f}%[/green]"
                elif rate >= 50:
                    rate_cell = f"[yellow]{rate:.1f}%[/yellow]"
                else:
                    rate_cell = f"[red]{rate:.1f}%[/red]"
            else:
                rate_cell = "N/A"
            
            table.add_row(
                language.upper(),
                str(total),
                f"[green]{passed}[/green]" if passed > 0 else "0",
                f"[red]{failed}[/red]" if failed > 0 else "0",
                f"[yellow]{skipped}[/yellow]" if skipped > 0 else "0",
                rate_cell
            )
        
        self.console.print(table)
    
    def print_progress_bar(self, description: str, total: int) -> Progress:
        """
        Create and return a progress bar.
        
        Args:
            description: Progress description
            total: Total items
            
        Returns:
            Progress object
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
        
        return progress
    
    def create_multi_file_progress(
        self,
        description: str,
        show_time: bool = True,
        show_speed: bool = False
    ) -> Progress:
        """
        Create an enhanced progress bar for multi-file processing.
        
        Shows percentage completion and optionally estimates time remaining.
        
        Args:
            description: Description of the operation
            show_time: Whether to show time remaining estimate
            show_speed: Whether to show processing speed
            
        Returns:
            Rich Progress object configured for multi-file operations
        """
        from rich.progress import TimeRemainingColumn, TransferSpeedColumn
        
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ]
        
        if show_time:
            columns.append(TimeRemainingColumn())
        
        if show_speed:
            columns.append(TransferSpeedColumn())
        
        progress = Progress(*columns, console=self.console)
        
        return progress
    
    def create_live_table(
        self,
        title: str = "Test Results",
        refresh_per_second: int = 4
    ) -> tuple:
        """
        Create a live-updating table for watch mode.
        
        Uses Rich.Live context manager to update table rows without
        re-rendering the entire screen.
        
        Args:
            title: Table title
            refresh_per_second: How many times per second to refresh
            
        Returns:
            Tuple of (Live object, Table object)
        """
        # Create table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        table.add_column("Language", style="cyan", width=12)
        table.add_column("Test Name", style="white", width=30)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Details", style="dim", width=40)
        
        # Create Live context
        live = Live(table, console=self.console, refresh_per_second=refresh_per_second)
        
        return live, table
    
    def update_live_table(
        self,
        table: Table,
        result: Dict[str, Any],
        highlight: bool = True
    ) -> None:
        """
        Add a row to a live-updating table.
        
        Adds a new test result row to the table with optional highlighting
        for recently changed rows.
        
        Args:
            table: Rich Table object to update
            result: Test result dictionary
            highlight: Whether to highlight the new row
        """
        # Get values
        language = result.get('language', 'unknown').upper()
        test_name = result.get('test_name', 'N/A')
        status = result.get('status', 'UNKNOWN')
        duration = result.get('duration', 0.0)
        details = result.get('details', '')
        
        # Format duration
        duration_str = f"{duration:.2f}s"
        
        # Truncate long details
        if len(details) > 40:
            details = details[:37] + "..."
        
        # Format status with color
        if status == "PASS":
            status_cell = "[green]✔ PASS[/green]"
        elif status == "FAIL":
            status_cell = "[red]✘ FAIL[/red]"
        elif status == "SKIP":
            status_cell = "[yellow]⊘ SKIP[/yellow]"
        else:
            status_cell = status
        
        # Format duration with color
        if duration < 1.0:
            duration_cell = f"[green]{duration_str}[/green]"
        elif duration < 5.0:
            duration_cell = f"[yellow]{duration_str}[/yellow]"
        else:
            duration_cell = f"[red]{duration_str}[/red]"
        
        # Highlight recent changes
        if highlight:
            test_name = f"[bold]{test_name}[/bold]"
        
        # Add row to table
        table.add_row(
            language,
            test_name,
            status_cell,
            duration_cell,
            details
        )
    
    def create_spinner(self, message: str, spinner_type: str = "dots") -> Any:
        """
        Create a spinner for long-running operations.
        
        Args:
            message: Message to display with spinner
            spinner_type: Type of spinner animation (dots, line, etc.)
            
        Returns:
            Console status object for use in context manager
        """
        return self.console.status(f"[bold blue]{message}[/bold blue]", spinner=spinner_type)
    
    def print_with_spinner(
        self,
        operation: str,
        language: Optional[Language] = None,
        spinner_type: str = "dots"
    ) -> Any:
        """
        Create a spinner for specific operations.
        
        Provides pre-configured spinners for common operations:
        - Analyzing code
        - Generating tests
        - Running tests
        
        Args:
            operation: Type of operation (analyzing/generating/running)
            language: Optional language being processed
            spinner_type: Spinner animation type
            
        Returns:
            Console status object
        """
        # Build message based on operation
        if operation.lower() in ['analyze', 'analyzing']:
            base_msg = "Analyzing code"
        elif operation.lower() in ['generate', 'generating']:
            base_msg = "Generating tests"
        elif operation.lower() in ['run', 'running']:
            base_msg = "Running tests"
        elif operation.lower() in ['execute', 'executing']:
            base_msg = "Executing tests"
        else:
            base_msg = operation
        
        # Add language if specified
        if language:
            message = f"{base_msg} for [cyan]{language.value}[/cyan]..."
        else:
            message = f"{base_msg}..."
        
        return self.console.status(f"[bold blue]{message}[/bold blue]", spinner=spinner_type)
    
    def print_error(self, message: str, details: Optional[str] = None) -> None:
        """
        Print an error message.
        
        Args:
            message: Error message
            details: Optional error details
        """
        content = f"[bold red]Error:[/bold red] {message}"
        if details:
            content += f"\n\n[dim]{details}[/dim]"
        
        panel = Panel(
            content,
            title="[red]Error[/red]",
            border_style="red"
        )
        
        self.console.print(panel)
    
    def print_warning(self, message: str) -> None:
        """
        Print a warning message.
        
        Args:
            message: Warning message
        """
        self.console.print(f"[yellow]⚠ Warning:[/yellow] {message}")
    
    def print_success(self, message: str) -> None:
        """
        Print a success message.
        
        Args:
            message: Success message
        """
        self.console.print(f"[green]✓ Success:[/green] {message}")
    
    def print_info(self, message: str) -> None:
        """
        Print an info message.
        
        Args:
            message: Info message
        """
        self.console.print(f"[blue]ℹ Info:[/blue] {message}")
    
    def print_status_indicator(
        self,
        status: str,
        message: str,
        use_panel: bool = True
    ) -> None:
        """
        Print a status indicator with emoji/icon for quick scanning.
        
        Args:
            status: Status type (success/failure/warning/info)
            message: Status message
            use_panel: Whether to use Rich.Panel border
        """
        # Select emoji and color based on status
        if status.lower() in ['success', 'pass', 'passed']:
            emoji = "✅"
            color = "green"
            border_style = "green"
        elif status.lower() in ['failure', 'fail', 'failed', 'error']:
            emoji = "❌"
            color = "red"
            border_style = "red"
        elif status.lower() in ['warning', 'warn']:
            emoji = "⚠️"
            color = "yellow"
            border_style = "yellow"
        elif status.lower() in ['info', 'information']:
            emoji = "ℹ️"
            color = "blue"
            border_style = "blue"
        elif status.lower() in ['skip', 'skipped']:
            emoji = "⊘"
            color = "yellow"
            border_style = "yellow"
        else:
            emoji = "•"
            color = "white"
            border_style = "white"
        
        # Format content
        content = f"{emoji} [{color}]{message}[/{color}]"
        
        # Display with or without panel
        if use_panel:
            panel = Panel(
                content,
                border_style=border_style,
                padding=(0, 1)
            )
            self.console.print(panel)
        else:
            self.console.print(content)
    
    def print_overall_status(
        self,
        total: int,
        passed: int,
        failed: int,
        skipped: int
    ) -> None:
        """
        Print color-coded overall status with visual indicators.
        
        Green if all pass, red if any fail, yellow if any skipped.
        
        Args:
            total: Total tests
            passed: Passed tests
            failed: Failed tests
            skipped: Skipped tests
        """
        # Determine overall status
        if total == 0:
            status = "NO TESTS"
            emoji = "⚠️"
            color = "yellow"
            border_style = "yellow"
        elif failed > 0:
            status = "FAILED"
            emoji = "❌"
            color = "red"
            border_style = "red"
        elif skipped > 0:
            status = "PARTIAL"
            emoji = "⚠️"
            color = "yellow"
            border_style = "yellow"
        elif passed == total:
            status = "SUCCESS"
            emoji = "✅"
            color = "green"
            border_style = "green"
        else:
            status = "UNKNOWN"
            emoji = "❓"
            color = "white"
            border_style = "white"
        
        # Create status summary
        summary_lines = []
        summary_lines.append(f"{emoji} [bold {color}]{status}[/bold {color}]")
        summary_lines.append("")
        summary_lines.append(f"Total: {total}")
        
        if passed > 0:
            summary_lines.append(f"[green]✔ Passed: {passed}[/green]")
        if failed > 0:
            summary_lines.append(f"[red]✘ Failed: {failed}[/red]")
        if skipped > 0:
            summary_lines.append(f"[yellow]⊘ Skipped: {skipped}[/yellow]")
        
        # Create panel
        content = "\n".join(summary_lines)
        panel = Panel(
            content,
            title=f"[bold]Overall Status[/bold]",
            border_style=border_style,
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()
    
    def print_separator(self) -> None:
        """Print a separator line."""
        self.console.print("─" * self.console.width)


# Convenience function
def create_printer(use_color: bool = True) -> TerminalPrinter:
    """
    Create a terminal printer instance.
    
    Args:
        use_color: Whether to use colored output
        
    Returns:
        TerminalPrinter instance
    """
    return TerminalPrinter(use_color)
