"""
UI module for TestGen AI.

This module contains user interface components for:
- Terminal output formatting and color-coded matrices (Rich library)
- Test result visualization
- HTML/PDF report generation (Jinja2 templates)
- Progress indicators and spinners
"""

from .printer import TerminalPrinter, create_printer, RICH_AVAILABLE

__all__ = [
    "TerminalPrinter",
    "create_printer",
    "RICH_AVAILABLE",
    # More components will be added as we implement them
    # "reporter",
]
