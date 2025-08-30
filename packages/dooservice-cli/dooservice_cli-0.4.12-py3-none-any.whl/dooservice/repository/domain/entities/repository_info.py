from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RepositoryInfo:
    """
    Pure domain entity representing repository information.

    This entity contains all necessary information to identify and work with
    a repository without depending on external configuration formats.
    """

    name: str
    url: str
    branch: str
    local_path: Path
    recursive_submodules: bool = False

    def __post_init__(self):
        """Validate repository information after initialization."""
        if not self.name.strip():
            raise ValueError("Repository name cannot be empty")
        if not self.url.strip():
            raise ValueError("Repository URL cannot be empty")
        if not self.branch.strip():
            raise ValueError("Repository branch cannot be empty")


@dataclass(frozen=True)
class RepositoryState:
    """
    Pure domain entity representing the current state of a repository.

    Contains immutable state information about a repository at a specific point in time.
    """

    info: RepositoryInfo
    current_commit: Optional[str] = None
    current_branch: Optional[str] = None
    remote_commit: Optional[str] = None
    has_uncommitted_changes: bool = False
    exists_locally: bool = False
    is_valid_repository: bool = False

    @property
    def is_synchronized(self) -> bool:
        """Check if the repository is synchronized with remote."""
        return (
            self.exists_locally
            and self.is_valid_repository
            and not self.has_uncommitted_changes
            and self.current_branch == self.info.branch
            and self.current_commit == self.remote_commit
        )

    @property
    def needs_clone(self) -> bool:
        """Check if the repository needs to be cloned."""
        return not self.exists_locally or not self.is_valid_repository


@dataclass(frozen=True)
class RepositoryUpdateResult:
    """
    Pure domain entity representing the result of a repository update operation.

    Contains information about what changes occurred during an update operation.
    """

    repository_info: RepositoryInfo
    old_commit: Optional[str]
    new_commit: Optional[str]
    operation_performed: str  # "clone", "pull", "checkout", "no_change"
    success: bool
    error_message: Optional[str] = None

    @property
    def was_updated(self) -> bool:
        """Check if the repository was actually updated."""
        return self.success and self.old_commit != self.new_commit

    @property
    def was_cloned(self) -> bool:
        """Check if the repository was cloned during this operation."""
        return self.operation_performed == "clone" and self.success
