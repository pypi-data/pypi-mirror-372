from dataclasses import dataclass, fields, is_dataclass
from typing import Any, List, Optional


@dataclass
class Diff:
    """
    Represents a single difference found between two data structures.

    This is a data transfer object used to communicate changes between the
    domain layer and presentation layer.

    Attributes:
        type: The type of change. Can be 'added', 'removed', or 'changed'.
        path: A list of strings representing the nested path to the changed
              attribute. For example: ['deployment', 'docker', 'web', 'image'].
        old_value: The previous value of the attribute. Can be None.
        new_value: The new value of the attribute. Can be None.
    """

    type: str
    path: List[str]
    old_value: Any = None
    new_value: Any = None

    def __repr__(self) -> str:
        return (
            f"Diff(type='{self.type}', path={self.path}, "
            f"old_value={self.old_value}, new_value={self.new_value})"
        )


class DiffManager:
    """A domain service to compare complex Python objects.

    Generates a structured list of differences.

    Its primary role is to create a "plan" that can be shown to the user
    before applying configuration changes, such as when creating a new instance
    or syncing an existing one.
    """

    def compare(
        self,
        old_obj: Any,
        new_obj: Any,
        path: Optional[List[str]] = None,
    ) -> List[Diff]:
        """
        Recursively compares two objects and returns a list of Diff objects.

        The comparison logic handles nested dataclasses and dictionaries. It detects
        added, removed, and changed values at any level of nesting.

        - To detect additions, pass `old_obj=None`.
        - To detect removals, pass `new_obj=None`.

        Args:
            old_obj: The old object (or None if detecting a new creation).
            new_obj: The new object (or None if detecting a deletion).
            path: The current path used internally for tracking recursion depth.

        Returns:
            A list of Diff objects, each representing a single change.
        """
        if path is None:
            path = []

        diffs = []

        if old_obj is None and new_obj is not None:
            return [Diff(type="added", path=path, new_value=new_obj)]

        if new_obj is None and old_obj is not None:
            return [Diff(type="removed", path=path, old_value=old_obj)]

        if is_dataclass(new_obj) or is_dataclass(old_obj):
            # Assumes old and new are of the same type or one is None
            obj_for_fields = new_obj if is_dataclass(new_obj) else old_obj
            for field in fields(obj_for_fields):
                field_path = path + [field.name]
                old_value = getattr(old_obj, field.name, None) if old_obj else None
                new_value = getattr(new_obj, field.name, None) if new_obj else None
                diffs.extend(self.compare(old_value, new_value, field_path))

        elif isinstance(new_obj, dict) or isinstance(old_obj, dict):
            old_keys = set(old_obj.keys()) if isinstance(old_obj, dict) else set()
            new_keys = set(new_obj.keys()) if isinstance(new_obj, dict) else set()

            diffs.extend(
                [
                    Diff(
                        type="removed",
                        path=path + [str(key)],
                        old_value=old_obj[key],
                    )
                    for key in sorted(old_keys - new_keys)
                ]
            )

            diffs.extend(
                [
                    Diff(type="added", path=path + [str(key)], new_value=new_obj[key])
                    for key in sorted(new_keys - old_keys)
                ]
            )

            for key in sorted(old_keys & new_keys):
                key_path = path + [str(key)]
                diffs.extend(self.compare(old_obj.get(key), new_obj.get(key), key_path))

        elif old_obj != new_obj:
            diffs.append(
                Diff(type="changed", path=path, old_value=old_obj, new_value=new_obj),
            )

        return diffs
