from pathlib import Path
from typing import Optional

from dacite import (
    Config as DaciteConfig,
    from_dict,
)
import toml

from core.domain.entities.lockfile import LockFile
from core.domain.repositories.lock_repository import LockRepository
from shared.crypto.serialization import to_serializable


class FileLockRepository(LockRepository):
    """Repository implementation that persists LockFile to a TOML file.

    Persists the LockFile to a TOML file on the local filesystem.
    """

    LOCK_FILE_NAME = "dooservice.lock"

    def __init__(self, project_root: Path):
        self._project_root = project_root
        self._lock_file_path = self._project_root / self.LOCK_FILE_NAME

    def get(self) -> Optional[LockFile]:
        """Reads and parses the dooservice.lock file into a LockFile object."""
        if not self._lock_file_path.exists():
            return None

        with open(self._lock_file_path, encoding="utf-8") as f:
            data = toml.load(f)

        return from_dict(data_class=LockFile, data=data, config=DaciteConfig(cast=[]))

    def save(self, lock_file: LockFile):
        """Serializes a LockFile object and writes it to the dooservice.lock file.

        Writes the LockFile object to the dooservice.lock file in TOML format.
        """
        serializable_data = to_serializable(lock_file)

        # Filter out top-level keys with None values to keep the lock file clean.
        clean_data = {k: v for k, v in serializable_data.items() if v is not None}

        with open(self._lock_file_path, "w", encoding="utf-8") as f:
            toml.dump(clean_data, f)
