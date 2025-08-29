from dataclasses import dataclass, field
from typing import Dict, Optional

from core.domain.entities.backup_config import GlobalBackupConfig
from core.domain.entities.domain_config import BaseDomain, DomainConfig
from core.domain.entities.instance_config import InstanceConfig
from core.domain.entities.repository_config import Repository
from core.domain.entities.snapshot_config import GlobalSnapshotConfig


@dataclass
class BaseDomainLock(BaseDomain):
    """
    Represents the locked state of a single base domain.

    Inherits all fields from BaseDomain and adds a checksum.
    """

    checksum: str = ""  # The checksum of this specific domain's configuration.


@dataclass
class DomainLock(DomainConfig):
    """
    Represents the locked state of the entire [domains] section.

    Inherits fields from DomainConfig and adds a checksum.
    """

    base_domains: Dict[str, BaseDomainLock] = field(default_factory=dict)
    checksum: str = ""  # The checksum for the entire domains section.


@dataclass
class RepositoryLock(Repository):
    """
    Represents the locked state of a single repository.

    Inherits all fields from Repository and adds a checksum.
    """

    checksum: str = ""  # The checksum of this repository's configuration.


@dataclass
class InstanceLock(InstanceConfig):
    """
    Represents the locked state of a single instance.

    Inherits all fields from InstanceConfig and adds a checksum.
    The 'repositories' field is overridden to use RepositoryLock.
    """

    repositories: Dict[str, RepositoryLock] = field(default_factory=dict)
    checksum: str = ""  # The checksum for this specific instance's configuration.


@dataclass
class RepositoriesLock:
    """Represents the locked state of the global [repositories] section."""

    items: Dict[str, RepositoryLock] = field(
        default_factory=dict,
    )  # A map of repository names to their locked states.
    checksum: str = ""  # The checksum for the entire global repositories section.


@dataclass
class InstancesLock:
    """Represents the locked state of the [instances] section."""

    items: Dict[str, InstanceLock] = field(
        default_factory=dict,
    )  # A map of instance names to their locked states.
    checksum: str = ""  # The checksum for the entire instances section.


@dataclass
class BackupLock(GlobalBackupConfig):
    """Represents the locked state of the global backup configuration."""

    checksum: str = ""  # The checksum for the backup configuration.


@dataclass
class SnapshotLock(GlobalSnapshotConfig):
    """Represents the locked state of the global snapshot configuration."""

    checksum: str = ""  # The checksum for the snapshot configuration.


@dataclass
class LockFile:
    """Represents the entire dooservice.lock file.

    Contains a snapshot of the last successfully applied configuration.
    """

    version: str = "1.3"  # The version of the lock file format.
    last_synced: str = (
        ""  # ISO 8601 timestamp of when the lock file was last generated.
    )
    checksum: str = ""  # A global checksum for the entire lock file content.
    domains: Optional[DomainLock] = None  # The locked state of the domains section.
    repositories: Optional[RepositoriesLock] = (
        None  # The locked state of the global repositories section.
    )
    instances: Optional[InstancesLock] = (
        None  # The locked state of the instances section.
    )
    backup: Optional[BackupLock] = (
        None  # The locked state of the global backup configuration.
    )
    snapshot: Optional[SnapshotLock] = (
        None  # The locked state of the global snapshot configuration.
    )
