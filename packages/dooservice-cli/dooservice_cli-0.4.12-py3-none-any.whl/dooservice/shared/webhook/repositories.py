"""Repository interfaces for webhook system."""

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import RepositoryWatchConfig, WebhookAction, WebhookConfig


class WebhookConfigRepository(ABC):
    """Repository interface for webhook configuration."""

    @abstractmethod
    def get_webhook_config(self) -> Optional[WebhookConfig]:
        """Get the current webhook configuration."""

    @abstractmethod
    def update_webhook_config(self, config: WebhookConfig) -> None:
        """Update webhook configuration."""

    @abstractmethod
    def get_repository_watches(self) -> List[RepositoryWatchConfig]:
        """Get all repository watch configurations."""

    @abstractmethod
    def get_watches_for_repository(
        self, repository_url: str
    ) -> List[RepositoryWatchConfig]:
        """Get watch configurations for a specific repository."""


class WebhookActionRepository(ABC):
    """Repository interface for webhook actions."""

    @abstractmethod
    def save_action(self, action: WebhookAction) -> None:
        """Save a webhook action for execution."""

    @abstractmethod
    def get_pending_actions(self) -> List[WebhookAction]:
        """Get all pending webhook actions."""

    @abstractmethod
    def mark_action_completed(self, action: WebhookAction) -> None:
        """Mark a webhook action as completed."""

    @abstractmethod
    def mark_action_failed(self, action: WebhookAction, error: str) -> None:
        """Mark a webhook action as failed with error."""


class InstanceRepository(ABC):
    """Repository interface for instance operations."""

    @abstractmethod
    def pull_repository(self, instance_name: str, repository_url: str) -> None:
        """Pull latest changes for instance repository."""

    @abstractmethod
    def restart_instance(self, instance_name: str) -> None:
        """Restart the specified instance."""

    @abstractmethod
    def instance_exists(self, instance_name: str) -> bool:
        """Check if instance exists."""

    @abstractmethod
    def get_instance_repository_url(self, instance_name: str) -> Optional[str]:
        """Get the repository URL for an instance."""
