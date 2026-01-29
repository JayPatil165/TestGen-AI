import pytest
import calculator

def test_add_positive_integers():
    """Test adding two positive integers."""
    assert calculator.add(2, 3) == 5

def test_add_negative_integers():
    """Test adding two negative integers."""
    assert calculator.add(-2, -3) == -5

def test_add_mixed_integers():
    """Test adding a positive and a negative integer."""
    assert calculator.add(5, -3) == 2
    assert calculator.add(-5, 3) == -2

def test_add_zero():
    """Test adding with zero."""
    assert calculator.add(5, 0) == 5
    assert calculator.add(0, -3) == -3
    assert calculator.add(0, 0) == 0

def test_add_floats():
    """Test adding two floating-point numbers."""
    assert calculator.add(2.5, 3.5) == pytest.approx(6.0)
    assert calculator.add(-1.5, 2.0) == pytest.approx(0.5)

def test_add_large_numbers():
    """Test adding large numbers."""
    assert calculator.add(10**9, 10**9) == 2 * (10**9)
    assert calculator.add(10**18, -10**18) == 0

def test_subtract_positive_integers():
    """Test subtracting two positive integers."""
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(3, 5) == -2

def test_subtract_negative_integers():
    """Test subtracting two negative integers."""
    assert calculator.subtract(-5, -3) == -2
    assert calculator.subtract(-3, -5) == 2

def test_subtract_mixed_integers():
    """Test subtracting mixed positive and negative integers."""
    assert calculator.subtract(5, -3) == 8
    assert calculator.subtract(-5, 3) == -8

def test_subtract_zero():
    """Test subtracting with zero."""
    assert calculator.subtract(5, 0) == 5
    assert calculator.subtract(0, 5) == -5
    assert calculator.subtract(0, 0) == 0

def test_subtract_floats():
    """Test subtracting floating-point numbers."""
    assert calculator.subtract(5.5, 2.5) == pytest.approx(3.0)
    assert calculator.subtract(2.0, 3.5) == pytest.approx(-1.5)

def test_subtract_from_self():
    """Test subtracting a number from itself."""
    assert calculator.subtract(7, 7) == 0
    assert calculator.subtract(-7, -7) == 0
    assert calculator.subtract(7.7, 7.7) == pytest.approx(0.0)

def test_multiply_positive_integers():
    """Test multiplying two positive integers."""
    assert calculator.multiply(2, 3) == 6

def test_multiply_negative_integers():
    """Test multiplying two negative integers."""
    assert calculator.multiply(-2, -3) == 6

def test_multiply_mixed_integers():
    """Test multiplying a positive and a negative integer."""
    assert calculator.multiply(5, -3) == -15
    assert calculator.multiply(-5, 3) == -15

def test_multiply_by_zero():
    """Test multiplying by zero."""
    assert calculator.multiply(5, 0) == 0
    assert calculator.multiply(0, -3) == 0
    assert calculator.multiply(0, 0) == 0

def test_multiply_by_one():
    """Test multiplying by one."""
    assert calculator.multiply(5, 1) == 5
    assert calculator.multiply(-3, 1) == -3
    assert calculator.multiply(1, 7) == 7

def test_multiply_floats():
    """Test multiplying floating-point numbers."""
    assert calculator.multiply(2.5, 2.0) == pytest.approx(5.0)
    assert calculator.multiply(-1.5, 3.0) == pytest.approx(-4.5)

def test_multiply_large_numbers():
    """Test multiplying large numbers."""
    assert calculator.multiply(10**6, 10**6) == 10**12
    assert calculator.multiply(10**9, -2) == -2 * (10**9)

def test_divide_positive_integers():
    """Test dividing two positive integers."""
    assert calculator.divide(6, 3) == pytest.approx(2.0)
    assert calculator.divide(7, 2) == pytest.approx(3.5)

