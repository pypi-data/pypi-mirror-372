from repository.domain.entities.repository_info import (
    RepositoryInfo,
    RepositoryUpdateResult,
)
from repository.domain.services.repository_management_service import (
    RepositoryManagementService,
)


class UpdateRepository:
    """
    Use case for updating an existing repository to the latest version.

    This use case orchestrates the repository management service to
    pull latest changes from the remote repository.
    """

    def __init__(self, repository_management_service: RepositoryManagementService):
        """
        Initialize the update repository use case.

        Args:
            repository_management_service: Service for repository operations.
        """
        self._repository_service = repository_management_service

    def execute(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """
        Execute the update repository use case.

        Args:
            repo_info: Repository information.

        Returns:
            RepositoryUpdateResult with update details.
        """
        return self._repository_service.update_repository(repo_info)
