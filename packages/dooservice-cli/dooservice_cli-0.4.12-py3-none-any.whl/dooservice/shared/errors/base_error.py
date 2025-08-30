"""
Base error classes for the dooservice-cli application.

This module provides the foundation for all custom exceptions in the application,
following a structured approach to error handling.
"""

from typing import Any, Dict, Optional


class DooServiceError(Exception):
    """
    Base exception class for all dooservice-cli errors.

    This class provides a structured approach to error handling with
    support for error codes, context information, and user-friendly messages.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """
        Initialize a DooServiceError.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            context: Optional context information for debugging
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DomainError(DooServiceError):
    """
    Base class for domain-related errors.

    Domain errors represent violations of business rules or domain invariants.
    """


class ApplicationError(DooServiceError):
    """
    Base class for application-layer errors.

    Application errors represent issues with use case execution or
    application-level business logic.
    """


class InfrastructureError(DooServiceError):
    """
    Base class for infrastructure-related errors.

    Infrastructure errors represent issues with external systems,
    file I/O, network operations, etc.
    """
