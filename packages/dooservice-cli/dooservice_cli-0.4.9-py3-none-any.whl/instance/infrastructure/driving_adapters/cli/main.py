"""
Instance CLI management commands.

This module provides the main CLI interface for instance management operations
following the centralized configuration pattern.
"""

import click

from instance.infrastructure.driving_adapters.cli.commands.instance_commands import (
    create_instance,
    delete_instance,
    exec_db_instance,
    exec_web_instance,
    logs_instance,
    start_instance,
    status_instance,
    stop_instance,
    sync_instance,
)


@click.group(name="instance")
def instance_cli():
    """
    Instance management commands.

    Manage Odoo instances including creation, lifecycle operations,
    synchronization, and execution commands.
    """


# Add all instance commands
instance_cli.add_command(create_instance)
instance_cli.add_command(start_instance)
instance_cli.add_command(stop_instance)
instance_cli.add_command(status_instance)
instance_cli.add_command(logs_instance)
instance_cli.add_command(sync_instance)
instance_cli.add_command(delete_instance)
instance_cli.add_command(exec_web_instance)
instance_cli.add_command(exec_db_instance)
