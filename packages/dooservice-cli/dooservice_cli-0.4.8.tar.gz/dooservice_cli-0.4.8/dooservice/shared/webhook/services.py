"""Domain services for webhook processing."""

import logging
from typing import List

from .entities import (
    ActionType,
    WebhookAction,
    WebhookConfig,
    WebhookPayload,
    WebhookProcessingResult,
)
from .repositories import (
    InstanceRepository,
    WebhookActionRepository,
    WebhookConfigRepository,
)


class WebhookProcessingService:
    """Domain service for processing webhook events."""

    def __init__(
        self,
        config_repo: WebhookConfigRepository,
        action_repo: WebhookActionRepository,
        instance_repo: InstanceRepository,
    ):
        self.config_repo = config_repo
        self.action_repo = action_repo
        self.instance_repo = instance_repo
        self.logger = logging.getLogger(__name__)

    def process_webhook_event(self, payload: WebhookPayload) -> WebhookProcessingResult:
        """
        Process a webhook event and create appropriate actions.

        Args:
            payload: Parsed webhook payload

        Returns:
            WebhookProcessingResult with processing details
        """
        start_time = __import__("time").time()

        try:
            # Find matching repository watches
            watches = self.config_repo.get_watches_for_repository(
                payload.repository_url
            )

            if not watches:
                self.logger.info(
                    "No watches configured for repository: %s", payload.repository_url
                )
                return WebhookProcessingResult(
                    success=True,
                    processed_actions=[],
                    execution_time_ms=((__import__("time").time() - start_time) * 1000),
                )

            # Filter watches by branch and enabled status
            matching_watches = [
                watch
                for watch in watches
                if watch.enabled and self._branch_matches(watch.branch, payload.branch)
            ]

            if not matching_watches:
                self.logger.info(
                    "No enabled watches match branch %s for repository: %s",
                    payload.branch,
                    payload.repository_url,
                )
                return WebhookProcessingResult(
                    success=True,
                    processed_actions=[],
                    execution_time_ms=((__import__("time").time() - start_time) * 1000),
                )

            # Create actions for matching watches
            actions = []
            for watch in matching_watches:
                # Verify instance exists
                if not self.instance_repo.instance_exists(watch.instance_name):
                    self.logger.warning(
                        "Instance %s not found, skipping webhook action",
                        watch.instance_name,
                    )
                    continue

                # Create actions for each configured action type
                for action_type in watch.actions:
                    action = WebhookAction(
                        instance_name=watch.instance_name,
                        action_type=action_type,
                        repository_url=payload.repository_url,
                        branch=payload.branch,
                        triggered_by=payload,
                    )

                    # Save action for execution
                    self.action_repo.save_action(action)
                    actions.append(action)

                    self.logger.info(
                        "Created webhook action: %s for instance %s (repo: %s, "
                        "branch: %s)",
                        action_type.value,
                        watch.instance_name,
                        payload.repository_url,
                        payload.branch,
                    )

            return WebhookProcessingResult(
                success=True,
                processed_actions=actions,
                execution_time_ms=((__import__("time").time() - start_time) * 1000),
            )

        except (ValueError, KeyError, AttributeError, RuntimeError) as e:
            self.logger.error("Error processing webhook event: %s", e)
            return WebhookProcessingResult(
                success=False,
                processed_actions=[],
                error=str(e),
                execution_time_ms=((__import__("time").time() - start_time) * 1000),
            )

    def _branch_matches(self, watch_branch: str, payload_branch: str) -> bool:
        """
        Check if webhook branch matches watch configuration.

        Args:
            watch_branch: Branch pattern from watch config
            payload_branch: Branch from webhook payload

        Returns:
            True if branches match
        """
        # Remove refs/heads/ prefix if present
        payload_branch = payload_branch.replace("refs/heads/", "")

        # Simple wildcard matching
        if watch_branch == "*":
            return True

        # Exact match
        if watch_branch == payload_branch:
            return True

        # Pattern matching (could be extended with regex)
        if "*" in watch_branch:
            import fnmatch

            return fnmatch.fnmatch(payload_branch, watch_branch)

        return False


class WebhookActionExecutorService:
    """Domain service for executing webhook actions."""

    def __init__(
        self, action_repo: WebhookActionRepository, instance_repo: InstanceRepository
    ):
        self.action_repo = action_repo
        self.instance_repo = instance_repo
        self.logger = logging.getLogger(__name__)

    def execute_pending_actions(self) -> List[WebhookAction]:
        """
        Execute all pending webhook actions.

        Returns:
            List of executed actions
        """
        pending_actions = self.action_repo.get_pending_actions()
        executed_actions = []

        for action in pending_actions:
            try:
                self._execute_action(action)
                self.action_repo.mark_action_completed(action)
                executed_actions.append(action)

                self.logger.info(
                    "Successfully executed webhook action: %s for instance %s",
                    action.action_type.value,
                    action.instance_name,
                )

            except (ValueError, RuntimeError, NotImplementedError) as e:
                error_msg = f"Failed to execute webhook action: {e}"
                self.logger.error(error_msg)
                self.action_repo.mark_action_failed(action, error_msg)

        return executed_actions

    def _execute_action(self, action: WebhookAction) -> None:
        """
        Execute a single webhook action.

        Args:
            action: WebhookAction to execute
        """
        if action.action_type == ActionType.PULL:
            self.instance_repo.pull_repository(
                action.instance_name, action.repository_url
            )

        elif action.action_type == ActionType.RESTART:
            self.instance_repo.restart_instance(action.instance_name)

        elif action.action_type == ActionType.PULL_RESTART:
            # Execute pull first, then restart
            self.instance_repo.pull_repository(
                action.instance_name, action.repository_url
            )
            self.instance_repo.restart_instance(action.instance_name)

        elif action.action_type in [ActionType.BUILD, ActionType.DEPLOY]:
            # These could be implemented later for more advanced workflows
            raise NotImplementedError(
                f"Action type {action.action_type.value} not implemented yet"
            )

        else:
            raise ValueError(f"Unknown action type: {action.action_type}")


class WebhookRegistrationService:
    """Domain service for managing webhook registrations."""

    def __init__(self, config_repo: WebhookConfigRepository):
        self.config_repo = config_repo
        self.logger = logging.getLogger(__name__)

    def get_webhook_endpoint_url(self, base_url: str, provider: str) -> str:
        """
        Generate webhook endpoint URL for a provider.

        Args:
            base_url: Base server URL
            provider: Provider name (github, gitlab, etc.)

        Returns:
            Complete webhook endpoint URL
        """
        return f"{base_url.rstrip('/')}/webhooks/{provider.lower()}"

    def validate_webhook_config(self, config: WebhookConfig) -> List[str]:
        """
        Validate webhook configuration.

        Args:
            config: WebhookConfig to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate server config
        if config.server.port < 1 or config.server.port > 65535:
            errors.append("Server port must be between 1 and 65535")

        # Validate providers
        provider_names = [p.provider.value for p in config.providers]
        if len(provider_names) != len(set(provider_names)):
            errors.append("Duplicate providers detected")

        # Validate repositories
        for repo_config in config.repositories:
            if not repo_config.repository_url:
                errors.append("Repository URL cannot be empty")

            if not repo_config.instance_name:
                errors.append("Instance name cannot be empty")

            if not repo_config.actions:
                errors.append(
                    f"No actions configured for repository {repo_config.repository_url}"
                )

        return errors
