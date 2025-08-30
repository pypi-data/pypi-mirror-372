"""GitHub webhook payload parser."""

import hashlib
import hmac
from typing import Any, Dict, Optional

from ..entities import (
    WebhookEventType,
    WebhookPayload,
    WebhookPayloadParser,
    WebhookProvider,
)


class GitHubWebhookParser(WebhookPayloadParser):
    """Parser for GitHub webhook payloads."""

    @property
    def provider(self) -> WebhookProvider:
        """Return GitHub as the provider."""
        return WebhookProvider.GITHUB

    def parse(
        self, headers: Dict[str, str], payload: Dict[str, Any]
    ) -> Optional[WebhookPayload]:
        """
        Parse GitHub webhook payload.

        Args:
            headers: HTTP headers from webhook request
            payload: Raw webhook payload data

        Returns:
            Parsed WebhookPayload or None if not supported
        """
        event_type = headers.get("x-github-event", "").lower()

        if event_type == "push":
            return self._parse_push_event(payload)
        if event_type == "pull_request":
            return self._parse_pull_request_event(payload)
        if event_type == "create" and payload.get("ref_type") == "tag":
            # Handle tag creation
            return self._parse_tag_event(payload)

        # Event type not supported
        return None

    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            payload: Raw payload bytes
            signature: Signature from X-Hub-Signature-256 header
            secret: Webhook secret

        Returns:
            True if signature is valid
        """
        if not signature or not secret:
            return False

        # GitHub uses sha256 with format "sha256=<hash>"
        if not signature.startswith("sha256="):
            return False

        signature_hash = signature[7:]  # Remove "sha256=" prefix

        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        # Use secure comparison to prevent timing attacks
        return hmac.compare_digest(signature_hash, expected_signature)

    def _parse_push_event(self, payload: Dict[str, Any]) -> WebhookPayload:
        """Parse GitHub push event payload."""
        repository = payload.get("repository", {})
        head_commit = payload.get("head_commit", {})

        return WebhookPayload(
            provider=WebhookProvider.GITHUB,
            event_type=WebhookEventType.PUSH,
            repository_url=repository.get("clone_url", repository.get("html_url", "")),
            repository_name=repository.get("full_name", ""),
            branch=payload.get("ref", "").replace("refs/heads/", ""),
            commit_sha=head_commit.get("id"),
            commit_message=head_commit.get("message"),
            commit_author=head_commit.get("author", {}).get("name"),
            raw_payload=payload,
        )

    def _parse_pull_request_event(self, payload: Dict[str, Any]) -> WebhookPayload:
        """Parse GitHub pull request event payload."""
        pull_request = payload.get("pull_request", {})
        repository = payload.get("repository", {})
        head = pull_request.get("head", {})

        return WebhookPayload(
            provider=WebhookProvider.GITHUB,
            event_type=WebhookEventType.PULL_REQUEST,
            repository_url=repository.get("clone_url", repository.get("html_url", "")),
            repository_name=repository.get("full_name", ""),
            branch=head.get("ref", ""),
            commit_sha=head.get("sha"),
            commit_message=pull_request.get("title", ""),
            commit_author=pull_request.get("user", {}).get("login"),
            raw_payload=payload,
        )

    def _parse_tag_event(self, payload: Dict[str, Any]) -> WebhookPayload:
        """Parse GitHub tag creation event payload."""
        repository = payload.get("repository", {})

        return WebhookPayload(
            provider=WebhookProvider.GITHUB,
            event_type=WebhookEventType.TAG,
            repository_url=repository.get("clone_url", repository.get("html_url", "")),
            repository_name=repository.get("full_name", ""),
            branch=payload.get("ref", ""),  # For tags, this will be the tag name
            commit_sha=None,  # Tags don't have a specific commit in create event
            commit_message=f"Tag created: {payload.get('ref', '')}",
            commit_author=payload.get("sender", {}).get("login"),
            raw_payload=payload,
        )
