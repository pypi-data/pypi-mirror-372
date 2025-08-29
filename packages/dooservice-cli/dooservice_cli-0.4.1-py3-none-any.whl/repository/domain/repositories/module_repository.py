from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from repository.domain.entities.module_info import (
    AddonsPath,
    ModuleInfo,
    RepositoryModules,
)


class ModuleRepository(ABC):
    """An interface for detecting and analyzing Odoo modules in repositories."""

    @abstractmethod
    def scan_for_modules(self, base_path: Path) -> List[ModuleInfo]:
        """
        Scans a directory recursively and returns all detected Odoo modules.

        Args:
            base_path: The base directory to scan for modules.

        Returns:
            List of ModuleInfo objects for all detected modules.
        """

    @abstractmethod
    def get_module_info(self, module_path: Path) -> Optional[ModuleInfo]:
        """Analyzes a specific directory and returns module information if valid.

        Analyzes a specific directory and returns module information
        if it's a valid Odoo module.

        This method performs detailed analysis of a potential module directory.

        Args:
            module_path: Path to the potential module directory.

        Returns:
            ModuleInfo object if valid module, None otherwise.
        """

    @abstractmethod
    def find_addons_paths(self, base_path: Path) -> List[AddonsPath]:
        """
        Finds all addons paths (directories containing modules) within a base directory.

        Args:
            base_path: The base directory to search in.

        Returns:
            List of AddonsPath objects containing modules.
        """

    @abstractmethod
    def analyze_repository(
        self, repository_path: Path, repository_name: str
    ) -> RepositoryModules:
        """
        Performs a complete analysis of a repository for Odoo modules.

        Args:
            repository_path: Path to the repository to analyze.
            repository_name: Name of the repository for identification.

        Returns:
            RepositoryModules object with complete module analysis.
        """

    # Backward compatibility method
    def get_module_paths(self, base_path: str) -> List[str]:
        """
        Legacy method for backward compatibility.

        Args:
            base_path: Base path as string.

        Returns:
            List of module paths as strings.
        """
        modules = self.scan_for_modules(Path(base_path))
        return [str(module.path) for module in modules]
