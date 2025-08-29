"""Docker-based instance repository for webhook operations."""

import logging
from typing import Optional

import yaml

from ..repositories import InstanceRepository


class DockerInstanceWebhookRepository(InstanceRepository):
    """Docker-based implementation of instance repository for webhooks."""

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)

    def pull_repository(self, instance_name: str, repository_url: str) -> None:
        """Pull latest changes for instance repository."""
        # This would integrate with existing repository management
        # For now, log the action
        self.logger.info(
            "Pulling repository %s for instance %s", repository_url, instance_name
        )

        # Import and use existing repository sync functionality
        try:
            from repository.application.use_cases.sync_repositories_use_case import (
                SyncRepositoriesUseCase,
            )
            from repository.infrastructure.driven_adapters.git_repository_manager import (  # noqa: E501
                GitRepositoryManager,
            )

            # Initialize repository manager
            repo_manager = GitRepositoryManager()
            sync_use_case = SyncRepositoriesUseCase(repo_manager)

            # Load configuration
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            # Find the repository name for this URL
            repositories = data.get("repositories", {})
            repo_name = None
            for name, config in repositories.items():
                if config.get("url") == repository_url:
                    repo_name = name
                    break

            if repo_name:
                # Sync specific repository
                sync_use_case.sync_repository(data, repo_name)
                self.logger.info("Successfully pulled repository %s", repository_url)
            else:
                self.logger.warning("Repository %s not found in config", repository_url)

        except Exception as e:
            self.logger.error("Failed to pull repository %s: %s", repository_url, e)
            raise

    def restart_instance(self, instance_name: str) -> None:
        """Restart the specified instance."""
        self.logger.info("Restarting instance %s", instance_name)

        # Import and use existing instance management
        try:
            from instance.application.use_cases.restart_instance_use_case import (
                RestartInstanceUseCase,
            )
            from instance.infrastructure.driven_adapters.docker_instance_repository import (  # noqa: E501
                DockerInstanceRepository,
            )

            # Initialize instance repository and use case
            docker_repo = DockerInstanceRepository()
            restart_use_case = RestartInstanceUseCase(docker_repo)

            # Load configuration
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            # Restart instance
            restart_use_case.execute(data, instance_name)
            self.logger.info("Successfully restarted instance %s", instance_name)

        except Exception as e:
            self.logger.error("Failed to restart instance %s: %s", instance_name, e)
            raise

    def instance_exists(self, instance_name: str) -> bool:
        """Check if instance exists."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            instances = data.get("instances", {})
            return instance_name in instances

        except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
            self.logger.error("Error checking if instance exists: %s", e)
            return False

    def get_instance_repository_url(self, instance_name: str) -> Optional[str]:
        """Get the repository URL for an instance."""
        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            instances = data.get("instances", {})
            repositories = data.get("repositories", {})

            if instance_name not in instances:
                return None

            instance_config = instances[instance_name]
            repo_configs = instance_config.get("repositories", [])

            if isinstance(repo_configs, str):
                repo_configs = [repo_configs]

            # Return URL of first repository (could be extended to handle multiple)
            if repo_configs:
                repo_name = repo_configs[0]
                if repo_name in repositories:
                    return repositories[repo_name].get("url")

            return None

        except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
            self.logger.error(
                "Error getting repository URL for instance %s: %s", instance_name, e
            )
            return None
