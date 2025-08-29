"""Repository for tracking SSH keys managed by dooservice."""

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from github.domain.entities.github_auth import GitHubSSHKey


class ManagedSSHKeysRepository:
    """Repository for tracking SSH keys managed by dooservice."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the managed SSH keys repository.

        Args:
            storage_dir: Directory to store managed keys data
        """
        self.storage_dir = storage_dir or (Path.home() / ".dooservice")
        self.managed_keys_file = self.storage_dir / "managed_ssh_keys.json"
        self.logger = logging.getLogger(__name__)

        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Load existing managed keys
        self._managed_keys: Dict[str, Dict] = self._load_managed_keys()

    def _load_managed_keys(self) -> Dict[str, Dict]:
        """Load managed keys from storage."""
        if not self.managed_keys_file.exists():
            return {}

        try:
            with open(self.managed_keys_file) as f:
                data = json.load(f)
                return data.get("keys", {})
        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning("Failed to load managed keys: %s", e)
            return {}

    def _save_managed_keys(self):
        """Save managed keys to storage."""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "keys": self._managed_keys,
            }

            with open(self.managed_keys_file, "w") as f:
                json.dump(data, f, indent=2)

        except OSError as e:
            self.logger.error("Failed to save managed keys: %s", e)

    def register_managed_key(self, ssh_key: GitHubSSHKey, source: str = "dooservice"):
        """
        Register an SSH key as managed by dooservice.

        Args:
            ssh_key: The SSH key that was added to GitHub
            source: Source that created this key (default: dooservice)
        """
        key_data = {
            "id": ssh_key.id,
            "title": ssh_key.title,
            "fingerprint": ssh_key.fingerprint,
            "key": ssh_key.key,
            "source": source,
            "managed_at": datetime.utcnow().isoformat(),
            "read_only": ssh_key.read_only,
            "created_at": ssh_key.created_at.isoformat()
            if ssh_key.created_at
            else None,
        }

        # Use key ID as the unique identifier
        self._managed_keys[str(ssh_key.id)] = key_data
        self._save_managed_keys()

        self.logger.info(
            "Registered managed SSH key: %s (ID: %s)", ssh_key.title, ssh_key.id
        )

    def unregister_managed_key(self, key_id: int):
        """
        Unregister an SSH key from being managed by dooservice.

        Args:
            key_id: ID of the SSH key to unregister
        """
        key_id_str = str(key_id)
        if key_id_str in self._managed_keys:
            title = self._managed_keys[key_id_str].get("title", "Unknown")
            del self._managed_keys[key_id_str]
            self._save_managed_keys()
            self.logger.info("Unregistered managed SSH key: %s (ID: %s)", title, key_id)
        else:
            self.logger.warning("Attempted to unregister unknown key ID: %s", key_id)

    def is_managed_key(self, key_id: int) -> bool:
        """
        Check if an SSH key is managed by dooservice.

        Args:
            key_id: ID of the SSH key to check

        Returns:
            True if the key is managed by dooservice
        """
        return str(key_id) in self._managed_keys

    def get_managed_key_ids(self) -> Set[int]:
        """
        Get all managed SSH key IDs.

        Returns:
            Set of managed SSH key IDs
        """
        return {int(key_id) for key_id in self._managed_keys}

    def filter_managed_keys(self, all_keys: List[GitHubSSHKey]) -> List[GitHubSSHKey]:
        """
        Filter a list of SSH keys to only include managed ones.

        Args:
            all_keys: List of all SSH keys from GitHub

        Returns:
            List of SSH keys that are managed by dooservice
        """
        managed_ids = self.get_managed_key_ids()
        return [key for key in all_keys if key.id in managed_ids]

    def get_managed_keys_metadata(self) -> List[Dict]:
        """
        Get metadata about all managed keys.

        Returns:
            List of managed key metadata
        """
        return list(self._managed_keys.values())

    def cleanup_orphaned_keys(self, current_keys: List[GitHubSSHKey]):
        """
        Remove tracked keys that no longer exist in GitHub.

        Args:
            current_keys: List of current SSH keys from GitHub
        """
        current_key_ids = {key.id for key in current_keys}
        managed_ids = self.get_managed_key_ids()

        orphaned_ids = managed_ids - current_key_ids

        for orphaned_id in orphaned_ids:
            self.logger.info("Cleaning up orphaned managed key: %s", orphaned_id)
            self.unregister_managed_key(orphaned_id)
