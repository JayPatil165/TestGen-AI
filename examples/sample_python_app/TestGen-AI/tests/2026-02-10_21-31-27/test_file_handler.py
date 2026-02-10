import pytest
import json
from pathlib import Path
from typing import Any, Dict, List

# Assuming the file_handler.py is in the same directory or accessible via PYTHONPATH
from file_handler import (
    read_json_file,
    write_json_file,
    read_lines,
    count_lines,
    search_in_file,
)


@pytest.fixture
def sample_json_data() -> Dict[str, Any]:
    """Fixture for sample JSON data."""
    return {"name": "Test User", "age": 30, "is_active": True, "items": [1, 2, 3]}


@pytest.fixture
def empty_json_data() -> Dict[str, Any]:
    """Fixture for empty JSON data."""
    return {}


@pytest.fixture
def sample_text_content() -> str:
    """Fixture for sample multiline text content."""
    return "Line 1: Hello World\nLine 2: Python is great\nLine 3: Hello again\nLine 4: End of file"


@pytest.fixture
def single_line_content() -> str:
    """Fixture for single line text content."""
    return "This is a single line."


@pytest.fixture
def empty_file_content() -> str:
    """Fixture for empty file content."""
    return ""


class TestReadJsonFile:
    """Tests for the read_json_file function."""

    def test_read_valid_json_file(self, tmp_path: Path, sample_json_data: Dict[str, Any]):
        """
        Test that read_json_file correctly reads and parses a valid JSON file.
        """
        filepath = tmp_path / "test.json"
        with filepath.open("w") as f:
            json.dump(sample_json_data, f)

        result = read_json_file(str(filepath))
        assert result == sample_json_data

    def test_read_empty_json_object_file(self, tmp_path: Path, empty_json_data: Dict[str, Any]):
        """
        Test that read_json_file correctly reads an empty JSON object file.
        """
        filepath = tmp_path / "empty.json"
        with filepath.open("w") as f:
            json.dump(empty_json_data, f)

        result = read_json_file(str(filepath))
        assert result == empty_json_data

    def test_read_json_file_not_found(self, tmp_path: Path):
        """
        Test that read_json_file raises FileNotFoundError if the file does not exist.
        """
        filepath = tmp_path / "non_existent.json"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            read_json_file(str(filepath))

    def test_read_invalid_json_file(self, tmp_path: Path):
        """
        Test that read_json_file raises json.JSONDecodeError for malformed JSON content.
        """
        filepath = tmp_path / "invalid.json"
        filepath.write_text("{'key': 'value'")  # Malformed JSON

        with pytest.raises(json.JSONDecodeError):
            read_json_file(str(filepath))

    def test_read_empty_file_as_json(self, tmp_path: Path):
        """
        Test that read_json_file raises json.JSONDecodeError for an empty file.
        """
        filepath = tmp_path / "empty_file.json"
        filepath.write_text("")

        with pytest.raises(json.JSONDecodeError):
            read_json_file(str(filepath))


class TestWriteJsonFile:
    """Tests for the write_json_file function."""

    def test_write_new_json_file(self, tmp_path: Path, sample_json_data: Dict[str, Any]):
        """
        Test that write_json_file correctly writes data to a new JSON file.
        """
        filepath = tmp_path / "output.json"
        write_json_file(str(filepath), sample_json_data)

        assert filepath.exists()
        with filepath.open("r") as f:
            content = json.load(f)
        assert content == sample_json_data

    def test_write_empty_json_data(self, tmp_path: Path, empty_json_data: Dict[str, Any]):
        """
        Test that write_json_file correctly writes an empty dictionary to a file.
        """
        filepath = tmp_path / "empty_output.json"
        write_json_file(str(filepath), empty_json_data)

        assert filepath.exists()
        with filepath.open("r") as f:
            content = json.load(f)
        assert content == empty_json_data

    def test_write_json_file_in_non_existent_directory(self, tmp_path: Path, sample_json_data: Dict[str, Any]):
        """
        Test that write_json_file creates parent directories if they don't exist.
        """
        nested_dir = tmp_path / "subdir" / "nested"
        filepath = nested_dir / "output.json"
        write_json_file(str(filepath), sample_json_data)

        assert filepath.exists()
        assert nested_dir.is_dir()
        with filepath.open("r") as f:
            content = json.load(f)
        assert content == sample_json_data

    def test_write_json_file_overwrites_existing_file(self, tmp_path: Path, sample_json_data: Dict[str, Any]):
        """
        Test that write_json_file overwrites an existing file with new content.
        """
        filepath = tmp_path / "overwrite.json"
        filepath.write_text('{"old_key": "old_value"}')

        new_data = {"new_key": "new_value"}
        write_json_file(str(filepath), new_data)

        assert filepath.exists()
        with filepath.open("r") as f:
            content = json.load(f)
        assert content == new_data


