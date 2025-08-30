"""GitHub configuration service for reading global GitHub settings."""

from typing import Optional

from core.domain.entities.github_config import (
    GitHubGlobalConfig,
    GitHubOAuthConfig,
)
from core.domain.services.config_service import ConfigService


class GitHubConfigService:
    """Service for managing GitHub configuration."""

    def __init__(self, config_service: ConfigService):
        """
        Initialize GitHub configuration service.

        Args:
            config_service: Core configuration service
        """
        self.config_service = config_service

    def get_github_config(self) -> Optional[GitHubGlobalConfig]:
        """
        Get GitHub global configuration.

        Returns:
            GitHub global configuration if available
        """
        try:
            dooservice_config = self.config_service.load_config()
            return dooservice_config.github
        except (ValueError, FileNotFoundError, OSError):
            return None

    def get_oauth_config(self) -> Optional[GitHubOAuthConfig]:
        """
        Get GitHub OAuth configuration.

        Returns:
            OAuth configuration if available
        """
        github_config = self.get_github_config()
        if github_config and github_config.oauth:
            return github_config.oauth
        return None

    def is_github_enabled(self) -> bool:
        """
        Check if GitHub integration is enabled.

        Returns:
            True if GitHub integration is enabled
        """
        github_config = self.get_github_config()
        return github_config.enabled if github_config else False

    def get_oauth_client_id(self) -> Optional[str]:
        """
        Get OAuth client ID from configuration.

        Returns:
            OAuth client ID if configured
        """
        oauth_config = self.get_oauth_config()
        return oauth_config.client_id if oauth_config else None

    def get_oauth_client_secret(self) -> Optional[str]:
        """
        Get OAuth client secret from configuration.

        Returns:
            OAuth client secret if configured
        """
        oauth_config = self.get_oauth_config()
        return oauth_config.client_secret if oauth_config else None

    def get_oauth_redirect_uri(self) -> str:
        """
        Get OAuth redirect URI from configuration.

        Returns:
            OAuth redirect URI (default if not configured)
        """
        oauth_config = self.get_oauth_config()
        return (
            oauth_config.redirect_uri
            if oauth_config
            else "http://localhost:8080/auth/callback"
        )

    def get_oauth_scopes(self) -> list[str]:
        """
        Get OAuth scopes from configuration.

        Returns:
            OAuth scopes (default if not configured)
        """
        oauth_config = self.get_oauth_config()
        return (
            oauth_config.scopes
            if oauth_config
            else ["repo", "read:user", "admin:public_key"]
        )

    def get_webhook_config(self) -> dict:
        """
        Get GitHub webhook configuration as dict.

        Returns:
            Webhook configuration dictionary
        """
        github_config = self.get_github_config()
        if github_config and github_config.webhook:
            webhook = github_config.webhook
            return {
                "host": webhook.default_host,
                "port": webhook.default_port,
                "default_port": webhook.default_port,
                "default_secret": webhook.default_secret,
            }
        return {
            "host": "localhost",
            "port": 8080,
            "default_port": 8080,
            "default_secret": None,
        }
