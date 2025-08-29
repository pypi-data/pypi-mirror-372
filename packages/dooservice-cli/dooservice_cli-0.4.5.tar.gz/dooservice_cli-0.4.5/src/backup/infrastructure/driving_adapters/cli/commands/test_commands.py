"""Backup testing and validation commands."""

import json
from pathlib import Path
from typing import Any, Dict

import click
import yaml

from backup.application.use_cases.backup_use_case import BackupUseCase
from backup.infrastructure.driven_adapters.xmlrpc_backup_executor import (
    XMLRPCBackupExecutor,
)
from backup.infrastructure.driving_adapters.cli.commands.create_commands import (
    _extract_backup_configs,
)
from backup.infrastructure.driving_adapters.cli.config_context import config_option
from instance.infrastructure.driven_adapters.docker_instance_repository import (
    DockerInstanceRepository,
)
from shared.errors.backup_error import BackupConfigurationError


@click.command("test")
@config_option()
@click.argument("instance", required=True)
@click.option("--database", "-d", help="Database name to test")
def test_backup(config: str, instance: str, database: str):
    """
    Test backup connection for INSTANCE.

    Examples:
      dooservice backup test myapp
      dooservice backup test myapp --database prod
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

        # Initialize backup system
        docker_repository = DockerInstanceRepository()
        backup_executor = XMLRPCBackupExecutor(docker_repository)
        backup_use_case = BackupUseCase(backup_executor)

        # Test connection
        click.echo(f"🔍 Testing backup for: {instance}")

        test_result = backup_use_case.test_backup_configuration(
            global_config,
            instance_config,
            instance,
            admin_password,
            cli_overrides,
        )

        _display_test_results(test_result)

    except (BackupConfigurationError, yaml.YAMLError, FileNotFoundError) as e:
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e


@click.command("databases")
@config_option()
@click.argument("instance", required=True)
def list_databases(config: str, instance: str):
    """
    List databases available for backup in INSTANCE.

    Examples:
      dooservice backup databases myapp
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

        # Initialize backup system
        docker_repository = DockerInstanceRepository()
        backup_executor = XMLRPCBackupExecutor(docker_repository)
        backup_use_case = BackupUseCase(backup_executor)

        # List databases
        databases = backup_use_case.list_available_databases(
            global_config,
            instance_config,
            instance,
            admin_password,
        )

        click.echo(f"\n📋 Databases in '{instance}':")
        click.echo("-" * 40)
        for db in databases:
            marker = "🎯" if db == instance_config.db_name else "🗄️ "
            click.echo(f"{marker} {db}")
        click.echo("-" * 40)
        click.echo(f"Total: {len(databases)} databases")

        if instance_config.db_name in databases:
            click.echo(f"✅ Target '{instance_config.db_name}' found")
        else:
            click.echo(f"⚠️  Target '{instance_config.db_name}' not found")

    except (BackupConfigurationError, yaml.YAMLError, FileNotFoundError) as e:
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e


@click.command("config")
@config_option()
@click.argument("instance", required=True)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show_config(config: str, instance: str, output_json: bool):
    """
    Show backup configuration for INSTANCE.

    Examples:
      dooservice backup config myapp
      dooservice backup config myapp --json
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

        # Initialize backup system
        docker_repository = DockerInstanceRepository()
        backup_executor = XMLRPCBackupExecutor(docker_repository)
        backup_use_case = BackupUseCase(backup_executor)

        # Get resolved configuration
        resolved_config = backup_use_case.get_resolved_configuration(
            global_config,
            instance_config,
            instance,
            admin_password,
        )

        if output_json:
            config_dict = resolved_config.to_dict()
            click.echo(json.dumps(config_dict, indent=2))
        else:
            _display_backup_config(resolved_config, verbose=True)

    except (BackupConfigurationError, yaml.YAMLError, FileNotFoundError) as e:
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ {e}", err=True)
        raise click.Abort() from e


def _display_test_results(result: Dict[str, Any]):
    """Display test results in table format."""
    click.echo("\n🧪 Connection Test")
    click.echo("=" * 30)

    if result.get("success"):
        click.echo("✅ Connection: SUCCESS")

        if "version_info" in result:
            version = result["version_info"]
            click.echo(f"📊 Odoo: {version.get('server_version', 'Unknown')}")

        if "databases" in result:
            databases = result["databases"]
            click.echo(f"🗄️  Databases: {len(databases)}")
            for db in databases[:3]:  # Show first 3
                click.echo(f"   • {db}")
            if len(databases) > 3:
                click.echo(f"   ... and {len(databases) - 3} more")

        if "target_db_exists" in result:
            status = "✅ Found" if result["target_db_exists"] else "❌ Not Found"
            click.echo(f"🎯 Target DB: {status}")
    else:
        click.echo("❌ Connection: FAILED")
        if "error" in result:
            click.echo(f"💥 Error: {result['error']}")

    # Show auto-detected values
    if "container_name" in result:
        click.echo(f"\n🐳 Container: {result['container_name']}")
    if "xmlrpc_url" in result:
        click.echo(f"🔗 URL: {result['xmlrpc_url']}")


def _display_backup_config(config, verbose: bool = False):
    """Display backup configuration in table format."""
    click.echo("\n📋 Backup Configuration")
    click.echo("=" * 40)
    click.echo(f"Instance: {config.instance_name}")
    click.echo(f"Database: {config.db_name}")
    click.echo(
        f"Status: {'✅ Active' if config.is_backup_enabled() else '❌ Disabled'}",
    )

    click.echo("\n🔗 Auto-detected:")
    click.echo(f"  Container: {config.get_container_name()}")
    click.echo(f"  URL: {config.get_xmlrpc_url()}")

    click.echo("\n📁 Output:")
    click.echo(f"  Directory: {config.output_dir}")
    click.echo(f"  Format: {config.format.value}")

    if verbose:
        click.echo("\n🗑️  Retention:")
        click.echo(f"  Days: {config.retention.days}")
        click.echo(f"  Max: {config.retention.max_backups}")

        click.echo("\n⏰ Auto backup:")
        click.echo(f"  Enabled: {'✅' if config.auto_backup_enabled else '❌'}")
        click.echo(
            f"  Schedule: {config.auto_backup_schedule.frequency.value} "
            f"at {config.auto_backup_schedule.time}"
        )
