from contextlib import contextmanager

import click


class ProgressBar:
    """A universal progress bar class for all types of operations in the application."""

    @staticmethod
    @contextmanager
    def create(
        iterable_or_length,
        label: str = "",
        show_percent: bool = True,
        show_pos: bool = False,
        width: int = 30,
        indent: str = "  ",
    ):
        """
        Creates a progress bar with consistent styling and alignment.

        Args:
            iterable_or_length: Either an iterable to iterate over, or an integer length
            label: Label to display before the progress bar
            show_percent: Whether to show percentage
            show_pos: Whether to show position
            width: Width of the progress bar
            indent: Indentation string
        """
        # Ensure proper alignment by padding the label
        formatted_label = f"{indent}{label:<18}" if label else indent

        if hasattr(iterable_or_length, "__iter__"):
            # It's an iterable
            with click.progressbar(
                iterable_or_length,
                label=formatted_label,
                show_percent=show_percent,
                show_pos=show_pos,
                bar_template="%(label)s[%(bar)s] %(info)s",
                width=width,
            ) as progress:
                yield progress
        else:
            # It's a length
            with click.progressbar(
                length=iterable_or_length,
                label=formatted_label,
                show_percent=show_percent,
                show_pos=show_pos,
                bar_template="%(label)s[%(bar)s] %(info)s",
                width=width,
            ) as progress:
                yield progress
