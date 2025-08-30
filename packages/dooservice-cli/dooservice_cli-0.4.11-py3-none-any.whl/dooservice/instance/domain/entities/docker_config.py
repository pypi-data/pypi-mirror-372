from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DockerConfig:
    """
    A standardized configuration object for creating a Docker container.

    This entity is used by the DockerRepository (port) and implemented by the
    DockerAdapter. It translates the declarative configuration from the YAML
    file into the specific parameters needed by the Docker SDK.
    """

    image: str  # The Docker image to use for the container.
    name: str  # The name of the container.
    restart_policy: str = "unless-stopped"  # Restart policy (e.g., 'unless-stopped').
    networks: List[str] = field(default_factory=list)  # List of networks to connect to.
    ports: Dict[str, Any] = field(default_factory=dict)  # Port mappings.
    volumes: Dict[str, dict] = field(default_factory=dict)  # Volume mappings.
    environment: Dict[str, str] = field(default_factory=dict)  # Environment variables.
    env_file: List[str] = field(default_factory=list)  # List of .env files to use.
    depends_on: List[str] = field(
        default_factory=list,
    )  # Containers this one depends on.
    detach: bool = True  # Whether to run the container in detached mode.
    healthcheck: Dict[str, Any] = field(
        default_factory=dict,
    )  # Health check configuration.
