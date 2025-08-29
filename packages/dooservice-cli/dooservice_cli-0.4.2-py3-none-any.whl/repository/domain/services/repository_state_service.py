from repository.domain.entities.repository_info import RepositoryInfo, RepositoryState
from repository.domain.repositories.git_repository import GitRepository


class RepositoryStateService:
    """
    Pure domain service to determine the current state of a repository.

    This service encapsulates the logic for checking repository state
    without depending on external infrastructure concerns.
    """

    def __init__(self, git_repository: GitRepository):
        """
        Initialize the repository state service.

        Args:
            git_repository: Git repository implementation for state checks.
        """
        self._git_repository = git_repository

    def get_repository_state(self, repo_info: RepositoryInfo) -> RepositoryState:
        """
        Get the current state of a repository.

        Args:
            repo_info: Repository information to check.

        Returns:
            RepositoryState with current status of the repository.
        """
        try:
            # Check if path exists
            exists_locally = repo_info.local_path.exists()

            if not exists_locally:
                return RepositoryState(
                    info=repo_info,
                    exists_locally=False,
                    is_valid_repository=False,
                )

            # Check if it's a valid Git repository
            is_valid_repository = self._git_repository.is_repository(
                str(repo_info.local_path)
            )

            if not is_valid_repository:
                return RepositoryState(
                    info=repo_info,
                    exists_locally=True,
                    is_valid_repository=False,
                )

            # Get repository state details
            current_commit = self._git_repository.get_current_commit(
                str(repo_info.local_path)
            )
            current_branch = self._git_repository.get_current_branch(
                str(repo_info.local_path)
            )
            has_uncommitted_changes = self._git_repository.has_uncommitted_changes(
                str(repo_info.local_path)
            )

            # Check if there are remote changes available
            remote_commit = self._get_remote_commit(repo_info)

            return RepositoryState(
                info=repo_info,
                current_commit=current_commit,
                current_branch=current_branch,
                has_uncommitted_changes=has_uncommitted_changes,
                remote_commit=remote_commit,
                exists_locally=True,
                is_valid_repository=True,
            )

        except (ValueError, OSError):
            # If any error occurs, assume repository is in invalid state
            return RepositoryState(
                info=repo_info,
                exists_locally=exists_locally
                if "exists_locally" in locals()
                else False,
                is_valid_repository=False,
            )

    def _get_remote_commit(self, repo_info: RepositoryInfo) -> str:
        """
        Get the latest commit from remote repository.

        Returns:
            Remote commit hash, or current commit if fetch fails.
        """
        try:
            return self._git_repository.get_remote_commit(
                str(repo_info.local_path), repo_info.branch
            )
        except (ValueError, OSError):
            # If we can't fetch remote, assume current commit is the latest
            try:
                return self._git_repository.get_current_commit(
                    str(repo_info.local_path)
                )
            except (ValueError, OSError):
                return ""
