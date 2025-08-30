from dataclasses import dataclass
from typing import Optional


@dataclass
class SnapshotRetentionConfig:
    """Configuration for snapshot retention policies."""

    days: int = 60  # Days to keep snapshots (0 = no limit)
    max_snapshots: int = 20  # Maximum number of snapshots to keep (0 = no limit)


@dataclass
class SnapshotConfig:
    """Configuration for snapshot system (global or per-instance)."""

    enabled: bool = True
    storage_dir: Optional[str] = None  # Will use default if None
    include_backup_by_default: bool = True
    retention: SnapshotRetentionConfig = None

    def __post_init__(self):
        if self.retention is None:
            self.retention = SnapshotRetentionConfig()


@dataclass
class GlobalSnapshotConfig(SnapshotConfig):
    """Global snapshot configuration."""

    default_storage_dir: str = "/opt/dooservice/snapshots"

    def __post_init__(self):
        super().__post_init__()
        if self.storage_dir is None:
            self.storage_dir = self.default_storage_dir
