"""Repository interface for GitHub authentication."""

from abc import ABC, abstractmethod
from typing import List, Optional

from github.domain.entities.github_auth import (
    GitHubAuth,
    GitHubRepository,
    GitHubSSHKey,
    GitHubUser,
)
from github.domain.entities.github_watch import (
    CreateWatchGitHubWebhookRequest,
    GitHubWatchWebhook,
)


class GitHubAuthRepository(ABC):
    """Repository for managing GitHub authentication."""

    @abstractmethod
    def save_auth(self, auth: GitHubAuth) -> None:
        """Save GitHub authentication data."""

    @abstractmethod
    def load_auth(self) -> Optional[GitHubAuth]:
        """Load saved GitHub authentication data."""

    @abstractmethod
    def delete_auth(self) -> None:
        """Delete saved authentication data."""

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with GitHub."""


class GitHubAPIRepository(ABC):
    """Repository for GitHub API operations."""

    @abstractmethod
    def get_user(self, access_token: str) -> GitHubUser:
        """Get authenticated user information."""

    @abstractmethod
    def list_ssh_keys(self, access_token: str) -> List[GitHubSSHKey]:
        """List user's SSH keys."""

    @abstractmethod
    def add_ssh_key(self, access_token: str, title: str, key: str) -> GitHubSSHKey:
        """Add SSH key to user's account."""

    @abstractmethod
    def delete_ssh_key(self, access_token: str, key_id: int) -> None:
        """Delete SSH key from user's account."""

    @abstractmethod
    def get_repository(
        self,
        access_token: str,
        owner: str,
        repo: str,
    ) -> GitHubRepository:
        """Get repository information."""

    @abstractmethod
    def list_user_repositories(self, access_token: str) -> List[GitHubRepository]:
        """List user's repositories."""

    @abstractmethod
    def list_repository_webhooks(
        self,
        access_token: str,
        owner: str,
        repo: str,
    ) -> List[GitHubWatchWebhook]:
        """List webhooks for a repository."""

    @abstractmethod
    def create_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_request: CreateWatchGitHubWebhookRequest,
    ) -> GitHubWatchWebhook:
        """Create a webhook for a repository."""

    @abstractmethod
    def delete_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> None:
        """Delete a webhook from a repository."""

    @abstractmethod
    def get_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> GitHubWatchWebhook:
        """Get a specific webhook from a repository."""
