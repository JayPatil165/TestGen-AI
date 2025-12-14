#!/usr/bin/env python
"""
Demo: Test File Writer - Creates actual test files you can inspect!

Run this to see the file writer in action!
Files will be saved to: demo_output/tests/
"""

from testgen.core.file_writer import TestFileWriter
from pathlib import Path

print("=" * 70)
print("FILE WRITER DEMO")
print("=" * 70)
print()

# Create writer - files will go to demo_output/tests/
writer = TestFileWriter(output_dir="demo_output/tests")

print("Creating test files...")
print()

# Example 1: Create test for a calculator module
calculator_tests = '''import pytest

def test_add():
    """Test addition."""
    from calculator import add
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    """Test subtraction."""
    from calculator import subtract
    assert subtract(5, 3) == 2
    assert subtract(10, 5) == 5

def test_multiply():
    """Test multiplication."""
    from calculator import multiply
    assert multiply(4, 5) == 20
    assert multiply(0, 100) == 0
'''

result1 = writer.save_test_file(
    code=calculator_tests,
    source_file="src/calculator.py"
)

print(f"1. Created: {result1.file_path}")
print(f"   Status: {result1.success}")
print(f"   Lines: {result1.lines_written}")
print()

# Example 2: Create test for a utils module
utils_tests = '''import pytest

def test_format_name():
    """Test name formatting."""
    from utils import format_name
    assert format_name("john", "doe") == "John Doe"
    assert format_name("ALICE", "SMITH") == "Alice Smith"

def test_validate_email():
    """Test email validation."""
    from utils import validate_email
    assert validate_email("test@example.com") == True
    assert validate_email("invalid") == False
'''

result2 = writer.save_test_file(
    code=utils_tests,
    source_file="src/utils.py"
)

print(f"2. Created: {result2.file_path}")
print(f"   Status: {result2.success}")
print(f"   Lines: {result2.lines_written}")
print()

# Example 3: Create test in subdirectory
api_tests = '''import pytest
from unittest.mock import Mock

def test_fetch_data():
    """Test API data fetching."""
    from core.api import fetch_data
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    # Test logic here
    assert True
'''

result3 = writer.save_test_file(
    code=api_tests,
    source_file="src/core/api.py"
)

print(f"3. Created: {result3.file_path}")
print(f"   Status: {result3.success}")
print(f"   Lines: {result3.lines_written}")
print()

print("=" * 70)
print("FILES CREATED SUCCESSFULLY!")
print("=" * 70)
print()
print("Location: demo_output/tests/")
print()
print("Generated files:")
print(f"  1. {result1.file_path}")
print(f"  2. {result2.file_path}")
print(f"  3. {result3.file_path}")
print()
print("You can now open these files to see the generated tests!")
print()

# Show the directory structure
print("Directory structure:")
demo_path = Path("demo_output")
if demo_path.exists():
    for item in sorted(demo_path.rglob("*")):
        if item.is_file():
            indent = "  " * (len(item.relative_to(demo_path).parts) - 1)
            print(f"  {indent}📄 {item.relative_to(demo_path)}")
        elif item.is_dir() and item != demo_path:
            indent = "  " * (len(item.relative_to(demo_path).parts) - 1)
            print(f"  {indent}📁 {item.name}/")

print()
print("=" * 70)
print("To view a file, use:")
print("  type demo_output\\tests\\test_calculator.py")
print("=" * 70)
