import os
import shutil

from core.domain.repositories.filesystem_repository import FilesystemRepository


class OsFilesystemRepository(FilesystemRepository):
    """A concrete implementation of FilesystemRepository using `os` and `shutil`.

    Uses the standard `os` and `shutil` modules to interact with the filesystem.
    """

    def create_directory(self, path: str, exist_ok: bool = True):
        """Creates a directory using the os.makedirs function."""
        os.makedirs(path, exist_ok=exist_ok)

    def delete_directory(self, path: str):
        """Recursively deletes a directory using shutil.rmtree."""
        if self.directory_exists(path):
            shutil.rmtree(path)

    def directory_exists(self, path: str) -> bool:
        """Checks if a path is an existing directory."""
        return os.path.isdir(path)
