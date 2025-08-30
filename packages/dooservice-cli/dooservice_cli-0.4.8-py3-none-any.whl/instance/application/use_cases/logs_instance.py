"""Get instance logs use case."""

from instance.domain.repositories.instance_repository import InstanceRepository


class LogsInstanceUseCase:
    """Use case for retrieving logs from an Odoo instance."""

    def __init__(self, instance_repository: InstanceRepository):
        self.instance_repository = instance_repository

    def execute(self, instance_name: str, tail: int = 50, follow: bool = False) -> str:
        """
        Get logs from an Odoo instance.

        Args:
            instance_name: Name of the instance
            tail: Number of lines to show from the end
            follow: Whether to follow the log stream

        Returns:
            Log output as string

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        return self.instance_repository.logs(instance_name, tail=tail, follow=follow)
