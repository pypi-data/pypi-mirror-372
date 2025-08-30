"""Get instance status use case."""

from typing import Dict

from core.domain.entities.instance_config import InstanceConfig
from instance.domain.services.instance_orchestrator import InstanceOrchestrator


class StatusInstanceUseCase:
    """Use case for getting comprehensive status of an Odoo instance."""

    def __init__(self, orchestrator: InstanceOrchestrator):
        self._orchestrator = orchestrator

    def execute(self, config: InstanceConfig) -> Dict[str, any]:
        """
        Get comprehensive status of an Odoo instance.

        Args:
            config: Instance configuration

        Returns:
            Dictionary with detailed status information

        Raises:
            InstanceNotFoundError: If instance doesn't exist
            DockerError: If Docker operation fails
        """
        return self._orchestrator.get_instance_status(config)
