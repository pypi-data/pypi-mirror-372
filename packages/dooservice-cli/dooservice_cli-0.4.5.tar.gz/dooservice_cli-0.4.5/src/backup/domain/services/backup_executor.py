"""
Backup executor service interface.

This service handles backup operations using XML-RPC with automatic instance detection.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from backup.domain.entities.backup_metadata import BackupMetadata
from core.domain.entities.backup_config import ResolvedBackupConfig


class BackupExecutor(ABC):
    """
    Abstract interface for backup executor.

    This service executes backups using XML-RPC with automatic instance detection.
    """

    @abstractmethod
    def execute_backup(
        self,
        backup_config: ResolvedBackupConfig,
        output_path: Optional[Path] = None,
    ) -> BackupMetadata:
        """
        Execute a backup using XML-RPC API with automatic instance detection.

        Args:
            backup_config: Resolved backup configuration
            output_path: Optional output path override

        Returns:
            BackupMetadata with information about the created backup

        Raises:
            BackupExecutionError: If backup fails
        """

    @abstractmethod
    def test_connection(self, backup_config: ResolvedBackupConfig) -> Dict[str, Any]:
        """
        Test connection to Odoo server using XML-RPC with automatic detection.

        Args:
            backup_config: Resolved backup configuration

        Returns:
            Dictionary with connection test results

        Raises:
            BackupConfigurationError: If connection test fails
        """

    @abstractmethod
    def list_databases(self, backup_config: ResolvedBackupConfig) -> List[str]:
        """
        List available databases on the Odoo server.

        Args:
            backup_config: Resolved backup configuration

        Returns:
            List of database names

        Raises:
            BackupConfigurationError: If unable to list databases
        """
