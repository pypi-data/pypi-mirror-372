"""
This module serves as the main entry point for the DooService CLI.

It uses the 'click' library to create a group of commands, aggregating them
from the different modules of the application. Each module now has its own
organized CLI structure in driving_adapters/cli.
"""

import click

from backup.infrastructure.driving_adapters.cli.main import backup_cli as backup_group
from core.infrastructure.driving_adapters.cli.config_cli import config_group
from core.infrastructure.driving_adapters.cli.lock_commands import lock
from github.infrastructure.driving_adapters.cli.main import github_cli as github_group
from instance.infrastructure.driving_adapters.cli.main import (
    instance_cli as instance_group,
)
from repository.infrastructure.driving_adapters.cli.main import repo_cli as repo_group
from snapshot.infrastructure.driving_adapters.cli.snapshot_commands import (
    snapshot_group,
)


@click.group()
def cli():
    """
    DooService CLI: A tool for managing complex Odoo instances declaratively.

    This CLI allows you to define your instances, repositories, and deployment
    configurations in a single `dooservice.yml` file and manage them from
    the terminal.

    All commands now support the --config/-c option for custom configuration files.
    """


cli.add_command(instance_group)
cli.add_command(config_group)
cli.add_command(repo_group)
cli.add_command(lock)
cli.add_command(backup_group)
cli.add_command(snapshot_group)
cli.add_command(github_group)

if __name__ == "__main__":
    cli()
