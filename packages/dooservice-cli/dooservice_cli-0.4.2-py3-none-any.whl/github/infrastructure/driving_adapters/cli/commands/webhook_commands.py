"""GitHub webhook server CLI commands."""

import json
from pathlib import Path
import subprocess
import time
from typing import Any, Dict

import click

from github.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    github_config_context,
)
from shared.errors.daemon_error import DaemonStartError, DaemonStopError


def _get_webhook_server_daemon(config_file: str = "dooservice.yml"):
    """Get webhook server daemon instance."""
    from shared.webhook.webhook_daemon import WebhookServerDaemon

    return WebhookServerDaemon(config_file)


def _get_daemon_script_path() -> Path:
    """Get webhook daemon script path."""
    return (
        Path(__file__).parent.parent.parent.parent.parent.parent
        / "shared"
        / "webhook"
        / "webhook_daemon.py"
    )


@click.group(name="webhook")
def webhook_group():
    """
    GitHub webhook server management.

    Start and manage webhook servers for automatic repository synchronization.
    """


@webhook_group.command(name="start")
@click.option("--host", help="Server host (overrides configuration)")
@click.option("--port", "-p", type=int, help="Server port (overrides configuration)")
@click.option("--foreground", is_flag=True, help="Run in foreground")
@config_option()
@github_config_context
def start_webhook_server(config, host, port, foreground):
    """
    Start GitHub webhook server.

    The webhook server listens for GitHub webhook events and automatically
    performs configured actions like pulling repository changes and restarting
    instances.
    """
    try:
        config_path = Path(config)
        if not config_path.exists():
            click.echo(f"❌ Configuration file not found: {config}")
            raise click.Abort()

        # Create webhook server instance
        webhook_server = _get_webhook_server_daemon(str(config_path))

        # Check if server is already running
        if webhook_server.is_background_running():
            status = webhook_server.get_background_status()
            click.echo(
                f"❌ Webhook server is already running (PID: {status.pid})",
            )
            click.echo("   Config: Running")
            click.echo(f"   Started: {status.started_at}")
            raise click.Abort()

        click.echo("🚀 Starting GitHub webhook server...")
        click.echo(f"   Config: {config_path.absolute()}")
        if host:
            click.echo(f"   Host: {host}")
        if port:
            click.echo(f"   Port: {port}")
        click.echo(f"   Mode: {'foreground' if foreground else 'daemon'}")

        if foreground:
            # For foreground mode, run the server directly
            from shared.webhook.webhook_daemon import WebhookServerDaemon

            daemon = WebhookServerDaemon(str(config_path), host, port)
            try:
                daemon.start_foreground()
            except KeyboardInterrupt:
                click.echo("\n🛑 Webhook server stopped by user")
        else:
            # Use daemon service
            daemon_script = _get_daemon_script_path()
            script_args = ["--config", str(config_path.absolute())]
            if host:
                script_args.extend(["--host", host])
            if port:
                script_args.extend(["--port", str(port)])

            daemon_info = webhook_server.start_background(daemon_script, script_args)

            # Give it a moment to start
            time.sleep(2)

            if webhook_server.is_background_running():
                click.echo("✅ Webhook server started successfully!")
                click.echo(f"   PID: {daemon_info.pid}")
                click.echo(
                    "\n📋 Use 'dooservice github webhook status' to check status",
                )
                click.echo("📋 Use 'dooservice github webhook logs' to view logs")
            else:
                click.echo("❌ Webhook server failed to start properly")
                raise click.Abort()

    except (
        DaemonStartError,
        subprocess.SubprocessError,
        FileNotFoundError,
        PermissionError,
    ) as e:
        click.echo(f"❌ Error starting webhook server: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error starting webhook server: {e}", err=True)
        raise click.Abort() from e


@webhook_group.command(name="stop")
@config_option()
@github_config_context
def stop_webhook_server(config):
    """Stop GitHub webhook server running in background."""
    try:
        # Create webhook server daemon service
        webhook_server = _get_webhook_server_daemon(config)

        if not webhook_server.is_background_running():
            click.echo("❌ Webhook server is not running")
            return

        # Get current status
        status = webhook_server.get_background_status()
        pid = status.pid

        click.echo(f"🛑 Stopping webhook server (PID: {pid})...")

        try:
            # Try graceful shutdown first
            stopped = webhook_server.stop_background(force=False)

            if stopped:
                click.echo("✅ Webhook server stopped successfully")
            else:
                # Force stop if graceful didn't work
                click.echo("⚠️  Graceful shutdown failed, forcing stop...")
                stopped = webhook_server.stop_background(force=True)

                if stopped:
                    click.echo("✅ Webhook server forcefully stopped")
                else:
                    click.echo("❌ Failed to stop webhook server")
                    raise click.Abort()

        except DaemonStopError as e:
            if "No such process" in str(e):
                click.echo("✅ Webhook server was already stopped")
            elif "Permission denied" in str(e):
                click.echo("❌ Permission denied - cannot stop server process")
                raise click.Abort() from e
            else:
                raise

    except (DaemonStopError, ProcessLookupError, PermissionError) as e:
        click.echo(f"❌ Error stopping webhook server: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error stopping webhook server: {e}", err=True)
        raise click.Abort() from e


