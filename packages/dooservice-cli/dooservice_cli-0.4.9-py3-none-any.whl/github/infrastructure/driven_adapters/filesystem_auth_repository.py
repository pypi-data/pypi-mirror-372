"""Filesystem-based implementation of GitHub authentication repository."""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Optional

from github.domain.entities.github_auth import GitHubAuth, GitHubUser
from github.domain.repositories.github_auth_repository import GitHubAuthRepository


class FilesystemGitHubAuthRepository(GitHubAuthRepository):
    """Filesystem-based GitHub authentication repository."""

    def __init__(self, config_dir: str = None):
        """
        Initialize the repository.

        Args:
            config_dir: Directory to store auth data (defaults to ~/.dooservice)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.dooservice")

        self.config_dir = Path(config_dir)
        self.auth_file = self.config_dir / "github_auth.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_auth(self, auth: GitHubAuth) -> None:
        """Save GitHub authentication data."""
        auth_data = {
            "access_token": auth.access_token,
            "user": {
                "login": auth.user.login,
                "id": auth.user.id,
                "name": auth.user.name,
                "email": auth.user.email,
                "avatar_url": auth.user.avatar_url,
            },
            "scopes": auth.scopes,
            "expires_at": auth.expires_at.isoformat() if auth.expires_at else None,
        }

        with open(self.auth_file, "w") as f:
            json.dump(auth_data, f, indent=2)

        # Set restrictive permissions on auth file
        os.chmod(self.auth_file, 0o600)

    def load_auth(self) -> Optional[GitHubAuth]:
        """Load saved GitHub authentication data."""
        if not self.auth_file.exists():
            return None

        try:
            with open(self.auth_file) as f:
                auth_data = json.load(f)

            user_data = auth_data["user"]
            user = GitHubUser(
                login=user_data["login"],
                id=user_data["id"],
                name=user_data.get("name"),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
            )

            expires_at = None
            if auth_data.get("expires_at"):
                expires_at = datetime.fromisoformat(auth_data["expires_at"])

            return GitHubAuth(
                access_token=auth_data["access_token"],
                user=user,
                scopes=auth_data["scopes"],
                expires_at=expires_at,
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            # If auth file is corrupted, remove it
            self.delete_auth()
            return None

    def delete_auth(self) -> None:
        """Delete saved authentication data."""
        if self.auth_file.exists():
            self.auth_file.unlink()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with GitHub."""
        auth = self.load_auth()
        return auth is not None and not auth.is_expired
