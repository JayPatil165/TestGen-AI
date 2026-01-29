import pytest
import re
from typing import Any

# Assuming the functions are in a file named 'validator.py'
# For testing purposes, we'll import them directly.
# In a real scenario, you might do:
# from your_app.validator import (
#     validate_email, validate_phone, validate_range,
#     validate_not_empty, validate_password_strength
# )

# For this example, we'll define them here or ensure they are accessible.
# Since the prompt provided the code, I'll assume it's available in the test context
# or that I should include a minimal setup to make it runnable.
# I will copy the functions here for self-contained test file,
# but in a real project, you'd import them.

"""
Validator module - Input validation functions.

Provides various validation utilities.
"""

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number (US format)."""
    pattern = r'^\+?1?\d{10}$'
    cleaned = re.sub(r'[^\d+]', '', phone)
    return bool(re.match(pattern, cleaned))

def validate_range(value: float, min_val: float, max_val: float) -> bool:
    """Check if value is within range."""
    return min_val <= value <= max_val

def validate_not_empty(value: Any) -> bool:
    """Check if value is not empty."""
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return len(value) > 0
    return True

def validate_password_strength(password: str) -> bool:
    """Validate password strength (min 8 chars, 1 upper, 1 lower, 1 digit)."""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


class TestValidatorFunctions:
    """Comprehensive test suite for validator functions."""

    @pytest.mark.parametrize("email, expected", [
        ("test@example.com", True),
        ("john.doe123@sub.domain.co.uk", True),
        ("user+tag@domain.net", True),
        ("a@b.co", True),  # Shortest valid
        ("firstname.lastname@domain-name.com", True),
        ("12345@domain.org", True),
        ("test@example.travel", True), # Longer TLD
        ("test@example.museum", True), # Longer TLD
        ("test@example.info", True), # Longer TLD
        ("test@example.name", True), # Longer TLD
        ("test@example.a", False), # TLD too short
        ("test@example.c", False), # TLD too short
        ("test@example.com.", False), # Trailing dot
        (".test@example.com", False), # Leading dot in username
        ("test@.example.com", False), # Leading dot in domain
        ("test@example..com", False), # Double dot in domain
        ("test@example", False), # Missing TLD
        ("testexample.com", False), # Missing @
        ("@example.com", False), # Missing username
        ("test@example_domain.com", False), # Underscore in domain (invalid)
        ("test@example-.com", False), # Hyphen at end of domain part
        ("test@-example.com", False), # Hyphen at start of domain part
        ("", False), # Empty string
        ("   test@example.com   ", False), # Leading/trailing spaces
        ("test@example.c1", False), # Digit in TLD
        ("test@example.c_o", False), # Underscore in TLD
    ])
    def test_validate_email(self, email: str, expected: bool):
        """
        Test validate_email with various valid and invalid email formats.
        Includes edge cases like short TLDs, special characters, and malformed structures.
        """
        assert validate_email(email) == expected

    @pytest.mark.parametrize("phone, expected", [
        ("1234567890", True),
        ("+11234567890", True),
        ("11234567890", True),
        ("(123) 456-7890", True), # Should clean to 1234567890
        ("123-456-7890", True), # Should clean to 1234567890
        ("+1 (123) 456-7890", True), # Should clean to +11234567890
        ("1 123 456 7890", True), # Should clean to 11234567890
        ("123.456.7890", True), # Should clean to 1234567890
        ("123456789", False), # Too short
        ("12345678901", False), # Too long (without +1 prefix)
        ("+112345678901", False), # Too long (with +1 prefix)
        ("abc1234567", False), # Contains letters
        ("", False), # Empty string
        ("   1234567890   ", True), # Leading/trailing spaces (should be cleaned)
        ("123-456-7890x123", False), # Extension not allowed
        ("0123456789", False), # Starts with 0 (US numbers typically don't) - current regex allows this
        ("+1-123-456-7890", True), # With hyphens and +1
        ("1-123-456-7890", True), # With hyphens and 1
        ("1234567890", True), # Exactly 10 digits
        ("+11234567890", True), # Exactly +1 and 10 digits
        ("11234567890", True), # Exactly 1 and 10 digits
    ])
    def test_validate_phone(self, phone: str, expected: bool):
        """
        Test validate_phone with various valid and invalid US phone number formats.
        Includes cleaning of non-digit characters and checks for length and prefixes.
        """
        assert validate_phone(phone) == expected

    @pytest.mark.parametrize("value, min_val, max_val, expected", [
        (5.0, 0.0, 10.0, True), # Within range
        (0.0, 0.0, 10.0, True), # At min_val
        (10.0, 0.0, 10.0, True), # At max_val
        (-5.0, -10.0, 0.0, True), # Negative range, within
        (-10.0, -10.0, 0.0, True), # Negative range, at min_val
        (0.0, -10.0, 0.0, True), # Negative range, at max_val
        (15.0, 0.0, 10.0, False), # Above max_val
        (-15.0, 0.0, 10.0, False), # Below min_val
        (5.0, 5.0, 5.0, True), # Min equals max, value equals
        (4.9, 5.0, 5.0, False), # Min equals max, value less
        (5.1, 5.0, 5.0, False), # Min equals max, value greater
        (0.0, 0.0, 0.0, True), # Zero range
        (0.1, 0.0, 0.2, True), # Floating point within
        (0.0, 0.0, 0.2, True), # Floating point at min
        (0.2, 0.0, 0.2, True), # Floating point at max
        (0.20000000000000001, 0.0, 0.2, False), # Floating point just above max
        (float('inf'), 0.0, float('inf'), True), # Value is infinity, max is infinity
        (float('-inf'), float('-inf'), 0.0, True), # Value is neg infinity, min is neg infinity
        (float('nan'), 0.0, 10.0, False), # NaN should always fail range checks
    ])
    def test_validate_range(self, value: float, min_val: float, max_val: float, expected: bool):
        """
        Test validate_range with various numeric values, including boundaries,
        negative numbers, zero, floating points, and special float values like NaN and infinity.
        """
        assert validate_range(value, min_val, max_val) == expected

    @pytest.mark.parametrize("value, expected", [
        ("hello", True), # Non-empty string
        ([1, 2, 3], True), # Non-empty list
        ({"a": 1}, True), # Non-empty dictionary
        (123, True), # Integer
        (0, True), # Zero integer (considered not empty)
        (3.14, True), # Float
        (True, True), # Boolean True
        (False, True), # Boolean False (considered not empty)
        (object(), True), # Any object
        ("", False), # Empty string
        ([], False), # Empty list
        ({}, False), # Empty dictionary
        (None, False), # None
    ])
    def test_validate_not_empty(self, value: Any, expected: bool):
        """
        Test validate_not_empty with various data types, including empty/non-empty
        strings, lists, dictionaries, numbers, booleans, and None.
        """
        assert validate_not_empty(value) == expected

    @pytest.mark.parametrize("password, expected", [
        ("Password123", True), # Valid: upper, lower, digit, >= 8 chars
        ("P@ssw0rd!", True), # Valid: with special chars
        ("aB123456", True), # Valid: exactly 8 chars
        ("MyStrongPassword1", True), # Valid: longer
        ("password123", False), # Missing uppercase
        ("PASSWORD123", False), # Missing lowercase
        ("PasswordABC", False), # Missing digit
        ("pass123", False), # Too short (< 8 chars), missing upper
        ("Pass", False), # Too short
        ("12345678", False), # Too short, missing upper/lower
        ("ABCDEFGH", False), # Missing lower/digit
        ("abcdefgh", False), # Missing upper/digit
        ("", False), # Empty string
        ("       ", False), # Spaces, too short
        ("P1a2s3s4", True), # Exactly 8 chars, all criteria met
        ("P1a2s3s4!", True), # With special char
    ])
    def test_validate_password_strength(self, password: str, expected: bool):
        """
        Test validate_password_strength with various passwords, checking for
        length, presence of uppercase, lowercase, and digits.
        """
        assert validate_password_strength(password) == expected
