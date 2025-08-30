"""Repository CLI for instance-based repository management."""

import click

from repository.infrastructure.driving_adapters.cli.commands import (
    instance_repo_commands as irc,
)

# Import specific functions from the commands module
list_instance_repos = irc.list_instance_repos
status_instance_repos = irc.status_instance_repos
sync_instance_repos = irc.sync_instance_repos


@click.group(name="repo")
def repo_cli():
    """
    Instance repository management.

    Manage repositories within specific instances, including viewing status,
    synchronizing changes, and analyzing module information.
    """


# Register instance-focused commands
repo_cli.add_command(list_instance_repos)
repo_cli.add_command(status_instance_repos)
repo_cli.add_command(sync_instance_repos)


if __name__ == "__main__":
    repo_cli()
