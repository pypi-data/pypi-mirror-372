"""OAuth entities and data structures."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class OAuthUser:
    """Represents a user from OAuth provider."""

    id: str
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "unknown"
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthConfig:
    """Configuration for OAuth provider."""

    provider_name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_url: str
    redirect_uri: str = "http://localhost:8080/auth/callback"
    scopes: List[str] = field(default_factory=list)
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuthToken:
    """OAuth access token information."""

    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_in:
            return False

        expiry_time = self.created_at + timedelta(seconds=self.expires_in)
        # Add 5 minute buffer for safety
        return datetime.utcnow() >= (expiry_time - timedelta(minutes=5))

    @property
    def authorization_header(self) -> str:
        """Get Authorization header value."""
        return f"{self.token_type} {self.access_token}"


@dataclass
class OAuthAuth:
    """Complete OAuth authentication data."""

    provider: str
    token: OAuthToken
    user: OAuthUser
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def access_token(self) -> str:
        """Convenience property for access token."""
        return self.token.access_token

    @property
    def is_expired(self) -> bool:
        """Check if authentication is expired."""
        return self.token.is_expired

    @property
    def scopes(self) -> List[str]:
        """Get token scopes."""
        return self.token.scopes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "provider": self.provider,
            "token": {
                "access_token": self.token.access_token,
                "token_type": self.token.token_type,
                "expires_in": self.token.expires_in,
                "refresh_token": self.token.refresh_token,
                "scopes": self.token.scopes,
                "created_at": self.token.created_at.isoformat(),
                "raw_data": self.token.raw_data,
            },
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
                "name": self.user.name,
                "avatar_url": self.user.avatar_url,
                "provider": self.user.provider,
                "raw_data": self.user.raw_data,
            },
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthAuth":
        """Create from dictionary."""
        token_data = data["token"]
        user_data = data["user"]

        token = OAuthToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scopes=token_data.get("scopes", []),
            created_at=datetime.fromisoformat(token_data["created_at"]),
            raw_data=token_data.get("raw_data", {}),
        )

        user = OAuthUser(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data.get("email"),
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            provider=user_data.get("provider", "unknown"),
            raw_data=user_data.get("raw_data", {}),
        )

        return cls(
            provider=data["provider"],
            token=token,
            user=user,
            created_at=datetime.fromisoformat(data["created_at"]),
        )
