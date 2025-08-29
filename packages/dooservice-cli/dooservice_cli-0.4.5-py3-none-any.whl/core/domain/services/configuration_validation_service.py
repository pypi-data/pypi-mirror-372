"""
Configuration Validation Service.

Pure domain service responsible for validating business rules and domain invariants
in dooservice configurations. Follows Single Responsibility Principle.
"""

import re
from typing import Any, Dict, List

from core.domain.entities.dooservice_config import DooServiceConfig
from shared.errors.config_validation_error import ConfigValidationError


class ConfigurationValidationService:
    """
    Domain service responsible for validating configuration business rules.

    This service enforces domain invariants and business rules without
    depending on external frameworks or infrastructure.
    """

    def __init__(self):
        """Initialize the validation service with a placeholder pattern."""
        self._placeholder_pattern = re.compile(r"\$\{.*?\}")

    def validate_business_rules(self, raw_config: Dict[str, Any]) -> List[str]:
        """
        Validates business rules for the configuration.

        Args:
            raw_config: The raw configuration dictionary

        Returns:
            List of validation error messages. Empty list if validation passes
        """
        errors: List[str] = []

        # Validate required top-level sections
        errors.extend(self._validate_required_sections(raw_config))

        # Validate instances section
        if "instances" in raw_config:
            errors.extend(self._validate_instances_section(raw_config["instances"]))

        # Validate repositories section
        if "repositories" in raw_config:
            errors.extend(
                self._validate_repositories_section(raw_config["repositories"]),
            )

        return errors

    def validate_domain_invariants(self, config: DooServiceConfig) -> None:
        """
        Validates domain invariants after the configuration is loaded.

        Args:
            config: The validated DooServiceConfig object

        Raises:
            ConfigValidationError: If domain invariants are violated
        """
        errors: List[str] = []

        # Check for port conflicts between instances
        errors.extend(self._validate_port_conflicts(config))

        # Check that referenced repositories exist
        errors.extend(self._validate_repository_references(config))

        if errors:
            raise ConfigValidationError(
                "Domain validation failed",
                validation_errors=errors,
            )

    def _validate_required_sections(self, raw_config: Dict[str, Any]) -> List[str]:
        """
        Validates that required top-level sections are present.

        Args:
            raw_config: Raw configuration dictionary

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        if "instances" not in raw_config:
            errors.append("Configuration must contain 'instances' section")

        if "repositories" not in raw_config:
            errors.append("Configuration must contain 'repositories' section")

        return errors

    def _validate_instances_section(self, instances: Any) -> List[str]:
        """
        Validates the instances section.

        Args:
            instances: Instances section from configuration

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        if not isinstance(instances, dict):
            errors.append("'instances' must be a dictionary")
            return errors

        if not instances:
            errors.append("At least one instance must be defined")
            return errors

        for instance_name, instance_config in instances.items():
            errors.extend(
                self._validate_single_instance(instance_name, instance_config),
            )

        return errors

    def _validate_repositories_section(self, repositories: Any) -> List[str]:
        """
        Validates the repositories section.

        Args:
            repositories: Repositories section from configuration

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        if not isinstance(repositories, dict):
            errors.append("'repositories' must be a dictionary")
            return errors

        for repo_name, repo_config in repositories.items():
            errors.extend(self._validate_single_repository(repo_name, repo_config))

        return errors

    def _validate_single_instance(self, name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validates an individual instance configuration.

        Args:
            name: Instance name
            config: Instance configuration dictionary

        Returns:
            List of validation error messages
        """
        errors: List[str] = []

        # Required fields validation
        errors.extend(self._validate_instance_required_fields(name, config))

        # Deployment configuration validation
        errors.extend(self._validate_instance_deployment(name, config))

        # Ports validation
        errors.extend(self._validate_instance_ports(name, config))

        return errors

    def _validate_instance_required_fields(
        self,
        name: str,
        config: Dict[str, Any],
    ) -> List[str]:
        """
        Validates required fields for an instance.

        Args:
            name: Instance name
            config: Instance configuration

        Returns:
            List of validation errors
        """
        errors: List[str] = []
        required_fields = ["odoo_version", "data_dir", "paths", "ports", "deployment"]

        errors.extend(
            [
                f"Instance '{name}' missing required field: {field}"
                for field in required_fields
                if field not in config
            ]
        )

        return errors

    def _validate_instance_deployment(
        self,
        name: str,
        config: Dict[str, Any],
    ) -> List[str]:
        """
        Validates deployment configuration for an instance.

        Args:
            name: Instance name
            config: Instance configuration

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        if "deployment" not in config:
            return errors

        deployment = config["deployment"]

        if not isinstance(deployment, dict):
            errors.append(f"Instance '{name}' deployment must be a dictionary")
            return errors

        if "type" not in deployment:
            errors.append(f"Instance '{name}' deployment missing 'type' field")
        elif deployment.get("type") == "docker" and "docker" not in deployment:
            errors.append(
                f"Instance '{name}' docker deployment missing 'docker' configuration",
            )

        return errors

    def _validate_instance_ports(self, name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validates port configuration for an instance.

        Args:
            name: Instance name
            config: Instance configuration

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        if "ports" not in config or not isinstance(config["ports"], dict):
            return errors

        for port_name, port_value in config["ports"].items():
            # Skip validation for placeholder values
            if isinstance(port_value, str) and self._placeholder_pattern.search(
                port_value,
            ):
                continue

            try:
                port_int = int(port_value)
                if not (1 <= port_int <= 65535):
                    errors.append(
                        f"Instance '{name}' port '{port_name}' must be between 1-65535",
                    )
            except (ValueError, TypeError):
                errors.append(
                    f"Instance '{name}' port '{port_name}' must be a valid integer",
                )

        return errors

    def _validate_single_repository(
        self,
        name: str,
        config: Dict[str, Any],
    ) -> List[str]:
        """
        Validates an individual repository configuration.

        Args:
            name: Repository name
            config: Repository configuration dictionary

        Returns:
            List of validation error messages
        """
        errors: List[str] = []

        # Required fields
        if "source_type" not in config:
            errors.append(f"Repository '{name}' missing required field: source_type")

        # Either 'source' or 'url' must be present (backward compatibility)
        if "source" not in config and "url" not in config:
            errors.append(
                f"Repository '{name}' must have either 'source' or 'url' field",
            )

        # Validate source_type
        if "source_type" in config:
            valid_types = ["git", "zip", "local", "tar.gz"]
            if config["source_type"] not in valid_types:
                errors.append(
                    f"Repository '{name}' source_type must be one of: {valid_types}",
                )

        return errors

    def _validate_port_conflicts(self, config: DooServiceConfig) -> List[str]:
        """
        Validates that there are no port conflicts between instances.

        Args:
            config: The validated DooServiceConfig object

        Returns:
            List of validation errors
        """
        errors: List[str] = []
        used_ports: Dict[str, str] = {}

        for instance_name, instance_config in config.instances.items():
            for port_name, port_value in instance_config.ports.items():
                port_key = f"{port_name}:{port_value}"

                if port_key in used_ports:
                    errors.append(
                        f"Port conflict: Instance '{instance_name}' and "
                        f"'{used_ports[port_key]}' both use port "
                        f"{port_name}:{port_value}",
                    )
                else:
                    used_ports[port_key] = instance_name

        return errors

    def _validate_repository_references(self, config: DooServiceConfig) -> List[str]:
        """
        Validates that all referenced repositories exist.

        Args:
            config: The validated DooServiceConfig object

        Returns:
            List of validation errors
        """
        errors: List[str] = []

        for instance_name, instance_config in config.instances.items():
            errors.extend(
                [
                    f"Instance '{instance_name}' references unknown repository "
                    f"'{repo_name}'"
                    for repo_name in instance_config.repositories
                    if repo_name not in config.repositories
                ]
            )

        return errors


def create_configuration_validator() -> ConfigurationValidationService:
    """
    Factory function to create a ConfigurationValidationService instance.

    Returns:
        New ConfigurationValidationService instance
    """
    return ConfigurationValidationService()
