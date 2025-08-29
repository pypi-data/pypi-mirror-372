"""XML-RPC backup executor implementation with automatic instance detection."""

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backup.domain.entities.backup_metadata import BackupMetadata
from backup.domain.services.backup_executor import BackupExecutor
from core.domain.entities.backup_config import ResolvedBackupConfig
from shared.errors.backup_error import BackupConfigurationError, BackupExecutionError

_logger = logging.getLogger(__name__)


class XMLRPCBackupExecutor(BackupExecutor):
    """
    XML-RPC backup executor implementation using existing Docker infrastructure.

    This implementation automatically detects instance URLs and containers,
    and uses ADMIN_PASSWD as the master password for XML-RPC operations.
    """

    def __init__(self, docker_repository):
        """Initialize the XML-RPC backup executor with Docker repository."""
        self._logger = _logger
        self._docker_repository = docker_repository

    def execute_backup(
        self,
        backup_config: ResolvedBackupConfig,
        output_path: Optional[Path] = None,
    ) -> BackupMetadata:
        """Execute a backup using XML-RPC API with automatic instance detection."""
        try:
            self._logger.info(
                "Starting XML-RPC backup for database: %s",
                backup_config.db_name,
            )

            # Validate configuration
            self._validate_backup_config(backup_config)

            # Determine output path
            if output_path is None:
                output_path = (
                    Path(backup_config.output_dir) / backup_config.instance_name
                )
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_format = backup_config.format.value
            backup_filename = f"{backup_config.db_name}_{timestamp}.{backup_format}"
            backup_filepath = output_path / backup_filename

            # Execute backup within Docker container
            backup_data = self._execute_xmlrpc_backup_in_container(backup_config)

            # Save backup file
            with open(backup_filepath, "wb") as f:
                f.write(backup_data)

            # Create backup metadata
            import hashlib

            # Calculate checksum
            with open(backup_filepath, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            metadata = BackupMetadata(
                backup_id=f"{backup_config.instance_name}_{timestamp}",
                instance_name=backup_config.instance_name,
                created_at=datetime.now(),
                file_path=str(backup_filepath),
                file_size=backup_filepath.stat().st_size,
                database_included=True,
                filestore_included=True,  # ZIP format includes filestore
                compressed=True,  # Both zip and dump are compressed
                checksum=checksum,
            )

            # Apply retention policy
            self._apply_retention_policy(backup_config, Path(backup_filepath).parent)

            self._logger.info("Backup completed successfully: %s", backup_filepath)
            return metadata

        except (
            BackupConfigurationError,
            BackupExecutionError,
            OSError,
            ValueError,
        ) as e:
            self._logger.error("Backup execution failed: %s", e)
            raise BackupExecutionError(f"XML-RPC backup failed: {str(e)}") from e
        except Exception as e:  # noqa: BLE001
            self._logger.error("Backup execution failed: %s", e)
            raise BackupExecutionError(f"XML-RPC backup failed: {str(e)}") from e

    def _execute_xmlrpc_backup_in_container(
        self,
        backup_config: ResolvedBackupConfig,
    ) -> bytes:
        """Execute XML-RPC backup within Docker container using simplified approach."""
        # Create the backup script that outputs base64 for safe text transport
        backup_script = f'''
import xmlrpc.client
import base64
import sys

url = "{backup_config.get_xmlrpc_url()}"
db_name = "{backup_config.db_name}"
master_pwd = "{backup_config.admin_password}"
backup_format = "{backup_config.format.value}"

try:
    # Connection to db service (same as provided script)
    db_proxy = xmlrpc.client.ServerProxy(f"{{url}}/xmlrpc/db")

    # Execute backup (returns base64 string)
    backup_b64 = db_proxy.dump(master_pwd, db_name, backup_format)

    # Output the base64 data directly for text transport
    print(backup_b64)

except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
    sys.exit(1)
'''

        # Execute the script within the container using Docker repository
        container_name = backup_config.get_container_name()

        self._logger.debug("Executing backup command in container: %s", container_name)

        # Use existing Docker implementation for command execution
        # Execute the Python script directly without writing to file
        # Escape the script properly for shell execution
        import shlex

        escaped_script = shlex.quote(backup_script)

        exec_cmd = f"python3 -c {escaped_script}"
        exit_code, output = self._docker_repository.exec_command(
            container_name,
            exec_cmd,
        )

        if exit_code != 0:
            raise BackupExecutionError(f"XML-RPC backup command failed: {output}")

        # Decode the base64 output to get binary data
        import base64

        try:
            return base64.b64decode(output.strip())
        except (ValueError, TypeError) as e:
            raise BackupExecutionError(f"Failed to decode backup data: {e}") from e

    def test_connection(self, backup_config: ResolvedBackupConfig) -> Dict[str, Any]:
        """Test connection to Odoo server using XML-RPC with automatic detection."""
        try:
            # Create connection test script
            test_script = f'''
import xmlrpc.client
import json

url = "{backup_config.get_xmlrpc_url()}"

try:
    # Test connection to common service
    common = xmlrpc.client.ServerProxy(f"{{url}}/xmlrpc/common")
    version_info = common.version()

    # Test db service
    db_proxy = xmlrpc.client.ServerProxy(f"{{url}}/xmlrpc/db")
    db_list = db_proxy.list()

    result = {{
        "success": True,
        "version_info": version_info,
        "databases": db_list,
        "target_db_exists": "{backup_config.db_name}" in db_list,
        "container_name": "{backup_config.get_container_name()}",
        "xmlrpc_url": "{backup_config.get_xmlrpc_url()}"
    }}

    print(json.dumps(result))

except Exception as e:
    result = {{
        "success": False,
        "error": str(e),
        "container_name": "{backup_config.get_container_name()}",
        "xmlrpc_url": "{backup_config.get_xmlrpc_url()}"
    }}
    print(json.dumps(result))
'''

            container_name = backup_config.get_container_name()

            import shlex

            escaped_script = shlex.quote(test_script)
            command = f"python3 -c {escaped_script}"

            exit_code, output = self._docker_repository.exec_command(
                container_name,
                command,
            )

            if exit_code != 0:
                return {
                    "success": False,
                    "error": f"Container execution failed: {output}",
                    "container_name": container_name,
                    "xmlrpc_url": backup_config.get_xmlrpc_url(),
                }

            # Parse JSON response
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Invalid response: {output}",
                    "container_name": container_name,
                    "xmlrpc_url": backup_config.get_xmlrpc_url(),
                }

        except Exception as e:  # noqa: BLE001
            return {
                "success": False,
                "error": str(e),
                "container_name": backup_config.get_container_name(),
                "xmlrpc_url": backup_config.get_xmlrpc_url(),
            }

    def list_databases(self, backup_config: ResolvedBackupConfig) -> List[str]:
        """List available databases on the Odoo server."""
        try:
            # Create database listing script
            list_script = f'''
import xmlrpc.client
import json

url = "{backup_config.get_xmlrpc_url()}"

try:
    db_proxy = xmlrpc.client.ServerProxy(f"{{url}}/xmlrpc/db")
    db_list = db_proxy.list()
    print(json.dumps(db_list))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
'''

            container_name = backup_config.get_container_name()

            import shlex

            escaped_script = shlex.quote(list_script)
            command = f"python3 -c {escaped_script}"

            exit_code, output = self._docker_repository.exec_command(
                container_name,
                command,
            )

            if exit_code != 0:
                raise BackupConfigurationError(f"Failed to list databases: {output}")

            try:
                response = json.loads(output)
                if isinstance(response, dict) and "error" in response:
                    raise BackupConfigurationError(
                        f"Database listing failed: {response['error']}",
                    )
                return response
            except json.JSONDecodeError:
                raise BackupConfigurationError(f"Invalid response: {output}") from None

        except BackupConfigurationError:
            raise
        except Exception as e:  # noqa: BLE001
            raise BackupConfigurationError(f"Failed to list databases: {str(e)}") from e

    def _validate_backup_config(self, config: ResolvedBackupConfig):
        """Validate the resolved backup configuration."""
        if not config.is_backup_enabled():
            raise BackupConfigurationError("Backup is not enabled for this instance")

        if not config.db_name:
            raise BackupConfigurationError("Database name is required")

        if not config.instance_name:
            raise BackupConfigurationError("Instance name is required")

        if not config.admin_password:
            raise BackupConfigurationError(
                "Admin password is required for XML-RPC backup",
            )

        # Test container availability using Docker repository
        container_name = config.get_container_name()
        container_status = self._docker_repository.status(container_name)

        if container_status == "not found":
            raise BackupConfigurationError(
                f"Container {container_name} is not available",
            )

        if container_status != "running":
            raise BackupConfigurationError(
                f"Container {container_name} is not running "
                f"(status: {container_status})",
            )

    def _apply_retention_policy(self, config: ResolvedBackupConfig, backup_dir: Path):
        """Apply retention policy to clean up old backups."""
        try:
            if config.retention.days <= 0 and config.retention.max_backups <= 0:
                return  # No retention policy

            # Get all backup files for this database
            pattern = f"{config.db_name}_*.{config.format.value}"
            backup_files = list(backup_dir.glob(pattern))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            files_to_delete = []

            # Apply max_backups limit
            if (
                config.retention.max_backups > 0
                and len(backup_files) > config.retention.max_backups
            ):
                files_to_delete.extend(backup_files[config.retention.max_backups :])

            # Apply days limit
            if config.retention.days > 0:
                cutoff_time = datetime.now().timestamp() - (
                    config.retention.days * 24 * 3600
                )
                old_files = [f for f in backup_files if f.stat().st_mtime < cutoff_time]
                files_to_delete.extend(old_files)

            # Remove duplicates and delete files
            files_to_delete = list(set(files_to_delete))
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    self._logger.info("Deleted old backup: %s", file_path)
                except OSError as e:
                    self._logger.warning(
                        "Failed to delete old backup %s: %s",
                        file_path,
                        e,
                    )

        except Exception as e:  # noqa: BLE001
            self._logger.warning("Failed to apply retention policy: %s", e)
            # Don't fail the backup for retention issues
