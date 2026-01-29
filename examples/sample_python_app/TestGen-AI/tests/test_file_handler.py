import pytest
import json
from pathlib import Path
from typing import Any, Dict, List

# Assuming the code to be tested is in a file named 'file_handler.py'
# For testing purposes, we'll import directly.
# In a real project, you might structure it as:
# from your_project.file_handler import (
#     read_json_file, write_json_file, read_lines, count_lines, search_in_file
# )

# For this example, we'll define the functions directly or assume they are in scope
# if this test file is placed in the same directory for demonstration.
# To make this runnable, I'll include the original functions here.
# In a real scenario, you would import them.

"""
File handler module - Complex file operations.

Provides file reading, writing, and manipulation.
"""

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


class TestFileHandler:
    """
    Comprehensive test suite for the file_handler module.
    Uses pytest's tmp_path fixture for isolated file operations.
    """

    def test_read_json_file_success(self, tmp_path: Path):
        """
        Test that read_json_file successfully reads and parses a valid JSON file.
        """
        file_content = {"name": "Test", "value": 123, "active": True}
        filepath = tmp_path / "test.json"
        filepath.write_text(json.dumps(file_content))

        result = read_json_file(str(filepath))
        assert result == file_content

    def test_read_json_file_empty_json(self, tmp_path: Path):
        """
        Test that read_json_file correctly reads an empty JSON object.
        """
        file_content = {}
        filepath = tmp_path / "empty.json"
        filepath.write_text(json.dumps(file_content))

        result = read_json_file(str(filepath))
        assert result == file_content

    def test_read_json_file_not_found(self, tmp_path: Path):
        """
        Test that read_json_file raises FileNotFoundError for a non-existent file.
        """
        filepath = tmp_path / "non_existent.json"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            read_json_file(str(filepath))

    def test_read_json_file_invalid_json(self, tmp_path: Path):
        """
        Test that read_json_file raises json.JSONDecodeError for an invalid JSON file.
        """
        filepath = tmp_path / "invalid.json"
        filepath.write_text("this is not json")

        with pytest.raises(json.JSONDecodeError):
            read_json_file(str(filepath))

    def test_write_json_file_success(self, tmp_path: Path):
        """
        Test that write_json_file successfully writes data to a JSON file.
        Verifies content by reading it back.
        """
        data_to_write = {"key": "value", "number": 42}
        filepath = tmp_path / "output.json"
        write_json_file(str(filepath), data_to_write)

        assert filepath.exists()
        with filepath.open('r') as f:
            read_data = json.load(f)
        assert read_data == data_to_write

    def test_write_json_file_empty_data(self, tmp_path: Path):
        """
        Test that write_json_file correctly writes an empty dictionary to a file.
        """
        data_to_write = {}
        filepath = tmp_path / "empty_output.json"
        write_json_file(str(filepath), data_to_write)

        assert filepath.exists()
        with filepath.open('r') as f:
            read_data = json.load(f)
        assert read_data == data_to_write

    def test_write_json_file_creates_directories(self, tmp_path: Path):
        """
        Test that write_json_file creates parent directories if they don't exist.
        """
        data_to_write = {"nested": True}
        nested_dir = tmp_path / "sub" / "sub_sub"
        filepath = nested_dir / "nested_output.json"
        write_json_file(str(filepath), data_to_write)

        assert filepath.exists()
        assert nested_dir.is_dir()
        with filepath.open('r') as f:
            read_data = json.load(f)
        assert read_data == data_to_write

    def test_read_lines_success(self, tmp_path: Path):
        """
        Test that read_lines successfully reads all lines from a multi-line file.
        """
        file_content = "Line 1\nLine 2\nLine 3"
        filepath = tmp_path / "lines.txt"
        filepath.write_text(file_content)

        result = read_lines(str(filepath))
        assert result == ["Line 1", "Line 2", "Line 3"]

    def test_read_lines_empty_file(self, tmp_path: Path):
        """
        Test that read_lines returns an empty list for an empty file.
        """
        filepath = tmp_path / "empty.txt"
        filepath.write_text("")

        result = read_lines(str(filepath))
        assert result == []

    def test_read_lines_single_line_file(self, tmp_path: Path):
        """
        Test that read_lines correctly reads a file with a single line.
        """
        file_content = "Single line content"
        filepath = tmp_path / "single.txt"
        filepath.write_text(file_content)

        result = read_lines(str(filepath))
        assert result == ["Single line content"]

    def test_read_lines_file_not_found(self, tmp_path: Path):
        """
        Test that read_lines raises FileNotFoundError for a non-existent file.
        """
        filepath = tmp_path / "non_existent_lines.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            read_lines(str(filepath))

    def test_count_lines_success(self, tmp_path: Path):
        """
        Test that count_lines correctly counts lines in a multi-line file.
        """
        file_content = "Line A\nLine B\nLine C\nLine D"
        filepath = tmp_path / "count.txt"
        filepath.write_text(file_content)

        result = count_lines(str(filepath))
        assert result == 4

    def test_count_lines_empty_file(self, tmp_path: Path):
        """
        Test that count_lines returns 0 for an empty file.
        """
        filepath = tmp_path / "empty_count.txt"
        filepath.write_text("")

        result = count_lines(str(filepath))
        assert result == 0

    def test_count_lines_single_line_file(self, tmp_path: Path):
        """
        Test that count_lines returns 1 for a single-line file.
        """
        file_content = "Just one line"
        filepath = tmp_path / "single_count.txt"
        filepath.write_text(file_content)

        result = count_lines(str(filepath))
        assert result == 1

    def test_count_lines_file_not_found(self, tmp_path: Path):
        """
        Test that count_lines raises FileNotFoundError for a non-existent file.
        """
        filepath = tmp_path / "non_existent_count.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            count_lines(str(filepath))

    def test_search_in_file_found_multiple_times(self, tmp_path: Path):
        """
        Test that search_in_file finds a term on multiple lines and returns correct line numbers.
        """
        file_content = "apple banana cherry\norange apple grape\nkiwi mango apple"
        filepath = tmp_path / "search.txt"
        filepath.write_text(file_content)

        result = search_in_file(str(filepath), "apple")
        assert result == [1, 2, 3]

    def test_search_in_file_not_found(self, tmp_path: Path):
        """
        Test that search_in_file returns an empty list if the term is not found.
        """
        file_content = "apple banana cherry\norange grape\nkiwi mango"
        filepath = tmp_path / "search_not_found.txt"
        filepath.write_text(file_content)

        result = search_in_file(str(filepath), "watermelon")
        assert result == []

    def test_search_in_file_case_sensitive(self, tmp_path: Path):
        """
        Test that search_in_file is case-sensitive.
        """
        file_content = "Apple banana\napple grape\nAPPLE kiwi"
        filepath = tmp_path / "search_case.txt"
        filepath.write_text(file_content)

        result = search_in_file(str(filepath), "apple")
        assert result == [2] # Only the lowercase 'apple' on line 2

    def test_search_in_file_empty_file(self, tmp_path: Path):
        """
        Test that search_in_file returns an empty list when searching an empty file.
        """
        filepath = tmp_path / "search_empty.txt"
        filepath.write_text("")

        result = search_in_file(str(filepath), "anything")
        assert result == []

    def test_search_in_file_term_in_single_line(self, tmp_path: Path):
        """
        Test that search_in_file finds a term in a single-line file.
        """
        file_content = "This is a test line."
        filepath = tmp_path / "search_single.txt"
        filepath.write_text(file_content)

        result = search_in_file(str(filepath), "test")
        assert result == [1]

    def test_search_in_file_multiple_occurrences_same_line(self, tmp_path: Path):
        """
        Test that search_in_file returns the line number once even if the term appears multiple times on the same line.
        """
        file_content = "apple banana apple cherry"
        filepath = tmp_path / "search_multi_on_line.txt"
        filepath.write_text(file_content)

        result = search_in_file(str(filepath), "apple")
        assert result == [1]

    def test_search_in_file_file_not_found(self, tmp_path: Path):
        """
        Test that search_in_file raises FileNotFoundError for a non-existent file.
        """
        filepath = tmp_path / "non_existent_search.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            search_in_file(str(filepath), "term")
