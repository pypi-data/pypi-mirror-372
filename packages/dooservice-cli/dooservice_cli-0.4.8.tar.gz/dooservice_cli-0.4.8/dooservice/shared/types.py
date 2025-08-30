"""
Type definitions for the dooservice-cli application.

This module contains custom type definitions that are used throughout
the application to improve type safety and code clarity.
"""

from typing import NewType

# Duration type represents time durations in nanoseconds
Duration = NewType("Duration", int)
