"""
TestGen AI - The Autonomous QA Agent from Your CLI

A Python-based CLI package that acts as an "Autonomous QA Pair-Programmer."
It lives in your terminal and automates the tedious parts of software testing:
understanding code, writing test cases, running them, and formatting reports.

With Watch Mode, TestGen AI writes tests while you write code, enabling
true Test-Driven Development without the overhead.
"""

__version__ = "0.1.0"
__author__ = "Jay Patil"
__email__ = "your.email@example.com"

# Package metadata
__all__ = [
    "__version__",
    "config",
]

# Import configuration for easy access
from testgen.config import config

# Package-level docstring for better IDE support
__doc__ = """
TestGen AI - Autonomous QA Agent

Main Features:
- 🤖 AI-powered test generation using LLMs (OpenAI, Claude, Ollama)
- 📊 Beautiful terminal dashboard with Rich
- 👀 Watch mode for real-time TDD
- 📈 HTML/PDF report generation
- ⚡ Smart context extraction to minimize costs
- 🎯 Support for pytest and Playwright

Quick Start:
    >>> from testgen import config
    >>> config.llm_provider
    'openai'

For CLI usage:
    $ testgen generate ./src
    $ testgen test
    $ testgen report
    $ testgen auto ./src

See documentation at: https://github.com/JayPatil165/TestGen-AI
"""
