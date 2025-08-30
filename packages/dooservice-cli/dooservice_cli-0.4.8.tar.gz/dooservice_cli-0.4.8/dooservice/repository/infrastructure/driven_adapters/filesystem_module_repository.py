import ast
import os
from pathlib import Path
from typing import Dict, List, Optional

from repository.domain.entities.module_info import (
    AddonsPath,
    ModuleInfo,
    RepositoryModules,
)
from repository.domain.repositories.module_repository import ModuleRepository


class FilesystemModuleRepository(ModuleRepository):
    """
    A filesystem-based implementation of ModuleRepository.

    Scans the local filesystem to detect Odoo modules by looking for manifest files
    and parsing their contents to extract module information.
    """

    def scan_for_modules(self, base_path: Path) -> List[ModuleInfo]:
        """
        Scans a directory recursively and returns all detected Odoo modules.

        Args:
            base_path: The base directory to scan for modules.

        Returns:
            List of ModuleInfo objects for all detected modules.
        """
        if not base_path.exists() or not base_path.is_dir():
            return []

        modules = []
        for root, _, files in os.walk(base_path):
            root_path = Path(root)
            module_info = self._check_for_module(root_path, files)
            if module_info:
                modules.append(module_info)

        return modules

    def get_module_info(self, module_path: Path) -> Optional[ModuleInfo]:
        """Analyzes a specific directory and returns module information if valid.

        Analyzes a specific directory and returns module information
        if it's a valid Odoo module.

        This method checks for Odoo module manifest files and extracts information.

        Args:
            module_path: Path to the potential module directory.

        Returns:
            ModuleInfo object if valid module, None otherwise.
        """
        if not module_path.exists() or not module_path.is_dir():
            return None

        try:
            files = [f.name for f in module_path.iterdir() if f.is_file()]
            return self._check_for_module(module_path, files)
        except (OSError, PermissionError):
            return None

    def find_addons_paths(self, base_path: Path) -> List[AddonsPath]:
        """
        Finds all addons paths (directories containing modules) within a base directory.

        Args:
            base_path: The base directory to search in.

        Returns:
            List of AddonsPath objects containing modules.
        """
        if not base_path.exists() or not base_path.is_dir():
            return []

        # Group modules by their parent directories
        modules_by_parent: Dict[Path, List[ModuleInfo]] = {}

        for module in self.scan_for_modules(base_path):
            parent_path = module.parent_directory
            if parent_path not in modules_by_parent:
                modules_by_parent[parent_path] = []
            modules_by_parent[parent_path].append(module)

        # Create AddonsPath objects
        addons_paths = []
        for parent_path, modules in modules_by_parent.items():
            addons_path = AddonsPath(path=parent_path, modules=modules)
            addons_paths.append(addons_path)

        return sorted(addons_paths, key=lambda ap: str(ap.path))

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
        addons_paths = self.find_addons_paths(repository_path)

        return RepositoryModules(
            repository_name=repository_name,
            repository_path=repository_path,
            addons_paths=addons_paths,
        )

    def _check_for_module(self, path: Path, files: List[str]) -> Optional[ModuleInfo]:
        """Check if a directory contains a valid Odoo module."""
        # Look for manifest files
        manifest_file = None
        if "__manifest__.py" in files:
            manifest_file = path / "__manifest__.py"
        elif "__openerp__.py" in files:
            manifest_file = path / "__openerp__.py"

        if not manifest_file:
            return None

        # Parse manifest file
        try:
            manifest_data = self._parse_manifest_file(manifest_file)

            return ModuleInfo(
                name=path.name,
                path=path,
                manifest_path=manifest_file,
                version=manifest_data.get("version"),
                description=(
                    manifest_data.get("summary") or manifest_data.get("description")
                ),
                author=manifest_data.get("author"),
                depends=manifest_data.get("depends", []),
                auto_install=manifest_data.get("auto_install", False),
                installable=manifest_data.get("installable", True),
            )
        except (ValueError, OSError, SyntaxError):
            # If we can't parse the manifest, still consider it a module
            # but with minimal information
            return ModuleInfo(
                name=path.name,
                path=path,
                manifest_path=manifest_file,
                depends=[],
                auto_install=False,
                installable=True,
            )

    def _parse_manifest_file(self, manifest_path: Path) -> Dict:
        """Parse an Odoo manifest file and return its contents as a dictionary."""
        try:
            with open(manifest_path, encoding="utf-8") as f:
                content = f.read()

            # Parse the Python dictionary in the manifest file
            tree = ast.parse(content)

            # The manifest should contain a dictionary literal
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    return ast.literal_eval(node)

            # If no dictionary found, try to evaluate the whole file
            return ast.literal_eval(content)

        except (ValueError, OSError, SyntaxError):
            # If parsing fails, return empty dict
            return {}

    # Backward compatibility
    def get_module_paths(self, base_path: str) -> List[str]:
        """Legacy method for backward compatibility."""
        modules = self.scan_for_modules(Path(base_path))
        return [str(module.path) for module in modules]
