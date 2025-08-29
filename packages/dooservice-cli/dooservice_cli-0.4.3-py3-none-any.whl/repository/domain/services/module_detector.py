from pathlib import Path
from typing import List

from repository.domain.entities.module_info import (
    AddonsPath,
    ModuleInfo,
    RepositoryModules,
)
from repository.domain.repositories.module_repository import ModuleRepository


class ModuleDetectorService:
    """
    A pure domain service for comprehensive Odoo module detection and analysis.

    This service provides high-level operations for discovering and analyzing
    Odoo modules in repository structures without external dependencies.
    """

    def __init__(self, module_repository: ModuleRepository):
        """Initialize the service with a module repository implementation."""
        self._module_repository = module_repository

    def analyze_repository_modules(
        self, repository_path: Path, repository_name: str
    ) -> RepositoryModules:
        """
        Perform a complete analysis of modules in a repository.

        Args:
            repository_path: Path to the repository to analyze.
            repository_name: Name of the repository for identification.

        Returns:
            RepositoryModules object with complete module structure analysis.
        """
        return self._module_repository.analyze_repository(
            repository_path, repository_name
        )

    def find_all_addons_paths(self, base_path: Path) -> List[AddonsPath]:
        """
        Find all directories that contain Odoo modules (addons paths).

        Args:
            base_path: The base directory to search in.

        Returns:
            List of AddonsPath objects containing modules.
        """
        return self._module_repository.find_addons_paths(base_path)

    def get_modules_in_directory(self, directory_path: Path) -> List[ModuleInfo]:
        """
        Get all modules found in a specific directory.

        Args:
            directory_path: Directory to scan for modules.

        Returns:
            List of ModuleInfo objects found in the directory.
        """
        return self._module_repository.scan_for_modules(directory_path)

    def is_module_directory(self, path: Path) -> bool:
        """
        Check if a directory is a valid Odoo module.

        Args:
            path: Path to check.

        Returns:
            True if the directory contains a valid Odoo module.
        """
        module_info = self._module_repository.get_module_info(path)
        return module_info is not None and module_info.is_valid

    def get_installable_modules(self, base_path: Path) -> List[ModuleInfo]:
        """
        Get only installable modules from a directory structure.

        Args:
            base_path: Base directory to search.

        Returns:
            List of installable ModuleInfo objects.
        """
        all_modules = self._module_repository.scan_for_modules(base_path)
        return [module for module in all_modules if module.installable]

    def get_module_dependencies(self, base_path: Path) -> dict[str, List[str]]:
        """
        Get a mapping of module names to their dependencies.

        Args:
            base_path: Base directory to analyze.

        Returns:
            Dictionary mapping module names to their dependency lists.
        """
        modules = self._module_repository.scan_for_modules(base_path)
        return {module.name: module.depends for module in modules}

    # Legacy method for backward compatibility
    def get_addons_paths(self, base_path: str) -> List[str]:
        """
        Legacy method that returns addons paths as string list.

        Args:
            base_path: Base path as string.

        Returns:
            List of addons paths as strings.
        """
        addons_paths = self.find_all_addons_paths(Path(base_path))
        return [str(addons_path.path) for addons_path in addons_paths]
