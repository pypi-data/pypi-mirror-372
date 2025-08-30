"""
Configuration validation error for the dooservice-cli application.

This module provides error classes for configuration validation failures.
"""

from typing import List, Optional

from shared.errors.base_error import DomainError


class ConfigValidationError(DomainError):
    """
    Raised when the configuration file fails validation.

    This error indicates that the configuration does not meet the required
    business rules or schema constraints.
    """

    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[str]] = None,
        config_path: Optional[str] = None,
    ) -> None:
        """
        Initialize a ConfigValidationError.

        Args:
            message: Human-readable error message
            validation_errors: List of specific validation errors
            config_path: Path to the configuration file that failed validation
        """
        context = {}
        if validation_errors:
            context["validation_errors"] = validation_errors
        if config_path:
            context["config_path"] = config_path

        super().__init__(
            message=message,
            error_code="CONFIG_VALIDATION_FAILED",
            context=context,
        )

        self.validation_errors = validation_errors or []
        self.config_path = config_path
