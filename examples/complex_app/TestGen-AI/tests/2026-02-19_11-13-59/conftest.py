import sys
from pathlib import Path

# Add the TestGen-AI project root to sys.path (for full package paths like examples.complex_app.main)
tool_root = r"D:/Programming/Projects/TestGen-AI"
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

# Add the analyzed project directory to sys.path (for short imports like 'from utils.string_utils import ...')
# This file sits at: <project>/TestGen-AI/tests/<run>/conftest.py
# So the project root is 3 levels up.
_conftest_dir = Path(__file__).parent
_project_root = _conftest_dir.parent.parent.parent  # up from <run>/ → tests/ → TestGen-AI/ → project/
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
