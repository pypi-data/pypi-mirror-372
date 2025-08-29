from abc import ABC, abstractmethod
from typing import Tuple

from core.domain.entities.instance_config import InstanceConfig


class InstanceRepository(ABC):
    """An interface for a repository that handles instance lifecycle management."""

    @abstractmethod
    def create(self, config: InstanceConfig) -> None:
        """Creates an instance based on the provided configuration."""

    @abstractmethod
    def start(self, name: str) -> None:
        """Starts an instance by its name."""

    @abstractmethod
    def stop(self, name: str) -> None:
        """Stops an instance by its name."""

    @abstractmethod
    def status(self, name: str) -> str:
        """Gets the status of an instance by its name."""

    @abstractmethod
    def logs(self, name: str, tail: int = 50, follow: bool = False) -> str:
        """Gets the logs of an instance by its name."""

    @abstractmethod
    def delete(self, name: str) -> None:
        """Deletes an instance by its name."""

    @abstractmethod
    def install_python_dependencies(self, name: str, dependencies: list[str]) -> None:
        """Installs Python dependencies inside the instance."""

    @abstractmethod
    def recreate(self, config: InstanceConfig) -> None:
        """Recreates an instance based on the provided configuration."""

    @abstractmethod
    def exec_command(
        self,
        name: str,
        command: str,
        stream: bool = False,
    ) -> Tuple[int, str]:
        """
        Executes a command inside a running instance.

        Returns a tuple of (exit_code, output).
        If stream is True, output is printed directly and an empty string is returned.
        """
