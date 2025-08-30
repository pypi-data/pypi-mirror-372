from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.domain.entities.domain_config import DomainConfig
from core.domain.entities.dooservice_config import DooServiceConfig
from core.domain.entities.instance_config import InstanceConfig
from core.domain.entities.lockfile import (
    BaseDomainLock,
    DomainLock,
    InstanceLock,
    InstancesLock,
    LockFile,
    RepositoriesLock,
    RepositoryLock,
)
from core.domain.entities.repository_config import Repository
from core.domain.services.lock_file_checksum_service import LockFileChecksumService
from core.infrastructure.driven_adapters.regex_placeholder_service import (
    RegexPlaceholderService,
)
from shared.crypto.checksum import generate_checksum


class LockManager:
    """
    A domain service to manage the lifecycle of the LockFile object.

    This service is responsible for translating a `DooServiceConfig` object into
    a `LockFile` object, which represents the last-applied state of the system.
    It orchestrates the complex process of generating nested checksums for all
    configuration entities, ensuring that any drift can be detected.
    """

    def __init__(self, lock_file_checksum_service: LockFileChecksumService):
        self.lock_file_checksum_service = lock_file_checksum_service
        self._placeholder_service = RegexPlaceholderService()

    def generate_from_config(self, config: DooServiceConfig) -> LockFile:
        """
        Generates a new LockFile object from a DooServiceConfig object.

        This is the main entry point for creating a complete, checksummed
        representation of the configuration.

        Args:
            config: The complete configuration object from dooservice.yml.

        Returns:
            A fully populated and checksummed LockFile object.
        """
        domain_lock = self._generate_domain_lock(config.domains)
        repositories_lock = self._generate_repositories_lock(config.repositories)
        instances_lock = self._generate_instances_lock(config.instances)

        lock_file = LockFile(
            version="1.1",
            last_synced=datetime.now(timezone.utc).isoformat(),
            domains=domain_lock,
            repositories=repositories_lock,
            instances=instances_lock,
            checksum="",  # Placeholder, will be calculated last.
        )

        lock_file.checksum = self._calculate_global_checksum(lock_file)
        return lock_file

    def _generate_domain_lock(
        self,
        domain_config: Optional[DomainConfig],
    ) -> Optional[DomainLock]:
        """Generates a DomainLock object from a DomainConfig."""
        if not domain_config:
            return None

        base_domain_locks = {
            bd.name: self._create_lock_with_checksum(BaseDomainLock, bd)
            for bd in domain_config.base_domains
        }

        return self._create_lock_with_checksum(
            DomainLock,
            domain_config,
            extra_fields={"base_domains": base_domain_locks},
        )

    def _generate_repositories_lock(
        self,
        repo_configs: Optional[Dict[str, Repository]],
    ) -> Optional[RepositoriesLock]:
        """Generates a RepositoriesLock object from Repository configs."""
        if not repo_configs:
            return None

        repo_locks = {
            name: self._create_lock_with_checksum(RepositoryLock, repo_conf)
            for name, repo_conf in repo_configs.items()
        }

        repositories_lock = RepositoriesLock(items=repo_locks, checksum="")
        repositories_lock.checksum = generate_checksum(repositories_lock.items)
        return repositories_lock

    def _generate_instances_lock(
        self,
        instance_configs: Optional[Dict[str, InstanceConfig]],
    ) -> Optional[InstancesLock]:
        """Generates an InstancesLock object from a dictionary of InstanceConfig."""
        if not instance_configs:
            return None

        instance_locks = {}
        for name, i_config in instance_configs.items():
            # Resolve placeholders for this instance
            resolved_config = self._resolve_instance_placeholders(i_config, name)
            instance_locks[name] = self._create_instance_lock(resolved_config)

        instances_lock = InstancesLock(items=instance_locks, checksum="")
        instances_lock.checksum = generate_checksum(instances_lock.items)
        return instances_lock

    def _resolve_instance_placeholders(
        self,
        instance_config: InstanceConfig,
        name: str,
    ) -> InstanceConfig:
        """
        Resolves placeholders in an instance configuration.

        Args:
            instance_config: The instance configuration with potential placeholders
            name: The name of the instance

        Returns:
            Instance configuration with resolved placeholders
        """
        resolved_config = instance_config
        for _ in range(5):  # Iterate to resolve nested placeholders
            context = asdict(resolved_config)
            context["name"] = name
            resolved_config = self._placeholder_service.resolve(
                resolved_config,
                context,
            )

        # Convert port values to int if they are strings
        if hasattr(resolved_config, "ports") and resolved_config.ports:
            resolved_config.ports = {
                k: int(v) if isinstance(v, str) and v.isdigit() else v
                for k, v in resolved_config.ports.items()
            }

        return resolved_config

    def _create_instance_lock(self, i_config: InstanceConfig) -> InstanceLock:
        """Creates a single, fully-checksummed InstanceLock."""
        instance_repo_locks = {
            repo_name: self._create_lock_with_checksum(RepositoryLock, repo_conf)
            for repo_name, repo_conf in i_config.repositories.items()
        }

        return self._create_lock_with_checksum(
            InstanceLock,
            i_config,
            extra_fields={"repositories": instance_repo_locks},
            ignored_keys=["checksum", "env_vars"],
        )

    def _calculate_global_checksum(self, lock_file: LockFile) -> str:
        """Calculates the global checksum for the entire LockFile."""
        ignored = ["checksum", "last_synced"]
        return generate_checksum(lock_file, ignored_keys=ignored)

    def _create_lock_with_checksum(
        self,
        lock_class,
        config_obj,
        extra_fields=None,
        ignored_keys=None,
    ) -> Any:
        """Generic helper to create a lock object and calculate its checksum."""
        if extra_fields is None:
            extra_fields = {}
        if ignored_keys is None:
            ignored_keys = ["checksum"]

        config_dict = asdict(config_obj)
        config_dict.update(extra_fields)

        lock_obj = lock_class(**config_dict, checksum="")
        lock_obj.checksum = generate_checksum(lock_obj, ignored_keys=ignored_keys)
        return lock_obj
