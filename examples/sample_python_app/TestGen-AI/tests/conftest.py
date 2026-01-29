"""
Pytest configuration for TestGen-AI generated tests.

This file automatically adds the parent directory to sys.path
so that generated tests can import source modules.
"""
import sys
from pathlib import Path

# Add parent directory (where source files are) to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
