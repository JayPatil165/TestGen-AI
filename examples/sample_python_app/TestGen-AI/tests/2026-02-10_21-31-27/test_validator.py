import pytest
import re
from typing import Any

# Assuming the code to be tested is in a file named 'validator.py'
# and we are importing it.
# For this example, we'll simulate the import by defining the functions directly
# or by assuming a module structure.
# Let's assume the functions are in a module named 'validator'.

# To make this runnable, we'll create a dummy validator.py or copy the functions.
# For the purpose of generating ONLY test code, I'll assume the functions
# are available via `import validator`.

# If running this directly, you might need to adjust the import path
# or copy the functions into this test file for simplicity.
# For a real project, the `validator.py` file would be in a discoverable path.

# --- Start of assumed validator.py content for local testing if needed ---
# (This part would normally be in validator.py, not in the test file)
# import re
# from typing import Any
#
# def validate_email(email: str) -> bool:
#     """Validate email address format."""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return bool(re.match(pattern, email))
#
# def validate_phone(phone: str) -> bool:
#     """Validate phone number (US format)."""
#     pattern = r'^\+?1?\d{10}$'
#     cleaned = re.sub(r'[^\d+]', '', phone)
#     return bool(re.match(pattern, cleaned))
#
# def validate_range(value: float, min_val: float, max_val: float) -> bool:
#     """Check if value is within range."""
#     return min_val <= value <= max_val
#
# def validate_not_empty(value: Any) -> bool:
#     """Check if value is not empty."""
#     if value is None:
#         return False
#     if isinstance(value, (str, list, dict)):
#         return len(value) > 0
#     return True
#
# def validate_password_strength(password: str) -> bool:
#     """Validate password strength (min 8 chars, 1 upper, 1 lower, 1 digit)."""
#     if len(password) < 8:
#         return False
#     has_upper = any(c.isupper() for c in password)
#     has_lower = any(c.islower() for c in password)
#     has_digit = any(c.isdigit() for c in password)
#     return has_upper and has_lower and has_digit
# --- End of assumed validator.py content ---


# Import the functions from the actual module
# If the file is D:\Programming\Projects\TestGen-AI\examples\sample_python_app\validator.py
# you might need to adjust your PYTHONPATH or import like this:
# import sys
# sys.path.append(r'D:\Programming\Projects\TestGen-AI\examples\sample_python_app')
import validator


