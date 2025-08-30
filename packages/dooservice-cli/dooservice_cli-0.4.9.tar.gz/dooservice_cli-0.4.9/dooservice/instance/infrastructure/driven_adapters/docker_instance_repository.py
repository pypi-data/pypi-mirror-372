import sys
import time
from typing import Any, Dict, Optional, Tuple

import docker

from core.domain.entities.deployment_config import (
    DockerDbServiceConfig,
    DockerWebServiceConfig,
)
from core.domain.entities.instance_config import InstanceConfig
from instance.domain.repositories.instance_repository import InstanceRepository
from shared.errors.docker_error import DockerError
from shared.ui.progress_bar import ProgressBar


class DockerInstanceRepository(InstanceRepository):
    """An adapter that implements the InstanceRepository interface using the Docker SDK.

    It handles the lifecycle of Docker containers.
    """

    def __init__(self, docker_client: Optional[docker.DockerClient] = None):
        """
        Initializes the Docker client.

        Args:
            docker_client: An optional pre-configured Docker client. If not
                           provided, a new client is created from the environment.

        Raises:
            DockerError: If the Docker daemon is not available.
        """
        try:
            self.docker_client = docker_client or docker.from_env()
        except docker.errors.DockerException as e:
            raise DockerError(f"Docker is not available: {e}") from e

    def create(self, config: InstanceConfig) -> None:
        """
        Creates Docker containers for an instance, including web and db services.

        Args:
            config: The instance configuration containing deployment details.

        Raises:
            DockerError: If the deployment type is not 'docker' or if a
                         container creation fails.
        """
        if not config.deployment or config.deployment.type != "docker":
            raise DockerError("Deployment config is not of type 'docker'.")

        docker_config = config.deployment.docker
        if not docker_config:
            raise DockerError("Docker deployment configuration is missing.")

        if docker_config.db:
            self._create_single_container(docker_config.db)
        if docker_config.web:
            self._create_single_container(docker_config.web)

    def start(self, name: str) -> None:
        """
        Starts a Docker container by its name.

        Args:
            name: The name of the container to start.

        Raises:
            DockerError: If the container is not found or fails to start.
        """
        try:
            container = self.docker_client.containers.get(name)
            container.start()
        except docker.errors.NotFound as e:
            raise DockerError(f"Container '{name}' not found.") from e
        except docker.errors.APIError as e:
            raise DockerError(f"Failed to start container '{name}': {e}") from e

    def stop(self, name: str) -> None:
        """
        Stops a Docker container by its name.

        Args:
            name: The name of the container to stop.

        Raises:
            DockerError: If the container is not found or fails to stop.
        """
        try:
            container = self.docker_client.containers.get(name)
            container.stop()
        except docker.errors.NotFound:
            pass  # If it doesn't exist, it's already "stopped".
        except docker.errors.APIError as e:
            raise DockerError(f"Failed to stop container '{name}': {e}") from e

    def delete(self, name: str) -> None:
        """
        Deletes a Docker container by its name, forcing removal if necessary.

        Args:
            name: The name of the container to delete.

        Raises:
            DockerError: If the container fails to be deleted.
        """
        try:
            container = self.docker_client.containers.get(name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass  # If it doesn't exist, it's already "deleted".
        except docker.errors.APIError as e:
            raise DockerError(f"Failed to delete container '{name}': {e}") from e

    def status(self, name: str) -> str:
        """
        Gets the status of a Docker container (e.g., 'running', 'exited').

        Args:
            name: The name of the container to check.

        Returns:
            The status string or 'not found' if the container does not exist.
        """
        try:
            container = self.docker_client.containers.get(name)
            return container.status
        except docker.errors.NotFound:
            return "not found"

    def logs(self, name: str, tail: int = 50, follow: bool = False) -> str:
        """
        Retrieves logs from a container.

        Args:
            name: The name of the container.
            tail: The number of lines to show from the end of the logs.
            follow: Whether to stream the logs continuously.

        Returns:
            The logs as a string, or an empty string if following.

        Raises:
            DockerError: If the container is not found.
        """
        try:
            container = self.docker_client.containers.get(name)
            if follow:
                log_stream = container.logs(tail=tail, stream=True, follow=True)
                for line in log_stream:
                    sys.stdout.write(line.decode("utf-8"))
                return ""
            logs_output = container.logs(tail=tail).decode("utf-8")
            sys.stdout.write(logs_output)
            return logs_output
        except docker.errors.NotFound as e:
            raise DockerError(f"Container '{name}' not found.") from e

    def install_python_dependencies(self, name: str, dependencies: list[str]) -> None:
        """
        Installs Python dependencies inside a running container using pip.

        Args:
            name: The name of the container.
            dependencies: A list of pip packages to install.

        Raises:
            DockerError: If the container is not running or installation fails.
        """
        if not dependencies:
            return

        # Show progress bar for dependency installation
        with ProgressBar.create(dependencies, label="Installing pkgs") as deps_progress:
            for dep in deps_progress:
                install_command = f"pip install --break-system-packages {dep}"
                exit_code, output = self.exec_command(name, install_command)

                if exit_code != 0:
                    raise DockerError(
                        f"Failed to install dependency '{dep}' in '{name}'. "
                        f"Exit code: {exit_code}. Output: {output}",
                    )

                # Small delay to make progress visible
                time.sleep(0.1)

    def exec_command(
        self,
        name: str,
        command: str,
        stream: bool = False,
    ) -> Tuple[int, str]:
        """
        Executes a command inside a running container.

        Args:
            name: The name of the container.
            command: The command to execute.
            stream: If True, streams the output to stdout/stderr.

        Returns:
            A tuple containing the exit code and the captured output.

        Raises:
            DockerError: If the container is not running or the command fails.
        """
        try:
            container = self.docker_client.containers.get(name)
            if container.status != "running":
                raise DockerError(f"Container '{name}' is not running.")

            exec_result = container.exec_run(
                cmd=command,
                user="root",
                stream=stream,
                demux=True,
            )

            if stream:
                for stdout, stderr in exec_result.output:
                    if stdout:
                        sys.stdout.write(stdout.decode("utf-8"))
                    if stderr:
                        sys.stderr.write(stderr.decode("utf-8"))
                # We can't get an exit code reliably from a stream this way.
                # A more advanced implementation would use websockets.
                return 0, ""
            exit_code, (stdout, stderr) = exec_result
            output = (stdout or b"") + (stderr or b"")
            return exit_code, output.decode("utf-8")

        except docker.errors.NotFound as e:
            raise DockerError(f"Container '{name}' not found.") from e
        except docker.errors.APIError as e:
            raise DockerError(f"Command execution failed in '{name}': {e}") from e

    def _create_single_container(
        self,
        service_config: DockerWebServiceConfig | DockerDbServiceConfig,
    ):
        try:
            self.docker_client.containers.get(service_config.container_name)
            return  # Container already exists
        except docker.errors.NotFound:
            pass  # Container does not exist, proceed to create it

        for network_name in service_config.networks:
            self._ensure_network_exists(network_name)

        try:
            params = self._build_container_params(service_config)
            self.docker_client.containers.create(**params)
        except docker.errors.APIError as e:
            raise DockerError(
                f"Failed to create container '{service_config.container_name}': {e}",
            ) from e

    def _build_container_params(self, service_config: ...) -> Dict[str, Any]:
        params = {
            "image": service_config.image,
            "name": service_config.container_name,
            "detach": True,
            "volumes": service_config.volumes,
            "environment": service_config.environment,
            "restart_policy": {"Name": service_config.restart_policy}
            if service_config.restart_policy
            else None,
            "network": service_config.networks[0]
            if service_config.networks
            else "bridge",
            "ports": {p.split(":")[1]: p.split(":")[0] for p in service_config.ports},
        }
        if service_config.user:
            params["user"] = service_config.user
        if service_config.healthcheck:
            params["healthcheck"] = {
                "test": service_config.healthcheck.test,
                "interval": service_config.healthcheck.interval,
                "timeout": service_config.healthcheck.timeout,
                "retries": service_config.healthcheck.retries,
                "start_period": service_config.healthcheck.start_period,
            }
        return params

    def _ensure_network_exists(self, network_name: str):
        try:
            self.docker_client.networks.get(network_name)
        except docker.errors.NotFound:
            self.docker_client.networks.create(name=network_name)

    def recreate(self, config: InstanceConfig) -> None:
        """
        Recreates the Docker containers for the instance.

        This is useful when the container configuration has changed.
        """
        if config.deployment.type != "docker" or not config.deployment.docker:
            raise DockerError(
                "Deployment type is not 'docker' or docker configuration is missing.",
            )

        docker_config = config.deployment.docker

        if docker_config.web:
            self.delete(docker_config.web.container_name)
            self._create_single_container(docker_config.web)
            self.start(docker_config.web.container_name)

        if docker_config.db:
            self.delete(docker_config.db.container_name)
            self._create_single_container(docker_config.db)
            self.start(docker_config.db.container_name)
