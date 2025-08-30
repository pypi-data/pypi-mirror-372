"""HTTP-based implementation of GitHub API repository."""

from datetime import datetime
from typing import List

import requests

from github.domain.entities.github_auth import (
    GitHubRepository,
    GitHubSSHKey,
    GitHubUser,
)
from github.domain.entities.github_watch import (
    CreateWatchGitHubWebhookRequest,
    GitHubWatchWebhook,
)
from github.domain.repositories.github_auth_repository import GitHubAPIRepository


class HTTPGitHubAPIRepository(GitHubAPIRepository):
    """HTTP-based GitHub API repository."""

    BASE_URL = "https://api.github.com"

    def __init__(self, timeout: int = 30):
        """Initialize the API repository."""
        self.timeout = timeout

    def get_user(self, access_token: str) -> GitHubUser:
        """
        Get authenticated user information.

        Makes HTTP request to: GET https://api.github.com/user
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/user",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            return GitHubUser(
                login=data["login"],
                id=data["id"],
                name=data.get("name"),
                email=data.get("email"),
                avatar_url=data.get("avatar_url"),
            )

        except requests.RequestException as e:
            raise ValueError(f"Failed to get user information: {e}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from GitHub API: {e}") from e

    def list_ssh_keys(self, access_token: str) -> List[GitHubSSHKey]:
        """
        List user's SSH keys.

        Makes HTTP request to: GET https://api.github.com/user/keys
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/user/keys",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            keys = []

            for key_data in data:
                try:
                    created_at = datetime.fromisoformat(
                        key_data["created_at"].replace("Z", "+00:00"),
                    )
                except (ValueError, KeyError):
                    created_at = datetime.utcnow()

                # GitHub API doesn't return fingerprint, so we generate a basic one
                fingerprint = f"SHA256:{key_data.get('id', 'unknown')}"

                keys.append(
                    GitHubSSHKey(
                        id=key_data["id"],
                        title=key_data["title"],
                        key=key_data["key"],
                        fingerprint=fingerprint,
                        created_at=created_at,
                        read_only=key_data.get("read_only", False),
                    ),
                )

            return keys

        except requests.RequestException as e:
            raise ValueError(f"Failed to list SSH keys: {e}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from GitHub API: {e}") from e

    def add_ssh_key(self, access_token: str, title: str, key: str) -> GitHubSSHKey:
        """
        Add SSH key to user's account.

        Makes HTTP request to: POST https://api.github.com/user/keys
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
            "Content-Type": "application/json",
        }

        payload = {"title": title, "key": key}

        try:
            response = requests.post(
                f"{self.BASE_URL}/user/keys",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            try:
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00"),
                )
            except (ValueError, KeyError):
                created_at = datetime.utcnow()

            # GitHub API doesn't return fingerprint, so we generate a basic one
            fingerprint = f"SHA256:{data.get('id', 'unknown')}"

            return GitHubSSHKey(
                id=data["id"],
                title=data["title"],
                key=data["key"],
                fingerprint=fingerprint,
                created_at=created_at,
                read_only=data.get("read_only", False),
            )

        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 422:
                    try:
                        error_data = e.response.json()
                        if "errors" in error_data:
                            error_messages = [
                                error.get("message", "Unknown error")
                                for error in error_data["errors"]
                            ]
                            raise ValueError(
                                f"GitHub API error: {'; '.join(error_messages)}",
                            )
                    except ValueError:
                        pass
                raise ValueError(
                    f"Failed to add SSH key (HTTP {e.response.status_code}): {e}",
                ) from e
            raise ValueError(f"Failed to add SSH key: {e}") from e
        except (KeyError, ValueError) as e:
            if "GitHub API error:" in str(e):
                raise
            raise ValueError(f"Invalid response from GitHub API: {e}") from e

    def delete_ssh_key(self, access_token: str, key_id: int) -> None:
        """
        Delete SSH key from user's account.

        Makes HTTP request to: DELETE https://api.github.com/user/keys/{key_id}
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.delete(
                f"{self.BASE_URL}/user/keys/{key_id}",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 404:
                    raise ValueError(f"SSH key with ID {key_id} not found") from e
                raise ValueError(
                    f"Failed to delete SSH key (HTTP {e.response.status_code}): {e}",
                ) from e
            raise ValueError(f"Failed to delete SSH key: {e}") from e

    def get_repository(
        self,
        access_token: str,
        owner: str,
        repo: str,
    ) -> GitHubRepository:
        """
        Get repository information.

        Note: This is a placeholder implementation.
        In a real implementation, this would make an HTTP request to:
        GET https://api.github.com/repos/{owner}/{repo}
        """
        # Placeholder implementation - would make real API call
        return GitHubRepository(
            owner=owner,
            name=repo,
            full_name=f"{owner}/{repo}",
            clone_url=f"https://github.com/{owner}/{repo}.git",
            ssh_url=f"git@github.com:{owner}/{repo}.git",
            default_branch="main",
            private=False,
        )

    def list_user_repositories(self, access_token: str) -> List[GitHubRepository]:
        """
        List user's repositories.

        Note: This is a placeholder implementation.
        In a real implementation, this would make an HTTP request to:
        GET https://api.github.com/user/repos
        """
        # Placeholder implementation - would make real API call
        return [
            GitHubRepository(
                owner="placeholder_user",
                name="example-repo",
                full_name="placeholder_user/example-repo",
                clone_url="https://github.com/placeholder_user/example-repo.git",
                ssh_url="git@github.com:placeholder_user/example-repo.git",
                default_branch="main",
                private=False,
            ),
        ]

    def list_repository_webhooks(
        self,
        access_token: str,
        owner: str,
        repo: str,
    ) -> List[GitHubWatchWebhook]:
        """
        List webhooks for a repository.

        Makes HTTP request to: GET https://api.github.com/repos/{owner}/{repo}/hooks
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/hooks",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            webhooks = []

            for webhook_data in data:
                try:
                    created_at = datetime.fromisoformat(
                        webhook_data["created_at"].replace("Z", "+00:00"),
                    )
                    updated_at = datetime.fromisoformat(
                        webhook_data["updated_at"].replace("Z", "+00:00"),
                    )
                except (ValueError, KeyError):
                    created_at = updated_at = datetime.utcnow()

                webhooks.append(
                    GitHubWatchWebhook(
                        id=webhook_data["id"],
                        name=webhook_data.get("name", "web"),
                        active=webhook_data.get("active", True),
                        events=webhook_data.get("events", []),
                        config=webhook_data.get("config", {}),
                        url=webhook_data["url"],
                        test_url=webhook_data["test_url"],
                        ping_url=webhook_data["ping_url"],
                        deliveries_url=webhook_data["deliveries_url"],
                        created_at=created_at,
                        updated_at=updated_at,
                    ),
                )

            return webhooks

        except requests.RequestException as e:
            raise ValueError(f"Failed to list repository webhooks: {e}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from GitHub API: {e}") from e

    def create_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_request: CreateWatchGitHubWebhookRequest,
    ) -> GitHubWatchWebhook:
        """
        Create a webhook for a repository.

        Makes HTTP request to: POST https://api.github.com/repos/{owner}/{repo}/hooks
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
            "Content-Type": "application/json",
        }

        payload = webhook_request.to_dict()

        try:
            response = requests.post(
                f"{self.BASE_URL}/repos/{owner}/{repo}/hooks",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            try:
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00"),
                )
                updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00"),
                )
            except (ValueError, KeyError):
                created_at = updated_at = datetime.utcnow()

            return GitHubWatchWebhook(
                id=data["id"],
                name=data.get("name", "web"),
                active=data.get("active", True),
                events=data.get("events", []),
                config=data.get("config", {}),
                url=data["url"],
                test_url=data["test_url"],
                ping_url=data["ping_url"],
                deliveries_url=data["deliveries_url"],
                created_at=created_at,
                updated_at=updated_at,
            )

        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 422:
                    try:
                        error_data = e.response.json()
                        if "errors" in error_data:
                            error_messages = [
                                error.get("message", "Unknown error")
                                for error in error_data["errors"]
                            ]
                            raise ValueError(
                                f"GitHub API error: {'; '.join(error_messages)}",
                            )
                        if "message" in error_data:
                            raise ValueError(
                                f"GitHub API error: {error_data['message']}"
                            )
                    except (ValueError, KeyError):
                        pass

                    # Common 422 error scenarios
                    raise ValueError(
                        "Failed to create webhook (HTTP 422): Validation failed. "
                        "Common causes: Invalid webhook URL (must be publicly "
                        "accessible), duplicate webhook, or insufficient permissions"
                    ) from e

                raise ValueError(
                    f"Failed to create webhook (HTTP {e.response.status_code}): {e}",
                ) from e
            raise ValueError(f"Failed to create webhook: {e}") from e
        except (KeyError, ValueError) as e:
            if "GitHub API error:" in str(e):
                raise
            raise ValueError(f"Invalid response from GitHub API: {e}") from e

    def delete_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> None:
        """
        Delete a webhook from a repository.

        Makes HTTP request to: DELETE https://api.github.com/repos/{owner}/{repo}/hooks/{webhook_id}
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.delete(
                f"{self.BASE_URL}/repos/{owner}/{repo}/hooks/{webhook_id}",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 404:
                    raise ValueError(
                        f"Webhook with ID {webhook_id} not found in {owner}/{repo}",
                    ) from e
                raise ValueError(
                    f"Failed to delete webhook (HTTP {e.response.status_code}): {e}",
                ) from e
            raise ValueError(f"Failed to delete webhook: {e}") from e

    def get_repository_webhook(
        self,
        access_token: str,
        owner: str,
        repo: str,
        webhook_id: int,
    ) -> GitHubWatchWebhook:
        """
        Get a specific webhook from a repository.

        Makes HTTP request to: GET https://api.github.com/repos/{owner}/{repo}/hooks/{webhook_id}
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DooService-CLI/1.0",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/hooks/{webhook_id}",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            try:
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00"),
                )
                updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00"),
                )
            except (ValueError, KeyError):
                created_at = updated_at = datetime.utcnow()

            return GitHubWatchWebhook(
                id=data["id"],
                name=data.get("name", "web"),
                active=data.get("active", True),
                events=data.get("events", []),
                config=data.get("config", {}),
                url=data["url"],
                test_url=data["test_url"],
                ping_url=data["ping_url"],
                deliveries_url=data["deliveries_url"],
                created_at=created_at,
                updated_at=updated_at,
            )

        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 404:
                    raise ValueError(
                        f"Webhook with ID {webhook_id} not found in {owner}/{repo}",
                    ) from e
                raise ValueError(
                    f"Failed to get webhook (HTTP {e.response.status_code}): {e}",
                ) from e
            raise ValueError(f"Failed to get webhook: {e}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from GitHub API: {e}") from e
