"""YAML-based webhook configuration repository."""

from typing import List, Optional

import yaml

from ..entities import ActionType, RepositoryWatchConfig, WebhookConfig
from ..repositories import WebhookConfigRepository


class YamlWebhookConfigRepository(WebhookConfigRepository):
    """YAML file-based webhook configuration repository."""

    def __init__(self, config_file: str):
        self.config_file = config_file

    def get_webhook_config(self) -> Optional[WebhookConfig]:
        """Get the current webhook configuration from YAML file."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            return self._parse_webhook_config(data)

        except (FileNotFoundError, yaml.YAMLError, KeyError, ValueError):
            return None

    def update_webhook_config(self, config: WebhookConfig) -> None:
        """Update webhook configuration (not implemented for YAML)."""
        raise NotImplementedError("YAML webhook config is read-only")

    def get_repository_watches(self) -> List[RepositoryWatchConfig]:
        """Get all repository watch configurations."""
        config = self.get_webhook_config()
        return config.repositories if config else []

    def get_watches_for_repository(
        self, repository_url: str
    ) -> List[RepositoryWatchConfig]:
        """Get watch configurations for a specific repository."""
        all_watches = self.get_repository_watches()
        return [
            watch for watch in all_watches if watch.repository_url == repository_url
        ]

    def _parse_webhook_config(self, data: dict) -> WebhookConfig:
        """Parse webhook configuration from YAML data."""
        # This is a simplified version - the full parsing logic would be
        # moved here from webhook_daemon.py for better separation of concerns

        github_config = data.get("github", {})
        webhook_config = github_config.get("webhook", {})

        return WebhookConfig(
            enabled=webhook_config.get("enabled", True),
            repositories=self._extract_repository_watches(data),
        )

    def _extract_repository_watches(self, data: dict) -> List[RepositoryWatchConfig]:
        """Extract repository watch configurations from YAML data."""
        repositories = []

        instances = data.get("instances", {})
        repos_config = data.get("repositories", {})
        github_repos = data.get("github", {}).get("repositories", {})

        for instance_name, instance_config in instances.items():
            repo_configs = instance_config.get("repositories", [])
            if isinstance(repo_configs, str):
                repo_configs = [repo_configs]

            for repo_name in repo_configs:
                repo_url = None
                if repo_name in repos_config:
                    repo_url = repos_config[repo_name].get("url")

                if not repo_url:
                    continue

                github_repo_config = github_repos.get(repo_name, {})
                auto_watch = github_repo_config.get("auto_watch", True)

                if not auto_watch:
                    excluded = github_repo_config.get("exclude_instances", [])
                    if instance_name in excluded:
                        continue

                default_actions = github_repo_config.get(
                    "default_action", "pull+restart"
                )
                if isinstance(default_actions, str):
                    default_actions = [default_actions]

                actions = []
                for action_str in default_actions:
                    if action_str == "pull+restart":
                        actions.append(ActionType.PULL_RESTART)
                    elif action_str == "pull":
                        actions.append(ActionType.PULL)
                    elif action_str == "restart":
                        actions.append(ActionType.RESTART)

                if not actions:
                    actions = [ActionType.PULL_RESTART]

                watch_config = RepositoryWatchConfig(
                    repository_url=repo_url,
                    instance_name=instance_name,
                    branch="main",
                    actions=actions,
                    enabled=True,
                )

                repositories.append(watch_config)

        return repositories
