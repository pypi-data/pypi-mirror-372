from pathlib import Path

from repository.domain.entities.module_info import RepositoryModules
from repository.domain.repositories.module_repository import ModuleRepository


class AnalyzeRepositoryModules:
    """
    Use case for analyzing Odoo modules within a repository.

    This use case orchestrates the module repository to scan and
    analyze all modules found in a repository structure.
    """

    def __init__(self, module_repository: ModuleRepository):
        """
        Initialize the analyze repository modules use case.

        Args:
            module_repository: Repository for module detection and analysis.
        """
        self._module_repository = module_repository

    def execute(self, repository_path: Path, repository_name: str) -> RepositoryModules:
        """
        Execute the analyze repository modules use case.

        Args:
            repository_path: Path to the repository to analyze.
            repository_name: Name of the repository for identification.

        Returns:
            RepositoryModules object with complete module analysis.
        """
        return self._module_repository.analyze_repository(
            repository_path, repository_name
        )
