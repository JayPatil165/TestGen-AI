"""
Unit tests for the string_utils module.
"""

import pytest
from string_utils import (
    capitalize_words,
    reverse_string,
    is_palindrome,
    count_vowels,
    truncate
)

class TestCapitalizeWords:
    """Tests for the capitalize_words function."""

    @pytest.mark.parametrize("input_text, expected_output", [
        ("hello world", "Hello World"),
        ("python programming", "Python Programming"),
        ("singleword", "Singleword"),
        ("", ""),  # Empty string
        ("  leading and trailing spaces  ", "Leading And Trailing Spaces"), # split() handles this
        ("multiple   spaces", "Multiple Spaces"), # split() handles this
        ("already Capitalized", "Already Capitalized"),
        ("123 test", "123 Test"), # Numbers are treated as part of words
        ("hello-world", "Hello-World"), # Hyphenated words are treated as single words
        ("  ", ""), # String with only spaces
        ("a", "A"), # Single character
        ("UPPERCASE TEXT", "Uppercase Text"), # Ensure only first letter is capitalized
        ("mixED cASE", "Mixed Case"),
    ])
    def test_capitalize_words_valid_inputs(self, input_text, expected_output):
        """
        Test capitalize_words with various valid string inputs, including
        empty strings, multiple spaces, and mixed cases.
        """
        assert capitalize_words(input_text) == expected_output

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        ['hello', 'world'],
        {'key': 'value'}
    ])
    def test_capitalize_words_invalid_types(self, invalid_input):
        """
        Test capitalize_words with invalid input types to ensure it raises
        a TypeError or AttributeError as expected by string methods.
        """
        with pytest.raises((TypeError, AttributeError)):
            capitalize_words(invalid_input)

class TestReverseString:
    """Tests for the reverse_string function."""

    @pytest.mark.parametrize("input_text, expected_output", [
        ("hello", "olleh"),
        ("python", "nohtyp"),
        ("", ""),  # Empty string
        ("a", "a"),  # Single character
        ("hello world", "dlrow olleh"),
        ("12345", "54321"),
        ("!@#$", "$#@!"),
        ("racecar", "racecar"), # Palindrome
        ("  spaces  ", "  secaps  "), # Preserves spaces
    ])
    def test_reverse_string_valid_inputs(self, input_text, expected_output):
        """
        Test reverse_string with various valid string inputs, including
        empty strings, single characters, and strings with spaces/numbers/symbols.
        """
        assert reverse_string(input_text) == expected_output

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        ['hello'],
        {'key': 'value'}
    ])
    def test_reverse_string_invalid_types(self, invalid_input):
        """
        Test reverse_string with invalid input types to ensure it raises
        a TypeError.
        """
        with pytest.raises(TypeError):
            reverse_string(invalid_input)

class TestIsPalindrome:
    """Tests for the is_palindrome function."""

    @pytest.mark.parametrize("input_text, expected_output", [
        ("madam", True),
        ("racecar", True),
        ("A man, a plan, a canal: Panama", True), # Ignores case and non-alphanumeric
        ("No lemon, no melon", True),
        ("Was it a car or a cat I saw?", True),
        ("hello", False),
        ("python", False),
        ("", True),  # Empty string is a palindrome
        ("a", True),  # Single character is a palindrome
        ("ab", False),
        ("Aa", True), # Case insensitive
        ("121", True), # Numbers
        ("123", False),
        ("MadamImAdam", True), # No spaces, mixed case
        ("Rotor", True),
        ("Palindrome", False),
        ("!@#$a!@#$", True), # Only alphanumeric considered
        ("a!", True),
        ("!@#", True), # No alphanumeric characters, cleaned string is empty
    ])
    def test_is_palindrome_valid_inputs(self, input_text, expected_output):
        """
        Test is_palindrome with various valid string inputs, including
        palindromes, non-palindromes, empty strings, and strings with
        punctuation/spaces/mixed case.
        """
        assert is_palindrome(input_text) == expected_output

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        ['madam'],
        {'key': 'value'}
    ])
    def test_is_palindrome_invalid_types(self, invalid_input):
        """
        Test is_palindrome with invalid input types to ensure it raises
        a TypeError or AttributeError.
        """
        with pytest.raises((TypeError, AttributeError)):
            is_palindrome(invalid_input)

