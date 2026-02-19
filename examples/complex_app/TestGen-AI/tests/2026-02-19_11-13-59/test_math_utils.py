import pytest
# Assuming the test file is located in 'D:\Programming\Projects\TestGen-AI\examples\complex_app\tests\'
# and the source file is in 'D:\Programming\Projects\TestGen-AI\examples\complex_app\utils\math_utils.py'
# This import path assumes 'complex_app' is a Python package.
from examples.complex_app.utils.math_utils import add, subtract, multiply, divide

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-2, -3, -5),
    (2, -3, -1),
    (-2, 3, 1),
    (0, 5, 5),
    (5, 0, 5),
    (0, 0, 0),
    (0.1, 0.2, 0.3),  # Floating point addition
    (10**9, 1, 10**9 + 1),  # Large numbers
    (-10**9, -1, -(10**9 + 1)), # Large negative numbers
    (1.23, 4.56, 5.79), # More float cases
])
def test_add_various_numbers(a, b, expected):
    """
    Test the add function with various combinations of positive, negative,
    zero, float, and large numbers to ensure correctness.
    """
    assert add(a, b) == pytest.approx(expected)

@pytest.mark.parametrize("a, b, expected", [
    (5, 2, 3),
    (-5, -2, -3),
    (5, -2, 7),
    (-5, 2, -7),
    (5, 0, 5),
    (0, 5, -5),
    (0, 0, 0),
    (0.3, 0.1, 0.2),  # Floating point subtraction
    (5, 5, 0),  # Result is zero
    (10**9, 1, 10**9 - 1),  # Large numbers
    (-10**9, -1, -(10**9 - 1)), # Large negative numbers
    (4.56, 1.23, 3.33), # More float cases
])
def test_subtract_various_numbers(a, b, expected):
    """
    Test the subtract function with various combinations of positive, negative,
    zero, float, and large numbers to ensure correctness.
    """
    assert subtract(a, b) == pytest.approx(expected)

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 6),
    (-2, -3, 6),
    (2, -3, -6),
    (-2, 3, -6),
    (0, 5, 0),
    (5, 0, 0),
    (0, 0, 0),
    (5, 1, 5),  # Multiply by one
    (1, 5, 5),  # Multiply by one
    (-5, 1, -5),  # Multiply by one with negative
    (0.5, 2, 1.0),  # Floating point multiplication
    (10**6, 10**3, 10**9),  # Large numbers
    (-10**6, 10**3, -10**9), # Large numbers with negative
    (1.5, 2.0, 3.0), # More float cases
])
def test_multiply_various_numbers(a, b, expected):
    """
    Test the multiply function with various combinations of positive, negative,
    zero, float, and large numbers, including multiplication by one.
    """
    assert multiply(a, b) == pytest.approx(expected)

@pytest.mark.parametrize("a, b, expected", [
    (6, 2, 3.0),
    (-6, -2, 3.0),
    (6, -2, -3.0),
    (-6, 2, -3.0),
    (5, 1, 5.0),  # Divide by one
    (0, 5, 0.0),  # Divide zero by non-zero
    (1.0, 2.0, 0.5),  # Floating point division
    (5, 2, 2.5),  # Non-integer result
    (10, 3, 10/3),  # Result with recurring decimal
    (-10, 3, -10/3), # Negative result with recurring decimal
    (10**9, 10**3, 10**6), # Large numbers
])
def test_divide_various_numbers(a, b, expected):
    """
    Test the divide function with various combinations of positive, negative,
    zero (as numerator), float, and non-integer results, ensuring floating point precision.
    """
    assert divide(a, b) == pytest.approx(expected)

def test_divide_by_zero_raises_value_error():
    """
    Test that the divide function correctly raises a ValueError when the divisor is zero.
    """
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

def test_divide_zero_by_zero_raises_value_error():
    """
    Test that dividing zero by zero also correctly raises a ValueError,
    as it's an undefined operation in this context.
    """
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(0, 0)

def test_divide_negative_by_zero_raises_value_error():
    """
    Test that dividing a negative number by zero also correctly raises a ValueError.
    """
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(-5, 0)
