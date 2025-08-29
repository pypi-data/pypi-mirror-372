"""Dict utilities for data transformation."""

from typing import Dict, Any


def dict_to_nested(flat_dict: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """
    Convert a flat dictionary with dot-notation keys to a nested dictionary structure.

    Args:
        flat_dict: Dictionary with potentially dot-separated keys
        separator: Separator character to split keys on (default: '.')

    Returns:
        Nested dictionary structure

    Example:
        >>> input_dict = {
        ...     "abc": "123",
        ...     "col.aaa": "111",
        ...     "col.bbb": "222"
        ... }
        >>> dict_to_nested(input_dict)
        {
            "abc": "123",
            "col": {
                "aaa": "111",
                "bbb": "222"
            }
        }
    """
    result = {}

    for key, value in flat_dict.items():
        if separator in key:
            # if value is None:
            #     continue
            # Split the key by separator
            parts = key.split(separator)

            # Navigate/create the nested structure
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the final value
            current[parts[-1]] = value
        else:
            # No separator, just set the value directly
            result[key] = value

    return result
