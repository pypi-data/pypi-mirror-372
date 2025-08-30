"""
Centralized instance management commands.

This module contains all instance CLI commands using the centralized
configuration context pattern, removing configuration dependencies
from use cases.
"""

import click

from instance.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    instance_config_context,
)
from shared.errors.config_validation_error import ConfigValidationError
from shared.errors.instance_exists_error import InstanceExistsError


@click.command(name="create")
@click.argument("name")
@config_option()
@instance_config_context
def create_instance(config: str, name: str):
    """
    Create a new Odoo instance based on the configuration.

    This command reads the dooservice.yml file, validates the specified
    instance configuration, and orchestrates the entire setup process.
    """
    try:
        config_context = click.get_current_context().obj

        # Validate instance exists in configuration
        config_context.get_instance_config(name)

        # Display instance details before creation
        resolved_display_config = config_context.resolve_instance_config(name)

        click.secho(f"➤ Preparing to create instance '{name}'...", bold=True)
        click.secho("\nInstance Details:", bold=True)
        click.secho(f"  Name: {name}")
        click.secho(f"  Odoo Version: {resolved_display_config.odoo_version}")
        click.secho(f"  Data Directory: {resolved_display_config.data_dir}")

        if resolved_display_config.repositories:
            click.secho("  Repositories:")
            for repo_name, repo_config in resolved_display_config.repositories.items():
                click.secho(
                    f"    - {repo_name}: {repo_config.repository_url} "
                    f"(Branch: {repo_config.branch})"
                )

        if resolved_display_config.python_dependencies:
            click.secho("  Python Dependencies:")
            for dep in resolved_display_config.python_dependencies:
                click.secho(f"    - {dep}")

        # Execute creation with progress
        click.secho(f"\n➤ Creating instance '{name}'...", bold=True)
        config_context.create_instance_with_progress(name)

        click.secho(f"\n✔ Instance '{name}' created successfully.", fg="green")

    except (ConfigValidationError, InstanceExistsError) as e:
        click.secho(f"Configuration Error: {e}", fg="red")
        raise click.Abort() from e
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="start")
@click.argument("name")
@config_option()
@instance_config_context
def start_instance(config: str, name: str):
    """Start an instance."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        # Start containers in correct order (db first, then web)
        if resolved_config.deployment.docker.db:
            db_container = resolved_config.deployment.docker.db.container_name
            config_context.start_instance_simple(db_container)

        if resolved_config.deployment.docker.web:
            container_name = resolved_config.deployment.docker.web.container_name
            config_context.start_instance_simple(container_name)

        click.secho(f"✔ Instance '{name}' started successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error starting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="stop")
@click.argument("name")
@config_option()
@instance_config_context
def stop_instance(config: str, name: str):
    """Stop an instance."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        # Stop containers in correct order (web first, then db)
        if resolved_config.deployment.docker.web:
            container_name = resolved_config.deployment.docker.web.container_name
            config_context.stop_instance_simple(container_name)

        if resolved_config.deployment.docker.db:
            db_container = resolved_config.deployment.docker.db.container_name
            config_context.stop_instance_simple(db_container)

        click.secho(f"✔ Instance '{name}' stopped successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error stopping instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="status")
@click.argument("name")
@config_option()
@instance_config_context
def status_instance(config: str, name: str):
    """Show instance status."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        # For now, use the simple approach until we fully refactor
        if resolved_config.deployment.docker.web:
            container_name = resolved_config.deployment.docker.web.container_name
            status = config_context.status_instance_simple(container_name)

            click.secho(f"Instance '{name}' status: {status}")

            # Also check database if configured
            if resolved_config.deployment.docker.db:
                db_container = resolved_config.deployment.docker.db.container_name
                db_status = config_context.status_instance_simple(db_container)
                click.secho(f"  Database: {db_status}", fg="blue")
        else:
            click.secho(
                f"Instance '{name}' has no web container configured", fg="yellow"
            )

    except Exception as e:
        click.secho(f"Error getting instance status: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="logs")
@click.argument("name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--lines", "-n", default=100, help="Number of lines to show")
@config_option()
@instance_config_context
def logs_instance(config: str, name: str, follow: bool, lines: int):
    """Show instance logs."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        container_name = resolved_config.deployment.docker.web.container_name
        config_context.logs_instance_simple(container_name, follow, lines)

    except Exception as e:
        click.secho(f"Error getting instance logs: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="sync")
@click.argument("name")
@config_option()
@instance_config_context
def sync_instance(config: str, name: str):
    """Synchronize instance with configuration changes."""
    try:
        config_context = click.get_current_context().obj

        click.secho(f"➤ Synchronizing instance '{name}'...", bold=True)

        diffs, new_lock_file = config_context.sync_instance_with_diff(name)

        if not diffs:
            click.secho(f"✔ Instance '{name}' is already synchronized.", fg="green")
            return

        # Display changes
        click.secho("\nChanges detected:", bold=True)
        for diff in diffs:
            field_path = ".".join(diff.path)
            click.secho(f"  {field_path}: {diff.old_value} -> {diff.new_value}")

        click.secho(f"\n✔ Instance '{name}' synchronized successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error synchronizing instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="delete")
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
@config_option()
@instance_config_context
def delete_instance(config: str, name: str, force: bool):
    """Delete an instance."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        if not force:
            click.confirm(
                f"Are you sure you want to delete instance '{name}'?", abort=True
            )

        container_name = resolved_config.deployment.docker.web.container_name
        data_dir = resolved_config.data_dir

        config_context.delete_instance_simple(container_name, data_dir)

        click.secho(f"✔ Instance '{name}' deleted successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error deleting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="exec-web")
@click.argument("name")
@click.argument("command", nargs=-1, required=True)
@config_option()
@instance_config_context
def exec_web_instance(config: str, name: str, command: tuple):
    """Execute command in web container."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        container_name = resolved_config.deployment.docker.web.container_name
        command_str = " ".join(command)

        config_context.exec_web_instance_simple(container_name, command_str)

    except Exception as e:
        click.secho(f"Error executing command: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="exec-db")
@click.argument("name")
@click.argument("command", nargs=-1, required=True)
@config_option()
@instance_config_context
def exec_db_instance(config: str, name: str, command: tuple):
    """Execute command in database container."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        db_container_name = resolved_config.deployment.docker.db.container_name
        command_str = " ".join(command)

        config_context.exec_db_instance_simple(db_container_name, command_str)

    except Exception as e:
        click.secho(f"Error executing command: {e}", fg="red")
        raise click.Abort() from e
