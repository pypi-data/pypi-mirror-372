"""Generic OAuth 2.0 implementation for various providers."""

from shared.oauth.entities import OAuthAuth, OAuthConfig, OAuthToken, OAuthUser
from shared.oauth.oauth_callback_server import OAuthCallbackServer
from shared.oauth.oauth_client import OAuthClient
from shared.oauth.providers.github_provider import GitHubOAuthClient
from shared.oauth.template_loader import TemplateLoader

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
