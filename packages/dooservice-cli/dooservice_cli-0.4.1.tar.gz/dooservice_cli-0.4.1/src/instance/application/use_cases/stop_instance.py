"""Stop instance use case."""

from core.domain.entities.instance_config import InstanceConfig
from instance.domain.services.instance_orchestrator import InstanceOrchestrator


class StopInstanceUseCase:
    """Use case for stopping a running Odoo instance."""

    def __init__(self, orchestrator: InstanceOrchestrator):
        self._orchestrator = orchestrator

    def execute(self, config: InstanceConfig) -> None:
        """
        Stop an Odoo instance with all its services.

        Args:
            config: Instance configuration

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        self._orchestrator.stop_instance(config)
