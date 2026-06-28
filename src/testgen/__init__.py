"""
TestGen AI - The Autonomous QA Agent from Your CLI

A Python-based CLI package that acts as an "Autonomous QA Pair-Programmer."
It lives in your terminal and automates the tedious parts of software testing:
understanding code, writing test cases, running them, and formatting reports.

With Watch Mode, TestGen AI writes tests while you write code, enabling
true Test-Driven Development without the overhead.
"""

__version__ = "0.2.5"
__author__ = "Jay Patil"
__email__ = "your.email@example.com"

# Package metadata
__all__ = [
    "__version__",
    "config",
]

# Import configuration for easy access
from testgen.config import config

