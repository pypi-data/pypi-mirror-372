"""Snapshot repository interface for the domain layer."""

from abc import ABC, abstractmethod
from typing import List, Optional

from core.domain.entities.instance_config import InstanceConfig
from snapshot.domain.entities.snapshot_metadata import SnapshotMetadata


class SnapshotRepository(ABC):
    """
    Abstract repository for snapshot operations.

    Snapshots capture the complete state of an instance including
    configuration, repositories, modules, and data.
    """

    @abstractmethod
    def create_snapshot(
        self,
        instance_config: InstanceConfig,
        instance_name: str,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        include_backup: bool = True,
    ) -> SnapshotMetadata:
        """
        Create a snapshot of an instance's complete state.

        Args:
            instance_config: Configuration of instance to snapshot
            instance_name: Name of the instance
            tag: Optional tag for the snapshot (e.g., "v1.0.0")
            description: Optional description
            include_backup: Whether to include a full backup

        Returns:
            Metadata about the created snapshot
        """

    @abstractmethod
    def restore_snapshot(
        self,
        snapshot_id: str,
        target_instance: str,
        restore_data: bool = True,
        restore_modules: bool = True,
    ) -> None:
        """
        Restore an instance from a snapshot.

        Args:
            snapshot_id: ID of snapshot to restore
            target_instance: Name of target instance
            restore_data: Whether to restore database/filestore
            restore_modules: Whether to restore module states
        """

    @abstractmethod
    def list_snapshots(
        self,
        instance_name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[SnapshotMetadata]:
        """
        List available snapshots.

        Args:
            instance_name: Filter by instance name
            tag: Filter by tag

        Returns:
            List of snapshot metadata
        """

    @abstractmethod
    def delete_snapshot(self, snapshot_id: str) -> None:
        """
        Delete a snapshot by ID.

        Args:
            snapshot_id: ID of snapshot to delete
        """

    @abstractmethod
    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotMetadata]:
        """
        Get snapshot metadata by ID.

        Args:
            snapshot_id: ID of snapshot to retrieve

        Returns:
            Snapshot metadata or None if not found
        """
