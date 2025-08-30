"""Generic OAuth 2.0 implementation for various providers."""

from dooservice.shared.oauth.entities import (
    OAuthAuth,
    OAuthConfig,
    OAuthToken,
    OAuthUser,
)
from dooservice.shared.oauth.oauth_callback_server import OAuthCallbackServer
from dooservice.shared.oauth.oauth_client import OAuthClient
from dooservice.shared.oauth.providers.github_provider import GitHubOAuthClient
from dooservice.shared.oauth.template_loader import TemplateLoader

__all__ = [
    "OAuthAuth",
    "OAuthConfig",
    "OAuthToken",
    "OAuthUser",
    "OAuthClient",
    "OAuthCallbackServer",
    "GitHubOAuthClient",
    "TemplateLoader",
]
