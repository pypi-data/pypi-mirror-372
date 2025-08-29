"""Automatic backup scheduler commands."""

import json
from pathlib import Path
import subprocess
import time
from typing import Any, Dict

import click

from backup.infrastructure.driving_adapters.cli.config_context import config_option
from shared.errors.daemon_error import DaemonStartError, DaemonStopError


def _get_backup_scheduler():
    """Get backup scheduler daemon instance."""
    from backup.infrastructure.driven_adapters.backup_scheduler_daemon import (
        BackupSchedulerDaemon,
    )

    return BackupSchedulerDaemon("backup_scheduler")


def _get_daemon_script_path() -> Path:
    """Get backup scheduler daemon script path."""
    return (
        Path(__file__).parent.parent.parent
        / "driven_adapters"
        / "backup_scheduler_daemon.py"
    )


@click.group(name="auto")
def auto_group():
    """Automatic backup scheduler commands."""


@auto_group.command("start")
@config_option()
@click.option("--foreground", is_flag=True, help="Run in foreground")
def start_auto(config: str, foreground: bool):
    """
    Start automatic backup scheduler.

    The scheduler reads the execution time from backup.auto_backup.schedule.time
    in the dooservice.yml configuration file.
    """
    try:
        config = Path(config)
        # Create backup scheduler instance
        scheduler = _get_backup_scheduler()

        # Check if scheduler is already running
        if scheduler.is_background_running():
            status = scheduler.get_background_status()
            click.echo(
                f"❌ Automatic backup scheduler is already running (PID: {status.pid})",
            )
            click.echo("   Config: Running")
            click.echo(f"   Started: {status.started_at}")
            raise click.Abort()

        click.echo("🚀 Starting automatic backup scheduler...")
        click.echo(f"   Config: {config.absolute()}")
        click.echo(f"   Mode: {'foreground' if foreground else 'daemon'}")

        if foreground:
            # For foreground mode, run the scheduler directly
            from backup.infrastructure.driven_adapters.backup_scheduler_daemon import (
                BackupSchedulerDaemon,
            )

            daemon = BackupSchedulerDaemon(str(config))
            try:
                daemon.start_foreground()
            except KeyboardInterrupt:
                click.echo("\n🛑 Scheduler stopped by user")
        else:
            # Use daemon service
            daemon_script = _get_daemon_script_path()
            script_args = ["--config", str(config.absolute())]
            daemon_info = scheduler.start_background(daemon_script, script_args)

            # Give it a moment to start
            time.sleep(2)

            if scheduler.is_background_running():
                click.echo("✅ Automatic backup scheduler started successfully!")
                click.echo(f"   PID: {daemon_info.pid}")
                click.echo(
                    "\n📋 Use 'dooservice backup auto status' to check status",
                )
                click.echo("📋 Use 'dooservice backup auto logs' to view logs")
            else:
                click.echo("❌ Scheduler failed to start properly")
                raise click.Abort()

    except (
        DaemonStartError,
        subprocess.SubprocessError,
        FileNotFoundError,
        PermissionError,
    ) as e:
        click.echo(f"❌ Error starting automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error starting automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e


@auto_group.command("stop")
@config_option()
def stop_auto(config: str):
    """Stop automatic backup scheduler."""
    try:
        # Create generic daemon service
        scheduler = _get_backup_scheduler()

        if not scheduler.is_background_running():
            click.echo("❌ Automatic backup scheduler is not running")
            return

        # Get current status
        status = scheduler.get_background_status()
        pid = status.pid

        click.echo(f"🛑 Stopping automatic backup scheduler (PID: {pid})...")

        try:
            # Try graceful shutdown first
            stopped = scheduler.stop_background(force=False)

            if stopped:
                click.echo("✅ Automatic backup scheduler stopped successfully")
            else:
                # Force stop if graceful didn't work
                click.echo("⚠️  Graceful shutdown failed, forcing stop...")
                stopped = scheduler.stop_background(force=True)

                if stopped:
                    click.echo("✅ Automatic backup scheduler forcefully stopped")
                else:
                    click.echo("❌ Failed to stop automatic backup scheduler")
                    raise click.Abort()

        except DaemonStopError as e:
            if "No such process" in str(e):
                click.echo("✅ Automatic backup scheduler was already stopped")
            elif "Permission denied" in str(e):
                click.echo("❌ Permission denied - cannot stop scheduler process")
                raise click.Abort() from e
            else:
                raise

    except (DaemonStopError, ProcessLookupError, PermissionError) as e:
        click.echo(f"❌ Error stopping automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error stopping automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e


@auto_group.command("status")
@config_option()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def status_auto(config: str, output_json: bool):
    """Show automatic backup scheduler status."""
    try:
        config_path = Path(config)
        scheduler = _get_backup_scheduler()
        daemon_status = scheduler.get_background_status()

        status = {
            "running": daemon_status.is_running(),
            "pid": daemon_status.pid,
            "started_at": daemon_status.started_at,
            "config_file": str(config_path.absolute()),
        }

        if output_json:
            click.echo(json.dumps(status, indent=2, default=str))
        else:
            _display_scheduler_status(status)

    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error getting automatic backup scheduler status: {e}", err=True)
        raise click.Abort() from e


@auto_group.command("logs")
@config_option()
@click.option(
    "--tail", "-n", type=int, default=50, help="Number of lines (default: 50)"
)
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
def logs_auto(config: str, tail: int, follow: bool):
    """Show automatic backup scheduler logs."""
    try:
        # Create generic daemon service
        scheduler = _get_backup_scheduler()

        if not follow:
            # Get logs using daemon service
            log_lines = scheduler.get_daemon_logs(tail)
            if not log_lines:
                click.echo(
                    "❌ Log file not found. Scheduler may not have been started yet.",
                )
                return

            for line in log_lines:
                click.echo(line)
        else:
            # For follow mode, use traditional tail -f approach
            log_file = Path.home() / ".dooservice" / "logs" / "backup_scheduler.log"

            if not log_file.exists():
                click.echo(
                    "❌ Log file not found. Scheduler may not have been started yet.",
                )
                return

            try:
                subprocess.run(["tail", "-f", str(log_file)], check=True)
            except KeyboardInterrupt:
                click.echo("\n📋 Log following stopped")
            except subprocess.CalledProcessError:
                # Fallback to showing recent logs
                log_lines = scheduler.get_daemon_logs(tail)
                for line in log_lines:
                    click.echo(line)

    except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
        click.echo(f"❌ Error reading logs: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error reading logs: {e}", err=True)
        raise click.Abort() from e


@auto_group.command("restart")
@config_option()
def restart_auto(config: str):
    """Restart automatic backup scheduler."""
    try:
        # Validate configuration file
        config_path = Path(config)
        if not config_path.exists():
            raise click.ClickException(f"Configuration file not found: {config_path}")

        # Create generic daemon service
        scheduler = _get_backup_scheduler()

        click.echo("🔄 Restarting automatic backup scheduler...")

        # Use daemon service restart method
        daemon_script = _get_daemon_script_path()
        script_args = ["--config", str(config_path.absolute())]
        daemon_info = scheduler.restart_background(daemon_script, script_args)

        click.echo("✅ Automatic backup scheduler restarted successfully!")
        click.echo(f"   PID: {daemon_info.pid}")
        click.echo(f"   Config: {config_path.absolute()}")

    except (DaemonStartError, DaemonStopError) as e:
        click.echo(f"❌ Error restarting automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error restarting automatic backup scheduler: {e}", err=True)
        raise click.Abort() from e


def _display_scheduler_status(status: Dict[str, Any]):
    """Display scheduler status in table format."""
    click.echo("\n📋 Automatic Backup Scheduler Status")
    click.echo("=" * 50)

    if status["running"]:
        click.echo("✅ Status: RUNNING")
        click.echo(f"🔧 PID: {status['pid']}")
        click.echo(f"📁 Config: {status['config_file']}")
        click.echo(f"⏰ Started: {status['started_at']}")

        click.echo("\n💡 Commands:")
        click.echo("   dooservice backup auto stop    - Stop automatic backups")
        click.echo("   dooservice backup auto logs    - View logs")
        click.echo("   dooservice backup auto logs -f - Follow logs")

    else:
        click.echo("❌ Status: NOT RUNNING")
        click.echo("\n💡 Start with:")
        click.echo("   dooservice backup auto start")
