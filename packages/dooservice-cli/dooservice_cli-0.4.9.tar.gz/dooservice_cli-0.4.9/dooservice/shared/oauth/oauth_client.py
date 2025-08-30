"""Generic OAuth 2.0 client for multiple providers."""

import contextlib
import secrets
from typing import Any, Dict
from urllib.parse import urlencode, urlparse
import webbrowser

import requests

from shared.oauth.entities import OAuthAuth, OAuthConfig, OAuthToken, OAuthUser
from shared.oauth.oauth_callback_server import OAuthCallbackServer


class OAuthClient:
    """Generic OAuth 2.0 client that works with multiple providers."""

    def __init__(self, config: OAuthConfig):
        """
        Initialize OAuth client with provider configuration.

        Args:
            config: OAuth provider configuration
        """
        self.config = config

    def initiate_oauth_flow(self) -> tuple[str, str]:
        """
        Initiate OAuth flow and return authorization URL and state.

        Returns:
            tuple: (authorization_url, state) for OAuth flow
        """
        state = secrets.token_urlsafe(32)

        auth_params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
            "response_type": "code",
            **self.config.additional_params,
        }

        auth_url = f"{self.config.auth_url}?{urlencode(auth_params)}"
        return auth_url, state

    def complete_oauth_flow(self, open_browser: bool = True) -> OAuthAuth:
        """
        Complete the full OAuth flow with temporary callback server.

        Args:
            open_browser: Whether to automatically open browser

        Returns:
            OAuthAuth: Authentication object with token and user info

        Raises:
            ValueError: If OAuth flow fails
        """
        # Parse redirect URI to get port for callback server
        parsed_uri = urlparse(self.config.redirect_uri)
        callback_port = parsed_uri.port or 8080

        # Start callback server
        callback_server = OAuthCallbackServer(port=callback_port)

        auth_url, state = self.initiate_oauth_flow()

        # Open browser if requested
        if open_browser:
            # Use contextlib.suppress for browser opening errors
            with contextlib.suppress(OSError, ImportError, webbrowser.Error):
                webbrowser.open(auth_url)

        # Wait for callback
        code, result_state = callback_server.start(timeout=300)  # 5 minute timeout

        if not code:
            if result_state == "timeout":
                raise ValueError("OAuth flow timed out. Please try again.")
            if result_state.startswith("port_"):
                port = result_state.split("_")[1]
                raise ValueError(
                    f"Port {port} is already in use. Please stop any service "
                    "using that port and try again."
                )
            raise ValueError(f"OAuth flow failed: {result_state}")

        # Verify state parameter
        if result_state != state:
            raise ValueError("OAuth state mismatch. Possible CSRF attack.")

        # Exchange code for token
        return self.exchange_code_for_token(code)

    def exchange_code_for_token(self, code: str) -> OAuthAuth:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from provider

        Returns:
            OAuthAuth: Authentication object with token and user info
        """
        # Exchange code for access token
        token_data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        headers = {
            "Accept": "application/json",
            "User-Agent": f"DooService-CLI/1.0 ({self.config.provider_name})",
        }

        try:
            response = requests.post(
                self.config.token_url,
                data=token_data,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            token_response = response.json()

            if "error" in token_response:
                error_desc = token_response.get(
                    "error_description", token_response["error"]
                )
                raise ValueError(
                    f"{self.config.provider_name} OAuth error: {error_desc}"
                )

            access_token = token_response.get("access_token")
            if not access_token:
                raise ValueError(
                    f"No access token received from {self.config.provider_name}"
                )

            # Create token object
            token = OAuthToken(
                access_token=access_token,
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                refresh_token=token_response.get("refresh_token"),
                scopes=self._parse_token_scopes(token_response),
                raw_data=token_response,
            )

            # Get user information
            user = self._get_user_info(token.access_token)

            return OAuthAuth(provider=self.config.provider_name, token=token, user=user)

        except requests.RequestException as e:
            raise ValueError(f"Failed to exchange OAuth code: {e}") from e
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"OAuth token exchange failed: {e}") from e

    def _parse_token_scopes(self, token_response: Dict[str, Any]) -> list[str]:
        """
        Parse scopes from token response.

        Args:
            token_response: Token response from provider

        Returns:
            List of scopes
        """
        scope_str = token_response.get("scope", "")
        if scope_str:
            # Different providers use different separators (space, comma)
            if "," in scope_str:
                return [s.strip() for s in scope_str.split(",")]
            return scope_str.split()
        return self.config.scopes

    def _get_user_info(self, access_token: str) -> OAuthUser:
        """
        Get user information from provider.

        Args:
            access_token: Access token for API calls

        Returns:
            OAuthUser with user information
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": f"DooService-CLI/1.0 ({self.config.provider_name})",
        }

        try:
            response = requests.get(self.config.user_url, headers=headers, timeout=30)
            response.raise_for_status()

            user_data = response.json()

            return self._parse_user_data(user_data)

        except requests.RequestException as e:
            raise ValueError(
                f"Failed to get user info from {self.config.provider_name}: {e}"
            ) from e

    def _parse_user_data(self, user_data: Dict[str, Any]) -> OAuthUser:
        """
        Parse user data from provider response.

        This method can be overridden by provider-specific implementations.

        Args:
            user_data: Raw user data from provider

        Returns:
            Parsed OAuthUser object
        """
        # Generic parsing - providers should override this
        return OAuthUser(
            id=str(user_data.get("id", user_data.get("sub", ""))),
            username=user_data.get(
                "login",
                user_data.get("username", user_data.get("preferred_username", "")),
            ),
            email=user_data.get("email"),
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url", user_data.get("picture")),
            provider=self.config.provider_name,
            raw_data=user_data,
        )

    def refresh_token(self, refresh_token: str) -> OAuthToken:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New OAuthToken with refreshed access token
        """
        if not refresh_token:
            raise ValueError("No refresh token available")

        token_data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = {
            "Accept": "application/json",
            "User-Agent": f"DooService-CLI/1.0 ({self.config.provider_name})",
        }

        try:
            response = requests.post(
                self.config.token_url,
                data=token_data,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            token_response = response.json()

            if "error" in token_response:
                error_desc = token_response.get(
                    "error_description", token_response["error"]
                )
                raise ValueError(
                    f"{self.config.provider_name} token refresh error: {error_desc}"
                )

            access_token = token_response.get("access_token")
            if not access_token:
                raise ValueError(
                    f"No access token received from {self.config.provider_name}"
                )

            return OAuthToken(
                access_token=access_token,
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                refresh_token=token_response.get(
                    "refresh_token", refresh_token
                ),  # Keep old if not provided
                scopes=self._parse_token_scopes(token_response),
                raw_data=token_response,
            )

        except requests.RequestException as e:
            raise ValueError(f"Failed to refresh token: {e}") from e
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"Token refresh failed: {e}") from e
