from abc import ABC, abstractmethod
from typing import Any, Dict


class ConfigRepository(ABC):
    """Interface for loading the raw configuration data."""

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """
        Loads the raw configuration from a source.

        Returns:
            A dictionary representing the raw configuration.
        """
