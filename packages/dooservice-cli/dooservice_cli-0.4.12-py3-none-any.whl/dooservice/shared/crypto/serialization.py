from dataclasses import asdict, is_dataclass
from typing import Any


def to_serializable(obj: Any) -> Any:
    """
    Recursively converts a dataclass object to a serializable dictionary.

    Ensures that nested dataclasses are also converted.
    This is a prerequisite for libraries like `toml` or `json` that
    do not natively handle dataclass objects.

    Args:
        obj: The object to convert (can be a dataclass, dict, list, etc.).

    Returns:
        A serializable representation of the object.
    """
    if is_dataclass(obj):
        return {k: to_serializable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj
