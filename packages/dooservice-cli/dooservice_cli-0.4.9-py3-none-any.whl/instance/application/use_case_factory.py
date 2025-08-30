"""Factory for creating instance use cases with proper dependencies."""

from core.infrastructure.driven_adapters.os_filesystem_repository import (
    OsFilesystemRepository,
)
from instance.application.use_cases.create_instance import CreateInstanceUseCase
from instance.application.use_cases.delete_instance import DeleteInstanceUseCase
from instance.application.use_cases.exec_instance import ExecInstanceUseCase
from instance.application.use_cases.logs_instance import LogsInstanceUseCase
from instance.application.use_cases.start_instance import StartInstanceUseCase
from instance.application.use_cases.status_instance import StatusInstanceUseCase
from instance.application.use_cases.stop_instance import StopInstanceUseCase
from instance.application.use_cases.sync_instance import SyncInstanceUseCase
from instance.domain.services.database_manager import DatabaseManager
from instance.domain.services.instance_orchestrator import InstanceOrchestrator
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


class InstanceUseCaseFactory:
    """Factory for creating instance use cases with proper dependencies."""

    def __init__(self):
        # Initialize repositories
        self._docker_instance_repository = DockerInstanceRepository()
        self._filesystem_repository = OsFilesystemRepository()
        self._git_repository = GitPythonRepository()
        self._module_repository = FilesystemModuleRepository()
        self._module_detector = ModuleDetectorService(self._module_repository)
        self._instance_environment_repository = LocalInstanceEnvironmentRepository(
            self._module_detector
        )

        # Initialize domain services
        self._instance_orchestrator = InstanceOrchestrator(
            self._docker_instance_repository, self._filesystem_repository
        )

        self._repository_manager = RepositoryManager(
            self._git_repository, self._filesystem_repository
        )

        self._database_manager = DatabaseManager(self._docker_instance_repository)

    def create_instance_use_case(self) -> CreateInstanceUseCase:
        """Create use case for instance creation."""
        return CreateInstanceUseCase(
            self._repository_manager,
            self._instance_environment_repository,
            self._docker_instance_repository,
        )

    def start_instance_use_case(self) -> StartInstanceUseCase:
        """Create use case for starting instances."""
        return StartInstanceUseCase(self._instance_orchestrator)

    def stop_instance_use_case(self) -> StopInstanceUseCase:
        """Create use case for stopping instances."""
        return StopInstanceUseCase(self._instance_orchestrator)

    def delete_instance_use_case(self) -> DeleteInstanceUseCase:
        """Create use case for deleting instances."""
        return DeleteInstanceUseCase(self._instance_orchestrator)

    def status_instance_use_case(self) -> StatusInstanceUseCase:
        """Create use case for getting instance status."""
        return StatusInstanceUseCase(self._instance_orchestrator)

    def logs_instance_use_case(self) -> LogsInstanceUseCase:
        """Create use case for getting instance logs."""
        return LogsInstanceUseCase(self._docker_instance_repository)

    def exec_instance_use_case(self) -> ExecInstanceUseCase:
        """Create use case for executing commands in instances."""
        return ExecInstanceUseCase(self._docker_instance_repository)

    def sync_instance_use_case(self) -> SyncInstanceUseCase:
        """Create use case for synchronizing instances."""
        return SyncInstanceUseCase(
            self._repository_manager,
            self._database_manager,
            self._docker_instance_repository,
            self._instance_environment_repository,
        )
