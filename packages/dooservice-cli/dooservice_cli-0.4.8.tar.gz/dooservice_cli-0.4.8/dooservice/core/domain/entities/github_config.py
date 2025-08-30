from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class GitHubWatcherConfig:
    """Configuration for a GitHub repository watcher."""

    instance: str  # Instance name that will be affected
    action: Union[str, List[str]] = (
        "pull+restart"  # Action(s) to trigger on push - single or multiple
    )
    enabled: bool = True  # Whether this watcher is enabled


@dataclass
class GitHubRepositoryConfig:
    """GitHub configuration for a repository."""

    auto_watch: bool = (
        True  # Automatically watch all instances that use this repository
    )
    default_action: Union[str, List[str]] = (
        "pull+restart"  # Default action(s) for auto-watch - single or multiple
    )
    watchers: List[GitHubWatcherConfig] = field(
        default_factory=list,
    )  # Specific watchers (optional)
    exclude_instances: List[str] = field(
        default_factory=list,
    )  # Instances to exclude from auto-watch


@dataclass
class GitHubOAuthConfig:
    """GitHub OAuth configuration."""

    client_id: str  # GitHub OAuth application client ID
    client_secret: str  # GitHub OAuth application client secret
    redirect_uri: str = "http://localhost:8080/auth/callback"  # OAuth redirect URI
    scopes: List[str] = field(
        default_factory=lambda: ["repo", "read:user", "admin:public_key"],
    )  # OAuth scopes


@dataclass
class GitHubWebhookConfig:
    """GitHub webhook listener configuration."""

    enabled: bool = True  # Enable webhook listener
    default_host: str = "localhost"  # Default host for webhook listener
    default_port: int = 8080  # Default port for webhook listener
    default_secret: Optional[str] = None  # Default webhook secret
    auto_start: bool = False  # Auto-start listener


@dataclass
class GitHubGlobalConfig:
    """Global GitHub integration configuration."""

    enabled: bool = True  # Enable GitHub integration globally
    oauth: Optional[GitHubOAuthConfig] = None  # OAuth configuration
    webhook: Optional[GitHubWebhookConfig] = None  # Webhook configuration
