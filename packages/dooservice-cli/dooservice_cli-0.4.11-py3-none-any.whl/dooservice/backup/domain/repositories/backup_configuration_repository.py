"""Repository interface for backup configurations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from dooservice.backup.domain.entities.backup_configuration import BackupConfiguration


class BackupConfigurationRepository(ABC):
    """
    Repository interface for managing backup configurations.

    Similar to Odoo's model interface but following hexagonal architecture.
    """

    @abstractmethod
    def save(self, config: BackupConfiguration) -> BackupConfiguration:
        """
        Save or update a backup configuration.

        Args:
            config: The backup configuration to save

        Returns:
            BackupConfiguration: The saved configuration with updated metadata
        """

    @abstractmethod
    def find_by_id(self, config_id: str) -> Optional[BackupConfiguration]:
        """
        Find a backup configuration by ID.

        Args:
            config_id: The configuration ID

        Returns:
            Optional[BackupConfiguration]: The configuration if found, None otherwise
        """

    @abstractmethod
    def find_by_instance(self, instance_name: str) -> List[BackupConfiguration]:
        """
        Find all backup configurations for a specific instance.

        Args:
            instance_name: Name of the instance

        Returns:
            List[BackupConfiguration]: List of configurations for the instance
        """

    @abstractmethod
    def find_active_configs(self) -> List[BackupConfiguration]:
        """
        Find all active backup configurations.

        Returns:
            List[BackupConfiguration]: List of active configurations
        """

    @abstractmethod
    def find_by_frequency(
        self,
        frequency,  # type: BackupFrequency
    ) -> List[BackupConfiguration]:
        """
        Find all configurations with a specific backup frequency.

        Args:
            frequency: The backup frequency to search for

        Returns:
            List[BackupConfiguration]: List of matching configurations
        """

    @abstractmethod
    def delete(self, config_id: str) -> bool:
        """
        Delete a backup configuration.

        Args:
            config_id: The configuration ID to delete

        Returns:
            bool: True if deletion was successful
        """

    @abstractmethod
    def list_all(self) -> List[BackupConfiguration]:
        """
        List all backup configurations.

        Returns:
            List[BackupConfiguration]: All configurations
        """

    @abstractmethod
    def find_due_for_backup(self) -> List[BackupConfiguration]:
        """
        Find configurations that are due for backup based on schedule.

        Returns:
            List[BackupConfiguration]: Configurations ready for backup
        """

    @abstractmethod
    def update_last_backup(
        self,
        config_id: str,
        filename: str,
        timestamp,  # type: datetime
    ) -> bool:
        """
        Update the last backup information for a configuration.

        Args:
            config_id: The configuration ID
            filename: The backup filename
            timestamp: The backup timestamp

        Returns:
            bool: True if update was successful
        """

    @abstractmethod
    def update_last_exception(self, config_id: str, exception: str) -> bool:
        """
        Update the last exception information for a configuration.

        Args:
            config_id: The configuration ID
            exception: The exception message

        Returns:
            bool: True if update was successful
        """
