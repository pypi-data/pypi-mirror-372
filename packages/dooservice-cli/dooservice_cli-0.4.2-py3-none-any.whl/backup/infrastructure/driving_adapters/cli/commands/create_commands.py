"""Backup creation commands."""

from pathlib import Path
from typing import Any, Dict

import click
import yaml

from backup.application.use_cases.backup_use_case import BackupUseCase
from backup.infrastructure.driven_adapters.xmlrpc_backup_executor import (
    XMLRPCBackupExecutor,
)
from backup.infrastructure.driving_adapters.cli.config_context import config_option
from core.domain.entities.backup_config import (
    BackupConfig,
    BackupFormat,
    BackupFrequency,
    BackupRetention,
    BackupSchedule,
    InstanceAutoBackupConfig,
)
from instance.infrastructure.driven_adapters.docker_instance_repository import (
    DockerInstanceRepository,
)
from shared.errors.backup_error import BackupConfigurationError


@click.command("create")
@config_option()
@click.argument("instance", required=True)
@click.option("--database", "-d", help="Database name (overrides config)")
@click.option("--format", type=click.Choice(["zip", "dump"]), help="Backup format")
@click.option("--output", "-o", help="Output directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def create_backup(
    config: str, instance: str, database: str, format: str, output: str, verbose: bool
):
    """
    Create a backup for INSTANCE.

    Examples:
      dooservice backup create myapp
      dooservice backup create myapp --database prod --format zip
    """
    try:
        # Load configuration
        config_path = Path(config)
        if not config_path.exists():
            raise click.ClickException(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            yaml_data = yaml.safe_load(f)

        # Extract configurations
        global_config, instance_config, admin_password = _extract_backup_configs(
            yaml_data,
            instance,
        )

        # Apply CLI overrides
        cli_overrides = {}
        if database:
            cli_overrides["database"] = database
        if format:
            cli_overrides["format"] = format
        if output:
            cli_overrides["output_dir"] = output

        # Initialize backup system
        docker_repository = DockerInstanceRepository()
        backup_executor = XMLRPCBackupExecutor(docker_repository)
        backup_use_case = BackupUseCase(backup_executor)

        # Execute backup
        click.echo(f"🚀 Creating backup for: {instance}")

        metadata = backup_use_case.execute_backup(
            global_config,
            instance_config,
            instance,
            admin_password,
            cli_overrides,
        )

        click.echo("✅ Backup created successfully!")
        click.echo(f"📁 File: {metadata.file_path}")
        click.echo(f"📊 Size: {_format_bytes(metadata.file_size)}")
        click.echo(f"🗄️  Database: {metadata.instance_name}")

        if verbose:
            click.echo("\n📋 Details:")
            click.echo(f"   Format: {format or 'zip'}")
            click.echo("   Method: XML-RPC (auto)")
            click.echo(f"   Checksum: {metadata.checksum[:16]}...")

    except (BackupConfigurationError, yaml.YAMLError, FileNotFoundError) as e:
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e


def _extract_backup_configs(yaml_data: Dict[str, Any], instance_name: str) -> tuple:
    """Extract simplified backup configurations from YAML data."""
    # Extract global backup config
    global_backup_data = yaml_data.get("backup", {})

    # Build retention config
    retention_data = global_backup_data.get("retention", {})
    retention = BackupRetention(
        days=retention_data.get("days", 30),
        max_backups=retention_data.get("max_backups", 10),
    )

    # Build auto backup schedule
    auto_backup_data = global_backup_data.get("auto_backup", {})
    schedule_data = auto_backup_data.get("schedule", {})
    schedule = BackupSchedule(
        frequency=BackupFrequency(schedule_data.get("frequency", "daily")),
        time=schedule_data.get("time", "02:00"),
    )

    # Build auto backup config
    from core.domain.entities.backup_config import AutoBackupConfig

    auto_backup = AutoBackupConfig(
        enabled=auto_backup_data.get("enabled", False),
        schedule=schedule,
        format=BackupFormat(global_backup_data.get("format", "zip")),
    )

    # Build global config
    global_config = BackupConfig(
        enabled=global_backup_data.get("enabled", True),
        output_dir=global_backup_data.get("output_dir"),
        retention=retention,
        auto_backup=auto_backup,
    )

    # Extract instance config
    instances_data = yaml_data.get("instances", {})
    instance_data = instances_data.get(instance_name, {})

    if not instance_data:
        raise BackupConfigurationError(
            f"Instance '{instance_name}' not found in configuration",
        )

    # Build instance config (only auto_backup section)
    auto_backup_data = instance_data.get("auto_backup", {})

    instance_config = InstanceAutoBackupConfig(
        enabled=auto_backup_data.get("enabled", True),
        db_name=auto_backup_data.get("db_name", f"{instance_name}_db"),
    )

    # Extract admin password from env_vars
    env_vars = instance_data.get("env_vars", {})
    admin_password = env_vars.get("ADMIN_PASSWD", "")

    if not admin_password:
        raise BackupConfigurationError(
            f"ADMIN_PASSWD not found in env_vars for instance '{instance_name}'",
        )

    return global_config, instance_config, admin_password


def _format_bytes(bytes_size: int) -> str:
    """Format bytes into human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} PB"
