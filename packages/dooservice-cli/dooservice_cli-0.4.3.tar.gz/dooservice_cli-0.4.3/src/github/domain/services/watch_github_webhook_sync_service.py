"""GitHub webhook synchronization service."""

import logging
from typing import List, Optional

from github.domain.entities.github_auth import GitHubAuth
from github.domain.entities.github_watch import (
    CreateWatchGitHubWebhookRequest,
    RepositoryWatchGitHub,
    WatchGitHubStatus,
)
from github.domain.repositories.github_auth_repository import GitHubAPIRepository


class WatchGitHubWebhookSyncService:
    """Service for synchronizing GitHub webhooks with configured watches."""

    def __init__(self, github_api_repository: GitHubAPIRepository):
        """Initialize the service."""
        self.github_api = github_api_repository
        self.logger = logging.getLogger(__name__)

    def get_webhook_status(
        self, auth: GitHubAuth, watch: RepositoryWatchGitHub, webhook_url: str
    ) -> WatchGitHubStatus:
        """Get the current status of a webhook for a repository watch."""
        try:
            webhooks = self.github_api.list_repository_webhooks(
                auth.access_token, watch.repository_owner, watch.repository_repo
            )

            # Find webhook that matches our URL
            for webhook in webhooks:
                webhook_config_url = webhook.config.get("url", "")
                if webhook_config_url == webhook_url:
                    return WatchGitHubStatus(
                        exists=True,
                        webhook_id=webhook.id,
                        webhook_url=webhook_config_url,
                        active=webhook.active,
                        last_delivery=webhook.updated_at,
                        secret_configured=bool(webhook.config.get("secret")),
                        events=webhook.events,
                    )

            # No matching webhook found
            return WatchGitHubStatus(exists=False)

        except (ValueError, KeyError) as e:
            self.logger.error(
                "Error getting webhook status for %s: %s", watch.repository_name, e
            )
            return WatchGitHubStatus(exists=False, error=str(e))

    def create_webhook(
        self,
        auth: GitHubAuth,
        watch: RepositoryWatchGitHub,
        webhook_url: str,
        webhook_secret: Optional[str] = None,
    ) -> WatchGitHubStatus:
        """Create a webhook for a repository watch."""
        try:
            # Prepare webhook configuration
            config = {
                "url": webhook_url,
                "content_type": "json",
            }

            if webhook_secret:
                config["secret"] = webhook_secret

            # Create webhook request
            webhook_request = CreateWatchGitHubWebhookRequest(
                name="web",
                active=True,
                events=["push"],  # We mainly care about push events
                config=config,
            )

            # Create webhook via GitHub API
            webhook = self.github_api.create_repository_webhook(
                auth.access_token,
                watch.repository_owner,
                watch.repository_repo,
                webhook_request,
            )

            return WatchGitHubStatus(
                exists=True,
                webhook_id=webhook.id,
                webhook_url=webhook.config.get("url", ""),
                active=webhook.active,
                last_delivery=webhook.created_at,
                secret_configured=bool(webhook.config.get("secret")),
                events=webhook.events,
            )

        except (ValueError, KeyError) as e:
            self.logger.error(
                "Error creating webhook for %s: %s", watch.repository_name, e
            )
            return WatchGitHubStatus(exists=False, error=str(e))

    def delete_webhook(
        self,
        auth: GitHubAuth,
        watch: RepositoryWatchGitHub,
        webhook_id: int,
    ) -> bool:
        """Delete a webhook from a repository."""
        try:
            self.github_api.delete_repository_webhook(
                auth.access_token,
                watch.repository_owner,
                watch.repository_repo,
                webhook_id,
            )
            return True

        except (ValueError, KeyError) as e:
            self.logger.error(
                "Error deleting webhook for %s: %s", watch.repository_name, e
            )
            return False

    def sync_webhook(
        self,
        auth: GitHubAuth,
        watch: RepositoryWatchGitHub,
        webhook_url: str,
        webhook_secret: Optional[str] = None,
    ) -> WatchGitHubStatus:
        """Synchronize a single webhook - create if missing, update if needed."""
        current_status = self.get_webhook_status(auth, watch, webhook_url)

        if not watch.enabled:
            # Watch is disabled - remove webhook if it exists
            if current_status.exists and current_status.webhook_id:
                if self.delete_webhook(auth, watch, current_status.webhook_id):
                    return WatchGitHubStatus(exists=False)
                return current_status  # Keep current status if deletion failed
            return WatchGitHubStatus(exists=False)

        if not current_status.exists:
            # Webhook doesn't exist - create it
            return self.create_webhook(auth, watch, webhook_url, webhook_secret)

        # Webhook exists - check if it needs updating
        needs_update = False
        if not current_status.active:
            needs_update = True

        # Check if secret configuration changed
        has_secret = bool(webhook_secret)
        if has_secret != current_status.secret_configured:
            needs_update = True

        if (
            needs_update
            and current_status.webhook_id
            and self.delete_webhook(auth, watch, current_status.webhook_id)
        ):
            return self.create_webhook(auth, watch, webhook_url, webhook_secret)

        return current_status

    def cleanup_orphaned_webhooks(
        self,
        auth: GitHubAuth,
        watches: List[RepositoryWatchGitHub],
        known_repos: List[str],
        webhook_url: str,
        dry_run: bool = False,
    ) -> List[str]:
        """Find and remove webhooks not associated with any configured watch."""
        orphaned = []

        # Group watches by repository
        repo_watches = {}
        for watch in watches:
            repo_key = f"{watch.repository_owner}/{watch.repository_repo}"
            if repo_key not in repo_watches:
                repo_watches[repo_key] = []
            repo_watches[repo_key].append(watch)

        # Use all known repositories to check for orphaned webhooks
        for repo_key in known_repos:
            owner, repo = repo_key.split("/")

            try:
                # Get all webhooks for this repository
                webhooks = self.github_api.list_repository_webhooks(
                    auth.access_token, owner, repo
                )

                for webhook in webhooks:
                    webhook_config_url = webhook.config.get("url", "")

                    # Check if this webhook matches our webhook URL but has no
                    # corresponding watch
                    if webhook_config_url == webhook_url:
                        # This is our webhook, but check if there's a configured
                        # watch for it
                        repo_watch_list = repo_watches.get(repo_key, [])
                        has_watch = any(w.enabled for w in repo_watch_list)

                        if not has_watch:
                            # This webhook is orphaned
                            if dry_run:
                                # Just track it for reporting
                                orphaned.append(f"{owner}/{repo}")
                            # Actually delete it
                            elif self.delete_webhook_by_id(
                                auth, owner, repo, webhook.id
                            ):
                                orphaned.append(f"{owner}/{repo}")

            except (ValueError, KeyError) as e:
                self.logger.error(
                    "Error checking orphaned webhooks for %s: %s", repo_key, e
                )

        return orphaned

    def delete_webhook_by_id(
        self, auth: GitHubAuth, owner: str, repo: str, webhook_id: int
    ) -> bool:
        """Delete a webhook by ID."""
        try:
            self.github_api.delete_repository_webhook(
                auth.access_token, owner, repo, webhook_id
            )
            return True
        except (ValueError, KeyError) as e:
            self.logger.error(
                "Error deleting webhook %s from %s/%s: %s", webhook_id, owner, repo, e
            )
            return False

    def validate_webhook_connectivity(self, webhook_url: str) -> bool:
        """Validate that webhook URL is accessible (basic connectivity check)."""
        try:
            # This is a simple check - in a real implementation, you might want to
            # make an HTTP request to check if the webhook server is running
            import urllib.parse

            parsed = urllib.parse.urlparse(webhook_url)
            return bool(parsed.scheme and parsed.netloc)
        except (ValueError, TypeError):
            return False
