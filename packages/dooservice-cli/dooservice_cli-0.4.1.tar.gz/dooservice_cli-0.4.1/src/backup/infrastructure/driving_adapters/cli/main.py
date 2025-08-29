"""Main backup CLI entry point with centralized command integration."""

import click

from backup.infrastructure.driving_adapters.cli.commands.auto_commands import auto_group
from backup.infrastructure.driving_adapters.cli.commands.create_commands import (
    create_backup,
)
from backup.infrastructure.driving_adapters.cli.commands.test_commands import (
    list_databases,
    show_config,
    test_backup,
)


@click.group(name="backup")
def backup_cli():
    """Backup management with automatic instance detection."""


# Register individual backup commands
backup_cli.add_command(create_backup)
backup_cli.add_command(test_backup)
backup_cli.add_command(list_databases)
backup_cli.add_command(show_config)

# Register backup command groups
backup_cli.add_command(auto_group)


if __name__ == "__main__":
    backup_cli()
