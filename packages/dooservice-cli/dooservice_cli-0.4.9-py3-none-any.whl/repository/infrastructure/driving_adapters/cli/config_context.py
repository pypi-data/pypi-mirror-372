"""Centralized configuration context for repository CLI commands."""

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

import click

from core.infrastructure.driven_adapters.os_filesystem_repository import (
    OsFilesystemRepository,
)
from core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from core.infrastructure.driving_adapters.cli.config_cli import create_config_service
from repository.application.use_cases.analyze_repository_modules import (
    AnalyzeRepositoryModules,
)
from repository.application.use_cases.check_repository_status import (
    CheckRepositoryStatus,
)
from repository.application.use_cases.ensure_repository import EnsureRepository
from repository.application.use_cases.update_repository import UpdateRepository
from repository.domain.entities.repository_info import RepositoryInfo
from repository.domain.services.repository_management_service import (
    RepositoryManagementService,
)
from repository.infrastructure.driven_adapters.filesystem_module_repository import (
    FilesystemModuleRepository,
)
from repository.infrastructure.driven_adapters.git_python_repository import (
    GitPythonRepository,
)
from shared.config.placeholder_resolver import PlaceholderResolver


class RepositoryConfigContext:
    """Centralized configuration context for instance-based repository CLI commands."""

    def __init__(self, config_file: str = "dooservice.yml"):
        """Initialize config context with configuration file."""
        self.config_file = Path(config_file)
        self._dooservice_config = None
        self._resolved_instances = None
        self._placeholder_resolver = PlaceholderResolver()

        # Initialize repositories and services
        self._git_repository = GitPythonRepository()
        self._filesystem_repository = OsFilesystemRepository()
        self._module_repository = FilesystemModuleRepository()
        self._repo_management_service = RepositoryManagementService(
            self._git_repository
        )

        # Initialize use cases
        self.ensure_repository_use_case = EnsureRepository(
            self._repo_management_service
        )
        self.update_repository_use_case = UpdateRepository(
            self._repo_management_service
        )
        self.check_repository_status_use_case = CheckRepositoryStatus(
            self._repo_management_service
        )
        self.analyze_repository_modules_use_case = AnalyzeRepositoryModules(
            self._module_repository
        )

    @property
    def dooservice_config(self):
        """Get validated DooService configuration, loading if necessary."""
        if self._dooservice_config is None:
            self._load_and_validate_config()
        return self._dooservice_config

    @property
    def resolved_instances(self) -> Dict[str, Any]:
        """Get instances with placeholders resolved, loading if necessary."""
        if self._resolved_instances is None:
            self._resolve_all_instances()
        return self._resolved_instances

    def _load_and_validate_config(self):
        """Load and validate configuration using the same logic as create_command."""
        try:
            config_repo = YAMLConfigRepository(str(self.config_file))
            config_service = create_config_service()
            raw_config = config_repo.load()
            self._dooservice_config = config_service.validate(raw_config)
        except (ValueError, OSError, RuntimeError) as e:
            raise click.ClickException(f"Error loading configuration: {e}") from e

    def _resolve_all_instances(self):
        """Resolve placeholders for all instances once."""
        self._resolved_instances = {}

        for instance_name, instance_config in self.dooservice_config.instances.items():
            # Resolve placeholders for this instance like create_command does
            resolved_config = instance_config
            for _ in range(5):  # Iterate to resolve nested placeholders
                context = asdict(resolved_config)
                context["name"] = instance_name
                resolved_config = self._placeholder_resolver.resolve(
                    resolved_config,
                    context,
                )

            self._resolved_instances[instance_name] = resolved_config

    def get_instance_config(self, instance_name: str):
        """Get configuration for a specific instance."""
        if instance_name not in self.resolved_instances:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            )

        return self.resolved_instances[instance_name]

    def get_repository_config_for_instance(self, repo_name: str, instance_name: str):
        """Get repository configuration within a specific instance."""
        instance_config = self.get_instance_config(instance_name)

        if (
            not hasattr(instance_config, "repositories")
            or not instance_config.repositories
        ):
            raise click.ClickException(
                f"Instance '{instance_name}' has no repositories configured"
            )

        if repo_name not in instance_config.repositories:
            raise click.ClickException(
                f"Repository '{repo_name}' not found in instance '{instance_name}'"
            )

        return instance_config.repositories[repo_name]

    def get_project_root(self) -> Path:
        """Get project root directory (parent of config file)."""
        return self.config_file.parent.absolute()

    def list_instances(self) -> list:
        """Get list of all configured instance names."""
        return list(self.resolved_instances.keys())

    def create_repository_info_for_instance(
        self, repo_name: str, instance_name: str
    ) -> RepositoryInfo:
        """
        Create a RepositoryInfo object for a repository within a specific instance.

        Args:
            repo_name: Name of the repository in configuration.
            instance_name: Name of the instance.

        Returns:
            RepositoryInfo object with instance-specific path.
        """
        # Get repository configuration from the instance
        repo_config = self.get_repository_config_for_instance(repo_name, instance_name)
        instance_config = self.get_instance_config(instance_name)

        addons_path = instance_config.paths.get("addons")
        if not addons_path:
            raise click.ClickException(
                f"Instance '{instance_name}' has no addons path configured"
            )

        # Repository path within instance addons directory
        local_path = Path(addons_path) / repo_name

        return RepositoryInfo(
            name=repo_name,
            url=repo_config.url,
            branch=repo_config.branch,
            local_path=local_path,
            recursive_submodules=getattr(repo_config, "submodules", False),
        )

    def reload_config(self):
        """Force reload of configuration and related data."""
        self._dooservice_config = None
        self._resolved_instances = None


# Context decorator for repository commands
def repository_config_context(f):
    """Decorator to inject config context into repository CLI commands."""

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        config_file = ctx.params.get("config", "dooservice.yml")
        ctx.obj = RepositoryConfigContext(config_file)
        return f(*args, **kwargs)

    return wrapper


# Standard config option decorator
def config_option():
    """Standard --config option decorator for repository CLI commands."""
    return click.option(
        "--config",
        "-c",
        "config",
        type=click.Path(exists=True),
        default="dooservice.yml",
        help="Path to dooservice.yml configuration file",
    )
