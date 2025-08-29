from core.domain.entities.instance_config import InstanceConfig
from core.domain.repositories.filesystem_repository import FilesystemRepository
from instance.domain.repositories.instance_repository import InstanceRepository


class InstanceLifecycleService:
    """
    Domain service for managing the lifecycle of an Odoo instance.

    This service orchestrates the starting and stopping of Docker containers
    associated with an instance.
    """

    def __init__(
        self,
        instance_repository: InstanceRepository,
        filesystem_repository: FilesystemRepository,
    ):
        self._instance_repository = instance_repository
        self._filesystem_repository = filesystem_repository

    def start_instance(self, config: InstanceConfig) -> None:
        """Starts the Docker containers for the given instance configuration."""
        if config.deployment.docker.db:
            self._instance_repository.start(config.deployment.docker.db.container_name)
        if config.deployment.docker.web:
            self._instance_repository.start(config.deployment.docker.web.container_name)

    def stop_instance(self, config: InstanceConfig) -> None:
        """Stops the Docker containers for the given instance configuration."""
        if config.deployment.docker.web:
            self._instance_repository.stop(config.deployment.docker.web.container_name)
        if config.deployment.docker.db:
            self._instance_repository.stop(config.deployment.docker.db.container_name)

    def delete_instance(self, config: InstanceConfig) -> None:
        """Deletes the Docker containers for the given instance configuration."""
        if config.deployment.docker.web:
            self._instance_repository.delete(
                config.deployment.docker.web.container_name,
            )
        if config.deployment.docker.db:
            self._instance_repository.delete(config.deployment.docker.db.container_name)

    def delete_data_directory(self, config: InstanceConfig) -> bool:
        """
        Deletes the data directory for the given instance configuration.

        Returns True if the directory was found and deleted, False otherwise.
        """
        if self._filesystem_repository.directory_exists(config.data_dir):
            self._filesystem_repository.delete_directory(config.data_dir)
            return True
        return False
