"""Use case for listing GitHub repository watches with status."""

from typing import List

from github.domain.entities.github_watch import RepositoryWatchGitHubWithStatus
from github.domain.repositories.github_auth_repository import GitHubAuthRepository
from github.domain.services.watch_github_management_service import (
    WatchGitHubManagementService,
)
from github.domain.services.watch_github_webhook_sync_service import (
    WatchGitHubWebhookSyncService,
)


class ListRepositoryWatchGitHubUseCase:
    """Use case for listing repository watches with their webhook status."""

    def __init__(
        self,
        watch_management_service: WatchGitHubManagementService,
        webhook_sync_service: WatchGitHubWebhookSyncService,
        auth_repository: GitHubAuthRepository,
        webhook_server_url: str,
    ):
        """Initialize the use case."""
        self.watch_management_service = watch_management_service
        self.webhook_sync_service = webhook_sync_service
        self.auth_repository = auth_repository
        self.webhook_server_url = webhook_server_url

    def execute(self) -> List[RepositoryWatchGitHubWithStatus]:
        """Execute the use case."""
        # Get all configured watches
        configured_watches = self.watch_management_service.get_configured_watches()

        if not configured_watches:
            return []

        # Get GitHub authentication
        auth = self.auth_repository.load_auth()
        if not auth:
            # Return watches with error status if not authenticated
            return [
                RepositoryWatchGitHubWithStatus(
                    watch=watch,
                    status=self._create_error_status("Not authenticated with GitHub"),
                )
                for watch in configured_watches
            ]

        # Get webhook status for each watch
        results = []
        for watch in configured_watches:
            status = self.webhook_sync_service.get_webhook_status(
                auth, watch, self.webhook_server_url
            )
            results.append(RepositoryWatchGitHubWithStatus(watch=watch, status=status))

        return results

    def _create_error_status(self, error_message: str):
        """Create a status object indicating an error."""
        from github.domain.entities.github_watch import WatchGitHubStatus

        return WatchGitHubStatus(exists=False, error=error_message)
