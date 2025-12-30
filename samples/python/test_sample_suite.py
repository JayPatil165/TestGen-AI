"""
Sample Python Test Suite for TestGen AI.

Mix of passing, failing, and slow tests for testing the runner.
"""

import time
import pytest


def test_addition_pass():
    """Simple passing test."""
    assert 2 + 2 == 4


def test_subtraction_pass():
    """Another passing test."""
    assert 10 - 5 == 5


def test_multiplication_pass():
    """Passing multiplication test."""
    assert 3 * 4 == 12


def test_division_fail():
    """This test should fail."""
    assert 10 / 2 == 6  # Wrong! Should be 5


def test_assertion_fail():
    """This test fails with assertion error."""
    result = [1, 2, 3]
    assert len(result) == 5  # Wrong! Length is 3


def test_slow_operation():
    """Slow test (>1s) that should trigger warning."""
    time.sleep(1.5)
    assert True


def test_very_slow_operation():
    """Very slow test (>5s) that should trigger critical warning."""
    time.sleep(6.0)
    assert True


def test_exception_error():
    """Test that raises an exception."""
    raise ValueError("This is a test exception")


@pytest.mark.skip(reason="Demonstrating skipped test")
def test_skipped():
    """This test is skipped."""
    assert False


def test_list_operations():
    """Test list operations."""
    my_list = [1, 2, 3, 4, 5]
    assert len(my_list) == 5
    assert my_list[0] == 1
    assert my_list[-1] == 5


def test_string_operations():
    """Test string operations."""
    text = "Hello, World!"
    assert text.lower() == "hello, world!"
    assert text.upper() == "HELLO, WORLD!"
    assert "World" in text


def test_dictionary_operations():
    """Test dictionary operations."""
    data = {"name": "TestGen", "version": "1.0"}
    assert data["name"] == "TestGen"
    assert "version" in data
    assert len(data) == 2
