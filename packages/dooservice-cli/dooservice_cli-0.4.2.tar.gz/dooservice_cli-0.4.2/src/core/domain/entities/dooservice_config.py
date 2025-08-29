from dataclasses import dataclass, field
from typing import Dict, Optional

from core.domain.entities.backup_config import GlobalBackupConfig
from core.domain.entities.domain_config import DomainConfig
from core.domain.entities.github_config import GitHubGlobalConfig
from core.domain.entities.instance_config import InstanceConfig
from core.domain.entities.repository_config import Repository
from core.domain.entities.snapshot_config import GlobalSnapshotConfig


@dataclass
class DooServiceConfig:
    """The root configuration object mapping the entire `dooservice.yml` file."""

    version: str  # The version of the configuration file format.
    domains: Optional[DomainConfig] = None  # Global domain settings.
    repositories: Dict[str, Repository] = field(
        default_factory=dict,
    )  # Global repository definitions.
    instances: Dict[str, InstanceConfig] = field(
        default_factory=dict,
    )  # All instance definitions.
    backup: Optional[GlobalBackupConfig] = None  # Global backup settings.
    snapshot: Optional[GlobalSnapshotConfig] = None  # Global snapshot settings.
    github: Optional[GitHubGlobalConfig] = None  # Global GitHub integration settings.
