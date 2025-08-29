"""Delete instance use case."""

from core.domain.entities.instance_config import InstanceConfig
from instance.domain.services.instance_orchestrator import InstanceOrchestrator


class DeleteInstanceUseCase:
    """Use case for deleting an Odoo instance and optionally its data."""

    def __init__(self, orchestrator: InstanceOrchestrator):
        self._orchestrator = orchestrator

    def execute(self, config: InstanceConfig, remove_data: bool = False) -> None:
        """
        Delete an Odoo instance and optionally its data.

        Args:
            config: Instance configuration
            remove_data: Whether to also remove data directory

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        self._orchestrator.delete_instance(config, remove_data=remove_data)
