from datetime import datetime, timezone

from core.domain.entities.lockfile import (
    InstanceLock,
    LockFile,
)
from shared.crypto.checksum import generate_checksum


class LockFileChecksumService:
    """A domain service for updating checksums within a LockFile object."""

    def __init__(self):
        # No direct dependencies needed for checksum generation
        pass

    def update_checksums(self, lock_file: LockFile) -> LockFile:
        """
        Updates all checksums in a modified LockFile object.

        This is useful after a partial update (e.g., a git pull) to bring
        all checksums back in sync with the new state.

        Args:
            lock_file: The LockFile object with modified data.

        Returns:
            The same LockFile object with all checksums recalculated.
        """
        if lock_file.domains:
            for bd in lock_file.domains.base_domains.values():
                bd.checksum = generate_checksum(bd, ignored_keys=["checksum"])
            lock_file.domains.checksum = generate_checksum(
                lock_file.domains,
                ignored_keys=["checksum"],
            )

        if lock_file.repositories:
            for repo in lock_file.repositories.items.values():
                repo.checksum = generate_checksum(repo, ignored_keys=["checksum"])
            lock_file.repositories.checksum = generate_checksum(
                lock_file.repositories.items,
            )

        if lock_file.instances:
            for instance in lock_file.instances.items.values():
                self._update_instance_checksums(instance)
            lock_file.instances.checksum = generate_checksum(lock_file.instances.items)

        lock_file.checksum = self._calculate_global_checksum(lock_file)
        lock_file.last_synced = datetime.now(timezone.utc).isoformat()
        return lock_file

    def _update_instance_checksums(self, instance: InstanceLock):
        """Updates the checksums for a single InstanceLock and its children."""
        if instance.repositories:
            for repo in instance.repositories.values():
                repo.checksum = generate_checksum(repo, ignored_keys=["checksum"])
        instance.checksum = generate_checksum(
            instance,
            ignored_keys=["checksum", "env_vars"],
        )

    def _calculate_global_checksum(self, lock_file: LockFile) -> str:
        """Calculates the global checksum for the entire LockFile."""
        ignored = ["checksum", "last_synced"]
        return generate_checksum(lock_file, ignored_keys=ignored)
