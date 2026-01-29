"""
Validator module - Input validation functions.

Provides various validation utilities.
"""

import re
from typing import Any

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
