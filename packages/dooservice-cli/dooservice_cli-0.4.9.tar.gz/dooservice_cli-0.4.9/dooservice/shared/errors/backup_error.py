"""Backup-related error classes for the dooservice-cli application."""

from typing import Any, Dict, Optional

from shared.errors.base_error import DomainError


class BackupError(DomainError):
    """Base class for backup-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "BACKUP_ERROR",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, context=context)


class BackupCreationError(BackupError):
    """Raised when backup creation fails."""

    def __init__(
        self,
        message: str,
        instance_name: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        context = {}
        if instance_name:
            context["instance_name"] = instance_name
        if reason:
            context["reason"] = reason

        super().__init__(
            message=message,
            error_code="BACKUP_CREATION_FAILED",
            context=context,
        )


class BackupRestoreError(BackupError):
    """Raised when backup restoration fails."""

    def __init__(
        self,
        message: str,
        backup_id: Optional[str] = None,
        target_instance: Optional[str] = None,
    ) -> None:
        context = {}
        if backup_id:
            context["backup_id"] = backup_id
        if target_instance:
            context["target_instance"] = target_instance

        super().__init__(
            message=message,
            error_code="BACKUP_RESTORE_FAILED",
            context=context,
        )


class BackupNotFoundError(BackupError):
    """Raised when a requested backup is not found."""

    def __init__(self, backup_id: str) -> None:
        super().__init__(
            message=f"Backup '{backup_id}' not found",
            error_code="BACKUP_NOT_FOUND",
            context={"backup_id": backup_id},
        )


class BackupSchedulerError(BackupError):
    """Raised when backup scheduler operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, error_code="BACKUP_SCHEDULER_ERROR")


class BackupExecutionError(BackupError):
    """Raised when backup execution fails."""

    def __init__(self, message: str, instance_name: Optional[str] = None) -> None:
        context = {}
        if instance_name:
            context["instance_name"] = instance_name

        super().__init__(
            message=message,
            error_code="BACKUP_EXECUTION_ERROR",
            context=context,
        )


class BackupConfigurationError(BackupError):
    """Raised when backup configuration is invalid or operations fail."""

    def __init__(self, message: str, config_id: Optional[str] = None) -> None:
        context = {}
        if config_id:
            context["config_id"] = config_id

        super().__init__(
            message=message,
            error_code="BACKUP_CONFIGURATION_ERROR",
            context=context,
        )


class BackupConnectionError(BackupError):
    """Raised when backup destination connection fails."""

    def __init__(self, message: str, destination: Optional[str] = None) -> None:
        context = {}
        if destination:
            context["destination"] = destination

        super().__init__(
            message=message,
            error_code="BACKUP_CONNECTION_ERROR",
            context=context,
        )


class BackupUploadError(BackupError):
    """Raised when backup upload fails."""

    def __init__(self, message: str, destination: Optional[str] = None) -> None:
        context = {}
        if destination:
            context["destination"] = destination

        super().__init__(
            message=message,
            error_code="BACKUP_UPLOAD_ERROR",
            context=context,
        )
