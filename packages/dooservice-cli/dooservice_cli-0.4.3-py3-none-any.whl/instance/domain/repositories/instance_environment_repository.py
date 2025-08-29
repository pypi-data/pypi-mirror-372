from abc import ABC, abstractmethod

from core.domain.entities.instance_config import InstanceConfig


class InstanceEnvironmentRepository(ABC):
    """
    An interface for a repository that handles the setup of the instance's environment.

    Handles the setup of the instance's environment, such as creating configuration
    files.
    """

    @abstractmethod
    def setup(self, instance_config: InstanceConfig) -> None:
        """Sets up the environment for a given instance."""
