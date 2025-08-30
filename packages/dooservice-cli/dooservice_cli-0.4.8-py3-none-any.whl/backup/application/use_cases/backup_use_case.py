"""Backup use case for managing backups with automatic instance detection."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backup.domain.entities.backup_metadata import BackupMetadata
from backup.domain.services.backup_executor import BackupExecutor
from core.domain.entities.backup_config import (
    BackupConfig,
    BackupFormat,
    InstanceAutoBackupConfig,
    ResolvedBackupConfig,
    merge_backup_configs,
)
from shared.errors.backup_error import BackupConfigurationError

_logger = logging.getLogger(__name__)


class BackupUseCase:
    """
    Simplified use case for managing backups using the new simplified configuration.

    This use case handles:
    - Loading simplified backup configuration from YAML
    - Automatic instance detection
    - Executing backups with minimal configuration
    - Managing backup retention and cleanup
    """

    def __init__(self, backup_executor: BackupExecutor):
        """
        Initialize the simplified backup use case.

        Args:
            backup_executor: Simple backup executor implementation
        """
        self._backup_executor = backup_executor
        self._logger = _logger

    def execute_backup(
        self,
        global_config: BackupConfig,
        instance_config: InstanceAutoBackupConfig,
        instance_name: str,
        admin_password: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
    ) -> BackupMetadata:
        """
        Execute a backup with simplified configuration.

        Args:
            global_config: Global backup configuration from YAML
            instance_config: Instance-specific auto backup configuration
            instance_name: Name of the instance
            admin_password: Admin password from env_vars.ADMIN_PASSWD
            cli_overrides: Optional CLI parameter overrides
            output_path: Optional output path override

        Returns:
            BackupMetadata with information about the created backup

        Raises:
            BackupConfigurationError: If configuration is invalid
            BackupExecutionError: If backup execution fails
        """
        try:
            self._logger.info(
                "Starting simplified backup for instance: %s",
                instance_name,
            )

            # Resolve configuration (merge global + instance + CLI overrides)
            resolved_config = self._resolve_configuration(
                global_config,
                instance_config,
                instance_name,
                admin_password,
                cli_overrides,
            )

            # Validate resolved configuration
            self._validate_resolved_config(resolved_config)

            # Execute backup
            metadata = self._backup_executor.execute_backup(
                resolved_config,
                output_path,
            )

            self._logger.info("Backup completed successfully: %s", metadata.file_path)
            return metadata

        except Exception as e:
            self._logger.error("Backup execution failed: %s", e)
            raise

    def test_backup_configuration(
        self,
        global_config: BackupConfig,
        instance_config: InstanceAutoBackupConfig,
        instance_name: str,
        admin_password: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Test backup configuration and connectivity.

        Args:
            global_config: Global backup configuration from YAML
            instance_config: Instance-specific auto backup configuration
            instance_name: Name of the instance
            admin_password: Admin password from env_vars.ADMIN_PASSWD
            cli_overrides: Optional CLI parameter overrides

        Returns:
            Dictionary with test results
        """
        try:
            # Resolve configuration
            resolved_config = self._resolve_configuration(
                global_config,
                instance_config,
                instance_name,
                admin_password,
                cli_overrides,
            )

            # Test connection
            return self._backup_executor.test_connection(resolved_config)

        except (ConnectionError, BackupConfigurationError) as e:
            return {"success": False, "error": str(e)}

    def list_available_databases(
        self,
        global_config: BackupConfig,
        instance_config: InstanceAutoBackupConfig,
        instance_name: str,
        admin_password: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        List available databases for backup.

        Args:
            global_config: Global backup configuration from YAML
            instance_config: Instance-specific auto backup configuration
            instance_name: Name of the instance
            admin_password: Admin password from env_vars.ADMIN_PASSWD
            cli_overrides: Optional CLI parameter overrides

        Returns:
            List of available database names
        """
        try:
            # Resolve configuration
            resolved_config = self._resolve_configuration(
                global_config,
                instance_config,
                instance_name,
                admin_password,
                cli_overrides,
            )

            # List databases
            return self._backup_executor.list_databases(resolved_config)

        except (ConnectionError, BackupConfigurationError) as e:
            self._logger.error("Failed to list databases: %s", e)
            raise BackupConfigurationError(f"Failed to list databases: {str(e)}") from e

    def get_resolved_configuration(
        self,
        global_config: BackupConfig,
        instance_config: InstanceAutoBackupConfig,
        instance_name: str,
        admin_password: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
    ) -> ResolvedBackupConfig:
        """
        Get the resolved backup configuration for inspection.

        Args:
            global_config: Global backup configuration from YAML
            instance_config: Instance-specific auto backup configuration
            instance_name: Name of the instance
            admin_password: Admin password from env_vars.ADMIN_PASSWD
            cli_overrides: Optional CLI parameter overrides

        Returns:
            Resolved backup configuration
        """
        return self._resolve_configuration(
            global_config,
            instance_config,
            instance_name,
            admin_password,
            cli_overrides,
        )

    def _resolve_configuration(
        self,
        global_config: BackupConfig,
        instance_config: InstanceAutoBackupConfig,
        instance_name: str,
        admin_password: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
    ) -> ResolvedBackupConfig:
        """
        Resolve final backup config by merging global, instance, and CLI.

        Priority order (highest to lowest):
        1. CLI overrides
        2. Instance-specific configuration
        3. Global configuration
        """
        # Start with merge of global + instance
        resolved = merge_backup_configs(
            global_config,
            instance_config,
            instance_name,
            admin_password,
        )

        # Apply CLI overrides if provided
        if cli_overrides:
            resolved = self._apply_cli_overrides(resolved, cli_overrides)

        return resolved

    def _apply_cli_overrides(
        self,
        resolved_config: ResolvedBackupConfig,
        cli_overrides: Dict[str, Any],
    ) -> ResolvedBackupConfig:
        """Apply CLI parameter overrides to resolved configuration."""
        # Create a copy to avoid modifying the original
        from dataclasses import replace

        overrides = {}

        # Map CLI parameters to configuration fields
        if "format" in cli_overrides and cli_overrides["format"]:
            overrides["format"] = BackupFormat(cli_overrides["format"])

        if "output_dir" in cli_overrides and cli_overrides["output_dir"]:
            overrides["output_dir"] = cli_overrides["output_dir"]

        if "database" in cli_overrides and cli_overrides["database"]:
            overrides["db_name"] = cli_overrides["database"]

        # Apply overrides
        return replace(resolved_config, **overrides)

    def _validate_resolved_config(self, config: ResolvedBackupConfig):
        """Validate the resolved backup configuration."""
        if not config.is_backup_enabled():
            raise BackupConfigurationError("Backup is disabled for this instance")

        if not config.db_name:
            raise BackupConfigurationError("Database name is required")

        if not config.instance_name:
            raise BackupConfigurationError("Instance name is required")

        if not config.admin_password:
            raise BackupConfigurationError(
                "Admin password is required for XML-RPC backup",
            )
