from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Tuple

import click

from core.domain.entities.dooservice_config import DooServiceConfig
from core.domain.entities.instance_config import InstanceConfig
from core.domain.entities.lockfile import LockFile
from core.domain.services.config_service import create_config_service
from core.domain.services.diff_manager import Diff, DiffManager
from core.domain.services.lock_file_checksum_service import LockFileChecksumService
from core.domain.services.lock_manager import LockManager
from core.infrastructure.driven_adapters.file_lock_repository import FileLockRepository
from core.infrastructure.driven_adapters.os_filesystem_repository import (
    OsFilesystemRepository,
)
from core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from instance.application.use_case_factory import InstanceUseCaseFactory
from instance.domain.services.instance_lifecycle_service import (
    InstanceLifecycleService,
)
from instance.domain.services.repository_manager import RepositoryManager
from instance.infrastructure.driven_adapters.docker_instance_repository import (
    DockerInstanceRepository,
)
from instance.infrastructure.driven_adapters.local_instance_environment_repository import (  # noqa: E501
    LocalInstanceEnvironmentRepository,
)
from repository.domain.services.module_detector import ModuleDetectorService
from repository.infrastructure.driven_adapters.filesystem_module_repository import (
    FilesystemModuleRepository,
)
from repository.infrastructure.driven_adapters.git_python_repository import (
    GitPythonRepository,
)
from shared.config.placeholder_resolver import PlaceholderResolver


