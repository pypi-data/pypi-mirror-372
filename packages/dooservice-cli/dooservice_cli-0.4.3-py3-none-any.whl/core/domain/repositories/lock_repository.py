from abc import ABC, abstractmethod
from typing import Optional

from core.domain.entities.lockfile import LockFile


class LockRepository(ABC):
    """
    An interface (Port) for persisting and retrieving the LockFile.

    This abstracts the storage mechanism from the application logic.
    """

    @abstractmethod
    def get(self) -> Optional[LockFile]:
        """
        Loads the LockFile from the persistence layer.

        Returns None if the lock file does not exist.
        """

    @abstractmethod
    def save(self, lock_file: LockFile):
        """Saves a LockFile to the persistence layer."""
