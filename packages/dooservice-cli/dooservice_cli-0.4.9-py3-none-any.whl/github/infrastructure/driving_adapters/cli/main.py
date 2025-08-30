"""
GitHub CLI management commands.

This module provides the main CLI interface for GitHub integration operations
following the centralized configuration pattern.
"""

import click

from github.infrastructure.driving_adapters.cli.commands.auth_commands import (
    github_login,
    github_logout,
    github_status,
)
from github.infrastructure.driving_adapters.cli.commands.ssh_commands import (
    key_group,
)
from github.infrastructure.driving_adapters.cli.commands.watch_commands import (
    watch_group,
)
from github.infrastructure.driving_adapters.cli.commands.webhook_commands import (
    webhook_group,
)


@click.group(name="github")
def github_cli():
    """
    GitHub integration commands.

    Manage GitHub authentication and SSH key management.
    """


# Add authentication commands
github_cli.add_command(github_login)
github_cli.add_command(github_logout)
github_cli.add_command(github_status)

# Add command groups
github_cli.add_command(key_group)
github_cli.add_command(webhook_group)
github_cli.add_command(watch_group)
