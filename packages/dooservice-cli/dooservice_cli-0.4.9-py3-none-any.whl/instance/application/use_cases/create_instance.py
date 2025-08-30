from core.domain.entities.instance_config import InstanceConfig
from instance.domain.repositories.instance_environment_repository import (
    InstanceEnvironmentRepository,
)
from instance.domain.repositories.instance_repository import InstanceRepository
from instance.domain.services.repository_manager import RepositoryManager


class CreateInstanceUseCase:
    """
    Pure domain use case for creating a new instance.

    This use case focuses on the core business logic of instance creation
    without external configuration concerns.
    """

    def __init__(
        self,
        repository_manager: RepositoryManager,
        instance_env_repo: InstanceEnvironmentRepository,
        instance_repo: InstanceRepository,
    ):
        self._repository_manager = repository_manager
        self._instance_env_repo = instance_env_repo
        self._instance_repo = instance_repo

    def execute(self, resolved_config: InstanceConfig) -> None:
        """
        Execute the core instance creation logic.

        Args:
            resolved_config: Fully resolved instance configuration.
        """
        # 1. Ensure repositories are set up
        self._repository_manager.ensure_repositories(resolved_config)

        # 2. Set up instance environment (e.g., odoo.conf)
        self._instance_env_repo.setup(resolved_config)

        # 3. Create the instance infrastructure (e.g., Docker containers)
        self._instance_repo.create(resolved_config)

    def install_dependencies(self, config: InstanceConfig) -> None:
        """Install Python dependencies for instance."""
        if not config.deployment.docker or not config.deployment.docker.web:
            return

        web_container = config.deployment.docker.web.container_name
        was_started = self._instance_repo.status(web_container) == "running"

        if not was_started:
            self._instance_repo.start(web_container)

        self._instance_repo.install_python_dependencies(
            name=web_container,
            dependencies=config.python_dependencies,
        )

        if not was_started:
            self._instance_repo.stop(web_container)
