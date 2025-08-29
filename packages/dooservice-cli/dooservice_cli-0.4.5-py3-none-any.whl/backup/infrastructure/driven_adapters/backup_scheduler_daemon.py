#!/usr/bin/env python3
"""
Backup scheduler daemon - automated backups using GenericDaemonBase.

This daemon inherits from GenericDaemonBase and implements backup scheduling.
"""

import argparse
from datetime import datetime, time
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

import yaml

# Add src to path so we can import our modules
src_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_path))

from backup.application.use_cases.backup_use_case import BackupUseCase  # noqa: E402
from backup.infrastructure.driven_adapters.xmlrpc_backup_executor import (  # noqa: E402
    XMLRPCBackupExecutor,
)
from core.domain.entities.backup_config import (  # noqa: E402
    AutoBackupConfig,
    BackupConfig,
    BackupFormat,
    BackupFrequency,
    BackupRetention,
    BackupSchedule,
    InstanceAutoBackupConfig,
)
from instance.infrastructure.driven_adapters.docker_instance_repository import (  # noqa: E402
    DockerInstanceRepository,
)
from shared.daemon import DaemonConfig, ScheduledDaemonBase  # noqa: E402
from shared.errors.backup_error import (  # noqa: E402
    BackupConfigurationError,
    BackupExecutionError,
)


