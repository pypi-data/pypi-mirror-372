"""GitHub OAuth provider implementation."""

from typing import Any, Dict

from shared.oauth.entities import OAuthConfig, OAuthUser
from shared.oauth.oauth_client import OAuthClient


class GitHubOAuthClient(OAuthClient):
    """GitHub-specific OAuth client."""

    @classmethod
    def create_from_config(
        cls,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/auth/callback",
        scopes: list[str] = None,
    ) -> "GitHubOAuthClient":
        """
        Create GitHub OAuth client from configuration parameters.

        Args:
            client_id: GitHub OAuth app client ID
            client_secret: GitHub OAuth app client secret
            redirect_uri: OAuth redirect URI
            scopes: List of GitHub scopes to request

        Returns:
            Configured GitHubOAuthClient instance
        """
        if scopes is None:
            scopes = ["repo", "read:user", "admin:public_key"]

        config = OAuthConfig(
            provider_name="GitHub",
            client_id=client_id,
            client_secret=client_secret,
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",  # noqa: S106
            user_url="https://api.github.com/user",
            redirect_uri=redirect_uri,
            scopes=scopes,
            additional_params={"allow_signup": "false"},  # GitHub-specific parameter
        )

        return cls(config)

    def _parse_user_data(self, user_data: Dict[str, Any]) -> OAuthUser:
        """
        Parse GitHub user data from API response.

        Args:
            user_data: Raw user data from GitHub API

        Returns:
            Parsed OAuthUser object with GitHub-specific fields
        """
        return OAuthUser(
            id=str(user_data.get("id", "")),
            username=user_data.get("login", ""),
            email=user_data.get("email"),
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            provider="GitHub",
            raw_data=user_data,
        )