class InstanceConfigContext:
    """Centralized configuration context for instance CLI commands."""

    def __init__(self, config_file: str = "dooservice.yml"):
        """Initialize config context with configuration file."""
        self.config_file = Path(config_file)
        self._dooservice_config = None
        self._lock_file = None
        self._placeholder_resolver = PlaceholderResolver()

        # Initialize repositories and services
        self._filesystem_repo = OsFilesystemRepository()
        self._git_repo = GitPythonRepository()
        self._module_repo = FilesystemModuleRepository()

        # Initialize services
        self._module_detector = ModuleDetectorService(self._module_repo)
        self._instance_env_repo = LocalInstanceEnvironmentRepository(
            self._module_detector
        )
        self._instance_repo = DockerInstanceRepository()
        self._lock_manager = LockManager(LockFileChecksumService())
        self._lock_repo = FileLockRepository(self.config_file.parent)
        self._config_repo = YAMLConfigRepository(str(self.config_file))
        self._config_service = create_config_service()

        # Initialize domain services
        self._diff_manager = DiffManager()
        self._repository_manager = RepositoryManager(
            self._git_repo, self._filesystem_repo
        )
        self._instance_lifecycle_service = InstanceLifecycleService(
            self._instance_repo, self._instance_env_repo
        )

        # Initialize use case factory
        self._use_case_factory = InstanceUseCaseFactory()

        # Get use cases from factory for backward compatibility
        self.create_instance_use_case = (
            self._use_case_factory.create_instance_use_case()
        )
        self.sync_instance_use_case = self._use_case_factory.sync_instance_use_case()

    @property
    def dooservice_config(self) -> DooServiceConfig:
        """Load and validate dooservice configuration."""
        if self._dooservice_config is None:
            self._load_config()
        return self._dooservice_config

    @property
    def lock_file(self) -> Optional[LockFile]:
        """Load lock file if it exists."""
        if self._lock_file is None:
            try:
                self._lock_file = self._lock_repo.get()
            except (FileNotFoundError, ValueError, KeyError):
                self._lock_file = None
        return self._lock_file

    def _load_config(self):
        """Load and validate configuration."""
        try:
            raw_config = self._config_repo.load()
            self._dooservice_config = self._config_service.validate(raw_config)
        except Exception as e:
            raise click.ClickException(f"Error loading configuration: {e}") from e

    def get_instance_config(self, instance_name: str) -> InstanceConfig:
        """Get configuration for a specific instance."""
        instance_config = self.dooservice_config.instances.get(instance_name)
        if not instance_config:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            )
        return instance_config

    def resolve_instance_config(self, instance_name: str) -> InstanceConfig:
        """Resolve placeholders in instance configuration."""
        instance_config = self.get_instance_config(instance_name)

        # Resolve placeholders iteratively
        resolved_config = instance_config
        for _ in range(5):  # Iterate to resolve nested placeholders
            context = asdict(resolved_config)
            context["name"] = instance_name
            resolved_config = self._placeholder_resolver.resolve(
                resolved_config, context
            )

        # Convert port values to int
        resolved_config.ports = {k: int(v) for k, v in resolved_config.ports.items()}

        # Set the instance name
        resolved_config.instance_name = instance_name

        return resolved_config

    def get_all_instance_names(self) -> List[str]:
        """Get list of all instance names."""
        return list(self.dooservice_config.instances.keys())

    def create_instance_with_progress(self, instance_name: str) -> InstanceConfig:
        """Create instance with progress tracking and all configuration handling."""
        resolved_config = self.resolve_instance_config(instance_name)

        # Execute core creation logic through use case
        click.secho("□ Executing instance creation...", dim=True)
        self.create_instance_use_case.execute(resolved_config)
        click.secho("\r✔ Executing instance creation...", fg="green")

        # Install Python dependencies if needed
        if resolved_config.python_dependencies:
            click.secho("□ Installing Python dependencies...", dim=True)
            self.create_instance_use_case.install_dependencies(resolved_config)
            click.secho("\r✔ Installing Python dependencies...", fg="green")

        # Generate and save lock file
        click.secho("□ Generating lock file...", dim=True)
        self._generate_and_save_lock_file(instance_name, resolved_config)
        click.secho("\r✔ Generating lock file...", fg="green")

        # Start instance
        click.secho("□ Starting instance...", dim=True)
        self._instance_repo.start(resolved_config.deployment.docker.web.container_name)
        click.secho("\r✔ Starting instance...", fg="green")

        return resolved_config

    def sync_instance_with_diff(
        self, instance_name: str
    ) -> Tuple[List[Diff], LockFile]:
        """Sync instance with configuration changes and return diff."""
        new_config = self.dooservice_config
        lock_file = self.lock_file

        if not lock_file:
            raise click.ClickException(
                "No lock file found. Please create instance first."
            )

        resolved_instance_config = self.resolve_instance_config(instance_name)
        locked_instance_config = lock_file.instances.items.get(instance_name)

        # Compare configurations
        diffs = self._diff_manager.compare(
            locked_instance_config, resolved_instance_config
        )

        if not diffs:
            return [], lock_file

        # Sync database credentials BEFORE other synchronization if needed
        self._sync_database_credentials_if_needed(
            diffs, resolved_instance_config, locked_instance_config
        )

        # Execute synchronization through use case
        self.sync_instance_use_case.execute(
            resolved_instance_config, locked_instance_config
        )

        # Generate new lock file
        updated_config = DooServiceConfig(
            version=new_config.version,
            domains=new_config.domains,
            repositories=new_config.repositories,
            instances={**new_config.instances, instance_name: resolved_instance_config},
        )
        new_lock_file = self._lock_manager.generate_from_config(updated_config)
        self._lock_repo.save(new_lock_file)

        return diffs, new_lock_file

    def _sync_database_credentials_if_needed(
        self, diffs, resolved_instance_config, locked_instance_config
    ):
        """
        Check if database credentials changed and sync them if necessary.

        This method handles all the diff analysis and configuration logic,
        keeping the domain services pure.
        """
        # Check if there are database credential changes
        db_credential_changes = self._has_database_credential_changes(diffs)
        if not db_credential_changes:
            return

        # Ensure we have the necessary deployment configuration
        if (
            not resolved_instance_config.deployment
            or not resolved_instance_config.deployment.docker
            or not resolved_instance_config.deployment.docker.db
        ):
            return

        # Extract credential information
        db_container = resolved_instance_config.deployment.docker.db
        new_user = resolved_instance_config.env_vars.get("DB_USER")
        new_password = resolved_instance_config.env_vars.get("DB_PASSWORD")

        if not new_user or not new_password:
            return

        # Get old credentials if available
        old_user = None
        if locked_instance_config and locked_instance_config.env_vars:
            old_user = locked_instance_config.env_vars.get("DB_USER")

        # Execute credential sync through use case
        # Use old_user as superuser if available, otherwise new_user
        # This handles cases where user is changing vs password only
        superuser = old_user if old_user else new_user

        click.secho("□ Synchronizing database credentials...", dim=True)
        self.sync_instance_use_case.sync_database_credentials(
            db_container.container_name,
            old_user,
            new_user,
            new_password,
            superuser,
        )
        click.secho("\r✔ Synchronizing database credentials...", fg="green")

    def _has_database_credential_changes(self, diffs) -> bool:
        """
        Check if any of the diffs involve database credential changes.

        Args:
            diffs: List of configuration differences.

        Returns:
            True if DB_USER or DB_PASSWORD have changed.
        """
        db_credential_paths = {
            ("env_vars", "DB_USER"),
            ("env_vars", "DB_PASSWORD"),
        }

        for diff in diffs:
            if diff.type == "changed" and len(diff.path) >= 2:
                path_tuple = tuple(diff.path[-2:])  # Get last two path elements
                if path_tuple in db_credential_paths:
                    return True
        return False

    def delete_instance_simple(self, container_name: str, data_dir: str) -> None:
        """Simple delete instance functionality."""
        # Stop and remove container
        self._instance_repo.stop(container_name)
        self._instance_repo.delete(container_name)

        # Remove data directory
        import shutil

        if Path(data_dir).exists():
            shutil.rmtree(data_dir)

    def start_instance_simple(self, container_name: str) -> None:
        """Simple start instance functionality."""
        self._instance_repo.start(container_name)

    def stop_instance_simple(self, container_name: str) -> None:
        """Simple stop instance functionality."""
        self._instance_repo.stop(container_name)

    def status_instance_simple(self, container_name: str) -> str:
        """Simple status instance functionality."""
        return self._instance_repo.status(container_name)

    def logs_instance_simple(
        self, container_name: str, follow: bool, lines: int
    ) -> None:
        """Simple logs instance functionality."""
        self._instance_repo.logs(container_name, follow=follow, tail=lines)

    def exec_web_instance_simple(self, container_name: str, command: str) -> None:
        """Simple exec web instance functionality."""
        self._instance_repo.exec_command(container_name, command)

    def exec_db_instance_simple(self, container_name: str, command: str) -> None:
        """Simple exec db instance functionality."""
        self._instance_repo.exec_command(container_name, command)

    def _generate_and_save_lock_file(
        self, instance_name: str, resolved_config: InstanceConfig
    ):
        """Generate and save lock file."""
        # Update config with resolved instance
        updated_config = DooServiceConfig(
            version=self.dooservice_config.version,
            domains=self.dooservice_config.domains,
            repositories=self.dooservice_config.repositories,
            instances={
                **self.dooservice_config.instances,
                instance_name: resolved_config,
            },
        )
        new_lock_file = self._lock_manager.generate_from_config(updated_config)
        self._lock_repo.save(new_lock_file)


# Decorators for instance CLI commands
def instance_config_context(f):
    """Decorator to inject config context into instance CLI commands."""

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        config_file = ctx.params.get("config", "dooservice.yml")
        ctx.obj = InstanceConfigContext(config_file)
        return f(*args, **kwargs)

    return wrapper


# Standard config option decorator
def config_option():
    """Standard --config option decorator for instance CLI commands."""
    return click.option(
        "--config",
        "-c",
        "config",
        type=click.Path(exists=True),
        default="dooservice.yml",
        help="Path to dooservice.yml configuration file",
    )
