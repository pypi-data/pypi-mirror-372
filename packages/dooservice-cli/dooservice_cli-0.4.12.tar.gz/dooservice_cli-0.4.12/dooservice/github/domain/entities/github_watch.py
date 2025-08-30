"""GitHub watch entities for repository monitoring."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class WatchGitHubActionType(Enum):
    """Actions that can be triggered by a GitHub watch."""

    PULL = "pull"
    RESTART = "restart"
    PULL_RESTART = "pull+restart"
    BACKUP = "backup"
    SNAPSHOT = "snapshot"


class WatchGitHubType(Enum):
    """Types of GitHub watches."""

    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class GitHubWatchWebhook:
    """GitHub webhook information."""

    id: int
    name: str = "web"
    active: bool = True
    events: List[str] = field(default_factory=lambda: ["push"])
    config: dict = field(default_factory=dict)
    url: str = ""
    test_url: str = ""
    ping_url: str = ""
    deliveries_url: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateWatchGitHubWebhookRequest:
    """Request to create a GitHub webhook."""

    name: str = "web"
    active: bool = True
    events: List[str] = field(default_factory=lambda: ["push"])
    config: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for API request."""
        return {
            "name": self.name,
            "active": self.active,
            "events": self.events,
            "config": self.config,
        }


@dataclass
class WatchGitHubStatus:
    """Status of a GitHub watch including webhook state."""

    exists: bool
    webhook_id: Optional[int] = None
    webhook_url: Optional[str] = None
    active: bool = False
    last_delivery: Optional[datetime] = None
    secret_configured: bool = False
    events: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class RepositoryWatchGitHub:
    """GitHub repository watch configuration."""

    repository_name: str
    repository_url: str
    repository_owner: str
    repository_repo: str
    instance_name: str
    actions: List[WatchGitHubActionType]
    enabled: bool = True
    webhook_secret: Optional[str] = None
    branch: str = "main"
    watch_type: WatchGitHubType = WatchGitHubType.MANUAL

    @classmethod
    def from_config(
        cls, repo_name: str, repo_config: dict, instance_name: str, github_config: dict
    ) -> "RepositoryWatchGitHub":
        """Create from configuration dictionary."""
        repo_url = repo_config.get("url", "")
        owner, repo = cls._parse_github_url(repo_url)

        # Parse actions
        actions_str = github_config.get("default_action", "pull+restart")
        if isinstance(actions_str, str):
            actions = [WatchGitHubActionType(actions_str)]
        else:
            actions = [WatchGitHubActionType(a) for a in actions_str]

        return cls(
            repository_name=repo_name,
            repository_url=repo_url,
            repository_owner=owner,
            repository_repo=repo,
            instance_name=instance_name,
            actions=actions,
            enabled=True,
            webhook_secret=github_config.get("webhook_secret"),
            branch=repo_config.get("branch", "main"),
            watch_type=WatchGitHubType.AUTO
            if github_config.get("auto_watch", True)
            else WatchGitHubType.MANUAL,
        )

    @staticmethod
    def _parse_github_url(url: str) -> tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        if "github.com" in url:
            # Handle both https://github.com/owner/repo.git and
            # git@github.com:owner/repo.git
            if url.startswith("git@"):
                # git@github.com:owner/repo.git
                parts = url.split(":")[-1].replace(".git", "").split("/")
            else:
                # https://github.com/owner/repo.git
                parts = (
                    url.replace("https://github.com/", "")
                    .replace(".git", "")
                    .split("/")
                )

            if len(parts) >= 2:
                return parts[0], parts[1]

        return "", ""


@dataclass
class RepositoryWatchGitHubWithStatus:
    """Repository watch with current GitHub webhook status."""

    watch: RepositoryWatchGitHub
    status: WatchGitHubStatus

    @property
    def is_healthy(self) -> bool:
        """Check if watch is in a healthy state."""
        return self.status.exists and self.status.active and not self.status.error


@dataclass
class WatchGitHubSyncReport:
    """Report of synchronization operations."""

    created: List[RepositoryWatchGitHub] = field(default_factory=list)
    updated: List[RepositoryWatchGitHub] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)  # Repository names
    errors: List[tuple[str, str]] = field(
        default_factory=list
    )  # (repo_name, error_message)

    @property
    def has_changes(self) -> bool:
        """Check if any changes were made."""
        return bool(self.created or self.updated or self.deleted)

    @property
    def total_changes(self) -> int:
        """Get total number of changes."""
        return len(self.created) + len(self.updated) + len(self.deleted)
