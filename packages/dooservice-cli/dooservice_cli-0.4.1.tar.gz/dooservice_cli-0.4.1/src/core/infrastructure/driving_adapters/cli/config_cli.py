"""
This module defines the CLI commands for the 'config' group.

It acts as a driving adapter, translating user commands into calls
to the appropriate application service (use case).
"""

import click

from core.application.use_cases.validate_config import ValidateConfig
from core.domain.services.config_service import create_config_service
from core.infrastructure.driven_adapters.regex_placeholder_service import (
    RegexPlaceholderService,
)
from core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from shared.errors.config_validation_error import ConfigValidationError


@click.group(name="config")
def config_group():
    """Manages the service configuration."""


@config_group.command(name="validate")
@click.option(
    "--file",
    "-f",
    default="dooservice.yml",
    help="Path to the configuration file.",
)
def validate_config_cmd(file: str):
    """Validates the syntax and structure of the configuration file."""
    try:
        config_repository = YAMLConfigRepository(file)
        config_service = create_config_service()
        placeholder_service = RegexPlaceholderService()
        validate_use_case = ValidateConfig(
            config_repository,
            config_service,
            placeholder_service,
        )
        validate_use_case.execute()
        click.secho("✓ Configuration is valid.", fg="green")
    except ConfigValidationError as e:
        click.secho(f"Configuration error:\n{e}", fg="red")
    except Exception as e:  # noqa: BLE001
        click.secho(f"An unexpected error occurred: {e}", fg="red")
