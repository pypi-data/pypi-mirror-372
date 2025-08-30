"""Backup metadata entities for tracking backup information."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BackupMetadata:
    """Metadata about a backup operation."""

    backup_id: str  # Unique identifier for the backup
    instance_name: str  # Name of the instance backed up
    created_at: datetime  # When the backup was created
    file_path: str  # Path to the backup file
    file_size: int  # Size of backup file in bytes
    database_included: bool  # Whether database was backed up
    filestore_included: bool  # Whether filestore was backed up
    compressed: bool  # Whether backup is compressed
    checksum: str  # SHA256 checksum of backup file
    version: str = "1.0"  # Backup format version
    description: Optional[str] = None  # Optional description

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
