"""Use case for synchronizing GitHub repository webhooks."""

from typing import Optional

from github.domain.entities.github_watch import WatchGitHubSyncReport
from github.domain.repositories.github_auth_repository import GitHubAuthRepository
from github.domain.services.watch_github_management_service import (
    WatchGitHubManagementService,
)
from github.domain.services.watch_github_webhook_sync_service import (
    WatchGitHubWebhookSyncService,
)


class SyncRepositoryWatchGitHubUseCase:
    """Use case for synchronizing GitHub webhooks with configured watches."""

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

    def execute(
        self,
        dry_run: bool = False,
        force: bool = False,
        webhook_secret: Optional[str] = None,
    ) -> WatchGitHubSyncReport:
        """Execute the synchronization."""
        report = WatchGitHubSyncReport()

        # Check authentication
        auth = self.auth_repository.load_auth()
        if not auth:
            report.errors.append(("authentication", "Not authenticated with GitHub"))
            return report

        # Get all configured watches
        configured_watches = self.watch_management_service.get_configured_watches()
        if not configured_watches:
            return report

        # Sync each watch
        for watch in configured_watches:
            try:
                # Get current webhook status
                current_status = self.webhook_sync_service.get_webhook_status(
                    auth, watch, self.webhook_server_url
                )

                # Determine what action to take
                action_needed = None

                if not watch.enabled and current_status.exists:
                    action_needed = "delete"
                elif watch.enabled and not current_status.exists:
                    action_needed = "create"
                elif watch.enabled and current_status.exists:
                    # Check if update needed
                    needs_update = False

                    if not current_status.active:
                        needs_update = True

                    if webhook_secret:
                        has_secret = bool(webhook_secret)
                        if has_secret != current_status.secret_configured:
                            needs_update = True

                    if needs_update or force:
                        action_needed = "update"

                # Perform the action (unless dry run)
                if action_needed and not dry_run:
                    if action_needed in ["create", "update"]:
                        result_status = self.webhook_sync_service.sync_webhook(
                            auth, watch, self.webhook_server_url, webhook_secret
                        )

                        if result_status.exists and not result_status.error:
                            if action_needed == "create":
                                report.created.append(watch)
                            else:
                                report.updated.append(watch)
                        else:
                            error_msg = (
                                result_status.error or "Unknown error during sync"
                            )
                            report.errors.append((watch.repository_name, error_msg))

                    elif action_needed == "delete" and current_status.webhook_id:
                        success = self.webhook_sync_service.delete_webhook(
                            auth, watch, current_status.webhook_id
                        )

                        if success:
                            report.deleted.append(watch.repository_name)
                        else:
                            report.errors.append(
                                (watch.repository_name, "Failed to delete webhook")
                            )

                # Track what would be done in dry run mode
                elif action_needed and dry_run:
                    if action_needed in ["create", "update"]:
                        if action_needed == "create":
                            report.created.append(watch)
                        else:
                            report.updated.append(watch)
                    elif action_needed == "delete":
                        report.deleted.append(watch.repository_name)

            except (ValueError, RuntimeError, OSError) as e:
                report.errors.append((watch.repository_name, str(e)))

        # Cleanup orphaned webhooks
        try:
            # Get all repositories (including disabled ones) for comprehensive cleanup
            all_known_repos = self.watch_management_service.get_all_known_repositories()
            orphaned = self.webhook_sync_service.cleanup_orphaned_webhooks(
                auth,
                configured_watches,
                all_known_repos,
                self.webhook_server_url,
                dry_run=dry_run,
            )
            for orphaned_repo in orphaned:
                if orphaned_repo not in report.deleted:
                    report.deleted.append(orphaned_repo)
        except (ValueError, RuntimeError, OSError) as e:
            report.errors.append(("cleanup", f"Error during cleanup: {e}"))

        return report
