from abc import ABC, abstractmethod
from typing import Optional


class GitRepository(ABC):
    """An interface for a repository that handles Git operations."""

    @abstractmethod
    def clone(
        self, url: str, path: str, branch: str = "main", recursive: bool = False
    ) -> str:
        """
        Clones a Git repository from a URL to a specified path.

        Args:
            url: The repository URL to clone from.
            path: The destination path for the clone.
            branch: The branch to clone (default: "main").
            recursive: Whether to clone submodules recursively.

        Returns:
            The commit hash of the cloned repository's HEAD.

        Raises:
            GitOperationError: If the clone operation fails.
        """

    @abstractmethod
    def pull(self, path: str, branch: Optional[str] = None) -> str:
        """
        Pulls the latest changes from the remote repository.

        Args:
            path: The local path to the repository.
            branch: Optional specific branch to pull from.

        Returns:
            The new commit hash after pull.

        Raises:
            GitOperationError: If the pull operation fails.
            RepositoryNotFoundError: If the repository doesn't exist.
        """

    @abstractmethod
    def get_current_commit(self, path: str) -> str:
        """
        Gets the current commit hash of the repository's HEAD.

        Args:
            path: The local path to the repository.

        Returns:
            The current commit hash as a string.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If unable to retrieve commit hash.
        """

    @abstractmethod
    def get_current_branch(self, path: str) -> str:
        """
        Gets the current branch name of the repository.

        Args:
            path: The local path to the repository.

        Returns:
            The current branch name.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If unable to retrieve branch name.
        """

    @abstractmethod
    def checkout(self, path: str, branch: str) -> None:
        """
        Checks out a specific branch in the repository.

        Args:
            path: The local path to the repository.
            branch: The branch name to check out.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If the checkout operation fails.
        """

    @abstractmethod
    def sync_submodules(self, path: str) -> None:
        """
        Initializes and updates all submodules in the repository.

        Args:
            path: The local path to the repository.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If submodule sync fails.
        """

    @abstractmethod
    def is_repository(self, path: str) -> bool:
        """
        Checks if the given path is a valid Git repository.

        Args:
            path: The path to check.

        Returns:
            True if the path is a valid Git repository, False otherwise.
        """

    @abstractmethod
    def has_uncommitted_changes(self, path: str) -> bool:
        """
        Checks if the repository has uncommitted changes.

        Args:
            path: The local path to the repository.

        Returns:
            True if there are uncommitted changes, False otherwise.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If unable to check status.
        """

    @abstractmethod
    def get_remote_commit(self, path: str, branch: str) -> str:
        """
        Gets the latest commit hash from the remote repository for a specific branch.

        Args:
            path: The local path to the repository.
            branch: The branch name to check.

        Returns:
            The remote commit hash as a string.

        Raises:
            GitOperationError: If unable to fetch or retrieve remote commit.
        """
