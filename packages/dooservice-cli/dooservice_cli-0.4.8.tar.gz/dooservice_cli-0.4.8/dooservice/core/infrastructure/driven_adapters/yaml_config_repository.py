from typing import Any, Dict

import yaml

from core.domain.repositories.config_repository import ConfigRepository


class YAMLConfigRepository(ConfigRepository):
    """Implementation of ConfigRepository that loads configuration from a YAML file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> Dict[str, Any]:
        """
        Loads the raw configuration from the YAML file.

        Returns:
            A dictionary representing the raw configuration.
        """
        with open(self.file_path) as f:
            return yaml.safe_load(f)