class TestValidator:
    """
    Comprehensive test suite for the validator module.
    """

    @pytest.mark.parametrize("email", [
        "test@example.com",
        "john.doe123@sub.domain.co.uk",
        "user+tag@domain.net",
        "a@b.co",  # Minimum valid TLD length is 2
        "firstname.lastname@domain.com",
        "12345@domain.com",
        "test-email@domain-name.com",
        "test_email@domain.com",
        "test%email@domain.com",
    ])
    def test_validate_email_valid(self, email: str):
        """
        Test validate_email with various valid email addresses.
        """
        assert validator.validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "invalid-email",
        "missing@",
        "@missingdomain.com",
        "user@.com",
        "user@domain",
        "user@domain.",
        "user@domain.c",  # TLD too short
        "user@domain.toolongtld", # TLD too long (not strictly enforced by regex, but good to check)
        "user@domain..com",
        "user@domain_name.com",  # Underscore in domain not typically allowed
        " user@domain.com",  # Leading space
        "user@domain.com ",  # Trailing space
        "",  # Empty string
        "a@b.c", # TLD too short
        "test@example.c1", # TLD with digit
        "test@example.com-", # Trailing hyphen in domain
        "test@-example.com", # Leading hyphen in domain
    ])
    def test_validate_email_invalid(self, email: str):
        """
        Test validate_email with various invalid email addresses.
        """
        assert validator.validate_email(email) is False

    def test_validate_email_none_input(self):
        """
        Test validate_email with None input (should raise TypeError as per type hint).
        """
        with pytest.raises(TypeError):
            validator.validate_email(None) # type: ignore

    @pytest.mark.parametrize("phone", [
        "1234567890",
        "123-456-7890",
        "(123) 456-7890",
        "+1 123-456-7890",
        "1 123 456 7890",
        "+11234567890",
        "11234567890",
        "123.456.7890",
        "1234567890", # No prefix
    ])
    def test_validate_phone_valid(self, phone: str):
        """
        Test validate_phone with various valid US phone number formats.
        """
        assert validator.validate_phone(phone) is True

    @pytest.mark.parametrize("phone", [
        "123456789",  # Too short
        "12345678901",  # Too long (without +1 prefix)
        "+112345678901", # Too long (with +1 prefix)
        "abc-def-ghij",  # Non-numeric characters
        "12345",  # Very short
        "",  # Empty string
        "001234567890", # International prefix not matching +?1?
        "+441234567890", # UK number
        "123-456-7890x123", # Extension
        " 1234567890", # Leading space
        "1234567890 ", # Trailing space
    ])
    def test_validate_phone_invalid(self, phone: str):
        """
        Test validate_phone with various invalid phone number formats.
        """
        assert validator.validate_phone(phone) is False

    def test_validate_phone_none_input(self):
        """
        Test validate_phone with None input (should raise TypeError as per type hint).
        """
        with pytest.raises(TypeError):
            validator.validate_phone(None) # type: ignore

    @pytest.mark.parametrize("value, min_val, max_val, expected", [
        (5.0, 0.0, 10.0, True),   # Value within range
        (0.0, 0.0, 10.0, True),   # Value at min boundary
        (10.0, 0.0, 10.0, True),  # Value at max boundary
        (5, 0, 10, True),         # Integer values
        (-5.0, -10.0, 0.0, True), # Negative values
        (0.5, 0.1, 0.9, True),    # Floating point values
        (5.000000000000001, 5.0, 10.0, True), # Floating point precision (just above min)
        (9.999999999999999, 0.0, 10.0, True), # Floating point precision (just below max)
    ])
    def test_validate_range_valid(self, value: float, min_val: float, max_val: float, expected: bool):
        """
        Test validate_range with values that are within or at the boundaries of the range.
        """
        assert validator.validate_range(value, min_val, max_val) is expected

    @pytest.mark.parametrize("value, min_val, max_val, expected", [
        (-1.0, 0.0, 10.0, False),  # Value below min
        (11.0, 0.0, 10.0, False),  # Value above max
        (0.0, 1.0, 10.0, False),   # Value at min boundary but min_val is higher
        (10.0, 0.0, 9.0, False),   # Value at max boundary but max_val is lower
        (5.0, 10.0, 0.0, False),   # Inverted range (min > max), value is between them but outside "valid" range
        (15.0, 10.0, 0.0, False),  # Inverted range, value above min_val
        (-5.0, 10.0, 0.0, False),  # Inverted range, value below max_val
    ])
    def test_validate_range_invalid(self, value: float, min_val: float, max_val: float, expected: bool):
        """
        Test validate_range with values that are outside the specified range.
        Also tests inverted ranges where min_val > max_val.
        """
        assert validator.validate_range(value, min_val, max_val) is expected

    @pytest.mark.parametrize("value", [
        "hello",
        [1, 2, 3],
        {"a": 1},
        123,
        0.5,
        True,
        (1, 2),
        object(),
    ])
    def test_validate_not_empty_valid(self, value: Any):
        """
        Test validate_not_empty with various non-empty values.
        """
        assert validator.validate_not_empty(value) is True

    @pytest.mark.parametrize("value", [
        None,
        "",
        [],
        {},
        0,      # Integer zero
        0.0,    # Float zero
        False,  # Boolean False
        (),     # Empty tuple
    ])
    def test_validate_not_empty_invalid(self, value: Any):
        """
        Test validate_not_empty with various empty or "falsy" values.
        """
        assert validator.validate_not_empty(value) is False

    @pytest.mark.parametrize("password", [
        "Password123",
        "MyStrongP@ssw0rd",
        "aB12345678",
        "VERYlongPASSWORD123withmanycharacters",
        "P@ssw0rd!", # Special characters don't affect strength logic
    ])
    def test_validate_password_strength_valid(self, password: str):
        """
        Test validate_password_strength with passwords meeting all criteria.
        """
        assert validator.validate_password_strength(password) is True

    @pytest.mark.parametrize("password", [
        "short1A",  # Too short
        "password",  # No uppercase, no digit
        "PASSWORD123",  # No lowercase
        "passwordabc",  # No digit
        "Password",  # No digit
        "12345678",  # No upper, no lower
        "ABCDEFGH",  # No lower, no digit
        "abcdefgh",  # No upper, no digit
        "",  # Empty string
        "       ", # Spaces, too short
        "1234567890", # Only digits
        "abcdefghij", # Only lowercase
        "ABCDEFGHIJ", # Only uppercase
    ])
    def test_validate_password_strength_invalid(self, password: str):
        """
        Test validate_password_strength with passwords failing one or more criteria.
        """
        assert validator.validate_password_strength(password) is False

    def test_validate_password_strength_none_input(self):
        """
        Test validate_password_strength with None input (should raise TypeError as per type hint).
        """
        with pytest.raises(TypeError):
            validator.validate_password_strength(None) # type: ignore