class TestCountVowels:
    """Tests for the count_vowels function."""

    @pytest.mark.parametrize("input_text, expected_output", [
        ("hello world", 3), # e, o, o
        ("Python Programming", 5), # o, o, a, i, o
        ("", 0),  # Empty string
        ("rhythm", 0), # No vowels
        ("aeiouAEIOU", 10), # All vowels, mixed case
        ("a", 1),  # Single vowel
        ("b", 0),  # Single consonant
        ("12345!@#$", 0), # No letters
        ("h3ll0 w0rld!", 3), # Numbers and symbols ignored
        ("AEIOU", 5), # Uppercase vowels
        ("aEiOu", 5), # Mixed case vowels
    ])
    def test_count_vowels_valid_inputs(self, input_text, expected_output):
        """
        Test count_vowels with various valid string inputs, including
        strings with no vowels, all vowels, mixed case, and non-alphabetic characters.
        """
        assert count_vowels(input_text) == expected_output

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        ['hello'],
        {'key': 'value'}
    ])
    def test_count_vowels_invalid_types(self, invalid_input):
        """
        Test count_vowels with invalid input types to ensure it raises
        a TypeError.
        """
        with pytest.raises(TypeError):
            count_vowels(invalid_input)

class TestTruncate:
    """Tests for the truncate function."""

    @pytest.mark.parametrize("text, max_length, suffix, expected_output", [
        ("hello world", 15, "...", "hello world"), # No truncation needed
        ("hello world", 11, "...", "hello world"), # Exact length
        ("hello world", 10, "...", "hello w..."), # Truncation with default suffix
        ("a very long string", 10, "...", "a very l..."),
        ("short", 3, "...", "..."), # max_length <= len(suffix)
        ("short", 2, "...", "..."), # max_length < len(suffix)
        ("hello world", 7, "...", "hell..."), # Truncation with default suffix
        ("hello world", 10, "---", "hello---"), # Custom suffix
        ("hello", 5, "", "hello"), # Empty suffix, no truncation
        ("hello world", 5, "", "hello"), # Empty suffix, truncation
        ("", 5, "...", ""), # Empty text
        ("", 0, "...", "..."), # Empty text, max_length 0
        ("abc", 0, "...", "..."), # Text, max_length 0
        ("abc", 1, "...", "..."), # Text, max_length 1
        ("abc", 2, "...", "a..."), # Text, max_length 2
        ("abc", 3, "...", "abc"), # Text, max_length 3
        ("abcdefg", 5, "...", "ab..."),
        ("abcdefg", 5, "--", "abc--"), # Custom suffix shorter than default
        ("abcdefg", 5, "---", "ab---"), # Custom suffix same length as default
        ("abcdefg", 5, "----", "a----"), # Custom suffix longer than default
        ("abcdefg", 5, "----------", "----------"), # Custom suffix much longer than max_length
    ])
    def test_truncate_valid_inputs(self, text, max_length, suffix, expected_output):
        """
        Test truncate with various valid string inputs, max_lengths, and suffixes,
        covering cases where truncation is needed, not needed, and edge cases
        with suffix length relative to max_length.
        """
        assert truncate(text, max_length, suffix) == expected_output

    @pytest.mark.parametrize("text, max_length, suffix, expected_exception", [
        (None, 10, "...", TypeError), # Text is None
        (123, 10, "...", TypeError), # Text is not a string
        ([], 10, "...", TypeError), # Text is a list
        ("hello", None, "...", TypeError), # max_length is None
        ("hello", "10", "...", TypeError), # max_length is not an int
        ("hello", 10, None, TypeError), # Suffix is None
        ("hello", 10, 123, TypeError), # Suffix is not a string
    ])
    def test_truncate_invalid_types(self, text, max_length, suffix, expected_exception):
        """
        Test truncate with invalid input types for text, max_length, or suffix
        to ensure appropriate TypeErrors are raised.
        """
        with pytest.raises(expected_exception):
            truncate(text, max_length, suffix)

    @pytest.mark.parametrize("text, max_length, suffix, expected_output", [
        ("hello world", -1, "...", "..."), # Negative max_length
        ("hello world", -5, "...", "..."), # Negative max_length
        ("hello world", -1, "", ""), # Negative max_length with empty suffix
    ])
    def test_truncate_negative_max_length(self, text, max_length, suffix, expected_output):
        """
        Test truncate with negative max_length values. The current implementation
        will return just the suffix (or empty string if suffix is empty) as
        max_length - len(suffix) will be negative, resulting in text[:0].
        """
        assert truncate(text, max_length, suffix) == expected_output