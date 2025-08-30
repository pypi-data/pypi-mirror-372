"""
Placeholder Resolution Service.

Pure domain service for resolving variable placeholders in configuration objects.
Follows Single Responsibility Principle - only handles placeholder resolution logic.
"""

from dataclasses import fields, is_dataclass, replace
import re
from typing import Any, Dict, List, Match, Pattern


class PlaceholderResolutionService:
    """
    Domain service responsible for resolving placeholders in nested data structures.

    Supports placeholders like `${key}` or `${nested.key}`, which are replaced
    by values from a provided context dictionary.

    This is pure business logic with no external dependencies.
    """

    def __init__(self) -> None:
        """Initialize the service with compiled regex pattern for performance."""
        self._placeholder_pattern: Pattern[str] = re.compile(r"\$\{([^}]+)\}")

    def resolve_placeholders(self, obj: Any, context: Dict[str, Any]) -> Any:
        """
        Recursively resolves placeholders in the given object.

        Args:
            obj: The object (dataclass, dict, list, string) to process
            context: A dictionary providing values for ${key} placeholders

        Returns:
            A new object with all placeholders resolved

        Raises:
            ValueError: If context is None or invalid
        """
        if context is None:
            raise ValueError("Context dictionary cannot be None")

        return self._resolve_recursive(obj, context)

    def _resolve_recursive(self, obj: Any, context: Dict[str, Any]) -> Any:
        """
        Internal recursive resolution method.

        Args:
            obj: Object to process
            context: Replacement context

        Returns:
            Object with resolved placeholders
        """
        if isinstance(obj, str):
            return self._resolve_string_placeholders(obj, context)

        if isinstance(obj, list):
            return self._resolve_list_placeholders(obj, context)

        if isinstance(obj, dict):
            return self._resolve_dict_placeholders(obj, context)

        if is_dataclass(obj):
            return self._resolve_dataclass_placeholders(obj, context)

        # Return primitive types unchanged
        return obj

    def _resolve_string_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """
        Resolve placeholders in a string.

        Args:
            text: String containing placeholders
            context: Replacement context

        Returns:
            String with resolved placeholders
        """
        return self._placeholder_pattern.sub(
            lambda match: self._get_replacement_value(match, context),
            text,
        )

    def _resolve_list_placeholders(
        self,
        items: List[Any],
        context: Dict[str, Any],
    ) -> List[Any]:
        """
        Resolve placeholders in a list.

        Args:
            items: List containing items with potential placeholders
            context: Replacement context

        Returns:
            List with resolved placeholders
        """
        return [self._resolve_recursive(item, context) for item in items]

    def _resolve_dict_placeholders(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve placeholders in a dictionary.

        Args:
            data: Dictionary containing values with potential placeholders
            context: Replacement context

        Returns:
            Dictionary with resolved placeholders
        """
        return {
            key: self._resolve_recursive(value, context) for key, value in data.items()
        }

    def _resolve_dataclass_placeholders(self, obj: Any, context: Dict[str, Any]) -> Any:
        """
        Resolve placeholders in a dataclass.

        Args:
            obj: Dataclass instance
            context: Replacement context

        Returns:
            New dataclass instance with resolved placeholders
        """
        changes = {}

        for field in fields(obj):
            original_value = getattr(obj, field.name)
            resolved_value = self._resolve_recursive(original_value, context)

            if original_value != resolved_value:
                changes[field.name] = resolved_value

        return replace(obj, **changes) if changes else obj

    def _get_replacement_value(self, match: Match[str], context: Dict[str, Any]) -> str:
        """
        Get the replacement value for a matched placeholder.

        Handles nested keys like `env_vars.ODOO_HTTP_PORT`.

        Args:
            match: Regex match object containing the placeholder
            context: Replacement context

        Returns:
            Replacement value as string, or original placeholder if not found
        """
        placeholder_content = match.group(1)
        keys = placeholder_content.split(".")

        try:
            value = self._navigate_nested_context(keys, context)
            return str(value)
        except (KeyError, AttributeError, TypeError):
            # Return the original placeholder if no replacement is found
            return match.group(0)

    def _navigate_nested_context(self, keys: List[str], context: Dict[str, Any]) -> Any:
        """
        Navigate through nested keys in the context.

        Args:
            keys: List of keys to navigate (e.g., ['env_vars', 'PORT'])
            context: Context dictionary

        Returns:
            Final value after navigation

        Raises:
            KeyError: If key not found
            AttributeError: If attribute not found
            TypeError: If context structure is invalid
        """
        value = context

        for key in keys:
            value = value[key] if isinstance(value, dict) else getattr(value, key)

        return value


# Factory function for easier testing and dependency injection
def create_placeholder_resolver() -> PlaceholderResolutionService:
    """
    Factory function to create a PlaceholderResolutionService instance.

    Returns:
        New PlaceholderResolutionService instance
    """
    return PlaceholderResolutionService()
