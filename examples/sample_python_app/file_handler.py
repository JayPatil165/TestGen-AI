"""
File handler module - Complex file operations.

Provides file reading, writing, and manipulation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

def read_json_file(filepath: str) -> Dict[str, Any]:
    """Read and parse JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with path.open('r') as f:
        return json.load(f)

def write_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """Write data to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open('w') as f:
        json.dump(data, f, indent=2)

def read_lines(filepath: str) -> List[str]:
    """Read all lines from file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    return path.read_text().splitlines()

def count_lines(filepath: str) -> int:
    """Count lines in file."""
    return len(read_lines(filepath))

def search_in_file(filepath: str, search_term: str) -> List[int]:
    """Search for term in file, return line numbers."""
    lines = read_lines(filepath)
    return [i + 1 for i, line in enumerate(lines) if search_term in line]
