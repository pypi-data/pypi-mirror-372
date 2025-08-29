"""Centralized configuration context for backup CLI commands."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml


class BackupConfigContext:
    """Centralized configuration context for backup CLI commands."""

    def __init__(self, config_file: str = "dooservice.yml"):
        """Initialize config context with configuration file."""
        self.config_file = Path(config_file)
        self._config_data: Optional[Dict[str, Any]] = None
        self._placeholders: Dict[str, str] = {}

    @property
    def config_data(self) -> Dict[str, Any]:
        """Get configuration data, loading if necessary."""
        if self._config_data is None:
            self._load_config()
        return self._config_data

    @property
    def placeholders(self) -> Dict[str, str]:
        """Get resolved placeholders."""
        if not self._placeholders:
            self._resolve_placeholders()
        return self._placeholders

    def _load_config(self):
        """Load configuration from dooservice.yml file."""
        if not self.config_file.exists():
            raise click.ClickException(
                f"Configuration file not found: {self.config_file}"
            )

        try:
            with open(self.config_file, encoding="utf-8") as f:
                self._config_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise click.ClickException(
                f"Invalid YAML in configuration file: {e}"
            ) from e
        except OSError as e:
            raise click.ClickException(f"Error reading configuration file: {e}") from e

    def _resolve_placeholders(self):
        """Resolve placeholders from environment variables and config."""
        # Start with environment variables
        self._placeholders = dict(os.environ)

        # Add placeholders from config if they exist
        if "placeholders" in self.config_data:
            config_placeholders = self.config_data["placeholders"]
            if isinstance(config_placeholders, dict):
                for key, value in config_placeholders.items():
                    # Environment variables take precedence
                    if key not in self._placeholders:
                        self._placeholders[key] = str(value)

    def get_instance_config(self, instance_name: str) -> Dict[str, Any]:
        """Get configuration for a specific instance."""
        instances = self.config_data.get("instances", {})

        if instance_name not in instances:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            )

        return instances[instance_name]

    def get_backup_config(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """Get backup configuration, merging global and instance-specific settings."""
        global_backup = self.config_data.get("backup", {})

        if instance_name:
            instance_config = self.get_instance_config(instance_name)
            instance_backup = instance_config.get("backup", {})

            # Merge configurations (instance overrides global)
            return {**global_backup, **instance_backup}

        return global_backup

    def validate_config(self):
        """Validate basic configuration structure."""
        if not isinstance(self.config_data, dict):
            raise click.ClickException("Configuration must be a YAML object")

        if "instances" not in self.config_data:
            raise click.ClickException(
                "Configuration must contain an 'instances' section"
            )


# Context decorator for backup commands
def backup_config_context(f):
    """Decorator to inject config context into backup CLI commands."""

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        config_file = ctx.params.get("config", "dooservice.yml")
        ctx.obj = BackupConfigContext(config_file)
        return f(*args, **kwargs)

    return wrapper


# Standard config option decorator
def config_option():
    """Standard --config option decorator for backup CLI commands."""
    return click.option(
        "--config",
        "-c",
        "config",
        type=click.Path(exists=True),
        default="dooservice.yml",
        help="Path to dooservice.yml configuration file",
    )
