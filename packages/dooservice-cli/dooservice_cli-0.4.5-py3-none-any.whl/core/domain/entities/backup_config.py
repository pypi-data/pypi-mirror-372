"""Simplified backup configuration entities with automatic instance detection."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class BackupFormat(Enum):
    """Supported backup formats."""

    ZIP = "zip"
    DUMP = "dump"


class BackupFrequency(Enum):
    """Supported backup frequencies."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class BackupSchedule:
    """Backup schedule configuration."""

    frequency: BackupFrequency = BackupFrequency.DAILY
    time: str = "02:00"  # HH:MM format


@dataclass
class BackupRetention:
    """Backup retention policy."""

    days: int = 30
    max_backups: int = 10


@dataclass
class AutoBackupConfig:
    """Configuration for automatic backup scheduling."""

    enabled: bool = False
    schedule: BackupSchedule = field(default_factory=BackupSchedule)
    format: BackupFormat = BackupFormat.ZIP


@dataclass
class BackupConfig:
    """Simplified global backup configuration with essential settings only."""

    enabled: bool = True
    output_dir: Optional[str] = None  # Will use default if None
    retention: BackupRetention = field(default_factory=BackupRetention)
    auto_backup: AutoBackupConfig = field(default_factory=AutoBackupConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "output_dir": self.output_dir or "/opt/dooservice/backups",
            "retention": {
                "days": self.retention.days,
                "max_backups": self.retention.max_backups,
            },
            "auto_backup": {
                "enabled": self.auto_backup.enabled,
                "schedule": {
                    "frequency": self.auto_backup.schedule.frequency.value,
                    "time": self.auto_backup.schedule.time,
                },
                "format": self.auto_backup.format.value,
            },
        }


@dataclass
class InstanceAutoBackupConfig:
    """
    Simplified instance-specific auto backup configuration.

    Only contains the essential fields.
    """

    enabled: bool = True
    db_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "db_name": self.db_name,
        }


@dataclass
class ResolvedBackupConfig:
    """
    Final resolved backup configuration after merging global and instance settings.

    This contains all the information needed to execute a backup.
    """

    # From global config
    enabled: bool
    output_dir: str
    format: BackupFormat
    retention: BackupRetention
    auto_backup_enabled: bool
    auto_backup_schedule: BackupSchedule

    # From instance config
    instance_enabled: bool
    db_name: str
    instance_name: str

    # Automatically detected values
    container_name: str = ""
    xmlrpc_url: str = ""
    admin_password: str = ""  # Will be loaded from env_vars.ADMIN_PASSWD

    def is_backup_enabled(self) -> bool:
        """Check if backup is enabled (both global and instance must be enabled)."""
        return self.enabled and self.instance_enabled

    def get_xmlrpc_url(self) -> str:
        """Get the XML-RPC URL for this instance."""
        if self.xmlrpc_url:
            return self.xmlrpc_url
        # Auto-generate URL based on instance name
        return f"http://web_{self.instance_name}:8069"

    def get_container_name(self) -> str:
        """Get the Docker container name for this instance."""
        if self.container_name:
            return self.container_name
        # Auto-generate container name based on instance name
        return f"web_{self.instance_name}"

    def should_run_auto_backup(
        self,
        current_time: datetime = None,
        last_backup_time: datetime = None,
    ) -> bool:
        """
        Check if automatic backup should run based on schedule.

        Args:
            current_time: Current datetime
            last_backup_time: When the last backup was executed
        """
        if not self.is_backup_enabled() or not self.auto_backup_enabled:
            return False

        if current_time is None:
            current_time = datetime.now()

        # Parse target time for today
        try:
            hour, minute = map(int, self.auto_backup_schedule.time.split(":"))
            target_time = current_time.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0,
            )
        except ValueError:
            # Default to 2:00 AM if parsing fails
            target_time = current_time.replace(
                hour=2,
                minute=0,
                second=0,
                microsecond=0,
            )

        # Check if we already ran backup today
        if last_backup_time:
            # If last backup was today, don't run again
            if (
                last_backup_time.date() == current_time.date()
                and self.auto_backup_schedule.frequency == BackupFrequency.DAILY
            ):
                return False

            # For weekly backups, check if we ran this week
            if (
                self.auto_backup_schedule.frequency == BackupFrequency.WEEKLY
                and last_backup_time.isocalendar()[1] == current_time.isocalendar()[1]
                and last_backup_time.year == current_time.year
            ):
                return False

            # For monthly backups, check if we ran this month
            if (
                self.auto_backup_schedule.frequency == BackupFrequency.MONTHLY
                and last_backup_time.month == current_time.month
                and last_backup_time.year == current_time.year
            ):
                return False

        # Check if current time is exactly at the scheduled time (within same minute)
        # This prevents running multiple times in the same minute
        current_minute = current_time.replace(second=0, microsecond=0)
        target_minute = target_time.replace(second=0, microsecond=0)

        # Only run if we're exactly at the target minute
        return current_minute == target_minute

        # Only run if it's the right time and we haven't run today/week/month

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "output_dir": self.output_dir,
            "format": self.format.value,
            "retention": {
                "days": self.retention.days,
                "max_backups": self.retention.max_backups,
            },
            "auto_backup_enabled": self.auto_backup_enabled,
            "auto_backup_schedule": {
                "frequency": self.auto_backup_schedule.frequency.value,
                "time": self.auto_backup_schedule.time,
            },
            "instance_enabled": self.instance_enabled,
            "db_name": self.db_name,
            "instance_name": self.instance_name,
            "container_name": self.get_container_name(),
            "xmlrpc_url": self.get_xmlrpc_url(),
            "admin_password": "***masked***",  # Don't expose password
        }


def merge_backup_configs(
    global_config: BackupConfig,
    instance_config: InstanceAutoBackupConfig,
    instance_name: str,
    admin_password: str = "",
) -> ResolvedBackupConfig:
    """Merge global and instance backup configurations."""
    return ResolvedBackupConfig(
        # Global settings
        enabled=global_config.enabled,
        output_dir=global_config.output_dir or "/opt/dooservice/backups",
        format=global_config.auto_backup.format,
        retention=global_config.retention,
        auto_backup_enabled=global_config.auto_backup.enabled,
        auto_backup_schedule=global_config.auto_backup.schedule,
        # Instance settings
        instance_enabled=instance_config.enabled,
        db_name=instance_config.db_name or f"{instance_name}_db",
        instance_name=instance_name,
        # Auto-detected settings
        admin_password=admin_password,
    )


# Aliases for backward compatibility
BackupScheduleConfig = BackupSchedule
BackupRetentionConfig = BackupRetention
GlobalBackupConfig = BackupConfig
