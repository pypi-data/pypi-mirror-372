from abc import ABC, abstractmethod


class FilesystemRepository(ABC):
    """
    An interface for performing filesystem operations, such as creating directories.

    This allows the application to remain independent of the underlying OS.
    """

    @abstractmethod
    def create_directory(self, path: str, exist_ok: bool = True):
        """
        Creates a directory at the given path.

        Args:
            path: The path where the directory should be created.
            exist_ok: If True, do not raise an error if the directory already exists.
        """

    @abstractmethod
    def delete_directory(self, path: str):
        """
        Recursively deletes a directory at the given path.

        Args:
            path: The path of the directory to delete.
        """

    @abstractmethod
    def directory_exists(self, path: str) -> bool:
        """
        Checks if a directory exists at the given path.

        Args:
            path: The path to check.

        Returns:
            True if the directory exists, False otherwise.
        """
