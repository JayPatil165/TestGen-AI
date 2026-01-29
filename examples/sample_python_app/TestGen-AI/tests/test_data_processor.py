import pytest
from data_processor import (
    filter_by_key,
    group_by_key,
    calculate_average,
    find_duplicates,
    merge_dicts,
)

class TestFilterByKey:
    """Tests for the filter_by_key function."""

    def test_filter_by_existing_key_single_match(self):
        """Test filtering with an existing key and a single matching item."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        expected = [{"id": 1, "name": "Alice"}]
        assert filter_by_key(data, "id", 1) == expected

    def test_filter_by_existing_key_multiple_matches(self):
        """Test filtering with an existing key and multiple matching items."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "A", "value": 30},
        ]
        expected = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 30},
        ]
        assert filter_by_key(data, "category", "A") == expected

    def test_filter_by_existing_key_no_matches(self):
        """Test filtering with an existing key but no matching items."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        expected = []
        assert filter_by_key(data, "id", 99) == expected

    def test_filter_by_non_existent_key(self):
        """Test filtering by a key that does not exist in any dictionary."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        expected = []
        assert filter_by_key(data, "age", 30) == expected

    def test_filter_by_key_with_none_value(self):
        """Test filtering for items where the key's value is None."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": None},
            {"id": 3, "name": "Charlie"},
            {"id": 4, "age": 30}, # 'name' key is missing, .get('name') returns None
        ]
        expected = [
            {"id": 2, "name": None},
            {"id": 4, "age": 30},
        ]
        assert filter_by_key(data, "name", None) == expected

    def test_filter_empty_data_list(self):
        """Test filtering an empty list of dictionaries."""
        data = []
        expected = []
        assert filter_by_key(data, "id", 1) == expected

    def test_filter_data_with_single_item(self):
        """Test filtering a list containing a single dictionary."""
        data = [{"id": 1, "name": "Alice"}]
        expected = [{"id": 1, "name": "Alice"}]
        assert filter_by_key(data, "id", 1) == expected

    def test_filter_data_with_mixed_types(self):
        """Test filtering with mixed data types for the value."""
        data = [
            {"value": 1},
            {"value": "1"},
            {"value": True},
            {"value": 1.0},
        ]
        assert filter_by_key(data, "value", 1) == [{"value": 1}]
        assert filter_by_key(data, "value", "1") == [{"value": "1"}]
        assert filter_by_key(data, "value", True) == [{"value": True}]
        assert filter_by_key(data, "value", 1.0) == [{"value": 1.0}]

    def test_filter_by_key_value_zero(self):
        """Test filtering by a value of zero."""
        data = [{"count": 0}, {"count": 1}, {"count": -1}]
        expected = [{"count": 0}]
        assert filter_by_key(data, "count", 0) == expected

class TestGroupByKey:
    """Tests for the group_by_key function."""

    def test_group_by_existing_key_multiple_groups(self):
        """Test grouping by an existing key with multiple distinct values."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "A", "value": 30},
            {"category": "C", "value": 40},
        ]
        expected = {
            "A": [{"category": "A", "value": 10}, {"category": "A", "value": 30}],
            "B": [{"category": "B", "value": 20}],
            "C": [{"category": "C", "value": 40}],
        }
        assert group_by_key(data, "category") == expected

    def test_group_by_existing_key_single_group(self):
        """Test grouping by an existing key where all items belong to one group."""
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 20},
            {"category": "A", "value": 30},
        ]
        expected = {
            "A": [
                {"category": "A", "value": 10},
                {"category": "A", "value": 20},
                {"category": "A", "value": 30},
            ]
        }
        assert group_by_key(data, "category") == expected

    def test_group_by_non_existent_key(self):
        """Test grouping by a key that does not exist in any dictionary."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        # Items without the key will be grouped under None
        expected = {
            None: [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ]
        }
        assert group_by_key(data, "age") == expected

    def test_group_by_key_with_none_value(self):
        """Test grouping where some key values are None."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": None},
            {"id": 3, "name": "Charlie"},
            {"id": 4, "age": 30}, # 'name' key is missing, .get('name') returns None
        ]
        expected = {
            "Alice": [{"id": 1, "name": "Alice"}],
            None: [
                {"id": 2, "name": None},
                {"id": 4, "age": 30},
            ],
            "Charlie": [{"id": 3, "name": "Charlie"}],
        }
        assert group_by_key(data, "name") == expected

    def test_group_empty_data_list(self):
        """Test grouping an empty list of dictionaries."""
        data = []
        expected = {}
        assert group_by_key(data, "category") == expected

    def test_group_data_with_single_item(self):
        """Test grouping a list containing a single dictionary."""
        data = [{"id": 1, "name": "Alice"}]
        expected = {"Alice": [{"id": 1, "name": "Alice"}]}
        assert group_by_key(data, "name") == expected

    def test_group_by_key_with_numeric_values(self):
        """Test grouping by a key with numeric values."""
        data = [
            {"score": 10, "name": "A"},
            {"score": 20, "name": "B"},
            {"score": 10, "name": "C"},
        ]
        expected = {
            10: [{"score": 10, "name": "A"}, {"score": 10, "name": "C"}],
            20: [{"score": 20, "name": "B"}],
        }
        assert group_by_key(data, "score") == expected

