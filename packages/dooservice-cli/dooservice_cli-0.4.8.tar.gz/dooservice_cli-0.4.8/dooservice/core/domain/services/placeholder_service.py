from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar

T = TypeVar("T")


class PlaceholderService(ABC):
    """
    Abstract base class for a service that resolves placeholders in data structures.

    This service can resolve placeholders in various data types including:
    - Dictionaries
    - Lists
    - Dataclasses
    - Strings
    - Any nested combination of the above
    """

    @abstractmethod
    def resolve(self, data: T, context: Dict[str, Any]) -> T:
        """
        Resolves placeholders in the given data using the provided context.

        Args:
            data: The data structure in which to resolve placeholders.
            context: The dictionary containing the values for the placeholders.

        Returns:
            A new data structure with the placeholders resolved.
        """
