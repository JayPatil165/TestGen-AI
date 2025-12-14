"""
Auto-generated test file.

Tests for: src/calculator.py
Generated: 2025-12-14 11:32:36
Generator: TestGen AI

Feel free to modify these tests as needed.
"""

import pytest

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
