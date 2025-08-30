"""CLI commands for snapshot management."""

import click

from core.domain.services.config_service import create_config_service
from core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from snapshot.application.use_cases.create_snapshot import CreateSnapshotUseCase
from snapshot.infrastructure.driven_adapters.filesystem_snapshot_repository import (
    FilesystemSnapshotRepository,
)


@click.group(name="snapshot")
def snapshot_group():
    """Manage instance snapshots."""


@snapshot_group.command(name="create")
@click.argument("instance_name")
@click.option("--tag", "-t", help="Tag for the snapshot (e.g., v1.0.0)")
@click.option("--description", "-d", help="Description for the snapshot")
@click.option("--no-backup", is_flag=True, help="Don't include full backup in snapshot")
@click.option(
    "--file",
    "-f",
    "config_file",
    default="dooservice.yml",
    help="Configuration file",
)
def create_snapshot_cmd(
    instance_name: str,
    tag: str,
    description: str,
    no_backup: bool,
    config_file: str,
):
    """
    Create a snapshot of an instance's complete state.

    Snapshots capture configuration, repository states, installed modules,
    and optionally a full backup of data.
    """
    try:
        # Load configuration and resolve placeholders
        config_repo = YAMLConfigRepository(config_file)
        config_service = create_config_service()
        config = config_service.validate(config_repo.load())

        if instance_name not in config.instances:
            click.secho(f"Error: Instance '{instance_name}' not found", fg="red")
            return

        instance_config = config.instances[instance_name]

        # Resolve placeholders
        from dataclasses import asdict

        from core.infrastructure.driven_adapters.regex_placeholder_service import (
            RegexPlaceholderService,
        )

        placeholder_service = RegexPlaceholderService()
        resolved_config = instance_config

        for _ in range(5):
            context = asdict(resolved_config)
            context["name"] = instance_name
            resolved_config = placeholder_service.resolve(resolved_config, context)

        # Create snapshot
        snapshot_repo = FilesystemSnapshotRepository()
        create_snapshot_use_case = CreateSnapshotUseCase(snapshot_repo)

        click.secho(f"➤ Creating snapshot for instance '{instance_name}'...", bold=True)

        if tag:
            click.secho(f"  Tag: {tag}", dim=True)
        if description:
            click.secho(f"  Description: {description}", dim=True)

        if not no_backup:
            click.secho("  Including full backup...", dim=True)

        snapshot = create_snapshot_use_case.execute(
            instance_config=resolved_config,
            instance_name=instance_name,
            tag=tag,
            description=description,
            include_backup=not no_backup,
        )

        click.secho("✓ Snapshot created successfully!", fg="green")
        click.secho(f"  Snapshot ID: {snapshot.short_id}")
        click.secho(f"  Created: {snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if snapshot.tag:
            click.secho(f"  Tag: {snapshot.tag}")
        if snapshot.backup_id:
            click.secho(f"  Backup ID: {snapshot.backup_id}")

        click.secho(f"  Repositories: {len(snapshot.repositories)}")
        click.secho(f"  Modules: {len(snapshot.installed_modules)}")

    except (OSError, ValueError, RuntimeError) as e:
        click.secho(f"Error creating snapshot: {e}", fg="red")


@snapshot_group.command(name="list")
@click.option("--instance", "-i", help="Filter by instance name")
@click.option("--tag", "-t", help="Filter by tag")
def list_snapshots_cmd(instance: str, tag: str):
    """List available snapshots."""
    try:
        snapshot_repo = FilesystemSnapshotRepository()
        snapshots = snapshot_repo.list_snapshots(instance_name=instance, tag=tag)

        if not snapshots:
            if instance or tag:
                click.secho("No snapshots found matching criteria", fg="yellow")
            else:
                click.secho("No snapshots found", fg="yellow")
            return

        click.secho("\n📸 Available Snapshots", bold=True)
        click.secho("-" * 80)

        header = (
            f"{'ID':<10} {'Tag':<15} {'Instance':<15} {'Created':<20} {'Modules':<8}"
        )
        click.secho(header, bold=True)
        click.secho("-" * 80)

        for snapshot in snapshots:
            tag_display = (snapshot.tag or "")[:14]
            row = (
                f"{snapshot.short_id:<10} "
                f"{tag_display:<15} "
                f"{snapshot.instance_name:<15} "
                f"{snapshot.created_at.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{len(snapshot.installed_modules):<8}"
            )
            click.secho(row)

            if snapshot.description:
                click.secho(f"{'':>10} {snapshot.description}", dim=True)

        click.secho(f"\nTotal: {len(snapshots)} snapshot(s)")

    except (OSError, ValueError, RuntimeError) as e:
        click.secho(f"Error listing snapshots: {e}", fg="red")


@snapshot_group.command(name="restore")
@click.argument("snapshot_id")
@click.argument("target_instance")
@click.option("--no-data", is_flag=True, help="Don't restore backup data")
@click.option("--no-modules", is_flag=True, help="Don't restore module states")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def restore_snapshot_cmd(
    snapshot_id: str,
    target_instance: str,
    no_data: bool,
    no_modules: bool,
    yes: bool,
):
    """Restore an instance from a snapshot."""
    try:
        snapshot_repo = FilesystemSnapshotRepository()
        snapshot = snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            click.secho(f"Error: Snapshot '{snapshot_id}' not found", fg="red")
            return

        click.secho(f"➤ Restoring snapshot to '{target_instance}'", bold=True)
        click.secho(f"  Snapshot: {snapshot.display_name}")
        click.secho(f"  Source: {snapshot.instance_name}")
        click.secho(f"  Created: {snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if not yes:
            click.secho(
                f"\n⚠️  This will modify instance '{target_instance}'!",
                fg="yellow",
                bold=True,
            )
            if not click.confirm("Continue?"):
                click.secho("Restore cancelled.", fg="yellow")
                return

        # Restore snapshot
        click.secho("\n➤ Restoring snapshot...", bold=True)

        snapshot_repo.restore_snapshot(
            snapshot_id=snapshot.snapshot_id,
            target_instance=target_instance,
            restore_data=not no_data,
            restore_modules=not no_modules,
        )

        click.secho("✓ Snapshot restored successfully!", fg="green")

    except (OSError, ValueError, RuntimeError) as e:
        click.secho(f"Error restoring snapshot: {e}", fg="red")


@snapshot_group.command(name="delete")
@click.argument("snapshot_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_snapshot_cmd(snapshot_id: str, yes: bool):
    """Delete a snapshot by ID."""
    try:
        snapshot_repo = FilesystemSnapshotRepository()
        snapshot = snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            click.secho(f"Error: Snapshot '{snapshot_id}' not found", fg="red")
            return

        click.secho("➤ Deleting snapshot", bold=True)
        click.secho(f"  Snapshot: {snapshot.display_name}")
        click.secho(f"  Instance: {snapshot.instance_name}")
        click.secho(f"  Created: {snapshot.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if not yes and not click.confirm("\nDelete this snapshot?"):
            click.secho("Delete cancelled.", fg="yellow")
            return

        snapshot_repo.delete_snapshot(snapshot.snapshot_id)
        click.secho("✓ Snapshot deleted successfully!", fg="green")

    except (OSError, ValueError, RuntimeError) as e:
        click.secho(f"Error deleting snapshot: {e}", fg="red")
