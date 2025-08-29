"""
Repository Reference Resolver.

Pure domain service responsible for resolving repository references in configurations.
Follows Single Responsibility Principle.
"""

from copy import deepcopy
from typing import Any, Dict


class RepositoryReferenceResolver:
    """Domain service for resolving repository references in instance configurations.

    Converts list-based repository references to their full repository definitions
    from the global repositories section.
    """

    def resolve_repository_references(
        self,
        raw_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolves list-based repository references in instances.

        Resolves list-based repository references in instances against global
        definitions.

        Args:
            raw_config: The raw configuration dictionary

        Returns:
            Configuration with resolved repository references
        """
        # Create a deep copy to avoid modifying the original
        resolved_config = deepcopy(raw_config)

        if not self._has_required_sections(resolved_config):
            return resolved_config

        global_repos = resolved_config.get("repositories", {})

        for instance_data in resolved_config["instances"].values():
            self._resolve_instance_repositories(instance_data, global_repos)

        return resolved_config

    def _has_required_sections(self, config: Dict[str, Any]) -> bool:
        """
        Checks if the configuration has the required sections for resolution.

        Args:
            config: Configuration dictionary

        Returns:
            True if both instances and repositories sections exist
        """
        return "instances" in config and "repositories" in config

    def _resolve_instance_repositories(
        self,
        instance_data: Dict[str, Any],
        global_repos: Dict[str, Any],
    ) -> None:
        """
        Resolves repository references for a single instance.

        Args:
            instance_data: Instance configuration data (modified in place)
            global_repos: Global repository definitions
        """
        if "repositories" not in instance_data:
            return

        repo_section = instance_data["repositories"]

        # Only process list-based references
        if isinstance(repo_section, list):
            resolved_repos = self._resolve_repository_list(repo_section, global_repos)
            instance_data["repositories"] = resolved_repos

    def _resolve_repository_list(
        self,
        repo_references: list,
        global_repos: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolves a list of repository references to their full definitions.

        Args:
            repo_references: List of repository reference strings
            global_repos: Global repository definitions

        Returns:
            Dictionary of resolved repository configurations
        """
        resolved_repos = {}

        for repo_ref in repo_references:
            if self._is_valid_reference(repo_ref, global_repos):
                resolved_repos[repo_ref] = global_repos[repo_ref]

        return resolved_repos

    def _is_valid_reference(self, repo_ref: Any, global_repos: Dict[str, Any]) -> bool:
        """
        Checks if a repository reference is valid.

        Args:
            repo_ref: Repository reference to validate
            global_repos: Global repository definitions

        Returns:
            True if the reference is a valid string that exists in global_repos
        """
        return isinstance(repo_ref, str) and repo_ref in global_repos


def create_repository_reference_resolver() -> RepositoryReferenceResolver:
    """
    Factory function to create a RepositoryReferenceResolver instance.

    Returns:
        New RepositoryReferenceResolver instance
    """
    return RepositoryReferenceResolver()
