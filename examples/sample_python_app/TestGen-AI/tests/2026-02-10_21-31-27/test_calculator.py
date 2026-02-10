import pytest
from calculator import add, subtract, multiply, divide, power

class TestCalculator:
    """
    Comprehensive test suite for the calculator module.
    """

    # --- Tests for add function ---
    def test_add_positive_numbers(self):
        """
        Test adding two positive integers.
        """
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        """
        Test adding two negative integers.
        """
        assert add(-2, -3) == -5

    def test_add_positive_and_negative(self):
        """
        Test adding a positive and a negative integer.
        """
        assert add(5, -3) == 2

    def test_add_zero(self):
        """
        Test adding zero to a number.
        """
        assert add(0, 7) == 7
        assert add(7, 0) == 7
        assert add(0, 0) == 0

    def test_add_floats(self):
        """
        Test adding two floating-point numbers.
        """
        assert add(2.5, 3.5) == pytest.approx(6.0)
        assert add(-1.5, 0.5) == pytest.approx(-1.0)

    def test_add_large_numbers(self):
        """
        Test adding large integers.
        """
        assert add(1_000_000, 2_000_000) == 3_000_000

    # --- Tests for subtract function ---
    def test_subtract_positive_numbers(self):
        """
        Test subtracting two positive integers.
        """
        assert subtract(5, 3) == 2

    def test_subtract_negative_numbers(self):
        """
        Test subtracting a negative number from another negative number.
        """
        assert subtract(-5, -3) == -2

    def test_subtract_positive_from_negative(self):
        """
        Test subtracting a positive number from a negative number.
        """
        assert subtract(-5, 3) == -8

    def test_subtract_zero(self):
        """
        Test subtracting zero from a number and a number from zero.
        """
        assert subtract(7, 0) == 7
        assert subtract(0, 7) == -7
        assert subtract(0, 0) == 0

    def test_subtract_floats(self):
        """
        Test subtracting floating-point numbers.
        """
        assert subtract(5.5, 2.5) == pytest.approx(3.0)
        assert subtract(1.0, 0.1) == pytest.approx(0.9)

    def test_subtract_same_numbers(self):
        """
        Test subtracting a number from itself, resulting in zero.
        """
        assert subtract(5, 5) == 0
        assert subtract(-10, -10) == 0

    def test_subtract_large_numbers(self):
        """
        Test subtracting large integers.
        """
        assert subtract(2_000_000, 1_000_000) == 1_000_000

    # --- Tests for multiply function ---
    def test_multiply_positive_numbers(self):
        """
        Test multiplying two positive integers.
        """
        assert multiply(2, 3) == 6

    def test_multiply_negative_numbers(self):
        """
        Test multiplying two negative integers.
        """
        assert multiply(-2, -3) == 6

    def test_multiply_positive_and_negative(self):
        """
        Test multiplying a positive and a negative integer.
        """
        assert multiply(2, -3) == -6

    def test_multiply_by_zero(self):
        """
        Test multiplying any number by zero.
        """
        assert multiply(5, 0) == 0
        assert multiply(0, 5) == 0
        assert multiply(-10, 0) == 0

    def test_multiply_by_one(self):
        """
        Test multiplying any number by one.
        """
        assert multiply(5, 1) == 5
        assert multiply(1, -10) == -10

    def test_multiply_floats(self):
        """
        Test multiplying floating-point numbers.
        """
        assert multiply(2.5, 2.0) == pytest.approx(5.0)
        assert multiply(-1.5, 3.0) == pytest.approx(-4.5)

    def test_multiply_large_numbers(self):
        """
        Test multiplying large integers.
        """
        assert multiply(1_000, 1_000) == 1_000_000

    # --- Tests for divide function ---
    def test_divide_positive_numbers(self):
        """
        Test dividing two positive integers, resulting in a float.
        """
        assert divide(6, 3) == pytest.approx(2.0)

    def test_divide_negative_numbers(self):
        """
        Test dividing two negative integers.
        """
        assert divide(-6, -3) == pytest.approx(2.0)

    def test_divide_positive_by_negative(self):
        """
        Test dividing a positive by a negative integer.
        """
        assert divide(6, -3) == pytest.approx(-2.0)

    def test_divide_by_one(self):
        """
        Test dividing a number by one.
        """
        assert divide(5, 1) == pytest.approx(5.0)
        assert divide(-10, 1) == pytest.approx(-10.0)

    def test_divide_zero_by_number(self):
        """
        Test dividing zero by a non-zero number.
        """
        assert divide(0, 5) == pytest.approx(0.0)
        assert divide(0, -5) == pytest.approx(0.0)

    def test_divide_floats(self):
        """
        Test dividing floating-point numbers.
        """
        assert divide(7.5, 2.5) == pytest.approx(3.0)
        assert divide(10.0, 3.0) == pytest.approx(3.3333333333333335)

    def test_divide_large_numbers(self):
        """
        Test dividing large integers.
        """
        assert divide(1_000_000, 1_000) == pytest.approx(1000.0)

    def test_divide_by_zero_raises_error(self):
        """
        Test that dividing by zero raises a ValueError.
        """
        with pytest.raises(ValueError):
            divide(5, 0)

    def test_divide_by_zero_error_message(self):
        """
        Test that dividing by zero raises a ValueError with the correct message.
        """
        with pytest.raises(ValueError) as excinfo:
            divide(10, 0)
        assert "Cannot divide by zero" in str(excinfo.value)

    # --- Tests for power function ---
    def test_power_positive_integers(self):
        """
        Test raising a positive base to a positive integer exponent.
        """
        assert power(2, 3) == 8
        assert power(5, 2) == 25

    def test_power_zero_exponent(self):
        """
        Test raising any non-zero base to the power of zero.
        """
        assert power(5, 0) == 1
        assert power(-10, 0) == 1
        assert power(0.5, 0) == 1

    def test_power_one_exponent(self):
        """
        Test raising any base to the power of one.
        """
        assert power(5, 1) == 5
        assert power(-10, 1) == -10
        assert power(0.5, 1) == 0.5

    def test_power_negative_exponent(self):
        """
        Test raising a positive base to a negative integer exponent.
        """
        assert power(2, -2) == pytest.approx(0.25)  # 1 / (2^2) = 1/4
        assert power(10, -1) == pytest.approx(0.1)

    def test_power_zero_base_positive_exponent(self):
        """
        Test raising zero to a positive integer exponent.
        """
        assert power(0, 5) == 0

    def test_power_zero_base_zero_exponent(self):
        """
        Test raising zero to the power of zero (mathematically 1 in Python).
        """
        assert power(0, 0) == 1

    def test_power_one_base(self):
        """
        Test raising one to any exponent.
        """
        assert power(1, 100) == 1
        assert power(1, -5) == 1
        assert power(1, 0.5) == 1

    def test_power_negative_base_even_exponent(self):
        """
        Test raising a negative base to an even integer exponent.
        """
        assert power(-2, 2) == 4
        assert power(-3, 4) == 81

    def test_power_negative_base_odd_exponent(self):
        """
        Test raising a negative base to an odd integer exponent.
        """
        assert power(-2, 3) == -8
        assert power(-3, 1) == -3

    def test_power_float_exponent(self):
        """
        Test raising a base to a fractional (float) exponent (e.g., square root).
        """
        assert power(9, 0.5) == pytest.approx(3.0)
        assert power(8, 1/3) == pytest.approx(2.0)

    def test_power_float_base(self):
        """
        Test raising a float base to an integer exponent.
        """
        assert power(2.5, 2) == pytest.approx(6.25)
        assert power(0.5, 3) == pytest.approx(0.125)

    def test_power_large_exponent(self):
        """
        Test raising a base to a moderately large exponent.
        """
        assert power(2, 10) == 1024
        assert power(3, 5) == 243

    def test_power_negative_base_float_exponent_complex_result(self):
        """
        Test raising a negative base to a float exponent that would result in a complex number.
        Python's `**` operator handles this by returning a complex number.
        """
        # (-4)**0.5 is 2j
        assert power(-4, 0.5) == pytest.approx(2j)
        # (-8)**(1/3) is 1 + 1.73205081j (complex cube root)
        # Python's ** operator for negative base and fractional exponent
        # returns the principal value, which can be complex.
        # For real-valued results, typically base >= 0 is expected for non-integer exponents.
        # This test confirms Python's behavior.
        assert power(-8, 1/3) == pytest.approx(complex(1, 1.73205081))
