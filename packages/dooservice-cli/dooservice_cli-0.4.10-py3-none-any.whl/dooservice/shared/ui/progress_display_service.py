"""
Progress Display Service.

Infrastructure service for displaying progress bars in CLI applications.
This is UI-related infrastructure code, not business logic.
"""

from contextlib import contextmanager
from typing import Any, Generator, Iterator, Optional, Union

import click


class ProgressDisplayService:
    """
    Infrastructure service responsible for displaying progress indicators in CLI.

    This service abstracts the UI framework (Click) from the rest of the application,
    allowing for consistent progress display across all operations.
    """

    def __init__(
        self,
        default_width: int = 30,
        default_template: str = "%(label)s[%(bar)s] %(info)s",
        default_indent: str = "  ",
    ) -> None:
        """
        Initialize the progress display service.

        Args:
            default_width: Default width for progress bars
            default_template: Default template for progress bar display
            default_indent: Default indentation for labels
        """
        self._default_width = default_width
        self._default_template = default_template
        self._default_indent = default_indent

    @contextmanager
    def create_progress_bar(
        self,
        iterable_or_length: Union[Iterator[Any], int],
        label: str = "",
        show_percent: bool = True,
        show_pos: bool = False,
        width: Optional[int] = None,
        indent: Optional[str] = None,
    ) -> Generator[Any, None, None]:
        """
        Creates a progress bar with consistent styling and alignment.

        Args:
            iterable_or_length: Either an iterable to iterate over, or an integer length
            label: Label to display before the progress bar
            show_percent: Whether to show percentage
            show_pos: Whether to show position
            width: Width of the progress bar (uses default if None)
            indent: Indentation string (uses default if None)

        Yields:
            Progress bar context manager
        """
        # Use defaults if not provided
        actual_width = width or self._default_width
        actual_indent = indent or self._default_indent

        # Format label with consistent alignment
        formatted_label = self._format_label(label, actual_indent)

        # Create appropriate progress bar based on input type
        if hasattr(iterable_or_length, "__iter__"):
            progress_context = self._create_iterable_progress_bar(
                iterable_or_length,
                formatted_label,
                show_percent,
                show_pos,
                actual_width,
            )
        else:
            progress_context = self._create_length_progress_bar(
                iterable_or_length,
                formatted_label,
                show_percent,
                show_pos,
                actual_width,
            )

        with progress_context as progress:
            yield progress

    def _format_label(self, label: str, indent: str) -> str:
        """
        Format label with consistent alignment.

        Args:
            label: Raw label text
            indent: Indentation string

        Returns:
            Formatted label with proper alignment
        """
        if not label:
            return indent

        # Consistent label width for alignment
        label_width = 18
        return f"{indent}{label:<{label_width}}"

    def _create_iterable_progress_bar(
        self,
        iterable: Iterator[Any],
        formatted_label: str,
        show_percent: bool,
        show_pos: bool,
        width: int,
    ) -> click.progressbar:
        """
        Create progress bar for iterables.

        Args:
            iterable: Iterable to track
            formatted_label: Pre-formatted label
            show_percent: Whether to show percentage
            show_pos: Whether to show position
            width: Progress bar width

        Returns:
            Click progress bar context manager
        """
        return click.progressbar(
            iterable,
            label=formatted_label,
            show_percent=show_percent,
            show_pos=show_pos,
            bar_template=self._default_template,
            width=width,
        )

    def _create_length_progress_bar(
        self,
        length: int,
        formatted_label: str,
        show_percent: bool,
        show_pos: bool,
        width: int,
    ) -> click.progressbar:
        """
        Create progress bar for known lengths.

        Args:
            length: Total length/count
            formatted_label: Pre-formatted label
            show_percent: Whether to show percentage
            show_pos: Whether to show position
            width: Progress bar width

        Returns:
            Click progress bar context manager
        """
        return click.progressbar(
            length=length,
            label=formatted_label,
            show_percent=show_percent,
            show_pos=show_pos,
            bar_template=self._default_template,
            width=width,
        )


# Factory function for dependency injection
def create_progress_display_service() -> ProgressDisplayService:
    """
    Factory function to create a ProgressDisplayService instance.

    Returns:
        New ProgressDisplayService instance with default configuration
    """
    return ProgressDisplayService()


# Backwards compatibility class with simplified interface
class ProgressBar:
    """
    Simplified interface for backwards compatibility.

    Delegates to ProgressDisplayService.
    """

    _service = create_progress_display_service()

    @staticmethod
    @contextmanager
    def create(
        iterable_or_length: Union[Iterator[Any], int],
        label: str = "",
        show_percent: bool = True,
        show_pos: bool = False,
        width: int = 30,
        indent: str = "  ",
    ) -> Generator[Any, None, None]:
        """
        Creates a progress bar with consistent styling and alignment.

        Args:
            iterable_or_length: Either an iterable to iterate over, or an integer length
            label: Label to display before the progress bar
            show_percent: Whether to show percentage
            show_pos: Whether to show position
            width: Width of the progress bar
            indent: Indentation string

        Yields:
            Progress bar context manager
        """
        with ProgressBar._service.create_progress_bar(
            iterable_or_length=iterable_or_length,
            label=label,
            show_percent=show_percent,
            show_pos=show_pos,
            width=width,
            indent=indent,
        ) as progress:
            yield progress
