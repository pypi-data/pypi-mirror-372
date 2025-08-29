"""Webhook server daemon extending GenericDaemonBase."""

import argparse
import asyncio
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional

import yaml

# Add src to path so we can import our modules
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from shared.daemon import DaemonConfig, GenericDaemonBase  # noqa: E402
from shared.webhook.adapters.docker_instance_repository import (  # noqa: E402
    DockerInstanceWebhookRepository,
)
from shared.webhook.adapters.memory_webhook_action_repository import (  # noqa: E402
    MemoryWebhookActionRepository,
)
from shared.webhook.adapters.yaml_webhook_config_repository import (  # noqa: E402
    YamlWebhookConfigRepository,
)
from shared.webhook.entities import (  # noqa: E402
    ActionType,
    ProviderWebhookConfig,
    RepositoryWatchConfig,
    WebhookConfig,
    WebhookProvider,
    WebhookServerConfig,
)
from shared.webhook.services import (  # noqa: E402
    WebhookActionExecutorService,
    WebhookProcessingService,
)
from shared.webhook.webhook_server import WebhookServerFactory  # noqa: E402


class WebhookServerDaemon(GenericDaemonBase):
    """
    Webhook server daemon implementation.

    This daemon extends GenericDaemonBase to provide webhook server functionality
    with support for multiple providers (GitHub, GitLab, Bitbucket, etc.).
    It runs a FastAPI server that receives webhooks and executes configured actions.
    """

    def __init__(
        self, config_file: str, host: Optional[str] = None, port: Optional[int] = None
    ):
        """
        Initialize webhook server daemon.

        Args:
            config_file: Path to dooservice.yml configuration file
            host: Override server host
            port: Override server port
        """
        self.config_file = config_file
        self.host_override = host
        self.port_override = port
        self.webhook_server = None
        self.server_task = None

        super().__init__("webhook_server")

    def _create_default_config(self) -> DaemonConfig:
        """Create default configuration for webhook server daemon."""
        return DaemonConfig(
            name="webhook_server",
            working_directory=Path.cwd(),
            config_file=Path(self.config_file),
            startup_args={
                "config_file": self.config_file,
                "host": self.host_override,
                "port": self.port_override,
            },
        )

    def _initialize_daemon(self) -> None:
        """Initialize webhook server daemon resources."""
        self.logger.info("Initializing webhook server daemon")
        self.logger.info("Config file: %s", self.config_file)

        # Load webhook configuration
        webhook_config = self._load_webhook_config()
        if not webhook_config.enabled:
            raise ValueError("Webhook system is disabled in configuration")

        # Apply host/port overrides
        if self.host_override:
            webhook_config.server.host = self.host_override
        if self.port_override:
            webhook_config.server.port = self.port_override

        self.logger.info(
            "Starting webhook server on %s:%d",
            webhook_config.server.host,
            webhook_config.server.port,
        )

        # Initialize repositories and services
        config_repo = YamlWebhookConfigRepository(self.config_file)
        action_repo = MemoryWebhookActionRepository()
        instance_repo = DockerInstanceWebhookRepository(self.config_file)

        processing_service = WebhookProcessingService(
            config_repo, action_repo, instance_repo
        )
        executor_service = WebhookActionExecutorService(action_repo, instance_repo)

        # Create webhook server
        self.webhook_server = WebhookServerFactory.create_server(
            webhook_config, processing_service, executor_service
        )

        self.logger.info("Webhook server daemon initialized successfully")

    def _cleanup_daemon(self) -> None:
        """Clean up webhook server daemon resources."""
        self.logger.info("Cleaning up webhook server daemon resources")

        if self.server_task and not self.server_task.done():
            self.server_task.cancel()

        if self.webhook_server:
            asyncio.run(self.webhook_server.stop_server())

    def _run_daemon_loop(self) -> None:
        """Main daemon loop - run the FastAPI webhook server."""
        self.logger.info("Starting webhook server daemon loop")

        try:
            # Run the FastAPI server
            asyncio.run(self.webhook_server.start_server())
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error("Error in webhook server: %s", e)
            raise

    def _load_webhook_config(self) -> WebhookConfig:
        """Load webhook configuration from YAML file."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            # Get global GitHub configuration
            github_config = data.get("github", {})
            webhook_global = github_config.get("webhook", {})

            if not webhook_global.get("enabled", True):
                return WebhookConfig(enabled=False)

            # Server configuration
            server_config = WebhookServerConfig(
                host=webhook_global.get("host", "localhost"),
                port=webhook_global.get(
                    "port", webhook_global.get("default_port", 8080)
                ),
                secret=webhook_global.get("default_secret"),
                auto_start=webhook_global.get("auto_start", False),
            )

            # Provider configurations
            providers = []
            if github_config.get("enabled", True):
                github_provider = ProviderWebhookConfig(
                    provider=WebhookProvider.GITHUB,
                    enabled=True,
                    secret=webhook_global.get("default_secret"),
                    verify_signature=webhook_global.get("default_secret") is not None,
                    endpoint_path="/webhooks/github",
                )
                providers.append(github_provider)

            # Repository watch configurations
            repositories = self._extract_repository_watches(data)

            return WebhookConfig(
                enabled=True,
                server=server_config,
                providers=providers,
                repositories=repositories,
                auto_start=webhook_global.get("auto_start", False),
            )

        except (FileNotFoundError, yaml.YAMLError, KeyError, ValueError) as e:
            self.logger.error("Error loading webhook configuration: %s", e)
            raise ValueError(f"Failed to load webhook config: {e}") from e

    def _extract_repository_watches(self, data: dict) -> list[RepositoryWatchConfig]:
        """Extract repository watch configurations from YAML data."""
        repositories = []

        # Get instances and their repositories
        instances = data.get("instances", {})
        repos_config = data.get("repositories", {})
        github_repos = data.get("github", {}).get("repositories", {})

        # Process each instance
        for instance_name, instance_config in instances.items():
            # Get repository configuration from instance
            repo_configs = instance_config.get("repositories", [])
            if isinstance(repo_configs, str):
                repo_configs = [repo_configs]

            for repo_name in repo_configs:
                # Find repository URL
                repo_url = None
                if repo_name in repos_config:
                    repo_url = repos_config[repo_name].get("url")

                if not repo_url:
                    continue

                # Check if this repository has GitHub webhook config
                github_repo_config = github_repos.get(repo_name, {})

                # Check if auto_watch is enabled (default True)
                auto_watch = github_repo_config.get("auto_watch", True)
                if not auto_watch:
                    # Check if instance is excluded
                    excluded = github_repo_config.get("exclude_instances", [])
                    if instance_name in excluded:
                        continue

                # Get default action from GitHub config
                default_actions = github_repo_config.get(
                    "default_action", "pull+restart"
                )
                if isinstance(default_actions, str):
                    default_actions = [default_actions]

                # Parse actions
                actions = []
                for action_str in default_actions:
                    if action_str == "pull+restart":
                        actions.append(ActionType.PULL_RESTART)
                    elif action_str == "pull":
                        actions.append(ActionType.PULL)
                    elif action_str == "restart":
                        actions.append(ActionType.RESTART)

                if not actions:
                    actions = [ActionType.PULL_RESTART]  # Default

                # Create repository watch config
                watch_config = RepositoryWatchConfig(
                    repository_url=repo_url,
                    instance_name=instance_name,
                    branch="main",  # Default, could be configured per instance
                    actions=actions,
                    enabled=True,
                )

                repositories.append(watch_config)

                # Check for specific watchers
                specific_watchers = github_repo_config.get("watchers", [])
                for watcher in specific_watchers:
                    if watcher.get("instance") == instance_name:
                        # Override with specific watcher configuration
                        watch_config.enabled = watcher.get("enabled", True)

                        watcher_actions = watcher.get("action", "pull+restart")
                        if isinstance(watcher_actions, str):
                            watcher_actions = [watcher_actions]

                        watch_config.actions = []
                        for action_str in watcher_actions:
                            if action_str == "pull+restart":
                                watch_config.actions.append(ActionType.PULL_RESTART)
                            elif action_str == "pull":
                                watch_config.actions.append(ActionType.PULL)
                            elif action_str == "restart":
                                watch_config.actions.append(ActionType.RESTART)

                        break

        return repositories

    def _get_daemon_metadata(self) -> Dict[str, Any]:
        """Get webhook server daemon specific metadata."""
        metadata = super()._get_daemon_metadata()
        metadata.update(
            {
                "daemon_type": "WebhookServerDaemon",
                "config_file": self.config_file,
                "description": "Multi-provider webhook server daemon for "
                "repository event handling",
                "server_host": self.host_override or "localhost",
                "server_port": self.port_override or 8080,
            }
        )
        return metadata


def main():
    """Main entry point for webhook server daemon."""
    parser = argparse.ArgumentParser(description="Webhook server daemon")
    parser.add_argument("--config", "-c", required=True, help="Path to dooservice.yml")
    parser.add_argument("--host", help="Server host (overrides config)")
    parser.add_argument("--port", type=int, help="Server port (overrides config)")

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)

    # Create and start daemon
    daemon = WebhookServerDaemon(args.config, args.host, args.port)
    daemon.start()


if __name__ == "__main__":
    main()
