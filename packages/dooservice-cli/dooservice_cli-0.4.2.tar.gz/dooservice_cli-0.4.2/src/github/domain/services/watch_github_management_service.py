"""GitHub watch management service."""

from typing import List

from core.domain.services.config_service import ConfigService
from github.domain.entities.github_watch import (
    RepositoryWatchGitHub,
    WatchGitHubActionType,
    WatchGitHubType,
)


class WatchGitHubManagementService:
    """Service for managing GitHub repository watches."""

    def __init__(self, config_service: ConfigService):
        """Initialize the service."""
        self.config_service = config_service

    def get_configured_watches(self) -> List[RepositoryWatchGitHub]:
        """Get all configured repository watches."""
        try:
            doo_config = self.config_service.load_config()
            watches = []

            # Process individual repository github configurations
            for repo_name, repo in doo_config.repositories.items():
                # Check if repo has github config with auto_watch
                if repo.github and repo.github.auto_watch:
                    # For auto-watch repositories, find all instances that use this repo
                    for instance_name, instance in doo_config.instances.items():
                        instance_repos = instance.repositories
                        if isinstance(instance_repos, str):
                            instance_repos = [instance_repos]

                        if repo_name in instance_repos:
                            # Check if this instance should be excluded
                            exclude_instances = repo.github.exclude_instances or []
                            if instance_name not in exclude_instances:
                                watch = self._create_watch_from_repo_config(
                                    repo_name, repo, instance_name, repo.github
                                )
                                watches.append(watch)

                # Process explicit watchers
                if repo.github and repo.github.watchers:
                    for watcher in repo.github.watchers:
                        if watcher.enabled:
                            watch = self._create_watch_from_watcher_config(
                                repo_name, repo, watcher
                            )
                            watches.append(watch)

            # Process global github.repositories configurations
            if (
                doo_config.github
                and hasattr(doo_config.github, "repositories")
                and doo_config.github.repositories
            ):
                for repo_name, github_config in doo_config.github.repositories.items():
                    repo = doo_config.repositories.get(repo_name)
                    if not repo:
                        continue

                    if github_config.auto_watch:
                        # For auto-watch repositories, find all instances that use this
                        # repo
                        for instance_name, instance in doo_config.instances.items():
                            instance_repos = instance.repositories
                            if isinstance(instance_repos, str):
                                instance_repos = [instance_repos]

                            if repo_name in instance_repos:
                                # Check if this instance should be excluded
                                exclude_instances = (
                                    github_config.exclude_instances or []
                                )
                                if (
                                    instance_name not in exclude_instances
                                    and not self._watch_already_exists(
                                        watches, repo_name, instance_name
                                    )
                                ):
                                    watch = self._create_watch_from_global_config(
                                        repo_name,
                                        repo,
                                        instance_name,
                                        github_config,
                                    )
                                    watches.append(watch)

                    # Process explicit watchers
                    if github_config.watchers:
                        for watcher in github_config.watchers:
                            if watcher.enabled and not self._watch_already_exists(
                                watches, repo_name, watcher.instance
                            ):
                                watch = self._create_watch_from_global_watcher_config(
                                    repo_name, repo, watcher
                                )
                                watches.append(watch)

            return watches

        except (ValueError, KeyError, AttributeError) as e:
            # Log error but return empty list for now
            if hasattr(self, "logger"):
                self.logger.error("Error loading watch configuration: %s", e)
            return []

    def get_all_known_repositories(self) -> List[str]:
        """
        Get all known GitHub repositories from configuration (including disabled ones).

        Returns:
            List of repository names in 'owner/repo' format
        """
        try:
            doo_config = self.config_service.load_config()
            repos = []

            # Process individual repository github configurations
            for repo in doo_config.repositories.values():
                if (
                    repo.type == "github"
                    and hasattr(repo, "url")
                    and repo.url
                    and "github.com/" in repo.url
                ):
                    # Parse URL like: https://github.com/owner/repo.git
                    url_part = repo.url.split("github.com/")[-1]
                    if url_part.endswith(".git"):
                        url_part = url_part[:-4]
                    repos.append(url_part)

            return repos

        except (ValueError, KeyError, AttributeError) as e:
            if hasattr(self, "logger"):
                self.logger.error("Error getting all known repositories: %s", e)
            return []

    def validate_watch_configuration(self, watch: RepositoryWatchGitHub) -> List[str]:
        """Validate a watch configuration."""
        errors = []

        try:
            doo_config = self.config_service.load_config()

            # Check if repository exists
            if watch.repository_name not in doo_config.repositories:
                errors.append(
                    f"Repository '{watch.repository_name}' not found in configuration"
                )

            # Check if instance exists
            if watch.instance_name not in doo_config.instances:
                errors.append(
                    f"Instance '{watch.instance_name}' not found in configuration"
                )

            # Validate GitHub URL
            if not watch.repository_owner or not watch.repository_repo:
                errors.append("Invalid GitHub repository URL")

            # Validate actions
            errors.extend(
                f"Invalid action type: {action}"
                for action in watch.actions
                if not isinstance(action, WatchGitHubActionType)
            )

        except (ValueError, KeyError, AttributeError) as e:
            errors.append(f"Configuration validation error: {e}")

        return errors

    def _create_watch_from_repo_config(
        self, repo_name: str, repo, instance_name: str, github_config
    ) -> RepositoryWatchGitHub:
        """Create a watch from repository-level GitHub configuration."""
        repo_url = repo.url or repo.source
        owner, repo_name_parsed = RepositoryWatchGitHub._parse_github_url(repo_url)

        actions = self._parse_actions(github_config.default_action)

        return RepositoryWatchGitHub(
            repository_name=repo_name,
            repository_url=repo_url,
            repository_owner=owner,
            repository_repo=repo_name_parsed,
            instance_name=instance_name,
            actions=actions,
            enabled=True,
            webhook_secret=None,
            branch=repo.branch or "main",
            watch_type=WatchGitHubType.AUTO,
        )

    def _create_watch_from_watcher_config(
        self, repo_name: str, repo, watcher
    ) -> RepositoryWatchGitHub:
        """Create a watch from explicit watcher configuration."""
        repo_url = repo.url or repo.source
        owner, repo_name_parsed = RepositoryWatchGitHub._parse_github_url(repo_url)

        actions = self._parse_actions(watcher.action)

        return RepositoryWatchGitHub(
            repository_name=repo_name,
            repository_url=repo_url,
            repository_owner=owner,
            repository_repo=repo_name_parsed,
            instance_name=watcher.instance,
            actions=actions,
            enabled=watcher.enabled,
            webhook_secret=getattr(watcher, "webhook_secret", None),
            branch=repo.branch or "main",
            watch_type=WatchGitHubType.MANUAL,
        )

    def _create_watch_from_global_config(
        self, repo_name: str, repo, instance_name: str, github_config
    ) -> RepositoryWatchGitHub:
        """Create a watch from global GitHub configuration."""
        repo_url = repo.url or repo.source
        owner, repo_name_parsed = RepositoryWatchGitHub._parse_github_url(repo_url)

        actions = self._parse_actions(github_config.default_action)

        return RepositoryWatchGitHub(
            repository_name=repo_name,
            repository_url=repo_url,
            repository_owner=owner,
            repository_repo=repo_name_parsed,
            instance_name=instance_name,
            actions=actions,
            enabled=True,
            webhook_secret=None,
            branch=repo.branch or "main",
            watch_type=WatchGitHubType.AUTO,
        )

    def _create_watch_from_global_watcher_config(
        self, repo_name: str, repo, watcher
    ) -> RepositoryWatchGitHub:
        """Create a watch from global watcher configuration."""
        repo_url = repo.url or repo.source
        owner, repo_name_parsed = RepositoryWatchGitHub._parse_github_url(repo_url)

        actions = self._parse_actions(watcher.action)

        return RepositoryWatchGitHub(
            repository_name=repo_name,
            repository_url=repo_url,
            repository_owner=owner,
            repository_repo=repo_name_parsed,
            instance_name=watcher.instance,
            actions=actions,
            enabled=watcher.enabled,
            webhook_secret=getattr(watcher, "webhook_secret", None),
            branch=repo.branch or "main",
            watch_type=WatchGitHubType.MANUAL,
        )

    def _parse_actions(self, actions_str) -> List[WatchGitHubActionType]:
        """Parse action string into action types."""
        if isinstance(actions_str, str):
            return [WatchGitHubActionType(actions_str)]
        if isinstance(actions_str, list):
            return [WatchGitHubActionType(action) for action in actions_str]
        return [WatchGitHubActionType.PULL_RESTART]

    def _watch_already_exists(
        self, watches: List[RepositoryWatchGitHub], repo_name: str, instance_name: str
    ) -> bool:
        """Check if a watch already exists for the given repo and instance."""
        return any(
            w.repository_name == repo_name and w.instance_name == instance_name
            for w in watches
        )
