from dataclasses import dataclass, field
from typing import Dict, List, Optional

from shared.types import Duration


@dataclass
class DockerHealthcheckConfig:
    """
    Defines a Docker health check for a container.

    Allows Docker to monitor and report the container's health status.
    """

    test: List[str] = field(default_factory=list)  # The command to run to check health.
    interval: Duration = Duration(
        30000000000,
    )  # Time between health checks in nanoseconds (30s).
    timeout: Duration = Duration(
        30000000000,
    )  # Time to wait for the check to complete in nanoseconds (30s).
    retries: int = 3  # Number of consecutive failures before marking as unhealthy.
    start_period: Duration = Duration(
        0,
    )  # Grace period for the container to start up in nanoseconds (0s).


@dataclass
class DockerWebServiceConfig:
    """Configuration for the Odoo web service (main application) in Docker."""

    image: str  # The Docker image to use, e.g., 'odoo:16.0'.
    container_name: str  # The name for the Docker container.
    user: Optional[str] = None  # User to run the container as, e.g., 'root' or 'odoo'.
    restart_policy: Optional[str] = (
        None  # Docker restart policy, e.g., 'unless-stopped'.
    )
    volumes: List[str] = field(default_factory=list)  # List of volume mappings.
    networks: List[str] = field(default_factory=list)  # List of networks to connect to.
    ports: List[str] = field(default_factory=list)  # List of port mappings.
    depends_on: List[str] = field(
        default_factory=list,
    )  # Other services this one depends on.
    environment: Dict[str, str] = field(default_factory=dict)  # Environment variables.
    healthcheck: Optional[DockerHealthcheckConfig] = None  # Health check configuration.


@dataclass
class DockerDbServiceConfig:
    """Configuration for the database service (e.g., PostgreSQL) in Docker."""

    image: str  # The Docker image to use, e.g., 'postgres:15'.
    container_name: str  # The name for the Docker container.
    user: Optional[str] = None  # User to run the container as, e.g., 'root' or 'odoo'.
    restart_policy: Optional[str] = None  # Docker restart policy.
    volumes: List[str] = field(default_factory=list)  # List of volume mappings.
    ports: List[str] = field(default_factory=list)  # List of port mappings.
    depends_on: List[str] = field(
        default_factory=list,
    )  # Other services this one depends on.
    networks: List[str] = field(default_factory=list)  # List of networks to connect to.
    environment: Dict[str, str] = field(default_factory=dict)  # Environment variables.
    healthcheck: Optional[DockerHealthcheckConfig] = None  # Health check configuration.


@dataclass
class DockerConfig:
    """Groups the web and database service configurations for a Docker deployment."""

    web: DockerWebServiceConfig  # The main Odoo web service.
    db: Optional[DockerDbServiceConfig] = None  # The database service.


@dataclass
class DeploymentConfig:
    """Defines the deployment strategy and its configuration for an instance."""

    type: str  # The deployment type, e.g., 'docker'.
    docker: Optional[DockerConfig] = None  # Configuration if type is 'docker'.
