import pytest
# Assuming the test file is located in a directory that allows importing from 'utils'
# For example, if your project structure is:
# complex_app/
# ├── utils/
# │   └── string_utils.py
# └── tests/
#     └── test_string_utils.py
#
# You might need to adjust the import path based on your actual project setup.
# If running pytest from the 'complex_app' directory, 'utils.string_utils' should work.
from utils.string_utils import to_upper, to_lower, reverse_string

class TestStringUtils:
    """
    Comprehensive test suite for string utility functions:
    to_upper, to_lower, and reverse_string.
    """

    # --- Tests for to_upper function ---

    def test_to_upper_standard_lowercase_string(self):
        """
        Test to_upper with a standard lowercase string.
        """
        assert to_upper("hello") == "HELLO"

    def test_to_upper_already_uppercase_string(self):
        """
        Test to_upper with a string that is already entirely uppercase.
        """
        assert to_upper("WORLD") == "WORLD"

    def test_to_upper_mixed_case_string(self):
        """
        Test to_upper with a string containing a mix of uppercase and lowercase characters.
        """
        assert to_upper("PyThOn") == "PYTHON"

    def test_to_upper_empty_string(self):
        """
        Test to_upper with an empty string, expecting an empty string in return.
        """
        assert to_upper("") == ""

    def test_to_upper_string_with_numbers(self):
        """
        Test to_upper with a string containing numbers, ensuring numbers are unaffected.
        """
        assert to_upper("123abc") == "123ABC"

    def test_to_upper_string_with_symbols(self):
        """
        Test to_upper with a string containing symbols, ensuring symbols are unaffected.
        """
        assert to_upper("!@#$") == "!@#$"

    def test_to_upper_string_with_spaces(self):
        """
        Test to_upper with a string containing spaces, ensuring spaces are preserved.
        """
        assert to_upper("hello world") == "HELLO WORLD"

    def test_to_upper_string_with_mixed_content(self):
        """
        Test to_upper with a string containing letters, numbers, symbols, and spaces.
        """
        assert to_upper("Hello World 123!") == "HELLO WORLD 123!"

    def test_to_upper_unicode_characters(self):
        """
        Test to_upper with unicode characters, including those that change case and those that don't.
        """
        assert to_upper("straße") == "STRASSE"  # German eszett
        assert to_upper("你好世界") == "你好世界"  # Chinese characters (no case concept)

    def test_to_upper_none_input_raises_attribute_error(self):
        """
        Test to_upper with None input, expecting an AttributeError as None does not have .upper().
        """
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'upper'"):
            to_upper(None)

    def test_to_upper_non_string_int_input_raises_attribute_error(self):
        """
        Test to_upper with an integer input, expecting an AttributeError.
        """
        with pytest.raises(AttributeError, match="'int' object has no attribute 'upper'"):
            to_upper(123)

    def test_to_upper_non_string_list_input_raises_attribute_error(self):
        """
        Test to_upper with a list input, expecting an AttributeError.
        """
        with pytest.raises(AttributeError, match="'list' object has no attribute 'upper'"):
            to_upper(['a', 'b'])

    # --- Tests for to_lower function ---

    def test_to_lower_standard_uppercase_string(self):
        """
        Test to_lower with a standard uppercase string.
        """
        assert to_lower("HELLO") == "hello"

    def test_to_lower_already_lowercase_string(self):
        """
        Test to_lower with a string that is already entirely lowercase.
        """
        assert to_lower("world") == "world"

    def test_to_lower_mixed_case_string(self):
        """
        Test to_lower with a string containing a mix of uppercase and lowercase characters.
        """
        assert to_lower("PyThOn") == "python"

    def test_to_lower_empty_string(self):
        """
        Test to_lower with an empty string, expecting an empty string in return.
        """
        assert to_lower("") == ""

    def test_to_lower_string_with_numbers(self):
        """
        Test to_lower with a string containing numbers, ensuring numbers are unaffected.
        """
        assert to_lower("123ABC") == "123abc"

    def test_to_lower_string_with_symbols(self):
        """
        Test to_lower with a string containing symbols, ensuring symbols are unaffected.
        """
        assert to_lower("!@#$") == "!@#$"

    def test_to_lower_string_with_spaces(self):
        """
        Test to_lower with a string containing spaces, ensuring spaces are preserved.
        """
        assert to_lower("HELLO WORLD") == "hello world"

    def test_to_lower_string_with_mixed_content(self):
        """
        Test to_lower with a string containing letters, numbers, symbols, and spaces.
        """
        assert to_lower("Hello World 123!") == "hello world 123!"

    def test_to_lower_unicode_characters(self):
        """
        Test to_lower with unicode characters, including those that change case and those that don't.
        """
        assert to_lower("STRASSE") == "strasse"  # Python lower() does not reconstruct ß from STRASSE
        assert to_lower("你好世界") == "你好世界"  # Chinese characters (no case concept)

    def test_to_lower_none_input_raises_attribute_error(self):
        """
        Test to_lower with None input, expecting an AttributeError as None does not have .lower().
        """
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'lower'"):
            to_lower(None)

    def test_to_lower_non_string_int_input_raises_attribute_error(self):
        """
        Test to_lower with an integer input, expecting an AttributeError.
        """
        with pytest.raises(AttributeError, match="'int' object has no attribute 'lower'"):
            to_lower(123)

    def test_to_lower_non_string_list_input_raises_attribute_error(self):
        """
        Test to_lower with a list input, expecting an AttributeError.
        """
        with pytest.raises(AttributeError, match="'list' object has no attribute 'lower'"):
            to_lower(['A', 'B'])

    # --- Tests for reverse_string function ---

    def test_reverse_string_standard_string(self):
        """
        Test reverse_string with a typical string.
        """
        assert reverse_string("hello") == "olleh"

    def test_reverse_string_empty_string(self):
        """
        Test reverse_string with an empty string, expecting an empty string in return.
        """
        assert reverse_string("") == ""

    def test_reverse_string_single_character_string(self):
        """
        Test reverse_string with a single character string, expecting the same character.
        """
        assert reverse_string("a") == "a"

    def test_reverse_string_palindrome_string(self):
        """
        Test reverse_string with a palindrome string, expecting the string to remain unchanged.
        """
        assert reverse_string("madam") == "madam"

    def test_reverse_string_string_with_numbers(self):
        """
        Test reverse_string with a string containing numbers.
        """
        assert reverse_string("12345") == "54321"

    def test_reverse_string_string_with_symbols(self):
        """
        Test reverse_string with a string containing symbols.
        """
        assert reverse_string("!@#$") == "$#@!"

    def test_reverse_string_string_with_spaces(self):
        """
        Test reverse_string with a string containing spaces.
        """
        assert reverse_string("hello world") == "dlrow olleh"

    def test_reverse_string_string_with_mixed_content(self):
        """
        Test reverse_string with a string containing letters, numbers, symbols, and spaces.
        """
        assert reverse_string("Hello World 123!") == "!321 dlroW olleH"

    def test_reverse_string_unicode_characters(self):
        """
        Test reverse_string with unicode characters.
        """
        assert reverse_string("你好世界") == "界世好你"
        assert reverse_string("été") == "été"  # Palindrome with unicode

    def test_reverse_string_none_input_raises_type_error(self):
        """
        Test reverse_string with None input, expecting a TypeError as NoneType is not subscriptable.
        """
        with pytest.raises(TypeError, match="'NoneType' object is not subscriptable"):
            reverse_string(None)

    def test_reverse_string_non_string_int_input_raises_type_error(self):
        """
        Test reverse_string with an integer input, expecting a TypeError.
        """
        with pytest.raises(TypeError, match="'int' object is not subscriptable"):
            reverse_string(123)

    def test_reverse_string_non_string_list_input(self):
        """
        Test reverse_string with a list input.
        Python's slicing `[::-1]` works on any sequence type, including lists.
        While the function name implies string, the current implementation will correctly reverse a list.
        This test confirms this behavior.
        """
        assert reverse_string([1, 2, 3]) == [3, 2, 1]
        assert reverse_string(['a', 'b', 'c']) == ['c', 'b', 'a']

    def test_reverse_string_non_string_tuple_input(self):
        """
        Test reverse_string with a tuple input.
        Similar to lists, tuples are sequences and can be reversed using slicing.
        """
        assert reverse_string((1, 2, 3)) == (3, 2, 1)
        assert reverse_string(('x', 'y', 'z')) == ('z', 'y', 'x')
