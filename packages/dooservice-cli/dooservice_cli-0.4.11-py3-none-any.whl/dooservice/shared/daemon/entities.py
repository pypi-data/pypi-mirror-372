"""Daemon entities - simplified single file."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class DaemonStatus(Enum):
    """Daemon status enumeration."""

    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class DaemonConfig:
    """Daemon configuration."""

    name: str
    working_directory: Optional[Path] = None
    config_file: Optional[Path] = None
    startup_args: Optional[Dict[str, Any]] = None

    def get_log_file_path(self, log_dir: Path) -> Path:
        """Get log file path for this daemon."""
        return log_dir / f"{self.name}.log"


@dataclass
class DaemonInfo:
    """Daemon information and state."""

    name: str
    status: DaemonStatus
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def is_running(self) -> bool:
        """Check if daemon is currently running."""
        return self.status == DaemonStatus.RUNNING and self.pid is not None

    def is_stopped(self) -> bool:
        """Check if daemon is stopped."""
        return self.status == DaemonStatus.STOPPED

    def has_error(self) -> bool:
        """Check if daemon has an error status."""
        return self.status == DaemonStatus.ERROR

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        if not self.config:
            return default
        return self.config.get(key, default)

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a metadata value by key."""
        if not self.metadata:
            return default
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert daemon info to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status.value,
            "pid": self.pid,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "config": self.config or {},
            "metadata": self.metadata or {},
            "is_running": self.is_running(),
        }
