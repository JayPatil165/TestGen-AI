"""
TestGen AI - The Autonomous QA Agent from Your CLI

A Python-based CLI package that acts as an "Autonomous QA Pair-Programmer."
It lives in your terminal and automates the tedious parts of software testing:
understanding code, writing test cases, running them, and formatting reports.

With Watch Mode, TestGen AI writes tests while you write code, enabling
true Test-Driven Development without the overhead.
"""

__version__ = "0.1.9"
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
- 🌍 14+ languages supported
- 👀 Watch mode for real-time test generation
- 📊 Terminal dashboards and HTML reports
"""


def _ensure_in_path() -> None:
    """
    One-time initialization: Try to add testgen Scripts folder to PATH on Windows.
    This runs silently on import and only attempts once per installation.
    Does nothing on macOS/Linux (not needed there).
    """
    import platform
    import sys
    from pathlib import Path
    
    # Only attempt on Windows
    if platform.system() != "Windows":
        return
    
    # Check if already in PATH
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-c", "import shutil; shutil.which('testgen')"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            return  # Already in PATH
    except Exception:
        pass
    
    # Try to add to PATH via registry
    try:
        import winreg
        
        scripts_path = None
        # Try to find Scripts folder
        candidate = Path(sys.executable).parent / "Scripts"
        if candidate.exists():
            scripts_path = str(candidate)
        
        if not scripts_path:
            candidate = Path(sys.prefix) / "Scripts"
            if candidate.exists():
                scripts_path = str(candidate)
        
        if scripts_path:
            key_path = r"Environment"
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            
            try:
                path_value = winreg.QueryValueEx(reg_key, "Path")[0]
            except FileNotFoundError:
                path_value = ""
            
            # Check if already in PATH
            if path_value and scripts_path.lower() not in path_value.lower():
                # Add to PATH
                new_path = f"{path_value};{scripts_path}" if path_value else scripts_path
                try:
                    winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                except PermissionError:
                    # Silently fail if no admin access - user can run testgen setup manually
                    pass
            
            winreg.CloseKey(reg_key)
    except Exception:
        # Silently fail - this is not critical, user can run testgen setup manually
        pass


# Auto-setup on import (silent, non-blocking)
try:
    _ensure_in_path()
except Exception:
    pass  # Never crash on startup for any reason

