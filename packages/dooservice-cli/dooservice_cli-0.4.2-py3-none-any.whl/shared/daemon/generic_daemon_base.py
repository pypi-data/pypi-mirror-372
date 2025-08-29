"""Generic daemon base class with foreground and background execution modes."""

from abc import ABC, abstractmethod
import logging
import os
from pathlib import Path
import signal
import subprocess
import sys
from typing import Any, Dict, List, Optional

import psutil

from .entities import DaemonConfig, DaemonInfo, DaemonStatus


class GenericDaemonBase(ABC):
    """
    Generic base class for daemon implementations with dual execution modes.

    This class provides:
    1. Foreground mode: Run daemon directly in current process
       (for development/debugging)
    2. Background mode: Manage daemon as external process (for production)
    3. Shared functionality: Logging, signal handling, configuration management

    Specific daemon implementations should inherit from this class and implement
    the abstract methods for their business logic.
    """

    def __init__(
        self,
        daemon_name: str,
        config: Optional[DaemonConfig] = None,
        config_dir: Optional[Path] = None,
    ):
        """
        Initialize generic daemon base.

        Args:
            daemon_name: Name of the daemon
            config: Daemon configuration (optional)
            config_dir: Directory for PID files and logs (for background mode)
        """
        self.daemon_name = daemon_name
        self.config = config or self._create_default_config()
        self.running = False

        # Background mode process management setup
        self.config_dir = config_dir or Path.home() / ".dooservice"
        self.pid_file = self.config_dir / f"{daemon_name}.pid"
        self.log_dir = self.config_dir / "logs"

        # Initialize shared components
        self._setup_directories()
        self._setup_logging()
        self._setup_signal_handlers()

    # ========================================
    # Abstract Methods - Must be implemented by subclasses
    # ========================================

    @abstractmethod
    def _create_default_config(self) -> DaemonConfig:
        """Create default daemon configuration."""

    @abstractmethod
    def _run_daemon_loop(self) -> None:
        """Main daemon loop implementation. Must respect self.running flag."""

    @abstractmethod
    def _initialize_daemon(self) -> None:
        """Initialize daemon-specific resources before starting."""

    @abstractmethod
    def _cleanup_daemon(self) -> None:
        """Clean up daemon-specific resources during shutdown."""

    # ========================================
    # FOREGROUND MODE - Direct execution in current process
    # ========================================

    def start_foreground(self) -> None:
        """
        Start daemon in foreground mode (current process).

        Runs the daemon loop directly in the current process.
        Best for development, debugging, or when you want direct control.
        Process will block until daemon stops.
        """
        try:
            self._log_startup_info("foreground")

            # Initialize daemon-specific resources
            self._initialize_daemon()

            self.running = True
            self.logger.info(
                "Daemon '%s' started successfully in foreground", self.daemon_name
            )

            # Run main daemon loop (blocks here)
            self._run_daemon_loop()

        except (OSError, RuntimeError) as e:
            self.logger.error("Failed to start daemon '%s': %s", self.daemon_name, e)
            sys.exit(1)

    def stop_foreground(self) -> None:
        """
        Stop foreground daemon.

        Sets running flag to False and performs cleanup.
        The daemon loop should check self.running periodically to stop gracefully.
        """
        self.logger.info("Stopping foreground daemon: %s", self.daemon_name)
        self.running = False

        try:
            self._cleanup_daemon()
        except (OSError, RuntimeError) as e:
            self.logger.error("Error during foreground cleanup: %s", e)

        self.logger.info("Foreground daemon '%s' stopped", self.daemon_name)

    def get_foreground_status(self) -> DaemonInfo:
        """Get current foreground daemon status."""
        return self._create_daemon_info(self.running, foreground=True)

    # ========================================
    # BACKGROUND MODE - External process management
    # ========================================

    def start_background(
        self, daemon_script: Path, script_args: List[str] = None
    ) -> DaemonInfo:
        """
        Start daemon in background mode (external process).

        Launches the daemon as a separate process and manages it via PID file.
        Best for production deployments where you need process isolation.

        Args:
            daemon_script: Path to the daemon script to execute
            script_args: Arguments to pass to the daemon script

        Returns:
            DaemonInfo with daemon status
        """
        if self.is_background_running():
            return self.get_background_status()

        script_args = script_args or []
        cmd = [sys.executable, str(daemon_script)] + script_args

        try:
            process = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=Path.cwd(),
            )

            # Save PID for process management
            self._save_background_pid(process.pid)

            self.logger.info(
                "Daemon '%s' started in background with PID %d",
                self.daemon_name,
                process.pid,
            )

            return DaemonInfo(
                name=self.daemon_name,
                status=DaemonStatus.RUNNING,
                pid=process.pid,
            )

        except Exception as e:
            self.logger.error(
                "Failed to start background daemon '%s': %s", self.daemon_name, e
            )
            raise

    def stop_background(self, force: bool = False) -> bool:
        """
        Stop background daemon process.

        Sends SIGTERM (or SIGKILL if force=True) to the background process.

        Args:
            force: Use SIGKILL instead of SIGTERM

        Returns:
            True if daemon was stopped successfully
        """
        if not self.pid_file.exists():
            return True

        try:
            pid = self._read_background_pid()
            if pid is None:
                return True

            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            self._clear_background_pid()

            self.logger.info(
                "Background daemon '%s' stopped (PID: %d)", self.daemon_name, pid
            )
            return True

        except ProcessLookupError:
            # Process already dead
            self._clear_background_pid()
            return True
        except (OSError, RuntimeError) as e:
            self.logger.error("Error stopping background daemon: %s", e)
            return False

    def get_background_status(self) -> DaemonInfo:
        """Get background daemon process status."""
        pid = self._read_background_pid()

        if pid is None:
            return DaemonInfo(
                name=self.daemon_name,
                status=DaemonStatus.STOPPED,
                pid=None,
            )

        if self._is_process_running(pid):
            return DaemonInfo(
                name=self.daemon_name,
                status=DaemonStatus.RUNNING,
                pid=pid,
            )
        # Process died, clean up PID file
        self._clear_background_pid()
        return DaemonInfo(
            name=self.daemon_name,
            status=DaemonStatus.STOPPED,
            pid=None,
        )

    def is_background_running(self) -> bool:
        """Check if background daemon process is running."""
        status = self.get_background_status()
        return status.is_running()

    def restart_background(
        self, daemon_script: Path, script_args: List[str] = None
    ) -> DaemonInfo:
        """
        Restart background daemon process.

        Stops the current background process (if running) and starts a new one.

        Args:
            daemon_script: Path to the daemon script
            script_args: Arguments to pass to the daemon script

        Returns:
            DaemonInfo with daemon status
        """
        self.stop_background(force=True)
        return self.start_background(daemon_script, script_args)

    # ========================================
    # SHARED FUNCTIONALITY - Used by both modes
    # ========================================

    def get_daemon_logs(self, tail_lines: int = 50) -> List[str]:
        """
        Get daemon logs (works for both foreground and background modes).

        Args:
            tail_lines: Number of lines to return from end of log

        Returns:
            List of log lines
        """
        log_file = self._get_log_file_path()

        if not log_file.exists():
            return []

        try:
            with open(log_file) as f:
                lines = f.readlines()
                return [line.rstrip() for line in lines[-tail_lines:]]
        except OSError:
            return []

    def get_log_file_path(self) -> Path:
        """Get the log file path for this daemon."""
        return self._get_log_file_path()

    # ========================================
    # PRIVATE METHODS - Internal implementation
    # ========================================

    def _setup_directories(self) -> None:
        """Setup required directories for daemon operation."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        """Setup logging to file and console."""
        log_file = self._get_log_file_path()

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals (SIGTERM, SIGINT)."""
        self.logger.info("Received signal %s, shutting down...", signum)
        self.stop_foreground()  # Stop foreground mode
        sys.exit(0)

    def _log_startup_info(self, mode: str) -> None:
        """Log daemon startup information."""
        self.logger.info("Starting daemon in %s mode: %s", mode, self.daemon_name)

    def _create_daemon_info(
        self, running: bool = True, foreground: bool = False
    ) -> DaemonInfo:
        """Create DaemonInfo for current daemon state."""
        from datetime import datetime

        return DaemonInfo(
            name=self.daemon_name,
            status=DaemonStatus.RUNNING if running else DaemonStatus.STOPPED,
            pid=os.getpid() if running and foreground else None,
            started_at=datetime.now() if running else None,
            config=self.config.startup_args if self.config else None,
            metadata=self._get_daemon_metadata(),
        )

    def _get_daemon_metadata(self) -> Dict[str, Any]:
        """Get daemon-specific metadata."""
        return {
            "daemon_type": self.__class__.__name__,
            "working_directory": (
                str(self.config.working_directory)
                if self.config and self.config.working_directory
                else None
            ),
        }

    def _get_log_file_path(self) -> Path:
        """Get log file path for this daemon."""
        return self.log_dir / f"{self.daemon_name}.log"

    # Background process management helpers

    def _save_background_pid(self, pid: int) -> None:
        """Save background process PID to file."""
        self.pid_file.write_text(str(pid))

    def _read_background_pid(self) -> Optional[int]:
        """Read background process PID from file."""
        if not self.pid_file.exists():
            return None

        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, OSError):
            return None

    def _clear_background_pid(self) -> None:
        """Clear background process PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running."""
        try:
            return psutil.pid_exists(pid)
        except (ImportError, OSError):
            # Fallback method if psutil fails
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False
