from repository.domain.entities.repository_info import (
    RepositoryInfo,
    RepositoryUpdateResult,
)
from repository.domain.services.repository_management_service import (
    RepositoryManagementService,
)


class EnsureRepository:
    """
    Use case for ensuring a repository exists locally and is up to date.

    This use case orchestrates the repository management service to
    clone or update a repository as needed.
    """

    def __init__(self, repository_management_service: RepositoryManagementService):
        """
        Initialize the ensure repository use case.

        Args:
            repository_management_service: Service for repository operations.
        """
        self._repository_service = repository_management_service

    def execute(self, repo_info: RepositoryInfo) -> RepositoryUpdateResult:
        """
        Execute the ensure repository use case.

        Args:
            repo_info: Repository information with all necessary details.

        Returns:
            RepositoryUpdateResult indicating what action was taken.
        """
        return self._repository_service.ensure_repository(repo_info)