class BackupSchedulerDaemon(ScheduledDaemonBase):
    """
    Backup scheduler daemon implementation.

    This daemon implements automated backups by extending ScheduledDaemonBase.
    It executes backups at specific configured times instead of continuous polling.
    """

    def __init__(self, config_file: str):
        """
        Initialize backup scheduler daemon.

        Args:
            config_file: Path to dooservice.yml configuration file
        """
        self.config_file = config_file
        self.last_backup_times: Dict[str, datetime] = {}

        super().__init__("backup_scheduler")

    def _create_default_config(self) -> DaemonConfig:
        """Create default configuration for backup scheduler daemon."""
        return DaemonConfig(
            name="backup_scheduler",
            working_directory=Path.cwd(),
            config_file=Path(self.config_file),
            startup_args={
                "config_file": self.config_file,
            },
        )

    def _initialize_daemon(self) -> None:
        """Initialize backup scheduler daemon resources."""
        self.logger.info("Initializing backup scheduler daemon")
        self.logger.info("Config file: %s", self.config_file)

        # Initialize backup components
        docker_repo = DockerInstanceRepository()
        backup_executor = XMLRPCBackupExecutor(docker_repo)
        self.backup_use_case = BackupUseCase(backup_executor)

    def _cleanup_daemon(self) -> None:
        """Clean up backup scheduler daemon resources."""
        self.logger.info("Cleaning up backup scheduler daemon resources")
        # No specific cleanup needed for backup scheduler

    def get_scheduled_times(self) -> List[time]:
        """Get list of times when backups should be executed daily."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            # Get backup schedule from config
            backup_config = data.get("backup", {})
            auto_backup = backup_config.get("auto_backup", {})

            if not auto_backup.get("enabled", False):
                self.logger.info("Auto backup is disabled in configuration")
                return []

            schedule_config = auto_backup.get("schedule", {})
            time_str = schedule_config.get("time", "02:00")

            # Parse time string (format: HH:MM)
            try:
                hour, minute = map(int, time_str.split(":"))
                scheduled_time = time(hour, minute)
                self.logger.info("Backup scheduled for %s daily", time_str)
                return [scheduled_time]
            except ValueError:
                self.logger.error("Invalid time format in config: %s", time_str)
                return []

        except (OSError, yaml.YAMLError, KeyError) as e:
            self.logger.error("Error reading backup schedule from config: %s", e)
            return []

    def execute_scheduled_task(self) -> None:
        """Execute backup task for all enabled instances."""
        current_time = datetime.now()
        enabled_instances = self._get_enabled_instances()

        self.logger.info(
            "Starting scheduled backup execution for %d instances",
            len(enabled_instances),
        )

        backup_results = []
        for instance_name in enabled_instances:
            try:
                result = self._backup_instance(instance_name, current_time)
                backup_results.append(
                    {
                        "instance": instance_name,
                        "success": result is not None,
                        "file_path": result.file_path if result else None,
                    }
                )
                if result:
                    self.logger.info(
                        "Backup completed for %s: %s", instance_name, result.file_path
                    )
            except (BackupExecutionError, BackupConfigurationError, OSError) as e:
                self.logger.error("Backup failed for %s: %s", instance_name, e)
                backup_results.append(
                    {
                        "instance": instance_name,
                        "success": False,
                        "error": str(e),
                    }
                )

        # Log execution results
        successful_backups = [r for r in backup_results if r["success"]]
        failed_backups = [r for r in backup_results if not r["success"]]

        self.logger.info(
            "Backup execution completed: %d successful, %d failed",
            len(successful_backups),
            len(failed_backups),
        )

    def _get_enabled_instances(self) -> List[str]:
        """Get instances with auto backup enabled."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            global_backup = data.get("backup", {})
            if not global_backup.get("auto_backup", {}).get("enabled", False):
                return []

            enabled = []
            instances = data.get("instances", {})
            for name, config in instances.items():
                if config.get("auto_backup", {}).get("enabled", False) and config.get(
                    "env_vars", {}
                ).get("ADMIN_PASSWD"):
                    enabled.append(name)

            return enabled
        except (OSError, yaml.YAMLError, KeyError) as e:
            self.logger.error("Error loading config: %s", e)
            return []

    def _backup_instance(self, instance_name: str, current_time: datetime):
        """Execute backup for a specific instance."""
        with open(self.config_file) as f:
            data = yaml.safe_load(f)

        global_config, instance_config, admin_password = self._extract_configs(
            data, instance_name
        )

        self.logger.info("Executing backup for instance: %s", instance_name)

        metadata = self.backup_use_case.execute_backup(
            global_config, instance_config, instance_name, admin_password
        )

        self.last_backup_times[instance_name] = current_time
        return metadata

    def _extract_configs(self, data: dict, instance_name: str) -> tuple:
        """Extract backup configurations from YAML data."""
        # Global config
        global_backup = data.get("backup", {})
        retention = BackupRetention(
            days=global_backup.get("retention", {}).get("days", 30),
            max_backups=global_backup.get("retention", {}).get("max_backups", 10),
        )

        auto_backup_data = global_backup.get("auto_backup", {})
        schedule = BackupSchedule(
            frequency=BackupFrequency(
                auto_backup_data.get("schedule", {}).get("frequency", "daily")
            ),
            time=auto_backup_data.get("schedule", {}).get("time", "02:00"),
        )

        auto_backup = AutoBackupConfig(
            enabled=auto_backup_data.get("enabled", False),
            schedule=schedule,
            format=BackupFormat(global_backup.get("format", "zip")),
        )

        global_config = BackupConfig(
            enabled=global_backup.get("enabled", True),
            output_dir=global_backup.get("output_dir"),
            retention=retention,
            auto_backup=auto_backup,
        )

        # Instance config
        instance_data = data.get("instances", {}).get(instance_name, {})
        if not instance_data:
            raise BackupConfigurationError(f"Instance '{instance_name}' not found")

        instance_config = InstanceAutoBackupConfig(
            enabled=instance_data.get("auto_backup", {}).get("enabled", True),
            db_name=instance_data.get("auto_backup", {}).get(
                "db_name", f"{instance_name}_db"
            ),
        )

        admin_password = instance_data.get("env_vars", {}).get("ADMIN_PASSWD", "")
        if not admin_password:
            raise BackupConfigurationError(
                f"ADMIN_PASSWD not found for instance '{instance_name}'"
            )

        return global_config, instance_config, admin_password

    def _get_daemon_metadata(self) -> Dict[str, Any]:
        """Get backup scheduler daemon specific metadata."""
        metadata = super()._get_daemon_metadata()
        metadata.update(
            {
                "daemon_type": "BackupSchedulerDaemon",
                "config_file": self.config_file,
                "description": "Time-scheduled backup daemon for Odoo instances",
                "scheduled_times": [
                    t.strftime("%H:%M") for t in self.get_scheduled_times()
                ],
                "last_backup_times": {
                    instance: backup_time.isoformat()
                    for instance, backup_time in self.last_backup_times.items()
                },
            }
        )
        return metadata


def main():
    """Main entry point for backup scheduler daemon."""
    parser = argparse.ArgumentParser(description="Backup scheduler daemon")
    parser.add_argument("--config", "-c", required=True, help="Path to dooservice.yml")

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)

    # Create and start daemon
    daemon = BackupSchedulerDaemon(args.config)
    daemon.start()


if __name__ == "__main__":
    main()
