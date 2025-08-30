from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from core.domain.entities.backup_config import InstanceAutoBackupConfig
from core.domain.entities.deployment_config import DeploymentConfig
from core.domain.entities.repository_config import Repository
from core.domain.entities.snapshot_config import SnapshotConfig


@dataclass
class InstanceDomainConfig:
    """Domain-specific (URL) configuration for an instance."""

    base: str  # The base domain name, e.g., 'example.com'.
    subdomain: Optional[str] = None  # The subdomain, e.g., 'my-instance'.
    use_root_domain: bool = False  # If true, use the base domain without a subdomain.


@dataclass
class InstanceConfig:
    """Defines a single Odoo instance with all its parameters."""

    odoo_version: str  # Version of Odoo, e.g., "16.0".
    data_dir: str  # The root directory on the host for all instance data.
    paths: Dict[str, str]  # A mapping of logical names to host paths.
    ports: Dict[str, Union[int, str]]  # A mapping of logical names to host ports.
    deployment: DeploymentConfig  # The deployment configuration for this instance.
    instance_name: Optional[str] = None  # Name of the instance (set programmatically)
    repositories: Dict[str, Repository] = field(
        default_factory=dict,
    )  # Repositories used by this instance.
    env_vars: Dict[str, Union[str, int, float, bool]] = field(
        default_factory=dict,
    )  # Environment variables for this instance.
    domain: Optional[InstanceDomainConfig] = (
        None  # Domain configuration for this instance.
    )
    python_dependencies: List[str] = field(
        default_factory=list,
    )  # Python dependencies to be installed with pip
    auto_backup: Optional[InstanceAutoBackupConfig] = (
        None  # Backup configuration for this instance
    )
    snapshot: Optional[SnapshotConfig] = (
        None  # Snapshot configuration for this instance
    )