@webhook_group.command(name="status")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@config_option()
@github_config_context
def webhook_server_status(config, output_json):
    """Show webhook server status and configuration."""
    try:
        config_path = Path(config)
        webhook_server = _get_webhook_server_daemon(str(config_path))
        daemon_status = webhook_server.get_background_status()

        status = {
            "running": daemon_status.is_running(),
            "pid": daemon_status.pid,
            "started_at": daemon_status.started_at,
            "config_file": str(config_path.absolute()),
        }

        # Load webhook config for additional info
        try:
            daemon = webhook_server
            daemon._initialize_daemon()
            webhook_config = daemon._load_webhook_config()

            status.update(
                {
                    "webhook_enabled": webhook_config.enabled,
                    "server_host": webhook_config.server.host,
                    "server_port": webhook_config.server.port,
                    "providers": len(webhook_config.providers),
                    "repository_watches": len(webhook_config.repositories),
                }
            )
        except (ValueError, OSError, AttributeError):
            # If we can't load config, just show basic status
            pass

        if output_json:
            click.echo(json.dumps(status, indent=2, default=str))
        else:
            _display_webhook_status(status, webhook_server)

    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error getting webhook server status: {e}", err=True)
        raise click.Abort() from e


@webhook_group.command(name="restart")
@click.option("--host", help="Server host (overrides configuration)")
@click.option("--port", "-p", type=int, help="Server port (overrides configuration)")
@config_option()
@github_config_context
def restart_webhook_server(config, host, port):
    """Restart GitHub webhook server in background."""
    try:
        # Validate configuration file
        config_path = Path(config)
        if not config_path.exists():
            raise click.ClickException(f"Configuration file not found: {config_path}")

        # Create webhook server daemon service
        webhook_server = _get_webhook_server_daemon(str(config_path))

        click.echo("🔄 Restarting webhook server...")

        # Use daemon service restart method
        daemon_script = _get_daemon_script_path()
        script_args = ["--config", str(config_path.absolute())]
        if host:
            script_args.extend(["--host", host])
        if port:
            script_args.extend(["--port", str(port)])

        daemon_info = webhook_server.restart_background(daemon_script, script_args)

        click.echo("✅ Webhook server restarted successfully!")
        click.echo(f"   PID: {daemon_info.pid}")
        click.echo(f"   Config: {config_path.absolute()}")

    except (DaemonStartError, DaemonStopError) as e:
        click.echo(f"❌ Error restarting webhook server: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error restarting webhook server: {e}", err=True)
        raise click.Abort() from e


@webhook_group.command(name="logs")
@click.option(
    "--tail", "-n", type=int, default=50, help="Number of lines (default: 50)"
)
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@config_option()
@github_config_context
def webhook_server_logs(config, tail, follow):
    """Show webhook server logs."""
    try:
        # Create webhook server daemon service
        webhook_server = _get_webhook_server_daemon(config)

        if not follow:
            # Get logs using daemon service
            log_lines = webhook_server.get_daemon_logs(tail)
            if not log_lines:
                click.echo(
                    "❌ Log file not found. Server may not have been started yet.",
                )
                return

            for line in log_lines:
                click.echo(line)
        else:
            # For follow mode, use traditional tail -f approach
            log_file = Path.home() / ".dooservice" / "logs" / "webhook_server.log"

            if not log_file.exists():
                click.echo(
                    "❌ Log file not found. Server may not have been started yet.",
                )
                return

            try:
                subprocess.run(["tail", "-f", str(log_file)], check=True)
            except KeyboardInterrupt:
                click.echo("\n📋 Log following stopped")
            except subprocess.CalledProcessError:
                # Fallback to showing recent logs
                log_lines = webhook_server.get_daemon_logs(tail)
                for line in log_lines:
                    click.echo(line)

    except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
        click.echo(f"❌ Error reading logs: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:  # noqa: BLE001
        click.echo(f"❌ Error reading logs: {e}", err=True)
        raise click.Abort() from e


def _display_webhook_status(status: Dict[str, Any], webhook_server):
    """Display webhook server status in table format."""
    click.echo("\n📋 GitHub Webhook Server Status")
    click.echo("=" * 50)

    if status["running"]:
        click.echo("✅ Status: RUNNING")
        click.echo(f"🔧 PID: {status['pid']}")
        click.echo(f"📁 Config: {status['config_file']}")
        click.echo(f"⏰ Started: {status['started_at']}")

        if "server_host" in status and "server_port" in status:
            click.echo(f"🌐 Server: {status['server_host']}:{status['server_port']}")
            click.echo(f"📦 Providers: {status.get('providers', 'Unknown')}")
            click.echo(
                f"📂 Repository watches: {status.get('repository_watches', 'Unknown')}"
            )

        # Show repository watches if available
        try:
            daemon = webhook_server
            daemon._initialize_daemon()
            webhook_config = daemon._load_webhook_config()

            if webhook_config.repositories:
                click.echo("\n=== Repository Watches ===")
                for watch in webhook_config.repositories:
                    status_icon = "✓" if watch.enabled else "✗"
                    click.echo(
                        f"{status_icon} {watch.instance_name} <- {watch.repository_url}"
                    )
        except (ValueError, OSError, AttributeError):
            pass

        click.echo("\n💡 Commands:")
        click.echo("   dooservice github webhook stop    - Stop webhook server")
        click.echo("   dooservice github webhook logs    - View logs")
        click.echo("   dooservice github webhook logs -f - Follow logs")

    else:
        click.echo("❌ Status: NOT RUNNING")
        click.echo("\n💡 Start with:")
        click.echo("   dooservice github webhook start")
        click.echo("   dooservice github webhook start --foreground")
