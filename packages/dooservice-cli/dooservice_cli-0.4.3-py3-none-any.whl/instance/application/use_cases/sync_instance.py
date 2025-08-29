from typing import Optional

from core.domain.entities.instance_config import InstanceConfig
from instance.domain.repositories.instance_environment_repository import (
    InstanceEnvironmentRepository,
)
from instance.domain.repositories.instance_repository import InstanceRepository
from instance.domain.services.database_manager import DatabaseManager
from instance.domain.services.repository_manager import RepositoryManager


class SyncInstanceUseCase:
    """Pure domain use case for synchronizing an instance."""

    def __init__(
        self,
        repository_manager: RepositoryManager,
        database_manager: DatabaseManager,
        instance_repo: InstanceRepository,
        instance_env_repo: InstanceEnvironmentRepository,
    ):
        self._repository_manager = repository_manager
        self._database_manager = database_manager
        self._instance_repo = instance_repo
        self._instance_env_repo = instance_env_repo

    def execute(
        self,
        resolved_instance_config: InstanceConfig,
        locked_instance_config: InstanceConfig,
    ) -> None:
        """
        Execute the synchronization process for an instance.

        Args:
            resolved_instance_config: New resolved configuration.
            locked_instance_config: Current locked configuration.
        """
        # 1. Sync repositories
        self._repository_manager.sync_repositories(
            resolved_instance_config,
            locked_instance_config,
        )

        # 2. Update instance environment (odoo.conf, .env files)
        self._instance_env_repo.setup(resolved_instance_config)

        # 3. Recreate Docker containers
        self._instance_repo.recreate(resolved_instance_config)

    def sync_database_credentials(
        self,
        db_container_name: str,
        old_user: Optional[str],
        new_user: str,
        new_password: str,
        superuser: Optional[str] = None,
    ) -> None:
        """
        Synchronize database credentials using the domain service.

        Args:
            db_container_name: Name of the database container.
            old_user: Previous username (if available).
            new_user: New username.
            new_password: New password.
            superuser: Database superuser to connect as.
        """
        self._database_manager.sync_credentials(
            db_container_name,
            old_user,
            new_user,
            new_password,
            superuser,
        )
