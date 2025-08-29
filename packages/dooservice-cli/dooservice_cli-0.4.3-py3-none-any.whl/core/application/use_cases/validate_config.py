from typing import Any, Dict

from core.domain.repositories.config_repository import ConfigRepository
from core.domain.services.config_service import ConfigService
from core.domain.services.placeholder_service import PlaceholderService


class ValidateConfig:
    """Application Service to validate the service configuration file."""

    def __init__(
        self,
        config_repository: ConfigRepository,
        config_service: ConfigService,
        placeholder_service: PlaceholderService,
    ):
        """
        Initializes the ValidateConfig use case.

        Args:
            config_repository: The repository for loading the configuration.
            config_service: The service for validating the configuration.
            placeholder_service: The service for resolving placeholders.
        """
        self.config_repository = config_repository
        self.config_service = config_service
        self.placeholder_service = placeholder_service

    def execute(self) -> None:
        """Executes the configuration validation process."""
        raw_config = self.config_repository.load()

        # Resolve placeholders for each instance
        placeholder_resolved_config = self._resolve_placeholders(raw_config)

        # Validate the complete configuration using the orchestrated domain services
        self.config_service.validate(placeholder_resolved_config)

    def _resolve_placeholders(self, raw_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves placeholders in instance configurations.

        Args:
            raw_config: Raw configuration dictionary

        Returns:
            Configuration with resolved placeholders
        """
        if "instances" not in raw_config:
            return raw_config

        # Create a copy to avoid modifying the original
        config_copy = raw_config.copy()
        config_copy["instances"] = {}

        # Resolve placeholders for each instance
        for name, instance_data in raw_config["instances"].items():
            # Add instance name to context
            instance_with_name = instance_data.copy()
            instance_with_name["name"] = name

            # Resolve placeholders using the instance as context
            resolved_instance = self.placeholder_service.resolve(
                instance_with_name,
                instance_with_name,
            )
            config_copy["instances"][name] = resolved_instance

        return config_copy
