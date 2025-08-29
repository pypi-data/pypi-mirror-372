"""Consolidated repository management service for instances."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.domain.entities.instance_config import InstanceConfig
from core.domain.repositories.filesystem_repository import FilesystemRepository
from repository.application.use_cases.ensure_repository import EnsureRepository
from repository.application.use_cases.update_repository import UpdateRepository
from repository.domain.entities.repository_info import (
    RepositoryInfo,
    RepositoryUpdateResult,
)
from repository.domain.repositories.git_repository import GitRepository
from repository.domain.services.repository_management_service import (
    RepositoryManagementService,
)


class RepositoryManager:
    """
    Consolidated service for managing all repository operations for instances.

    This service provides a clean interface for repository management with
    improved error handling, logging, and separation of concerns.
    """

    def __init__(
        self,
        git_repository: GitRepository,
        filesystem_repository: FilesystemRepository,
        logger: Optional[logging.Logger] = None,
    ):
        self._git_repository = git_repository
        self._filesystem_repository = filesystem_repository
        self._logger = logger or logging.getLogger(__name__)

        # Initialize management service and use cases
        self._repo_management_service = RepositoryManagementService(git_repository)
        self._ensure_repository_use_case = EnsureRepository(
            self._repo_management_service
        )
        self._update_repository_use_case = UpdateRepository(
            self._repo_management_service
        )

    def sync_repositories(
        self,
        new_config: InstanceConfig,
        locked_config: Optional[InstanceConfig] = None,
    ) -> List[RepositoryUpdateResult]:
        """
        Synchronize all repositories for an instance.

        Args:
            new_config: New instance configuration with repository definitions
            locked_config: Previous locked configuration for comparison (optional)

        Returns:
            List of repository update results
        """
        instance_name = new_config.instance_name
        self._logger.info("Synchronizing repositories for instance '%s'", instance_name)

        results = []

        try:
            if locked_config:
                # Incremental sync based on changes
                results = self._sync_with_changes(new_config, locked_config)
            else:
                # Fresh sync - ensure all repositories
                results = self._sync_all_repositories(new_config)

            self._logger.info(
                "Synchronized %d repositories for instance '%s'",
                len(results),
                instance_name,
            )

        except Exception as e:
            self._logger.error(
                "Failed to synchronize repositories for instance '%s': %s",
                instance_name,
                e,
            )
            raise

        return results

    def ensure_repositories(
        self, instance_config: InstanceConfig
    ) -> List[RepositoryUpdateResult]:
        """
        Ensure all repositories exist and are set up correctly.

        Args:
            instance_config: Instance configuration

        Returns:
            List of repository update results
        """
        instance_name = instance_config.instance_name
        self._logger.info("Ensuring repositories for instance '%s'", instance_name)

        results = []

        if not instance_config.repositories:
            self._logger.debug(
                "No repositories configured for instance '%s'", instance_name
            )
            return results

        try:
            for repo_name, repo_config in instance_config.repositories.items():
                self._logger.debug("Ensuring repository '%s'", repo_name)

                # Create repository info
                repo_info = self._create_repository_info(
                    repo_name, repo_config, instance_config.addons_path
                )

                # Ensure repository exists
                result = self._ensure_repository_use_case.execute(repo_info)
                results.append(result)

            self._logger.info(
                "Ensured %d repositories for instance '%s'", len(results), instance_name
            )

        except Exception as e:
            self._logger.error(
                "Failed to ensure repositories for instance '%s': %s", instance_name, e
            )
            raise

        return results

    def get_repository_status(self, instance_config: InstanceConfig) -> Dict[str, dict]:
        """
        Get status information for all repositories in an instance.

        Args:
            instance_config: Instance configuration

        Returns:
            Dictionary mapping repository names to status information
        """
        instance_name = instance_config.instance_name
        status = {}

        if not instance_config.repositories:
            return status

        try:
            for repo_name, repo_config in instance_config.repositories.items():
                repo_path = instance_config.addons_path / repo_name

                if not repo_path.exists():
                    status[repo_name] = {"exists": False, "status": "not_found"}
                    continue

                # Get git status
                try:
                    git_status = self._git_repository.get_status(str(repo_path))
                    status[repo_name] = {
                        "exists": True,
                        "status": "ok",
                        "branch": repo_config.branch,
                        "clean": git_status.get("clean", False),
                        "ahead": git_status.get("ahead", 0),
                        "behind": git_status.get("behind", 0),
                    }
                except (ValueError, KeyError, OSError) as e:
                    status[repo_name] = {
                        "exists": True,
                        "status": "error",
                        "error": str(e),
                    }

        except (ValueError, KeyError, OSError) as e:
            self._logger.error(
                "Failed to get repository status for instance '%s': %s",
                instance_name,
                e,
            )

        return status

    def _sync_with_changes(
        self, new_config: InstanceConfig, locked_config: InstanceConfig
    ) -> List[RepositoryUpdateResult]:
        """Sync repositories based on configuration changes."""
        changes = self._analyze_repository_changes(new_config, locked_config)
        results = []

        if not changes.has_changes():
            self._logger.debug("No repository changes detected")
            return results

        # Handle removed repositories
        for repo_name in changes.removed:
            self._logger.info("Repository '%s' removed from configuration", repo_name)
            # Note: We don't automatically delete repository directories
            # This is a safety measure - manual cleanup required

        # Handle new repositories
        for repo_name, repo_config in changes.added:
            self._logger.info("Adding new repository '%s'", repo_name)
            repo_info = self._create_repository_info(
                repo_name, repo_config, new_config.addons_path
            )
            result = self._ensure_repository_use_case.execute(repo_info)
            results.append(result)

        # Handle updated repositories
        for repo_name, repo_config in changes.updated:
            self._logger.info("Updating repository '%s'", repo_name)
            repo_info = self._create_repository_info(
                repo_name, repo_config, new_config.addons_path
            )
            result = self._update_repository_use_case.execute(repo_info)
            results.append(result)

        return results

    def _sync_all_repositories(
        self, config: InstanceConfig
    ) -> List[RepositoryUpdateResult]:
        """Sync all repositories without comparison."""
        return self.ensure_repositories(config)

    def _create_repository_info(
        self, repo_name: str, repo_config, addons_path: Path
    ) -> RepositoryInfo:
        """Create RepositoryInfo from configuration."""
        return RepositoryInfo(
            name=repo_name,
            url=repo_config.repository_url,
            branch=repo_config.branch,
            local_path=addons_path / repo_name,
        )

    def _analyze_repository_changes(
        self, new_config: InstanceConfig, locked_config: InstanceConfig
    ) -> "RepositoryChanges":
        """Analyze changes between repository configurations."""
        new_repos = new_config.repositories or {}
        locked_repos = locked_config.repositories or {}

        # Find added repositories
        added = [
            (name, config)
            for name, config in new_repos.items()
            if name not in locked_repos
        ]

        # Find removed repositories
        removed = [name for name in locked_repos if name not in new_repos]

        # Find updated repositories
        updated = []
        for name, new_repo_config in new_repos.items():
            if name in locked_repos:
                locked_repo_config = locked_repos[name]
                # Check if configuration changed
                if (
                    new_repo_config.repository_url != locked_repo_config.repository_url
                    or new_repo_config.branch != locked_repo_config.branch
                ):
                    updated.append((name, new_repo_config))

        return RepositoryChanges(added, removed, updated)


class RepositoryChanges:
    """Data class representing repository configuration changes."""

    def __init__(
        self,
        added: List[Tuple[str, any]],
        removed: List[str],
        updated: List[Tuple[str, any]],
    ):
        self.added = added
        self.removed = removed
        self.updated = updated

    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(self.added or self.removed or self.updated)
