from dataclasses import dataclass
from typing import Optional

from core.domain.entities.github_config import GitHubRepositoryConfig


@dataclass
class Repository:
    """Defines a source code repository, typically for Odoo addons."""

    source_type: str  # Type of the source, e.g., 'git'.
    path: Optional[str] = None  # Local path to the repository, if applicable.
    type: Optional[str] = None  # Type of git source, e.g., 'http', 'ssh'.
    url: Optional[str] = None  # URL of the remote repository (legacy field).
    source: Optional[str] = (
        None  # URL or path of the repository source (preferred field).
    )
    branch: Optional[str] = None  # Git branch to check out.
    commit: Optional[str] = None  # Specific commit hash to check out.
    ssh_key_path: Optional[str] = None  # Path to the SSH key for authentication.
    submodules: bool = False  # Whether to initialize and update git submodules.
    github: Optional[GitHubRepositoryConfig] = None  # GitHub integration configuration

    def __post_init__(self):
        """Ensure either url or source is provided, preferring source."""
        if not self.source and not self.url:
            raise ValueError("Either 'source' or 'url' must be provided")

        # If only url is provided, copy it to source for internal consistency
        if not self.source and self.url:
            self.source = self.url

        # If only source is provided, copy it to url for backward compatibility
        if not self.url and self.source:
            self.url = self.source

    @property
    def repository_url(self) -> str:
        """Get the repository URL, preferring source over url."""
        return self.source or self.url
