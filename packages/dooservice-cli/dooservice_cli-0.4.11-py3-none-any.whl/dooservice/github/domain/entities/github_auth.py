"""GitHub authentication entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class GitHubSSHKey:
    """Represents a GitHub SSH key."""

    id: int
    title: str
    key: str
    fingerprint: str
    created_at: datetime
    read_only: bool = False


@dataclass
class GitHubUser:
    """Represents a GitHub user."""

    login: str
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class GitHubAuth:
    """Represents GitHub authentication state."""

    access_token: str
    user: GitHubUser
    scopes: List[str]
    expires_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Check if the authentication token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at


@dataclass
class GitHubRepository:
    """Represents a GitHub repository."""

    owner: str
    name: str
    full_name: str
    clone_url: str
    ssh_url: str
    default_branch: str
    private: bool = False

    @property
    def identifier(self) -> str:
        """Get repository identifier (owner/name)."""
        return f"{self.owner}/{self.name}"
