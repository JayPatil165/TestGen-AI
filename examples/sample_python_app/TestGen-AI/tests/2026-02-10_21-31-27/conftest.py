import sys
from pathlib import Path

# Add project root to sys.path
# Structure: root/TestGen-AI/tests/timestamp/conftest.py
# We need to add 'root' to sys.path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))