class TestCalculateAverage:
    """Tests for the calculate_average function."""

    def test_average_positive_integers(self):
        """Test calculating the average of a list of positive integers."""
        numbers = [1, 2, 3, 4, 5]
        expected = 3.0
        assert calculate_average(numbers) == expected

    def test_average_positive_floats(self):
        """Test calculating the average of a list of positive floats."""
        numbers = [1.5, 2.5, 3.5]
        expected = 2.5
        assert calculate_average(numbers) == expected

    def test_average_mixed_positive_numbers(self):
        """Test calculating the average of a list of mixed positive integers and floats."""
        numbers = [1, 2.0, 3, 4.0]
        expected = 2.5
        assert calculate_average(numbers) == expected

    def test_average_negative_numbers(self):
        """Test calculating the average of a list of negative numbers."""
        numbers = [-1, -2, -3]
        expected = -2.0
        assert calculate_average(numbers) == expected

    def test_average_mixed_positive_and_negative_numbers(self):
        """Test calculating the average of a list of mixed positive and negative numbers."""
        numbers = [-1, 0, 1, 2, -2]
        expected = 0.0
        assert calculate_average(numbers) == expected

    def test_average_list_with_zero(self):
        """Test calculating the average of a list containing zero."""
        numbers = [0, 0, 0]
        expected = 0.0
        assert calculate_average(numbers) == expected

    def test_average_single_number(self):
        """Test calculating the average of a list with a single number."""
        numbers = [7.7]
        expected = 7.7
        assert calculate_average(numbers) == expected

    def test_average_empty_list_raises_value_error(self):
        """Test that calculating the average of an empty list raises a ValueError."""
        numbers = []
        with pytest.raises(ValueError) as excinfo:
            calculate_average(numbers)
        assert "Cannot calculate average of empty list" in str(excinfo.value)

    def test_average_large_numbers(self):
        """Test calculating the average with large numbers."""
        numbers = [1_000_000, 2_000_000, 3_000_000]
        expected = 2_000_000.0
        assert calculate_average(numbers) == expected

    def test_average_small_numbers(self):
        """Test calculating the average with very small numbers."""
        numbers = [0.0001, 0.0002, 0.0003]
        expected = 0.0002
        assert calculate_average(numbers) == pytest.approx(expected)

