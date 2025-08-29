"""
Utility functions for the dooservice-cli application.

This module contains commonly used utility functions that are shared
across different parts of the application.
"""

from typing import Union

from shared.types import Duration
from shared.utils.duration_parser import parse_duration_to_nanoseconds


def duration_hook(value: Union[str, int]) -> Duration:
    """
    Converts a duration value to nanoseconds.

    This function is used as a type hook for dacite to convert duration
    strings (e.g., "30s", "5m") to nanosecond values.

    Args:
        value: The duration value, either as a string (e.g., "30s") or
               as an integer representing nanoseconds.

    Returns:
        A Duration object representing the value in nanoseconds.

    Examples:
        >>> duration_hook("30s")
        Duration(30000000000)
        >>> duration_hook(5000000000)
        Duration(5000000000)
    """
    if isinstance(value, str):
        return Duration(parse_duration_to_nanoseconds(value))
    return Duration(value)
