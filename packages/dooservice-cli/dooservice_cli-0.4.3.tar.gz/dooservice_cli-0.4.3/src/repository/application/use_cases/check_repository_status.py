from repository.domain.entities.repository_info import RepositoryInfo
from repository.domain.services.repository_management_service import (
    RepositoryManagementService,
)


class CheckRepositoryStatus:
    """
    Use case for checking repository synchronization status.

    This use case orchestrates the repository management service to
    check if a repository is properly synchronized.
    """

    def __init__(self, repository_management_service: RepositoryManagementService):
        """
        Initialize the check repository status use case.

        Args:
            repository_management_service: Service for repository operations.
        """
        self._repository_service = repository_management_service

    def execute(self, repo_info: RepositoryInfo) -> bool:
        """
        Execute the check repository status use case.

        Args:
            repo_info: Repository information to check.

        Returns:
            True if repository is synchronized, False otherwise.
        """
        return self._repository_service.check_repository_status(repo_info)
