"""
Auto-generated test file.

Tests for: src/utils.py
Generated: 2025-12-14 11:32:36
Generator: TestGen AI

Feel free to modify these tests as needed.
"""

import pytest

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
