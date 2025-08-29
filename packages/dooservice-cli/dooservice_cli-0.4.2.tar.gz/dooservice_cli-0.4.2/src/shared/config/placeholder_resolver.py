from dataclasses import fields, is_dataclass, replace
import re


class PlaceholderResolver:
    """
    Resolves placeholders in nested data structures like dataclasses, dicts, and lists.

    Supports placeholders like `${key}`, which are replaced by a value from a
    provided context dictionary.
    """

    _placeholder_pattern = re.compile(r"\$\{([^}]+)\}")

    def resolve(self, obj: any, context: dict) -> any:
        """
        Recursively resolves placeholders in the given object.

        Args:
            obj: The object (dataclass, dict, list, string) to process.
            context: A dictionary providing values for ${key} placeholders.

        Returns:
            A new object with all placeholders resolved.
        """
        if isinstance(obj, str):
            return self._placeholder_pattern.sub(
                lambda m: self._replacer(m, context),
                obj,
            )

        if isinstance(obj, list):
            return [self.resolve(item, context) for item in obj]

        if isinstance(obj, dict):
            return {k: self.resolve(v, context) for k, v in obj.items()}

        if is_dataclass(obj):
            changes = {}
            for f in fields(obj):
                original_value = getattr(obj, f.name)
                resolved_value = self.resolve(original_value, context)
                if original_value != resolved_value:
                    changes[f.name] = resolved_value
            return replace(obj, **changes) if changes else obj

        return obj

    def _replacer(self, match: re.Match, context: dict) -> str:
        """
        Determines the replacement value for a matched placeholder.

        Handles nested keys like `env_vars.ODOO_HTTP_PORT`.
        """
        placeholder_content = match.group(1)
        keys = placeholder_content.split(".")
        value = context
        try:
            for key in keys:
                value = value[key] if isinstance(value, dict) else getattr(value, key)
            return str(value)
        except (KeyError, AttributeError):
            # Return the original placeholder if no replacement is found
            return match.group(0)
