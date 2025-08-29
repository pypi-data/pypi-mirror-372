"""Create snapshot use case."""

from typing import Optional

from core.domain.entities.instance_config import InstanceConfig
from snapshot.domain.entities.snapshot_metadata import SnapshotMetadata
from snapshot.domain.repositories.snapshot_repository import SnapshotRepository


class CreateSnapshotUseCase:
    """Use case for creating instance snapshots."""

    def __init__(self, snapshot_repository: SnapshotRepository):
        self._snapshot_repository = snapshot_repository

    def execute(
        self,
        instance_config: InstanceConfig,
        instance_name: str,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        include_backup: bool = True,
    ) -> SnapshotMetadata:
        """Create a snapshot of instance state."""
        return self._snapshot_repository.create_snapshot(
            instance_config=instance_config,
            instance_name=instance_name,
            tag=tag,
            description=description,
            include_backup=include_backup,
        )
