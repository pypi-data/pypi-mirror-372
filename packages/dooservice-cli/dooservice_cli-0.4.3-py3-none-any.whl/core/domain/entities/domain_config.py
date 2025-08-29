from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProviderConfig:
    """Defines authentication credentials for a DNS provider."""

    email: Optional[str] = None
    api_token: Optional[str] = None
    zone_id: Optional[str] = None
    api_key: Optional[str] = None


@dataclass
class BaseDomain:
    """Configuration for a base domain (e.g., 'example.com')."""

    name: str  # The domain name, e.g., "example.com"
    ssl_provider: Optional[str] = None  # Name of the SSL provider to use.
    ssl: Optional[bool] = None  # Enable or disable SSL.
    force_ssl: Optional[bool] = None  # Redirect HTTP to HTTPS.
    redirect_www: Optional[bool] = None  # Redirect www. to non-www. or vice-versa.
    hsts: Optional[bool] = None  # Enable HSTS headers.
    cname_target: Optional[str] = None  # CNAME target for the domain.
    dns_challenge: Optional[bool] = None  # Use DNS challenge for SSL.


@dataclass
class DomainConfig:
    """Top-level settings for domain and DNS management."""

    default_provider: Optional[str] = None
    default_ssl: Optional[bool] = None
    default_force_ssl: Optional[bool] = None
    default_redirect_www: Optional[bool] = None
    default_hsts: Optional[bool] = None
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    base_domains: List[BaseDomain] = field(default_factory=list)
