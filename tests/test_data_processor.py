import pytest
from typing import List, Dict, Any
from data_processor import (
    filter_by_key,
    group_by_key,
    calculate_average,
    find_duplicates,
    merge_dicts,
)


class TestFilterByKey:
    """Tests for the filter_by_key function."""

    def test_filter_by_existing_key_value(self):
        """Test filtering by an existing key-value pair with multiple matches."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": "LA"},
            {"id": 3, "name": "Charlie", "city": "NY"},
        ]
        expected = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 3, "name": "Charlie", "city": "NY"},
        ]
        assert filter_by_key(data, "city", "NY") == expected

    def test_filter_by_non_existent_value(self):
        """Test filtering by a value that does not exist."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": "LA"},
        ]
        expected = []
        assert filter_by_key(data, "city", "SF") == expected

    def test_filter_by_non_existent_key(self):
        """Test filtering by a key that does not exist in any dictionary."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": "LA"},
        ]
        expected = []
        assert filter_by_key(data, "country", "USA") == expected

    def test_filter_empty_list(self):
        """Test filtering an empty list of dictionaries."""
        data: List[Dict[str, Any]] = []
        expected: List[Dict[str, Any]] = []
        assert filter_by_key(data, "city", "NY") == expected

    def test_filter_by_none_value(self):
        """Test filtering by a None value."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": None},
            {"id": 3, "name": "Charlie", "city": "NY"},
        ]
        expected = [{"id": 2, "name": "Bob", "city": None}]
        assert filter_by_key(data, "city", None) == expected

    def test_filter_key_with_none_value_in_data(self):
        """Test filtering when the key exists but its value is None in some items."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": None},
            {"id": 3, "name": "Charlie"},  # 'city' key is missing
        ]
        expected = [{"id": 1, "name": "Alice", "city": "NY"}]
        assert filter_by_key(data, "city", "NY") == expected

    def test_filter_by_different_data_types(self):
        """Test filtering with different data types for the value."""
        data = [
            {"id": 1, "value": 10},
            {"id": 2, "value": "10"},
            {"id": 3, "value": 10.0},
            {"id": 4, "value": True},
        ]
        assert filter_by_key(data, "value", 10) == [{"id": 1, "value": 10}]
        assert filter_by_key(data, "value", "10") == [{"id": 2, "value": "10"}]
        assert filter_by_key(data, "value", 10.0) == [{"id": 3, "value": 10.0}]
        assert filter_by_key(data, "value", True) == [{"id": 4, "value": True}]


class TestGroupByKey:
    """Tests for the group_by_key function."""

    def test_group_by_existing_key(self):
        """Test grouping by an existing key with multiple groups."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": "LA"},
            {"id": 3, "name": "Charlie", "city": "NY"},
            {"id": 4, "name": "David", "city": "LA"},
        ]
        expected = {
            "NY": [
                {"id": 1, "name": "Alice", "city": "NY"},
                {"id": 3, "name": "Charlie", "city": "NY"},
            ],
            "LA": [
                {"id": 2, "name": "Bob", "city": "LA"},
                {"id": 4, "name": "David", "city": "LA"},
            ],
        }
        assert group_by_key(data, "city") == expected

    def test_group_by_non_existent_key(self):
        """Test grouping by a key that does not exist in any dictionary."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        expected = {
            None: [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ]
        }
        assert group_by_key(data, "city") == expected

    def test_group_empty_list(self):
        """Test grouping an empty list of dictionaries."""
        data: List[Dict[str, Any]] = []
        expected: Dict[str, List[Dict[str, Any]]] = {}
        assert group_by_key(data, "city") == expected

    def test_group_by_key_with_none_values(self):
        """Test grouping when some items have None for the group key."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": None},
            {"id": 3, "name": "Charlie", "city": "NY"},
            {"id": 4, "name": "David", "city": None},
        ]
        expected = {
            "NY": [
                {"id": 1, "name": "Alice", "city": "NY"},
                {"id": 3, "name": "Charlie", "city": "NY"},
            ],
            None: [
                {"id": 2, "name": "Bob", "city": None},
                {"id": 4, "name": "David", "city": None},
            ],
        }
        assert group_by_key(data, "city") == expected

    def test_group_by_key_with_mixed_types(self):
        """Test grouping when the group key has mixed data types."""
        data = [
            {"id": 1, "value": 1},
            {"id": 2, "value": "1"},
            {"id": 3, "value": 1},
            {"id": 4, "value": True},
        ]
        expected = {
            1: [{"id": 1, "value": 1}, {"id": 3, "value": 1}],
            "1": [{"id": 2, "value": "1"}],
            True: [{"id": 4, "value": True}],
        }
        assert group_by_key(data, "value") == expected

    def test_group_by_key_single_group(self):
        """Test grouping where all items belong to a single group."""
        data = [
            {"id": 1, "name": "Alice", "city": "NY"},
            {"id": 2, "name": "Bob", "city": "NY"},
        ]
        expected = {
            "NY": [
                {"id": 1, "name": "Alice", "city": "NY"},
                {"id": 2, "name": "Bob", "city": "NY"},
            ]
        }
        assert group_by_key(data, "city") == expected


