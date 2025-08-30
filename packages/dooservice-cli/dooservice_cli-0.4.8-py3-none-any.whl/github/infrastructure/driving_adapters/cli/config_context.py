"""Centralized configuration context for GitHub CLI commands."""

from pathlib import Path

import click

from core.domain.services.config_service import ConfigService
from github.application.use_cases.github_login import GitHubLoginUseCase
from github.application.use_cases.manage_ssh_keys import ManageSSHKeysUseCase
from github.domain.services.github_config_service import GitHubConfigService
from github.domain.services.github_oauth_service import GitHubOAuthService
from github.infrastructure.driven_adapters.filesystem_auth_repository import (
    FilesystemGitHubAuthRepository,
)
from github.infrastructure.driven_adapters.github_api_repository import (
    HTTPGitHubAPIRepository,
)


class GitHubConfigContext:
    """Centralized configuration context for GitHub CLI commands."""

    def __init__(self, config_file: str = "dooservice.yml"):
        """Initialize config context with configuration file."""
        self.config_file = Path(config_file)
        self._dooservice_config = None

        # Initialize core services
        self._config_service = ConfigService()
        self._github_config_service = GitHubConfigService(self._config_service)

        # Initialize repositories
        self._auth_repo = FilesystemGitHubAuthRepository()
        self._api_repo = HTTPGitHubAPIRepository()

        # Initialize domain services
        self._oauth_service = GitHubOAuthService(
            self._auth_repo, self._api_repo, self._github_config_service
        )

        # Initialize use cases
        self._login_use_case = GitHubLoginUseCase(self._oauth_service)
        self._ssh_keys_use_case = ManageSSHKeysUseCase(
            self._oauth_service,
            self._api_repo,
        )

    @property
    def github_config_service(self) -> GitHubConfigService:
        """Get GitHub configuration service."""
        return self._github_config_service

    @property
    def login_use_case(self) -> GitHubLoginUseCase:
        """Get GitHub login use case."""
        return self._login_use_case

    @property
    def ssh_keys_use_case(self) -> ManageSSHKeysUseCase:
        """Get SSH keys management use case."""
        return self._ssh_keys_use_case

    def is_github_enabled(self) -> bool:
        """Check if GitHub integration is enabled."""
        return self._github_config_service.is_github_enabled()

    def get_oauth_redirect_uri(self) -> str:
        """Get OAuth redirect URI from configuration."""
        return self._github_config_service.get_oauth_redirect_uri()


# Decorators for GitHub CLI commands
def github_config_context(f):
    """Decorator to inject config context into GitHub CLI commands."""

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        config_file = ctx.params.get("config", "dooservice.yml")
        ctx.obj = GitHubConfigContext(config_file)
        return f(*args, **kwargs)

    return wrapper


# Standard config option decorator
def config_option():
    """Standard --config option decorator for GitHub CLI commands."""
    return click.option(
        "--config",
        "-c",
        "config",
        type=click.Path(exists=True),
        default="dooservice.yml",
        help="Path to dooservice.yml configuration file",
    )
