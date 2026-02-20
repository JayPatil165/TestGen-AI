import sys
from pathlib import Path

# Add the TestGen-AI tool root to sys.path (for full package imports like examples.complex_app.main)
_tool_root = r"D:/Programming/Projects/TestGen-AI"
if _tool_root not in sys.path:
    sys.path.insert(0, _tool_root)

# Add the analyzed project directory to sys.path (for short imports like 'from utils.string_utils import ...')
# This file sits at: <project>/TestGen-AI/tests/<run>/conftest.py — project root is 3 levels up.
_conftest_dir = Path(__file__).parent
_project_root = _conftest_dir.parent.parent.parent  # <run>/ → tests/ → TestGen-AI/ → project/
_project_root_str = str(_project_root)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
