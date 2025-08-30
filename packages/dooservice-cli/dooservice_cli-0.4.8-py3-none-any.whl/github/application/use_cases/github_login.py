"""Use case for GitHub login/authentication."""

from typing import Optional

from github.domain.entities.github_auth import GitHubAuth
from github.domain.services.github_oauth_service import GitHubOAuthService


class GitHubLoginUseCase:
    """Use case for authenticating with GitHub."""

    def __init__(self, oauth_service: GitHubOAuthService):
        self.oauth_service = oauth_service

    def execute(self, open_browser: bool = True) -> GitHubAuth:
        """
        Execute complete GitHub authentication flow.

        Args:
            open_browser: Whether to automatically open browser

        Returns:
            GitHubAuth: Authentication object after successful login
        """
        return self.oauth_service.complete_oauth_flow(open_browser)

    def execute_legacy(self, open_browser: bool = True) -> tuple[str, str]:
        """
        Start GitHub authentication flow (legacy method).

        Args:
            open_browser: Whether to automatically open browser

        Returns:
            tuple: (authorization_url, state) for OAuth flow
        """
        if open_browser:
            return self.oauth_service.open_browser_for_auth()
        return self.oauth_service.initiate_oauth_flow()

    def complete_auth(self, code: str, state: str) -> GitHubAuth:
        """
        Complete authentication with authorization code (legacy method).

        Args:
            code: Authorization code from GitHub
            state: State parameter for verification

        Returns:
            GitHubAuth: Authentication object
        """
        return self.oauth_service.exchange_code_for_token(code)

    def get_current_auth(self) -> Optional[GitHubAuth]:
        """Get current authentication status."""
        return self.oauth_service.get_current_auth()

    def logout(self) -> None:
        """Logout from GitHub."""
        self.oauth_service.logout()

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.oauth_service.is_authenticated()
