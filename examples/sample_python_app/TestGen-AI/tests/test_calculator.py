import pytest
from calculator import add, subtract, multiply, divide, power

def test_add_positive_integers():
    """Test adding two positive integers."""
    assert add(2, 3) == 5

def test_add_negative_integers():
    """Test adding two negative integers."""
    assert add(-2, -3) == -5

def test_add_positive_and_negative_integers():
    """Test adding a positive and a negative integer."""
    assert add(5, -3) == 2
    assert add(-5, 3) == -2

def test_add_with_zero():
    """Test adding with zero."""
    assert add(0, 5) == 5
    assert add(5, 0) == 5
    assert add(0, 0) == 0

def test_add_float_numbers():
    """Test adding float numbers, using pytest.approx for precision."""
    assert add(2.5, 3.5) == 6.0
    assert add(0.1, 0.2) == pytest.approx(0.3)

def test_add_large_numbers():
    """Test adding large integer numbers."""
    assert add(10**9, 10**9) == 2 * (10**9)

def test_subtract_positive_integers():
    """Test subtracting two positive integers."""
    assert subtract(5, 3) == 2

def test_subtract_negative_integers():
    """Test subtracting two negative integers."""
    assert subtract(-5, -3) == -2

def test_subtract_positive_and_negative_integers():
    """Test subtracting a negative from a positive, and vice versa."""
    assert subtract(5, -3) == 8
    assert subtract(-5, 3) == -8

def test_subtract_with_zero():
    """Test subtracting with zero."""
    assert subtract(5, 0) == 5
    assert subtract(0, 5) == -5
    assert subtract(0, 0) == 0

def test_subtract_equal_numbers():
    """Test subtracting equal numbers resulting in zero."""
    assert subtract(7, 7) == 0

def test_subtract_float_numbers():
    """Test subtracting float numbers, using pytest.approx for precision."""
    assert subtract(5.5, 2.5) == 3.0
    assert subtract(0.3, 0.1) == pytest.approx(0.2)

def test_multiply_positive_integers():
    """Test multiplying two positive integers."""
    assert multiply(2, 3) == 6

def test_multiply_negative_integers():
    """Test multiplying two negative integers."""
    assert multiply(-2, -3) == 6

def test_multiply_positive_and_negative_integers():
    """Test multiplying a positive and a negative integer."""
    assert multiply(5, -3) == -15
    assert multiply(-5, 3) == -15

def test_multiply_by_zero():
    """Test multiplying by zero."""
    assert multiply(5, 0) == 0
    assert multiply(0, 5) == 0
    assert multiply(0, 0) == 0

def test_multiply_by_one():
    """Test multiplying by one."""
    assert multiply(5, 1) == 5
    assert multiply(1, 5) == 5
    assert multiply(-5, 1) == -5

def test_multiply_float_numbers():
    """Test multiplying float numbers, using pytest.approx for precision."""
    assert multiply(2.5, 2.0) == 5.0
    assert multiply(0.1, 0.2) == pytest.approx(0.02)

def test_multiply_large_numbers():
    """Test multiplying large integer numbers."""
    assert multiply(10**5, 10**5) == 10**10

def test_divide_positive_integers():
    """Test dividing two positive integers."""
    assert divide(6, 3) == 2.0

def test_divide_negative_integers():
    """Test dividing two negative integers."""
    assert divide(-6, -3) == 2.0

def test_divide_positive_by_negative():
    """Test dividing a positive by a negative integer."""
    assert divide(6, -3) == -2.0

def test_divide_negative_by_positive():
    """Test dividing a negative by a positive integer."""
    assert divide(-6, 3) == -2.0

def test_divide_by_one():
    """Test dividing by one."""
    assert divide(5, 1) == 5.0
    assert divide(-5, 1) == -5.0

def test_divide_zero_by_number():
    """Test dividing zero by a non-zero number."""
    assert divide(0, 5) == 0.0
    assert divide(0, -5) == 0.0

def test_divide_float_numbers():
    """Test dividing float numbers, using pytest.approx for precision."""
    assert divide(5.0, 2.0) == 2.5
    assert divide(1.0, 3.0) == pytest.approx(0.3333333333333333)

def test_divide_by_zero_raises_error():
    """Test that dividing by zero raises a ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(5, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(-5, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(0, 0)

def test_power_positive_integers():
    """Test power with positive integer base and exponent."""
    assert power(2, 3) == 8
    assert power(5, 2) == 25

def test_power_base_zero():
    """Test power with base zero and positive exponent."""
    assert power(0, 5) == 0
    assert power(0, 1) == 0

def test_power_zero_to_zero():
    """Test 0 raised to the power of 0, which is 1 in Python."""
    assert power(0, 0) == 1

def test_power_exponent_zero():
    """Test power with exponent zero for non-zero base."""
    assert power(5, 0) == 1
    assert power(-5, 0) == 1
    assert power(0.5, 0) == 1

def test_power_exponent_one():
    """Test power with exponent one."""
    assert power(5, 1) == 5
    assert power(-5, 1) == -5

def test_power_negative_base_even_exponent():
    """Test power with negative base and even exponent."""
    assert power(-2, 2) == 4
    assert power(-3, 4) == 81

def test_power_negative_base_odd_exponent():
    """Test power with negative base and odd exponent."""
    assert power(-2, 3) == -8
    assert power(-3, 1) == -3

def test_power_negative_exponent():
    """Test power with a negative integer exponent."""
    assert power(2, -1) == 0.5
    assert power(2, -2) == 0.25

def test_power_float_base_and_exponent():
    """Test power with float base and exponent, using pytest.approx."""
    assert power(2.5, 2) == 6.25
    assert power(4, 0.5) == 2.0 # Square root
    assert power(8, 1/3) == pytest.approx(2.0) # Cube root

def test_power_large_exponent():
    """Test power with a large exponent."""
    assert power(2, 10) == 1024
    assert power(10, 5) == 100000

def test_power_fractional_exponent():
    """Test power with fractional exponents, using pytest.approx."""
    assert power(9, 0.5) == 3.0
    assert power(27, 1/3) == pytest.approx(3.0)
    assert power(16, 0.25) == pytest.approx(2.0)

def test_power_negative_base_fractional_exponent_complex_result():
    """
    Test power with negative base and fractional exponent resulting in a complex number.
    Python's `**` operator handles this by returning a complex number.
    """
    result = power(-1, 0.5)
    assert isinstance(result, complex)
    assert result.real == pytest.approx(0.0)
    assert result.imag == pytest.approx(1.0)