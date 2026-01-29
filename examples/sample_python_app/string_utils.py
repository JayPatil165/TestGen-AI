"""
String utilities module - Medium complexity string operations.

Provides various string manipulation functions.
"""

def capitalize_words(text):
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.split())

def reverse_string(text):
    """Reverse a string."""
    return text[::-1]

def is_palindrome(text):
    """Check if text is a palindrome."""
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]

def count_vowels(text):
    """Count vowels in text."""
    vowels = 'aeiouAEIOU'
    return sum(1 for char in text if char in vowels)

def truncate(text, max_length, suffix='...'):
    """Truncate text to max_length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
