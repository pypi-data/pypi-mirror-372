"""
Main entry point for the DooService application.

This module provides the top-level commands that can be used to run
different modes like CLI and future modes like agent.
"""

import click

from dooservice.cli import cli


@click.group()
def main():
    """
    DooService: A comprehensive tool for managing Odoo instances.

    Available modes:
    - cli: Interactive command-line interface for instance management
    - agent: (Future) Background agent for automated tasks
    """


# Register the CLI mode
main.add_command(cli, name="cli")


if __name__ == "__main__":
    main()
