"""Base class for time-scheduled daemons."""

from abc import abstractmethod
from datetime import datetime, time
import time as time_module
from typing import List, Optional

from .entities import DaemonConfig
from .generic_daemon_base import GenericDaemonBase


class ScheduledDaemonBase(GenericDaemonBase):
    """
    Base class for time-scheduled daemons that execute tasks at specific times.

    This daemon type is perfect for backup schedulers, maintenance tasks, etc.
    Instead of continuous polling, it calculates when the next execution should
    happen and sleeps until that time.
    """

    def __init__(self, daemon_name: str, config: Optional[DaemonConfig] = None):
        """Initialize scheduled daemon."""
        super().__init__(daemon_name, config)
        self._next_execution = None
        self._scheduled_tasks = []

    @abstractmethod
    def get_scheduled_times(self) -> List[time]:
        """
        Get list of times when tasks should be executed daily.

        Returns:
            List of time objects representing when to execute tasks
        """

    @abstractmethod
    def execute_scheduled_task(self) -> None:
        """
        Execute the scheduled task.

        This method is called at each scheduled time.
        """

    def _run_daemon_loop(self) -> None:
        """Main daemon loop for scheduled execution."""
        self.logger.info("Starting scheduled daemon loop")

        while self.running:
            try:
                # Calculate next execution time
                self._calculate_next_execution()

                if self._next_execution:
                    now = datetime.now()
                    sleep_seconds = (self._next_execution - now).total_seconds()

                    if sleep_seconds > 0:
                        self.logger.info(
                            "Next execution at %s (sleeping for %.1f seconds)",
                            self._next_execution.strftime("%Y-%m-%d %H:%M:%S"),
                            sleep_seconds,
                        )

                        # Sleep in chunks to allow for graceful shutdown
                        self._interruptible_sleep(sleep_seconds)

                    # Execute task if we're still running
                    if self.running and self._should_execute_now():
                        self.logger.info("Executing scheduled task")
                        try:
                            self.execute_scheduled_task()
                            self.logger.info("Scheduled task completed successfully")
                        except (OSError, RuntimeError) as e:
                            self.logger.error("Error executing scheduled task: %s", e)
                else:
                    # No scheduled times, sleep for a while
                    self._interruptible_sleep(3600)  # Sleep 1 hour

            except (OSError, RuntimeError) as e:
                self.logger.error("Error in scheduled daemon loop: %s", e)
                self._interruptible_sleep(60)  # Sleep 1 minute on error

    def _calculate_next_execution(self) -> None:
        """Calculate the next execution time based on scheduled times."""
        scheduled_times = self.get_scheduled_times()
        if not scheduled_times:
            self._next_execution = None
            return

        now = datetime.now()
        today = now.date()
        tomorrow = datetime.combine(today, time.min).replace(day=today.day + 1)

        # Find next execution time today
        next_today = None
        for scheduled_time in scheduled_times:
            execution_time = datetime.combine(today, scheduled_time)
            if execution_time > now:
                next_today = execution_time
                break

        if next_today:
            self._next_execution = next_today
        else:
            # No more executions today, use first time tomorrow
            first_time_tomorrow = datetime.combine(
                tomorrow.date(), min(scheduled_times)
            )
            self._next_execution = first_time_tomorrow

    def _should_execute_now(self) -> bool:
        """Check if we should execute now based on next execution time."""
        if not self._next_execution:
            return False

        now = datetime.now()
        # Execute if we're within 30 seconds of scheduled time
        time_diff = abs((self._next_execution - now).total_seconds())
        return time_diff <= 30

    def _interruptible_sleep(self, seconds: float) -> None:
        """Sleep for given seconds but wake up every second to check for shutdown."""
        end_time = time_module.time() + seconds
        while time_module.time() < end_time and self.running:
            time_module.sleep(min(1.0, end_time - time_module.time()))
