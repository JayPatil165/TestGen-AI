"""
TestGen-AI UI module.

Exports terminal printer and report generator functionality.
"""

from .printer import TerminalPrinter, create_printer, RICH_AVAILABLE
from .reporter import ReportGenerator, ExecutionSummary, create_reporter

__all__ = [
    'TerminalPrinter',
    'create_printer',
    'RICH_AVAILABLE',
    'ReportGenerator',
    'ExecutionSummary',
    'create_reporter',
]