class TestCalculateAverage:
    """Tests for the calculate_average function."""

    @pytest.mark.parametrize(
        "numbers, expected_average",
        [
            ([1, 2, 3, 4, 5], 3.0),
            ([10, 20, 30], 20.0),
            ([-1, 0, 1], 0.0),
            ([5], 5.0),
            ([2.5, 3.5, 4.0], 3.3333333333333335),
            ([0, 0, 0], 0.0),
            ([-10, -20, -30], -20.0),
        ],
    )
    def test_calculate_average_valid_inputs(self, numbers, expected_average):
        """Test calculating average with various valid lists of numbers."""
        assert calculate_average(numbers) == pytest.approx(expected_average)

    def test_calculate_average_empty_list_raises_error(self):
        """Test that calculating average of an empty list raises a ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            calculate_average([])


class TestFindDuplicates:
    """Tests for the find_duplicates function."""

    def test_find_duplicates_with_multiple_duplicates(self):
        """Test finding multiple duplicate items."""
        items = [1, 2, 2, 3, 4, 4, 4, 5, 1]
        expected = [1, 2, 4]
        assert sorted(find_duplicates(items)) == sorted(expected)

    def test_find_duplicates_no_duplicates(self):
        """Test finding duplicates in a list with no duplicates."""
        items = [1, 2, 3, 4, 5]
        expected: List[Any] = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_empty_list(self):
        """Test finding duplicates in an empty list."""
        items: List[Any] = []
        expected: List[Any] = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_single_item_list(self):
        """Test finding duplicates in a list with a single item."""
        items = [1]
        expected: List[Any] = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_with_mixed_types(self):
        """Test finding duplicates with mixed data types."""
        items = [1, "a", 1, "b", "a", None, None, True, False, True]
        expected = [1, "a", None, True]
        assert sorted(find_duplicates(items), key=str) == sorted(expected, key=str)

    def test_find_duplicates_all_items_are_duplicates(self):
        """Test finding duplicates when all items are duplicates."""
        items = [1, 1, 1, 1]
        expected = [1]
        assert find_duplicates(items) == expected

    def test_find_duplicates_with_complex_objects(self):
        """Test finding duplicates with hashable complex objects (tuples)."""
        items = [(1, 2), (3, 4), (1, 2), (5, 6), (3, 4)]
        expected = [(1, 2), (3, 4)]
        assert sorted(find_duplicates(items)) == sorted(expected)


class TestMergeDicts:
    """Tests for the merge_dicts function."""

    def test_merge_two_dictionaries(self):
        """Test merging two simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_dictionaries_with_overlapping_keys(self):
        """Test merging dictionaries where later dictionaries overwrite earlier keys."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = {"c": 5, "d": 6}
        expected = {"a": 1, "b": 3, "c": 5, "d": 6}
        assert merge_dicts(dict1, dict2, dict3) == expected

    def test_merge_empty_dictionaries(self):
        """Test merging multiple empty dictionaries."""
        dict1 = {}
        dict2 = {}
        expected = {}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_with_one_empty_dictionary(self):
        """Test merging a non-empty dictionary with an empty one."""
        dict1 = {"a": 1}
        dict2 = {}
        expected = {"a": 1}
        assert merge_dicts(dict1, dict2) == expected
        assert merge_dicts(dict2, dict1) == expected

    def test_merge_no_dictionaries_passed(self):
        """Test calling merge_dicts with no arguments."""
        expected = {}
        assert merge_dicts() == expected

    def test_merge_single_dictionary(self):
        """Test merging a single dictionary (should return a copy)."""
        dict1 = {"a": 1, "b": 2}
        expected = {"a": 1, "b": 2}
        result = merge_dicts(dict1)
        assert result == expected
        assert result is not dict1  # Ensure it's a new dictionary

    def test_merge_dictionaries_with_different_value_types(self):
        """Test merging dictionaries with various value types."""
        dict1 = {"a": 1, "b": [1, 2]}
        dict2 = {"c": "hello", "d": {"key": "value"}}
        dict3 = {"a": None}
        expected = {"a": None, "b": [1, 2], "c": "hello", "d": {"key": "value"}}
        assert merge_dicts(dict1, dict2, dict3) == expected

    def test_merge_dictionaries_with_complex_keys(self):
        """Test merging dictionaries with complex (hashable) keys."""
        dict1 = {(1, 2): "tuple_key"}
        dict2 = {"a": 1, (1, 2): "new_tuple_value"}
        expected = {"a": 1, (1, 2): "new_tuple_value"}
        assert merge_dicts(dict1, dict2) == expected