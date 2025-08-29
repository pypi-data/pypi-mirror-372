from pathlib import Path

import click

from core.domain.services.config_service import create_config_service
from core.domain.services.diff_manager import DiffManager
from core.domain.services.lock_file_checksum_service import LockFileChecksumService
from core.domain.services.lock_manager import LockManager
from core.infrastructure.driven_adapters.file_lock_repository import FileLockRepository
from core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from core.infrastructure.driving_adapters.cli.diff_viewer import DiffViewer


@click.group()
def lock():
    """Manages the dooservice.lock file."""


@lock.command()
@click.option(
    "--file",
    "-f",
    default="dooservice.yml",
    help="Path to the configuration file.",
)
def generate(file):
    """Generates the dooservice.lock file from the configuration."""
    try:
        click.echo("Generating lock file...")
        config_repo = YAMLConfigRepository(file)
        config_service = create_config_service()
        config = config_service.validate(config_repo.load())

        project_root = Path(file).parent
        lock_repository = FileLockRepository(project_root)
        lock_file_checksum_service = LockFileChecksumService()
        lock_manager = LockManager(lock_file_checksum_service)

        new_lock_file = lock_manager.generate_from_config(config)
        lock_repository.save(new_lock_file)

        click.secho("✓ dooservice.lock generated successfully.", fg="green")
    except Exception as e:  # noqa: BLE001
        click.secho(f"Error generating lock file: {e}", fg="red")


@lock.command()
def validate():
    """Validates the integrity of the dooservice.lock file."""
    try:
        click.echo("Validating lock file...")
        project_root = Path.cwd()
        lock_repository = FileLockRepository(project_root)

        lock_file = lock_repository.get()
        if not lock_file:
            click.secho("dooservice.lock not found.", fg="red")
            return

        lock_file_checksum_service = LockFileChecksumService()
        lock_manager = LockManager(lock_file_checksum_service)

        # Create a copy to modify
        import copy

        lock_file_copy = copy.deepcopy(lock_file)

        # Recalculate checksums
        recalculated_lock_file = (
            lock_manager.lock_file_checksum_service.update_checksums(lock_file_copy)
        )

        # Compare checksums
        if recalculated_lock_file.checksum == lock_file.checksum:
            click.secho("✓ Lock file is valid.", fg="green")
        else:
            click.secho("✗ Lock file is invalid. Checksums do not match.", fg="red")
            # For debugging, we could show the diff
            # from core.domain.services.diff_service import DiffService
            # diff_service = DiffService()
            # diff = diff_service.generate_diff(lock_file, recalculated_lock_file)
            # click.echo(diff)

    except Exception as e:  # noqa: BLE001
        click.secho(f"Error validating lock file: {e}", fg="red")


@lock.command()
@click.option(
    "--file",
    "-f",
    default="dooservice.yml",
    help="Path to the configuration file.",
)
def diff(file):
    """Compares the current configuration with the lock file."""
    try:
        # 1. Load the existing lock file
        project_root = Path(file).parent
        lock_repository = FileLockRepository(project_root)
        old_lock_file = lock_repository.get()

        if not old_lock_file:
            click.secho(
                "No lock file found. Run 'lock generate' to create one.",
                fg="yellow",
            )
            # Optionally, show the full new config as the diff
            return

        # 2. Generate a new lock file from the current config
        config_repo = YAMLConfigRepository(file)
        config_service = create_config_service()
        config = config_service.validate(config_repo.load())
        lock_file_checksum_service = LockFileChecksumService()
        lock_manager = LockManager(lock_file_checksum_service)
        new_lock_file = lock_manager.generate_from_config(config)

        # 3. Compare the two lock files using the DiffManager
        diff_manager = DiffManager()
        diffs = diff_manager.compare(old_lock_file, new_lock_file)

        # 4. Render the diff using the DiffViewer
        if diffs:
            click.secho("Changes detected:", bold=True)
            viewer = DiffViewer()
            rendered_diff = viewer.render(diffs)
            click.echo(rendered_diff)
        else:
            click.secho("✓ No changes detected. Lock file is up to date.", fg="green")

    except Exception as e:  # noqa: BLE001
        click.secho(f"Error generating diff: {e}", fg="red")