def test_divide_negative_integers():
    """Test dividing two negative integers."""
    assert calculator.divide(-6, -3) == pytest.approx(2.0)
    assert calculator.divide(-7, -2) == pytest.approx(3.5)

def test_divide_mixed_integers():
    """Test dividing mixed positive and negative integers."""
    assert calculator.divide(6, -3) == pytest.approx(-2.0)
    assert calculator.divide(-6, 3) == pytest.approx(-2.0)

def test_divide_by_one():
    """Test dividing by one."""
    assert calculator.divide(5, 1) == pytest.approx(5.0)
    assert calculator.divide(-3, 1) == pytest.approx(-3.0)

def test_divide_zero_by_non_zero():
    """Test dividing zero by a non-zero number."""
    assert calculator.divide(0, 5) == pytest.approx(0.0)
    assert calculator.divide(0, -5) == pytest.approx(0.0)

def test_divide_floats():
    """Test dividing floating-point numbers."""
    assert calculator.divide(7.5, 2.5) == pytest.approx(3.0)
    assert calculator.divide(10.0, 3.0) == pytest.approx(3.3333333333333335)

def test_divide_by_self():
    """Test dividing a number by itself."""
    assert calculator.divide(7, 7) == pytest.approx(1.0)
    assert calculator.divide(-7, -7) == pytest.approx(1.0)
    assert calculator.divide(7.7, 7.7) == pytest.approx(1.0)

def test_divide_by_zero_error():
    """Test that dividing by zero raises a ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(5, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(-5, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(0, 0)

def test_power_positive_integers():
    """Test raising a positive base to a positive integer exponent."""
    assert calculator.power(2, 3) == 8
    assert calculator.power(5, 2) == 25

def test_power_negative_base_even_exponent():
    """Test raising a negative base to an even exponent."""
    assert calculator.power(-2, 2) == 4
    assert calculator.power(-3, 4) == 81

def test_power_negative_base_odd_exponent():
    """Test raising a negative base to an odd exponent."""
    assert calculator.power(-2, 3) == -8
    assert calculator.power(-3, 1) == -3

def test_power_zero_exponent():
    """Test raising any number to the power of zero."""
    assert calculator.power(5, 0) == 1
    assert calculator.power(-5, 0) == 1
    assert calculator.power(0, 0) == 1 # Python's 0**0 is 1
    assert calculator.power(2.5, 0) == 1

def test_power_one_exponent():
    """Test raising any number to the power of one."""
    assert calculator.power(5, 1) == 5
    assert calculator.power(-5, 1) == -5
    assert calculator.power(0, 1) == 0

def test_power_base_is_zero():
    """Test raising zero to a positive exponent."""
    assert calculator.power(0, 5) == 0
    assert calculator.power(0, 100) == 0

def test_power_base_is_one():
    """Test raising one to any exponent."""
    assert calculator.power(1, 5) == 1
    assert calculator.power(1, -5) == 1
    assert calculator.power(1, 0.5) == 1

def test_power_negative_exponent():
    """Test raising a base to a negative exponent."""
    assert calculator.power(2, -2) == pytest.approx(0.25)
    assert calculator.power(4, -0.5) == pytest.approx(0.5)
    assert calculator.power(10, -1) == pytest.approx(0.1)

def test_power_fractional_exponent():
    """Test raising a base to a fractional exponent (roots)."""
    assert calculator.power(9, 0.5) == pytest.approx(3.0) # Square root
    assert calculator.power(8, 1/3) == pytest.approx(2.0) # Cube root
    assert calculator.power(16, 0.25) == pytest.approx(2.0) # Fourth root

def test_power_floats():
    """Test raising a float base to a float exponent."""
    assert calculator.power(2.5, 2) == pytest.approx(6.25)
    assert calculator.power(1.5, 1.5) == pytest.approx(1.8371173070873836)

def test_power_large_exponent():
    """Test raising a base to a large exponent."""
    assert calculator.power(2, 10) == 1024
    assert calculator.power(10, 5) == 100000