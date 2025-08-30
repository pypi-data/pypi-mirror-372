"""
Configuration service for the dooservice-cli application.

This module provides domain services for configuration validation and processing,
ensuring that all configurations meet business rules and constraints.
Orchestrates specialized domain services following Clean Architecture principles.
"""

import os
from typing import Any, Dict

from dacite import (
    Config as DaciteConfig,
    DaciteError,
    from_dict,
)
import yaml

from core.domain.entities.backup_config import BackupFormat, BackupFrequency
from core.domain.entities.dooservice_config import DooServiceConfig
from core.domain.services.configuration_validation_service import (
    ConfigurationValidationService,
    create_configuration_validator,
)
from core.domain.services.repository_reference_resolver import (
    RepositoryReferenceResolver,
    create_repository_reference_resolver,
)
from shared.errors.config_validation_error import ConfigValidationError
from shared.types import Duration
from shared.utils.utils import duration_hook


class ConfigService:
    """
    Domain service orchestrator for configuration validation and processing.

    Coordinates specialized domain services to validate and process configurations
    according to business rules and domain invariants.
    """

    def __init__(
        self,
        validation_service: ConfigurationValidationService = None,
        repository_resolver: RepositoryReferenceResolver = None,
    ):
        """
        Initialize the ConfigService with its dependencies.

        Args:
            validation_service: Service for validating business rules
            repository_resolver: Service for resolving repository references
        """
        self._validation_service = (
            validation_service or create_configuration_validator()
        )
        self._repository_resolver = (
            repository_resolver or create_repository_reference_resolver()
        )

    def load_config(self, config_file: str = "dooservice.yml") -> DooServiceConfig:
        """
        Load configuration from YAML file.

        Args:
            config_file: Path to configuration file

        Returns:
            Validated DooServiceConfig object

        Raises:
            ConfigValidationError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file) as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Invalid YAML in {config_file}: {e}") from e

        return self.validate(raw_config)

    def validate(self, raw_config: Dict[str, Any]) -> DooServiceConfig:
        """
        Validates the raw configuration and returns a DooServiceConfig object.

        Args:
            raw_config: The raw configuration dictionary

        Returns:
            A validated DooServiceConfig object

        Raises:
            ConfigValidationError: If the configuration is invalid
        """
        try:
            # Perform business rule validation first
            validation_errors = self._validation_service.validate_business_rules(
                raw_config,
            )
            if validation_errors:
                raise ConfigValidationError(
                    f"Configuration validation failed: {'; '.join(validation_errors)}",
                    validation_errors=validation_errors,
                )

            # Resolve repository references
            resolved_config = self._repository_resolver.resolve_repository_references(
                raw_config,
            )

            # Convert to dataclass using schema validation
            config = self._convert_to_dataclass(resolved_config)

            # Validate domain invariants
            self._validation_service.validate_domain_invariants(config)

            return config

        except DaciteError as e:
            raise ConfigValidationError(f"Schema validation failed: {e}") from e

    def resolve_repository_references(
        self,
        raw_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolves list-based repository references in instances.

        Resolves list-based repository references in instances against global
        definitions.

        Note: This method is kept for backward compatibility but delegates to the
        resolver service.
        """
        return self._repository_resolver.resolve_repository_references(raw_config)

    def _convert_to_dataclass(
        self,
        resolved_config: Dict[str, Any],
    ) -> DooServiceConfig:
        """
        Converts the resolved configuration dictionary to a DooServiceConfig dataclass.

        Args:
            resolved_config: Configuration with resolved repository references

        Returns:
            DooServiceConfig instance

        Raises:
            DaciteError: If schema conversion fails
        """
        return from_dict(
            data_class=DooServiceConfig,
            data=resolved_config,
            config=DaciteConfig(
                type_hooks={
                    Duration: duration_hook,
                    BackupFrequency: lambda x: BackupFrequency(x)
                    if isinstance(x, str)
                    else x,
                    BackupFormat: lambda x: BackupFormat(x)
                    if isinstance(x, str)
                    else x,
                },
                check_types=True,
            ),
        )


def create_config_service() -> ConfigService:
    """
    Factory function to create a ConfigService with default dependencies.

    Returns:
        New ConfigService instance with default domain services
    """
    return ConfigService()
