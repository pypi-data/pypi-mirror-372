from typing import List, Optional

from repository.domain.entities.repository_info import (
    RepositoryInfo,
    RepositoryUpdateResult,
)
from repository.domain.repositories.git_repository import GitRepository
from repository.domain.services.repository_state_service import RepositoryStateService


class RepositoryManagementService:
    """
    Pure domain service for managing repositories within instances.

    This service provides repository operations that are used by instance
    management without depending on CLI or configuration concerns.
    """

    def __init__(self, git_repository: GitRepository):
        """
        Initialize repository management service.

        Args:
            git_repository: Git repository implementation.
        """
        self._git_repository = git_repository
        self._state_service = RepositoryStateService(git_repository)

    def ensure_repository(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """
        Ensure a repository exists locally and is up to date.

        This method will clone the repository if it doesn't exist,
        or update it if it does exist but is out of sync.

        Args:
            repo_info: Repository information with all necessary details.

        Returns:
            RepositoryUpdateResult indicating what action was taken.
        """
        current_state = self._state_service.get_repository_state(repo_info)

        if current_state.needs_clone:
            return self._clone_repository(repo_info)

        if not current_state.is_synchronized:
            return self._update_repository(repo_info)

        # Repository is already synchronized
        return RepositoryUpdateResult(
            repository_info=repo_info,
            old_commit=current_state.current_commit,
            new_commit=current_state.current_commit,
            operation_performed="no_change",
            success=True,
        )

    def update_repository(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """
        Update an existing repository to the latest version.

        Args:
            repo_info: Repository information.

        Returns:
            RepositoryUpdateResult with update details.
        """
        return self._update_repository(repo_info)

    def ensure_multiple_repositories(
        self, repositories: List[RepositoryInfo]
    ) -> List[RepositoryUpdateResult]:
        """
        Ensure multiple repositories are available and up to date.

        Args:
            repositories: List of repository information.

        Returns:
            List of RepositoryUpdateResult for each repository.
        """
        results = []
        for repo_info in repositories:
            result = self.ensure_repository(repo_info)
            results.append(result)
        return results

    def check_repository_status(self, repo_info: RepositoryInfo) -> bool:
        """
        Check if a repository is properly synchronized.

        Args:
            repo_info: Repository information to check.

        Returns:
            True if repository is synchronized, False otherwise.
        """
        state = self._state_service.get_repository_state(repo_info)
        return state.is_synchronized

    def get_repository_commit(self, repo_info: RepositoryInfo) -> Optional[str]:
        """
        Get the current commit hash of a repository.

        Args:
            repo_info: Repository information.

        Returns:
            Current commit hash if repository exists, None otherwise.
        """
        if not repo_info.local_path.exists():
            return None

        if not self._git_repository.is_repository(str(repo_info.local_path)):
            return None

        try:
            return self._git_repository.get_current_commit(str(repo_info.local_path))
        except (ValueError, OSError):
            return None

    def _clone_repository(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """Clone a repository."""
        try:
            new_commit = self._git_repository.clone(
                repo_info.url,
                str(repo_info.local_path),
                repo_info.branch,
                repo_info.recursive_submodules,
            )

            return RepositoryUpdateResult(
                repository_info=repo_info,
                old_commit=None,
                new_commit=new_commit,
                operation_performed="clone",
                success=True,
            )
        except (ValueError, OSError, KeyError) as e:
            return RepositoryUpdateResult(
                repository_info=repo_info,
                old_commit=None,
                new_commit=None,
                operation_performed="clone",
                success=False,
                error_message=str(e),
            )

    def _update_repository(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """Update an existing repository."""
        try:
            # Get old commit before update
            old_commit = self._git_repository.get_current_commit(
                str(repo_info.local_path)
            )

            # Switch to correct branch if needed
            current_branch = self._git_repository.get_current_branch(
                str(repo_info.local_path)
            )
            if current_branch != repo_info.branch:
                self._git_repository.checkout(
                    str(repo_info.local_path), repo_info.branch
                )

            # Pull latest changes
            new_commit = self._git_repository.pull(
                str(repo_info.local_path), repo_info.branch
            )

            operation = "no_change" if old_commit == new_commit else "pull"

            return RepositoryUpdateResult(
                repository_info=repo_info,
                old_commit=old_commit,
                new_commit=new_commit,
                operation_performed=operation,
                success=True,
            )
        except (ValueError, OSError, KeyError) as e:
            return RepositoryUpdateResult(
                repository_info=repo_info,
                old_commit=None,
                new_commit=None,
                operation_performed="pull",
                success=False,
                error_message=str(e),
            )
