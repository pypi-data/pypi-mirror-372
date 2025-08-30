"""Execute command in instance use case."""

from typing import List

from instance.domain.repositories.instance_repository import InstanceRepository


class ExecInstanceUseCase:
    """Use case for executing commands inside an Odoo instance."""

    def __init__(self, instance_repository: InstanceRepository):
        self.instance_repository = instance_repository

    def execute_web_command(self, instance_name: str, command: List[str]) -> str:
        """
        Execute a command in the web container of an instance.

        Args:
            instance_name: Name of the instance
            command: Command to execute as list of strings

        Returns:
            Command output

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        return self.instance_repository.exec_command(
            instance_name, command, service="web"
        )

    def execute_db_command(self, instance_name: str, command: List[str]) -> str:
        """
        Execute a command in the database container of an instance.

        Args:
            instance_name: Name of the instance
            command: Command to execute as list of strings

        Returns:
            Command output

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        return self.instance_repository.exec_command(
            instance_name, command, service="db"
        )
