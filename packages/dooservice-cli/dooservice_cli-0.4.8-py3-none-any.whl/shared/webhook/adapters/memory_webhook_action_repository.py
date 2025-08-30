"""In-memory webhook action repository."""

from datetime import datetime
import threading
from typing import List

from ..entities import WebhookAction
from ..repositories import WebhookActionRepository


class MemoryWebhookActionRepository(WebhookActionRepository):
    """In-memory implementation of webhook action repository."""

    def __init__(self):
        self._actions = []
        self._completed_actions = []
        self._failed_actions = []
        self._lock = threading.Lock()

    def save_action(self, action: WebhookAction) -> None:
        """Save a webhook action for execution."""
        with self._lock:
            self._actions.append(action)

    def get_pending_actions(self) -> List[WebhookAction]:
        """Get all pending webhook actions."""
        with self._lock:
            # Return copy to avoid concurrent modification
            return self._actions.copy()

    def mark_action_completed(self, action: WebhookAction) -> None:
        """Mark a webhook action as completed."""
        with self._lock:
            if action in self._actions:
                self._actions.remove(action)
                self._completed_actions.append((action, datetime.utcnow(), None))

    def mark_action_failed(self, action: WebhookAction, error: str) -> None:
        """Mark a webhook action as failed with error."""
        with self._lock:
            if action in self._actions:
                self._actions.remove(action)
                self._failed_actions.append((action, datetime.utcnow(), error))

    def get_completed_actions(self) -> List[tuple[WebhookAction, datetime, None]]:
        """Get completed actions (for monitoring/debugging)."""
        with self._lock:
            return self._completed_actions.copy()

    def get_failed_actions(self) -> List[tuple[WebhookAction, datetime, str]]:
        """Get failed actions (for monitoring/debugging)."""
        with self._lock:
            return self._failed_actions.copy()

    def clear_history(self) -> None:
        """Clear completed and failed action history."""
        with self._lock:
            self._completed_actions.clear()
            self._failed_actions.clear()
