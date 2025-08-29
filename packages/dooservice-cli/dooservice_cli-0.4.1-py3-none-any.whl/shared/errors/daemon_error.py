"""Daemon-related error classes."""

from shared.errors.base_error import DooServiceError


class DaemonError(DooServiceError):
    """Base class for daemon-related errors."""


class DaemonStartError(DaemonError):
    """Exception raised when daemon cannot be started."""


class DaemonStopError(DaemonError):
    """Exception raised when daemon cannot be stopped."""


class DaemonNotFoundError(DaemonError):
    """Exception raised when daemon is not found."""


class DaemonAlreadyRunningError(DaemonError):
    """Exception raised when trying to start an already running daemon."""


class DaemonConfigurationError(DaemonError):
    """Exception raised when daemon configuration is invalid."""
