"""Webhook domain entities and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class WebhookProvider(Enum):
    """Supported webhook providers."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class WebhookEventType(Enum):
    """Types of webhook events."""

    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE_REQUEST = "merge_request"
    TAG = "tag"


class ActionType(Enum):
    """Types of actions that can be triggered."""

    PULL = "pull"
    RESTART = "restart"
    PULL_RESTART = "pull+restart"
    BUILD = "build"
    DEPLOY = "deploy"


@dataclass
class WebhookPayload:
    """Generic webhook payload structure."""

    provider: WebhookProvider
    event_type: WebhookEventType
    repository_url: str
    repository_name: str
    branch: str
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    commit_author: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookAction:
    """Represents an action to be executed from a webhook."""

    instance_name: str
    action_type: ActionType
    repository_url: str
    branch: str
    triggered_by: WebhookPayload
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WebhookServerConfig:
    """Configuration for webhook server."""

    host: str = "localhost"
    port: int = 8080
    secret: Optional[str] = None
    auto_start: bool = False
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None


@dataclass
class ProviderWebhookConfig:
    """Provider-specific webhook configuration."""

    provider: WebhookProvider
    enabled: bool = True
    secret: Optional[str] = None
    verify_signature: bool = True
    endpoint_path: str = "/webhook"


@dataclass
class RepositoryWatchConfig:
    """Configuration for watching a specific repository."""

    repository_url: str
    instance_name: str
    branch: str = "main"
    actions: List[ActionType] = field(default_factory=lambda: [ActionType.PULL_RESTART])
    enabled: bool = True


@dataclass
class WebhookConfig:
    """Complete webhook system configuration."""

    enabled: bool = True
    server: WebhookServerConfig = field(default_factory=WebhookServerConfig)
    providers: List[ProviderWebhookConfig] = field(default_factory=list)
    repositories: List[RepositoryWatchConfig] = field(default_factory=list)
    auto_start: bool = False


class WebhookPayloadParser(ABC):
    """Abstract base class for parsing provider-specific webhook payloads."""

    @property
    @abstractmethod
    def provider(self) -> WebhookProvider:
        """Return the provider this parser handles."""

    @abstractmethod
    def parse(
        self, headers: Dict[str, str], payload: Dict[str, Any]
    ) -> Optional[WebhookPayload]:
        """
        Parse provider-specific webhook payload.

        Args:
            headers: HTTP headers from webhook request
            payload: Raw webhook payload data

        Returns:
            Parsed WebhookPayload or None if not supported
        """

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw payload bytes
            signature: Signature from headers
            secret: Webhook secret

        Returns:
            True if signature is valid
        """


@dataclass
class WebhookProcessingResult:
    """Result of processing a webhook event."""

    success: bool
    processed_actions: List[WebhookAction]
    error: Optional[str] = None
    execution_time_ms: float = 0.0
