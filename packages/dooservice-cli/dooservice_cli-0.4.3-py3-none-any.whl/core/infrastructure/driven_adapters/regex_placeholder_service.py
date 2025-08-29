from dataclasses import fields, is_dataclass, replace
import re
from typing import Any, Dict, TypeVar

from core.domain.services.placeholder_service import PlaceholderService

T = TypeVar("T")


class RegexPlaceholderService(PlaceholderService):
    """
    An infrastructure adapter that implements the PlaceholderService port.

    This class resolves placeholders in a nested dictionary structure. Placeholders
    are expected in the format `${path.to.value}`. It supports nested lookups
    in a provided context dictionary.
    """

    def __init__(self):
        """Initializes the resolver with a regex pattern for placeholders."""
        self._pattern = re.compile(r"\$\{(.*?)\}")
        self._context = {}

    def resolve(self, data: T, context: Dict[str, Any]) -> T:
        """
        Resolves all placeholders in the given data structure.

        Args:
            data: The data structure in which to resolve placeholders.
            context: The dictionary containing the values for the placeholders.

        Returns:
            A new data structure with all placeholders resolved.
        """
        self._context = context
        return self._resolve_part(data)

    def _resolve_part(self, part: Any) -> Any:
        """
        Recursively traverses and resolves placeholders in a part of the data.

        Supports dictionaries, lists, dataclasses, and strings.
        """
        if isinstance(part, dict):
            return {key: self._resolve_part(value) for key, value in part.items()}
        if isinstance(part, list):
            return [self._resolve_part(item) for item in part]
        if isinstance(part, str):
            return self._resolve_string(part)
        if is_dataclass(part):
            return self._resolve_dataclass(part)
        return part

    def _resolve_dataclass(self, obj: Any) -> Any:
        """
        Resolves placeholders in a dataclass instance.

        Args:
            obj: The dataclass instance to process.

        Returns:
            A new dataclass instance with resolved placeholders.
        """
        changes = {}
        for field in fields(obj):
            original_value = getattr(obj, field.name)
            resolved_value = self._resolve_part(original_value)
            if original_value != resolved_value:
                changes[field.name] = resolved_value

        return replace(obj, **changes) if changes else obj

    def _resolve_string(self, value: str) -> Any:
        """
        Repeatedly resolves placeholders in a string until none are left.

        This handles cases where a placeholder's value is another placeholder.
        """
        resolved_value = value
        # Limit iterations to avoid potential infinite loops
        for _ in range(10):
            new_value = self._pattern.sub(self._replace_match, str(resolved_value))
            if new_value == str(resolved_value):
                break
            resolved_value = new_value

        return self._cast_if_possible(value, resolved_value)

    def _replace_match(self, match: re.Match) -> Any:
        """Replaces a single regex match with its value from the context."""
        path = match.group(1)
        keys = path.split(".")

        try:
            value = self._context
            for key in keys:
                value = value[key]

            # If the resolved value is another placeholder, resolve it recursively
            if isinstance(value, str) and self._pattern.search(value):
                return self._resolve_string(value)

            return value
        except (KeyError, TypeError, IndexError):
            # If path is not found, return the original placeholder string
            return match.group(0)

    def _cast_if_possible(self, original_str: str, resolved_str: Any) -> Any:
        """If a string was fully replaced, attempts to cast to a specific type.

        Attempts to cast the resolved string to a more specific type like bool or int.
        """
        if str(resolved_str) == original_str or not isinstance(resolved_str, str):
            return resolved_str

        if resolved_str.lower() == "true":
            return True
        if resolved_str.lower() == "false":
            return False
        if resolved_str.isdigit():
            return int(resolved_str)

        return resolved_str
