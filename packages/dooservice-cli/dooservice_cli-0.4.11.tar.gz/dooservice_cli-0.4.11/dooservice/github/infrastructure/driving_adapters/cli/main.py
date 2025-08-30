"""
GitHub CLI management commands.

This module provides the main CLI interface for GitHub integration operations
following the centralized configuration pattern.
"""

import click

from dooservice.github.infrastructure.driving_adapters.cli.commands.auth_commands import (  # noqa: E501
    github_login,
    github_logout,
    github_status,
)
from dooservice.github.infrastructure.driving_adapters.cli.commands.ssh_commands import (  # noqa: E501
    key_group,
)
from dooservice.github.infrastructure.driving_adapters.cli.commands.watch_commands import (  # noqa: E501
    watch_group,
)
from dooservice.github.infrastructure.driving_adapters.cli.commands.webhook_commands import (  # noqa: E501
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
