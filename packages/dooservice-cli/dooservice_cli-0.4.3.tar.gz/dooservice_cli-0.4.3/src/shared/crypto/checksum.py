import hashlib
import json
from typing import Any, List, Optional

from shared.crypto.serialization import to_serializable


def generate_checksum(data: Any, ignored_keys: Optional[List[str]] = None) -> str:
    """
    Generates a deterministic SHA256 checksum for a given Python object.

    This function is crucial for detecting changes between desired
    configurations and the last applied state. By comparing checksums, the
    system can identify configuration drift efficiently.

    The checksum is guaranteed to be deterministic by following a strict
    serialization process before hashing:
    1.  Recursively converts any dataclasses to dictionaries.
    2.  Serializes the object to a JSON string.
    3.  Sorts all dictionary keys during serialization (`sort_keys=True`).
    4.  Uses a compact format without whitespace (`separators=(",", ":")`).

    Args:
        data: The data structure to checksum (e.g., a dataclass, dict, list).
        ignored_keys: A list of top-level keys to exclude from the checksum.
                      This is vital for ignoring volatile fields or the
                      checksum fields themselves.

    Returns:
        A string representing the SHA256 hash, prefixed with "sha256:".
    """
    if ignored_keys is None:
        ignored_keys = []

    serializable_data = to_serializable(data)

    if isinstance(serializable_data, dict):
        for key in ignored_keys:
            serializable_data.pop(key, None)

    encoded_data = json.dumps(
        serializable_data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    hasher = hashlib.sha256()
    hasher.update(encoded_data)
    hex_digest = hasher.hexdigest()

    return f"sha256:{hex_digest}"
