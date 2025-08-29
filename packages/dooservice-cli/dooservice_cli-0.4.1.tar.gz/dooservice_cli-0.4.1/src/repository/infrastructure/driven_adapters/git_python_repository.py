import os
from typing import Optional

import git

from repository.domain.repositories.git_repository import GitRepository
from shared.errors.git_operation_error import GitOperationError
from shared.errors.repository_not_found_error import RepositoryNotFoundError


class GitPythonRepository(GitRepository):
    """
    An implementation of the GitRepository interface using the GitPython library.

    Provides Git operations like cloning, pulling, and inspecting repositories
    with proper error handling and domain-specific exceptions.
    """

    def clone(
        self, url: str, path: str, branch: str = "main", recursive: bool = False
    ) -> str:
        """
        Clones a Git repository to a specified path.

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
        if os.path.exists(path):
            if self.is_repository(path):
                return self.get_current_commit(path)
            raise GitOperationError(
                f"Path '{path}' exists but is not a Git repository", "clone"
            )

        try:
            repo = git.Repo.clone_from(
                url,
                to_path=path,
                branch=branch,
            )

            if recursive:
                self.sync_submodules(path)

            return repo.head.commit.hexsha
        except git.exc.GitCommandError as e:
            raise GitOperationError(
                f"Failed to clone repository from '{url}': {e.stderr}", "clone"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Unexpected error during clone: {str(e)}", "clone"
            ) from e

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            return repo.active_branch.name
        except git.exc.InvalidGitRepositoryError as e:
            raise GitOperationError(
                f"'{path}' is not a valid Git repository", "get_current_branch"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Failed to get current branch: {str(e)}", "get_current_branch"
            ) from e

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            repo.git.checkout(branch)
        except git.exc.GitCommandError as e:
            raise GitOperationError(
                f"Failed to checkout branch '{branch}': {e.stderr}", "checkout"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Unexpected error during checkout: {str(e)}", "checkout"
            ) from e

    def sync_submodules(self, path: str) -> None:
        """
        Initializes and updates all submodules in the repository.

        Args:
            path: The local path to the repository.

        Raises:
            RepositoryNotFoundError: If the repository doesn't exist.
            GitOperationError: If submodule sync fails.
        """
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            if repo.submodules:
                repo.submodule_update(init=True, recursive=True)
        except git.exc.GitCommandError as e:
            raise GitOperationError(
                f"Failed to sync submodules: {e.stderr}", "sync_submodules"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Unexpected error during submodule sync: {str(e)}", "sync_submodules"
            ) from e

    def is_repository(self, path: str) -> bool:
        """
        Checks if the given path is a valid Git repository.

        Args:
            path: The path to check.

        Returns:
            True if the path is a valid Git repository, False otherwise.
        """
        try:
            git.Repo(path)
            return True
        except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
            return False

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            return repo.is_dirty(untracked_files=True)
        except git.exc.InvalidGitRepositoryError as e:
            raise GitOperationError(
                f"'{path}' is not a valid Git repository", "has_uncommitted_changes"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Failed to check repository status: {str(e)}",
                "has_uncommitted_changes",
            ) from e

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)

            # Switch to branch if specified
            if branch and repo.active_branch.name != branch:
                self.checkout(path, branch)

            # Get current branch if not specified
            current_branch = branch or repo.active_branch.name

            # First, fetch to get latest remote information
            origin = repo.remotes.origin
            origin.fetch()

            # Pull the specific branch
            origin.pull(current_branch)

            # Update submodules if they exist
            if repo.submodules:
                self.sync_submodules(path)

            return repo.head.commit.hexsha
        except git.exc.GitCommandError as e:
            raise GitOperationError(
                f"Failed to pull repository at '{path}': {e.stderr}", "pull"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Unexpected error during pull: {str(e)}", "pull"
            ) from e

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            return repo.head.commit.hexsha
        except git.exc.InvalidGitRepositoryError as e:
            raise GitOperationError(
                f"'{path}' is not a valid Git repository", "get_current_commit"
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            raise GitOperationError(
                f"Failed to get current commit: {str(e)}", "get_current_commit"
            ) from e

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
        self._validate_repo_path(path)

        try:
            repo = git.Repo(path)
            origin = repo.remotes.origin
            origin.fetch()

            # Get remote commit hash for the target branch
            remote_branch = f"origin/{branch}"
            if remote_branch in [ref.name for ref in repo.refs]:
                return repo.refs[remote_branch].commit.hexsha
            # Fallback to current commit if remote branch not found
            return self.get_current_commit(path)
        except git.exc.GitCommandError as e:
            raise GitOperationError(
                f"Failed to get remote commit for branch '{branch}': {e.stderr}",
                "get_remote_commit",
            ) from e
        except (ValueError, OSError, git.GitError) as e:
            # If we can't fetch, fallback to current commit
            try:
                return self.get_current_commit(path)
            except (ValueError, OSError, git.GitError):
                raise GitOperationError(
                    f"Failed to get remote commit: {str(e)}", "get_remote_commit"
                ) from e

    def _validate_repo_path(self, path: str) -> None:
        """Validates that the path exists and is a directory."""
        if not os.path.exists(path):
            raise RepositoryNotFoundError(f"Repository path does not exist: {path}")
        if not os.path.isdir(path):
            raise GitOperationError(f"Path '{path}' is not a directory", "validation")
        if not self.is_repository(path):
            raise GitOperationError(
                f"Path '{path}' is not a Git repository", "validation"
            )
