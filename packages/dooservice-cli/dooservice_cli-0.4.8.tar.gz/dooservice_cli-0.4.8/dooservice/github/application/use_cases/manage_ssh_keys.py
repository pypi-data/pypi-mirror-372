"""Use case for managing GitHub SSH keys."""

from typing import List

from github.domain.entities.github_auth import GitHubSSHKey
from github.domain.repositories.github_auth_repository import GitHubAPIRepository
from github.domain.services.github_oauth_service import GitHubOAuthService
from github.infrastructure.driven_adapters.managed_ssh_keys_repository import (
    ManagedSSHKeysRepository,
)


class ManageSSHKeysUseCase:
    """Use case for managing GitHub SSH keys."""

    def __init__(
        self,
        oauth_service: GitHubOAuthService,
        api_repository: GitHubAPIRepository,
        managed_keys_repo: ManagedSSHKeysRepository = None,
    ):
        self.oauth_service = oauth_service
        self.api_repository = api_repository
        self.managed_keys_repo = managed_keys_repo or ManagedSSHKeysRepository()

    def list_keys(self) -> List[GitHubSSHKey]:
        """
        List SSH keys managed by dooservice (not all user keys for security).

        Returns:
            List of SSH keys managed by dooservice

        Raises:
            ValueError: If user is not authenticated
        """
        auth = self.oauth_service.get_current_auth()
        if not auth:
            raise ValueError(
                "Not authenticated with GitHub. "
                "Run 'uv run dooservice cli github login' first.",
            )

        # Get all keys from GitHub
        all_keys = self.api_repository.list_ssh_keys(auth.access_token)

        # Clean up orphaned managed keys
        self.managed_keys_repo.cleanup_orphaned_keys(all_keys)

        # Return only keys managed by dooservice
        return self.managed_keys_repo.filter_managed_keys(all_keys)

    def add_key(self, title: str, public_key_content: str) -> GitHubSSHKey:
        """
        Add SSH key to GitHub account.

        Args:
            title: Title/name for the SSH key
            public_key_content: The public key content (ssh-rsa ... or ssh-ed25519 ...)

        Returns:
            GitHubSSHKey: The created SSH key

        Raises:
            ValueError: If user is not authenticated or key is invalid
        """
        auth = self.oauth_service.get_current_auth()
        if not auth:
            raise ValueError(
                "Not authenticated with GitHub. "
                "Run 'uv run dooservice cli github login' first.",
            )

        # Validate key format
        if not self._is_valid_public_key(public_key_content):
            raise ValueError("Invalid SSH public key format")

        # Add key to GitHub
        new_key = self.api_repository.add_ssh_key(
            auth.access_token,
            title,
            public_key_content,
        )

        # Register as managed key
        self.managed_keys_repo.register_managed_key(new_key, "dooservice")

        return new_key

    def remove_key(self, key_id: int) -> None:
        """
        Remove SSH key from GitHub account (only if managed by dooservice).

        Args:
            key_id: ID of the SSH key to remove

        Raises:
            ValueError: If user is not authenticated or key is not managed by dooservice
        """
        auth = self.oauth_service.get_current_auth()
        if not auth:
            raise ValueError(
                "Not authenticated with GitHub. "
                "Run 'uv run dooservice cli github login' first.",
            )

        # Security check: only allow removal of managed keys
        if not self.managed_keys_repo.is_managed_key(key_id):
            raise ValueError(
                f"Cannot remove SSH key {key_id}: not managed by dooservice. "
                "Only keys added through dooservice can be removed."
            )

        # Remove from GitHub
        self.api_repository.delete_ssh_key(auth.access_token, key_id)

        # Unregister from managed keys
        self.managed_keys_repo.unregister_managed_key(key_id)

    def find_key_by_fingerprint(self, fingerprint: str) -> GitHubSSHKey:
        """
        Find SSH key by fingerprint.

        Args:
            fingerprint: SSH key fingerprint

        Returns:
            GitHubSSHKey: The matching key

        Raises:
            ValueError: If key not found or user not authenticated
        """
        keys = self.list_keys()

        for key in keys:
            if key.fingerprint == fingerprint:
                return key

        raise ValueError(f"SSH key with fingerprint '{fingerprint}' not found")

    def _is_valid_public_key(self, key_content: str) -> bool:
        """
        Validate SSH public key format.

        Args:
            key_content: The public key content

        Returns:
            bool: True if valid format
        """
        # Basic validation - should start with ssh-rsa, ssh-ed25519, etc.
        valid_prefixes = [
            "ssh-rsa",
            "ssh-ed25519",
            "ssh-dss",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ]

        key_content = key_content.strip()
        if not key_content:
            return False

        return any(key_content.startswith(prefix) for prefix in valid_prefixes)
