from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set


@dataclass(frozen=True)
class ModuleInfo:
    """
    Pure domain entity representing an Odoo module.

    Contains information about a detected Odoo module without
    depending on external file formats or configurations.
    """

    name: str
    path: Path
    manifest_path: Path
    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    depends: List[str] = None
    auto_install: bool = False
    installable: bool = True

    def __post_init__(self):
        """Validate module information after initialization."""
        if not self.name.strip():
            raise ValueError("Module name cannot be empty")
        if not self.path.exists():
            raise ValueError(f"Module path does not exist: {self.path}")
        if not self.manifest_path.exists():
            raise ValueError(f"Module manifest does not exist: {self.manifest_path}")

        # Initialize depends as empty list if None
        if self.depends is None:
            object.__setattr__(self, "depends", [])

    @property
    def parent_directory(self) -> Path:
        """Get the parent directory of this module (the addons path)."""
        return self.path.parent

    @property
    def is_valid(self) -> bool:
        """Check if the module has a valid structure."""
        return self.path.is_dir() and self.manifest_path.is_file() and self.installable


@dataclass(frozen=True)
class AddonsPath:
    """
    Pure domain entity representing an addons path containing Odoo modules.

    Represents a directory that contains one or more Odoo modules.
    """

    path: Path
    modules: List[ModuleInfo]

    def __post_init__(self):
        """Validate addons path after initialization."""
        if not self.path.exists():
            raise ValueError(f"Addons path does not exist: {self.path}")
        if not self.path.is_dir():
            raise ValueError(f"Addons path is not a directory: {self.path}")

    @property
    def module_count(self) -> int:
        """Get the number of modules in this addons path."""
        return len(self.modules)

    @property
    def module_names(self) -> Set[str]:
        """Get a set of module names in this addons path."""
        return {module.name for module in self.modules}

    @property
    def installable_modules(self) -> List[ModuleInfo]:
        """Get only the installable modules from this addons path."""
        return [module for module in self.modules if module.installable]


@dataclass(frozen=True)
class RepositoryModules:
    """
    Pure domain entity representing all modules found in a repository.

    Aggregates all addons paths and modules found within a repository structure.
    """

    repository_name: str
    repository_path: Path
    addons_paths: List[AddonsPath]

    @property
    def all_modules(self) -> List[ModuleInfo]:
        """Get all modules from all addons paths."""
        modules = []
        for addons_path in self.addons_paths:
            modules.extend(addons_path.modules)
        return modules

    @property
    def all_module_names(self) -> Set[str]:
        """Get all module names from all addons paths."""
        names = set()
        for addons_path in self.addons_paths:
            names.update(addons_path.module_names)
        return names

    @property
    def addons_path_strings(self) -> List[str]:
        """Get addons paths as string list for Odoo configuration."""
        return [str(addons_path.path) for addons_path in self.addons_paths]

    @property
    def total_module_count(self) -> int:
        """Get total number of modules across all addons paths."""
        return sum(addons_path.module_count for addons_path in self.addons_paths)