class TestReadLines:
    """Tests for the read_lines function."""

    def test_read_multiple_lines_file(self, tmp_path: Path, sample_text_content: str):
        """
        Test that read_lines correctly reads all lines from a file.
        """
        filepath = tmp_path / "multiline.txt"
        filepath.write_text(sample_text_content)

        expected_lines = sample_text_content.splitlines()
        result = read_lines(str(filepath))
        assert result == expected_lines

    def test_read_single_line_file(self, tmp_path: Path, single_line_content: str):
        """
        Test that read_lines correctly reads a file with a single line.
        """
        filepath = tmp_path / "singleline.txt"
        filepath.write_text(single_line_content)

        result = read_lines(str(filepath))
        assert result == [single_line_content]

    def test_read_empty_file(self, tmp_path: Path, empty_file_content: str):
        """
        Test that read_lines returns an empty list for an empty file.
        """
        filepath = tmp_path / "empty.txt"
        filepath.write_text(empty_file_content)

        result = read_lines(str(filepath))
        assert result == []

    def test_read_lines_file_not_found(self, tmp_path: Path):
        """
        Test that read_lines raises FileNotFoundError if the file does not exist.
        """
        filepath = tmp_path / "non_existent.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            read_lines(str(filepath))


class TestCountLines:
    """Tests for the count_lines function."""

    def test_count_multiple_lines(self, tmp_path: Path, sample_text_content: str):
        """
        Test that count_lines correctly counts lines in a multiline file.
        """
        filepath = tmp_path / "multiline_count.txt"
        filepath.write_text(sample_text_content)

        expected_count = len(sample_text_content.splitlines())
        result = count_lines(str(filepath))
        assert result == expected_count

    def test_count_single_line(self, tmp_path: Path, single_line_content: str):
        """
        Test that count_lines correctly counts lines in a single-line file.
        """
        filepath = tmp_path / "singleline_count.txt"
        filepath.write_text(single_line_content)

        result = count_lines(str(filepath))
        assert result == 1

    def test_count_empty_file(self, tmp_path: Path, empty_file_content: str):
        """
        Test that count_lines returns 0 for an empty file.
        """
        filepath = tmp_path / "empty_count.txt"
        filepath.write_text(empty_file_content)

        result = count_lines(str(filepath))
        assert result == 0

    def test_count_lines_file_not_found(self, tmp_path: Path):
        """
        Test that count_lines raises FileNotFoundError if the file does not exist.
        """
        filepath = tmp_path / "non_existent_count.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            count_lines(str(filepath))


class TestSearchInFile:
    """Tests for the search_in_file function."""

    def test_search_for_existing_term_multiple_matches(self, tmp_path: Path, sample_text_content: str):
        """
        Test that search_in_file finds a term appearing on multiple lines and returns correct line numbers.
        """
        filepath = tmp_path / "search_multi.txt"
        filepath.write_text(sample_text_content)

        result = search_in_file(str(filepath), "Hello")
        assert result == [1, 3]

    def test_search_for_existing_term_single_match(self, tmp_path: Path, sample_text_content: str):
        """
        Test that search_in_file finds a term appearing on a single line.
        """
        filepath = tmp_path / "search_single.txt"
        filepath.write_text(sample_text_content)

        result = search_in_file(str(filepath), "Python")
        assert result == [2]

    def test_search_for_non_existent_term(self, tmp_path: Path, sample_text_content: str):
        """
        Test that search_in_file returns an empty list if the term is not found.
        """
        filepath = tmp_path / "search_none.txt"
        filepath.write_text(sample_text_content)

        result = search_in_file(str(filepath), "NonExistent")
        assert result == []

    def test_search_in_empty_file(self, tmp_path: Path, empty_file_content: str):
        """
        Test that search_in_file returns an empty list when searching in an empty file.
        """
        filepath = tmp_path / "search_empty.txt"
        filepath.write_text(empty_file_content)

        result = search_in_file(str(filepath), "any_term")
        assert result == []

    def test_search_for_empty_string(self, tmp_path: Path, sample_text_content: str):
        """
        Test that searching for an empty string matches all lines.
        """
        filepath = tmp_path / "search_empty_string.txt"
        filepath.write_text(sample_text_content)

        result = search_in_file(str(filepath), "")
        expected_lines = [1, 2, 3, 4]
        assert result == expected_lines

    def test_search_case_sensitivity(self, tmp_path: Path):
        """
        Test that search_in_file is case-sensitive.
        """
        filepath = tmp_path / "search_case.txt"
        filepath.write_text("hello world\nHello World")

        result = search_in_file(str(filepath), "hello")
        assert result == [1]

        result_case_sensitive = search_in_file(str(filepath), "Hello")
        assert result_case_sensitive == [2]

    def test_search_in_file_not_found(self, tmp_path: Path):
        """
        Test that search_in_file raises FileNotFoundError if the file does not exist.
        """
        filepath = tmp_path / "non_existent_search.txt"
        with pytest.raises(FileNotFoundError, match=f"File not found: {filepath}"):
            search_in_file(str(filepath), "term")
