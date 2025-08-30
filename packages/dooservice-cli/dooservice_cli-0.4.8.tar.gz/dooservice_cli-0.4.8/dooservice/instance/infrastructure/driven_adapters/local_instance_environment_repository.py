from pathlib import Path
from typing import Set

from core.domain.entities.instance_config import InstanceConfig
from instance.domain.repositories.instance_environment_repository import (
    InstanceEnvironmentRepository,
)
from repository.domain.services.module_detector import ModuleDetectorService
from shared.config.constants import ODOO_CONF_VARS


class LocalInstanceEnvironmentRepository(InstanceEnvironmentRepository):
    """
    A driven adapter that sets up the local environment for an instance.

    Including generating odoo.conf and .env files.
    """

    def __init__(self, module_detector: ModuleDetectorService):
        self._module_detector = module_detector

    def setup(self, instance: InstanceConfig) -> None:
        """Orchestrates the creation of all necessary configuration files."""
        self._generate_odoo_conf(instance)
        self._generate_env_file(instance)

    def _generate_odoo_conf(self, instance: InstanceConfig):
        config_path_str = instance.paths.get("config")
        if not config_path_str:
            return

        config_path = Path(config_path_str)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with config_path.open("w") as f:
            f.write("[options]\n")
            for key in ODOO_CONF_VARS:
                value = instance.env_vars.get(key)
                if value is not None:
                    f.write(f"{key.lower()} = {value}\n")

            addons_path_str = self._get_addons_path_string(instance)
            if addons_path_str:
                f.write(f"addons_path = {addons_path_str}\n")

    def _get_addons_path_string(self, instance: InstanceConfig) -> str:
        host_addons_base_path_str = instance.paths.get("addons")
        if not host_addons_base_path_str:
            return ""

        host_addons_base_path = Path(host_addons_base_path_str)
        discovered_paths = self._module_detector.get_addons_paths(
            str(host_addons_base_path),
        )
        container_mount_path = Path("/mnt/extra-addons")

        processed_paths: Set[Path] = set()
        for path_str in discovered_paths:
            path = Path(path_str)
            try:
                relative_path = path.relative_to(host_addons_base_path)
                processed_paths.add(container_mount_path / relative_path)
            except ValueError:
                continue

        if str(host_addons_base_path) in discovered_paths:
            processed_paths.add(container_mount_path)

        return ",".join(sorted([str(p) for p in processed_paths]))

    def _generate_env_file(self, instance: InstanceConfig):
        env_file_path_str = instance.paths.get("env_file")
        if not env_file_path_str:
            return

        env_file_path = Path(env_file_path_str)
        env_file_path.parent.mkdir(parents=True, exist_ok=True)

        with env_file_path.open("w") as f:
            for key, value in instance.env_vars.items():
                f.write(f'{key}="{value}"\n')
