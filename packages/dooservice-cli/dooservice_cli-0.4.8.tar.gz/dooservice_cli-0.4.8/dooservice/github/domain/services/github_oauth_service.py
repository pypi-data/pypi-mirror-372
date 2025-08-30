"""Service for handling GitHub OAuth authentication."""

from typing import Optional

from github.domain.entities.github_auth import GitHubAuth
from github.domain.repositories.github_auth_repository import (
    GitHubAPIRepository,
    GitHubAuthRepository,
)
from github.domain.services.github_config_service import GitHubConfigService
from shared.oauth.entities import OAuthAuth
from shared.oauth.providers.github_provider import GitHubOAuthClient


class GitHubOAuthService:
    """Service for managing GitHub OAuth authentication."""

    def __init__(
        self,
        auth_repository: GitHubAuthRepository,
        api_repository: GitHubAPIRepository,
        config_service: GitHubConfigService,
    ):
        self.auth_repository = auth_repository
        self.api_repository = api_repository
        self.config_service = config_service
        self._oauth_client: Optional[GitHubOAuthClient] = None

    def _get_oauth_client(self) -> GitHubOAuthClient:
        """Get or create OAuth client with current configuration."""
        if self._oauth_client is None:
            client_id = self.config_service.get_oauth_client_id()
            client_secret = self.config_service.get_oauth_client_secret()
            redirect_uri = self.config_service.get_oauth_redirect_uri()
            scopes = self.config_service.get_oauth_scopes()

            if not client_id or not client_secret:
                raise ValueError(
                    "GitHub OAuth client_id and client_secret not configured. "
                    "Please check your dooservice.yml file."
                )

            self._oauth_client = GitHubOAuthClient.create_from_config(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=scopes,
            )

        return self._oauth_client

    def initiate_oauth_flow(self) -> tuple[str, str]:
        """
        Initiate OAuth flow and return authorization URL and state.

        Returns:
            tuple: (authorization_url, state) for OAuth flow
        """
        oauth_client = self._get_oauth_client()
        return oauth_client.initiate_oauth_flow()

    def complete_oauth_flow(self, open_browser: bool = True) -> GitHubAuth:
        """
        Complete the full OAuth flow with temporary callback server.

        Args:
            open_browser: Whether to automatically open browser

        Returns:
            GitHubAuth: Authentication object with token and user info

        Raises:
            ValueError: If OAuth flow fails
        """
        oauth_client = self._get_oauth_client()
        oauth_auth = oauth_client.complete_oauth_flow(open_browser=open_browser)

        # Convert generic OAuth auth to GitHub auth
        github_auth = self._convert_to_github_auth(oauth_auth)

        # Save authentication
        self.auth_repository.save_auth(github_auth)

        return github_auth

    def open_browser_for_auth(self) -> tuple[str, str]:
        """
        Open browser for OAuth authentication (legacy method).

        Returns:
            tuple: (authorization_url, state)
        """
        return self.initiate_oauth_flow()

    def exchange_code_for_token(self, code: str) -> GitHubAuth:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub

        Returns:
            GitHubAuth: Authentication object with token and user info
        """
        oauth_client = self._get_oauth_client()
        oauth_auth = oauth_client.exchange_code_for_token(code)

        # Convert generic OAuth auth to GitHub auth
        github_auth = self._convert_to_github_auth(oauth_auth)

        # Save authentication
        self.auth_repository.save_auth(github_auth)

        return github_auth

    def _convert_to_github_auth(self, oauth_auth: OAuthAuth) -> GitHubAuth:
        """
        Convert generic OAuthAuth to GitHub-specific GitHubAuth.

        Args:
            oauth_auth: Generic OAuth authentication object

        Returns:
            GitHub-specific authentication object
        """
        # Get user information using existing API repository
        user = self.api_repository.get_user(oauth_auth.access_token)

        return GitHubAuth(
            access_token=oauth_auth.access_token, user=user, scopes=oauth_auth.scopes
        )

    def get_current_auth(self) -> Optional[GitHubAuth]:
        """Get current authentication if available and valid."""
        auth = self.auth_repository.load_auth()

        if not auth:
            return None

        if auth.is_expired:
            # Clean up expired auth
            self.auth_repository.delete_auth()
            return None

        return auth

    def logout(self) -> None:
        """Logout and clear authentication."""
        self.auth_repository.delete_auth()

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.get_current_auth() is not None
