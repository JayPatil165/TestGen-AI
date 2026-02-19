import pytest
from examples.complex_app.api.endpoints import get_user, create_user

def test_get_user_alice_id_1():
    """
    Test that get_user returns the correct user dictionary for user_id = 1 (Alice).
    """
    user = get_user(1)
    assert user == {"id": 1, "name": "Alice"}

def test_get_user_alice_id_1_float():
    """
    Test that get_user returns the correct user dictionary for user_id = 1.0 (Alice),
    demonstrating Python's type coercion for equality.
    """
    user = get_user(1.0)
    assert user == {"id": 1, "name": "Alice"}

def test_get_user_guest_id_0():
    """
    Test that get_user returns the default Guest user for user_id = 0.
    """
    user = get_user(0)
    assert user == {"id": 0, "name": "Guest"}

def test_get_user_guest_other_positive_id():
    """
    Test that get_user returns the default Guest user for a positive user_id other than 1.
    """
    user = get_user(5)
    assert user == {"id": 0, "name": "Guest"}

def test_get_user_guest_negative_id():
    """
    Test that get_user returns the default Guest user for a negative user_id.
    """
    user = get_user(-1)
    assert user == {"id": 0, "name": "Guest"}

def test_get_user_guest_none_id():
    """
    Test that get_user returns the default Guest user when user_id is None.
    This covers an edge case for input type.
    """
    user = get_user(None)
    assert user == {"id": 0, "name": "Guest"}

def test_get_user_guest_string_id():
    """
    Test that get_user returns the default Guest user when user_id is a string.
    This covers an edge case for input type, as "1" != 1.
    """
    user = get_user("1")
    assert user == {"id": 0, "name": "Guest"}
    user = get_user("abc")
    assert user == {"id": 0, "name": "Guest"}

def test_create_user_valid_name():
    """
    Test that create_user successfully creates a user with a standard valid name.
    """
    user = create_user("Bob")
    assert user == {"id": 99, "name": "Bob"}

def test_create_user_empty_name():
    """
    Test that create_user handles an empty string as a name.
    """
    user = create_user("")
    assert user == {"id": 99, "name": ""}

def test_create_user_none_name():
    """
    Test that create_user handles None as a name.
    This covers an edge case for input type.
    """
    user = create_user(None)
    assert user == {"id": 99, "name": None}

def test_create_user_numeric_name():
    """
    Test that create_user handles a numeric value as a name.
    This covers an edge case for input type.
    """
    user = create_user(123)
    assert user == {"id": 99, "name": 123}

def test_create_user_whitespace_name():
    """
    Test that create_user handles a name consisting only of whitespace characters.
    """
    user = create_user("   ")
    assert user == {"id": 99, "name": "   "}

def test_create_user_long_name_with_special_chars():
    """
    Test that create_user handles a long name containing various special characters.
    """
    long_name = "A very long name with special characters !@#$%^&*()_+-=[]{}|;:',.<>/?`~"
    user = create_user(long_name)
    assert user == {"id": 99, "name": long_name}
