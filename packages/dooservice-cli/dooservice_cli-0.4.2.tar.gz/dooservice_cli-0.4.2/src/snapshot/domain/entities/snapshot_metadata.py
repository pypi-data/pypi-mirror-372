"""Snapshot metadata entities for instance state management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class RepositorySnapshot:
    """Snapshot of repository state."""

    name: str
    url: str
    branch: str
    commit_hash: str
    path: str


@dataclass
class ModuleSnapshot:
    """Snapshot of installed module state."""

    name: str
    version: str
    state: str  # installed, uninstalled, to_upgrade, etc.
    auto_install: bool
    repository: Optional[str] = None


@dataclass
class SnapshotMetadata:
    """
    Complete snapshot of instance state.

    A snapshot captures not just the data (like backups) but also
    the complete state of the instance including configuration,
    repository states, installed modules, etc.
    """

    snapshot_id: str
    instance_name: str
    tag: Optional[str]  # Optional tag like "v1.0.0", "pre-migration", etc.
    created_at: datetime
    description: Optional[str]

    # Configuration state
    odoo_version: str
    configuration_checksum: str

    # Repository states
    repositories: List[RepositorySnapshot] = field(default_factory=list)

    # Module states
    installed_modules: List[ModuleSnapshot] = field(default_factory=list)

    # Backup reference (optional)
    backup_id: Optional[str] = None

    # Environment state
    python_dependencies: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Metadata
    file_path: str = ""
    file_size: int = 0
    version: str = "1.0"

    @property
    def short_id(self) -> str:
        """Get short version of snapshot ID."""
        return self.snapshot_id[:8]

    @property
    def display_name(self) -> str:
        """Get display name for snapshot."""
        if self.tag:
            return f"{self.tag} ({self.short_id})"
        return self.short_id
