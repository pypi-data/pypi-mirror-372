"""Instance orchestration service - consolidated lifecycle management."""

import logging
from typing import Optional

from core.domain.entities.instance_config import InstanceConfig
from core.domain.repositories.filesystem_repository import FilesystemRepository
from instance.domain.repositories.instance_repository import InstanceRepository


class InstanceOrchestrator:
    """
    Consolidated service for orchestrating all instance lifecycle operations.

    This service consolidates instance lifecycle management with improved
    error handling, logging, and separation of concerns.
    """

    def __init__(
        self,
        instance_repository: InstanceRepository,
        filesystem_repository: FilesystemRepository,
        logger: Optional[logging.Logger] = None,
    ):
        self._instance_repository = instance_repository
        self._filesystem_repository = filesystem_repository
        self._logger = logger or logging.getLogger(__name__)

    def start_instance(self, config: InstanceConfig, instance_name: str = None) -> None:
        """
        Start all services for an instance in correct order.

        Args:
            config: Instance configuration
            instance_name: Name of the instance to start

        Raises:
            InstanceNotFoundError: If containers don't exist
            DockerError: If Docker operations fail
        """
        # Use provided instance name or derive from config
        name = instance_name or "unknown_instance"
        self._logger.info("Starting instance '%s'", name)

        try:
            # Start database first, then web service
            if config.deployment.docker.db:
                db_container = config.deployment.docker.db.container_name
                self._logger.debug("Starting database container: %s", db_container)
                self._instance_repository.start(db_container)

            if config.deployment.docker.web:
                web_container = config.deployment.docker.web.container_name
                self._logger.debug("Starting web container: %s", web_container)
                self._instance_repository.start(web_container)

            self._logger.info("Successfully started instance '%s'", instance_name)

        except Exception as e:
            self._logger.error("Failed to start instance '%s': %s", instance_name, e)
            raise

    def stop_instance(self, config: InstanceConfig) -> None:
        """
        Stop all services for an instance in correct order.

        Args:
            config: Instance configuration

        Raises:
            InstanceNotFoundError: If containers don't exist
            DockerError: If Docker operations fail
        """
        instance_name = config.instance_name
        self._logger.info("Stopping instance '%s'", instance_name)

        try:
            # Stop web service first, then database
            if config.deployment.docker.web:
                web_container = config.deployment.docker.web.container_name
                self._logger.debug("Stopping web container: %s", web_container)
                self._instance_repository.stop(web_container)

            if config.deployment.docker.db:
                db_container = config.deployment.docker.db.container_name
                self._logger.debug("Stopping database container: %s", db_container)
                self._instance_repository.stop(db_container)

            self._logger.info("Successfully stopped instance '%s'", instance_name)

        except Exception as e:
            self._logger.error("Failed to stop instance '%s': %s", instance_name, e)
            raise

    def delete_instance(
        self, config: InstanceConfig, remove_data: bool = False
    ) -> None:
        """
        Delete all containers for an instance and optionally data.

        Args:
            config: Instance configuration
            remove_data: Whether to also remove data directory

        Raises:
            InstanceNotFoundError: If containers don't exist
            DockerError: If Docker operations fail
        """
        instance_name = config.instance_name
        self._logger.info(
            "Deleting instance '%s' (remove_data=%s)", instance_name, remove_data
        )

        try:
            # Stop instance first if running
            try:
                self.stop_instance(config)
            except (RuntimeError, OSError) as stop_error:
                # Continue with deletion even if stop fails
                self._logger.debug(
                    "Stop failed, continuing with deletion: %s", stop_error
                )

            # Delete containers
            if config.deployment.docker.web:
                web_container = config.deployment.docker.web.container_name
                self._logger.debug("Deleting web container: %s", web_container)
                self._instance_repository.delete(web_container)

            if config.deployment.docker.db:
                db_container = config.deployment.docker.db.container_name
                self._logger.debug("Deleting database container: %s", db_container)
                self._instance_repository.delete(db_container)

            # Remove data directory if requested
            if remove_data:
                data_removed = self._delete_data_directory(config)
                if data_removed:
                    self._logger.info("Removed data directory: %s", config.data_dir)
                else:
                    self._logger.warning(
                        "Data directory not found: %s", config.data_dir
                    )

            self._logger.info("Successfully deleted instance '%s'", instance_name)

        except Exception as e:
            self._logger.error("Failed to delete instance '%s': %s", instance_name, e)
            raise

    def get_instance_status(self, config: InstanceConfig) -> dict:
        """
        Get comprehensive status information for an instance.

        Args:
            config: Instance configuration

        Returns:
            Dictionary with status information for each service
        """
        instance_name = config.instance_name
        status = {
            "instance_name": instance_name,
            "web": None,
            "db": None,
            "overall": "unknown",
        }

        try:
            if config.deployment.docker.web:
                web_container = config.deployment.docker.web.container_name
                status["web"] = self._instance_repository.status(web_container)

            if config.deployment.docker.db:
                db_container = config.deployment.docker.db.container_name
                status["db"] = self._instance_repository.status(db_container)

            # Determine overall status
            web_running = status["web"] == "running"
            db_running = status["db"] == "running"

            if web_running and db_running:
                status["overall"] = "running"
            elif not web_running and not db_running:
                status["overall"] = "stopped"
            else:
                status["overall"] = "partial"

        except (RuntimeError, OSError) as e:
            self._logger.error(
                "Failed to get status for instance '%s': %s", instance_name, e
            )
            status["overall"] = "error"
            status["error"] = str(e)

        return status

    def _delete_data_directory(self, config: InstanceConfig) -> bool:
        """
        Delete the data directory for an instance.

        Args:
            config: Instance configuration

        Returns:
            True if directory was deleted, False if it didn't exist
        """
        if self._filesystem_repository.directory_exists(config.data_dir):
            self._filesystem_repository.delete_directory(config.data_dir)
            return True
        return False