class TestFindDuplicates:
    """Tests for the find_duplicates function."""

    def test_find_duplicates_with_multiple_duplicates(self):
        """Test finding multiple duplicate items in a list."""
        items = [1, 2, 2, 3, 4, 4, 4, 5, 1]
        expected = [1, 2, 4]
        assert sorted(find_duplicates(items)) == sorted(expected)

    def test_find_duplicates_with_single_duplicate(self):
        """Test finding a single duplicate item in a list."""
        items = ["apple", "banana", "apple", "orange"]
        expected = ["apple"]
        assert find_duplicates(items) == expected

    def test_find_duplicates_no_duplicates(self):
        """Test finding duplicates in a list with no duplicate items."""
        items = [1, 2, 3, 4, 5]
        expected = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_empty_list(self):
        """Test finding duplicates in an empty list."""
        items = []
        expected = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_single_item_list(self):
        """Test finding duplicates in a list with a single item."""
        items = [1]
        expected = []
        assert find_duplicates(items) == expected

    def test_find_duplicates_all_items_are_duplicates(self):
        """Test finding duplicates when all items in the list are duplicates."""
        items = [7, 7, 7, 7]
        expected = [7]
        assert find_duplicates(items) == expected

    def test_find_duplicates_mixed_types(self):
        """Test finding duplicates with mixed data types."""
        items = [1, "a", 1.0, "b", 1, "a"]
        # Note: 1 and 1.0 are considered equal but distinct types in sets,
        # but Python's `item in seen` will treat 1 and 1.0 as the same.
        # So, if 1 is seen, 1.0 will be considered a duplicate.
        expected = [1, "a"]
        assert sorted(find_duplicates(items), key=str) == sorted(expected, key=str)

    def test_find_duplicates_with_none(self):
        """Test finding duplicates including None values."""
        items = [None, 1, None, 2, 3]
        expected = [None]
        assert find_duplicates(items) == expected

    def test_find_duplicates_with_complex_hashable_objects(self):
        """Test finding duplicates with complex hashable objects (tuples)."""
        items = [(1, 2), (3, 4), (1, 2), (5, 6)]
        expected = [(1, 2)]
        assert find_duplicates(items) == expected

class TestMergeDicts:
    """Tests for the merge_dicts function."""

    def test_merge_two_dicts_no_overlap(self):
        """Test merging two dictionaries with no overlapping keys."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_two_dicts_with_overlap(self):
        """Test merging two dictionaries with overlapping keys, ensuring last dict wins."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        expected = {"a": 1, "b": 3, "c": 4}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_multiple_dicts(self):
        """Test merging more than two dictionaries."""
        dict1 = {"a": 1}
        dict2 = {"b": 2, "a": 10}
        dict3 = {"c": 3, "b": 20}
        expected = {"a": 10, "b": 20, "c": 3}
        assert merge_dicts(dict1, dict2, dict3) == expected

    def test_merge_no_dicts(self):
        """Test merging with no dictionaries provided."""
        expected = {}
        assert merge_dicts() == expected

    def test_merge_single_dict(self):
        """Test merging with a single dictionary provided."""
        dict1 = {"a": 1, "b": 2}
        expected = {"a": 1, "b": 2}
        assert merge_dicts(dict1) == expected

    def test_merge_with_empty_dicts(self):
        """Test merging with empty dictionaries."""
        dict1 = {"a": 1}
        dict2 = {}
        dict3 = {"b": 2}
        expected = {"a": 1, "b": 2}
        assert merge_dicts(dict1, dict2, dict3) == expected

    def test_merge_all_empty_dicts(self):
        """Test merging only empty dictionaries."""
        expected = {}
        assert merge_dicts({}, {}, {}) == expected

    def test_merge_dicts_with_none_values(self):
        """Test merging dictionaries containing None values."""
        dict1 = {"a": 1, "b": None}
        dict2 = {"c": 3, "b": 2}
        expected = {"a": 1, "b": 2, "c": 3}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_dicts_with_complex_values(self):
        """Test merging dictionaries with complex values like lists or other dicts."""
        dict1 = {"a": [1, 2], "b": {"x": 1}}
        dict2 = {"c": "hello", "a": [3, 4]}
        expected = {"a": [3, 4], "b": {"x": 1}, "c": "hello"}
        assert merge_dicts(dict1, dict2) == expected

    def test_merge_dicts_order_of_precedence(self):
        """Test that the last dictionary's value for a key takes precedence."""
        dict1 = {"key": "value1"}
        dict2 = {"key": "value2"}
        dict3 = {"key": "value3"}
        expected = {"key": "value3"}
        assert merge_dicts(dict1, dict2, dict3) == expected
