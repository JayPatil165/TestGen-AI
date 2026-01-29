"""
Data processor module - Higher complexity data operations.

Provides data processing and analysis functions.
"""

from typing import List, Dict, Any

def filter_by_key(data: List[Dict[str, Any]], key: str, value: Any) -> List[Dict[str, Any]]:
    """Filter list of dictionaries by key-value pair."""
    return [item for item in data if item.get(key) == value]

def group_by_key(data: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group list of dictionaries by key."""
    result = {}
    for item in data:
        group_key = item.get(key)
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result

def calculate_average(numbers: List[float]) -> float:
    """Calculate average of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

def find_duplicates(items: List[Any]) -> List[Any]:
    """Find duplicate items in list."""
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result
