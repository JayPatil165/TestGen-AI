"""
TestGen AI - Main entry point for CLI execution
"""
import sys
import io
import os

# Force UTF-8 output on Windows so Rich emoji/unicode never crash
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from testgen.main import cli

if __name__ == '__main__':
    cli()
