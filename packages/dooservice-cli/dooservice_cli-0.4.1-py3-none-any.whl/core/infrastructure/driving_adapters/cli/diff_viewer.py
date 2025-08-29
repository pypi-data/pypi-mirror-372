from dataclasses import asdict, is_dataclass
from pprint import pformat
from typing import List

import click

from core.domain.entities.instance_config import InstanceConfig
from core.domain.services.diff_manager import Diff


class DiffViewer:
    """A service to render Diff objects in colorized format for CLI.

    Renders a list of Diff objects in a user-friendly, colorized format for
    the command line.
    """

    def render(self, diffs: List[Diff], indent: int = 0) -> str:
        """
        Renders the list of differences into a formatted string.

        Args:
            diffs: A list of Diff objects from the DiffManager.
            indent: The indentation level for nested structures.

        Returns:
            A string formatted for display in the console.
        """
        output = []

        for diff in diffs:
            if diff.type == "added" and isinstance(diff.new_value, InstanceConfig):
                instance_name = diff.path[-1] if diff.path else ""
                output.append(
                    click.style(
                        f"{' ' * indent}+ Added instance '{instance_name}':",
                        fg="green",
                    )
                    + self._format_value(diff.new_value, indent),
                )
                continue

            path_str = ".".join(map(str, diff.path))

            if diff.type == "added":
                output.append(
                    click.style(f"{' ' * indent}+ Added '{path_str}':", fg="green")
                    + f"{self._format_value(diff.new_value, indent)}",
                )
            elif diff.type == "removed":
                output.append(
                    click.style(f"{' ' * indent}- Removed '{path_str}'", fg="red"),
                )
            elif diff.type == "changed":
                output.append(
                    click.style(f"{' ' * indent}~ Changed '{path_str}':", fg="yellow")
                    + (
                        f" {self._format_value(diff.old_value, indent, inline=True)}"
                        f" -> {self._format_value(diff.new_value, indent, inline=True)}"
                    ),
                )

        return "\n".join(output)

    def _format_instance_config_summary(self, data: dict, indent: int = 0) -> str:
        """Creates a summary of an InstanceConfig."""
        output = []
        indent_str = " " * (indent + 4)

        version = data.get("odoo_version")
        if version:
            output.append(f"{indent_str}Version: {version}")

        data_dir = data.get("data_dir")
        if data_dir:
            output.append(f"{indent_str}Location: {data_dir}")

        deployment_type = data.get("deployment", {}).get("type")
        if deployment_type:
            output.append(f"{indent_str}Deployment: {deployment_type}")

        repositories = data.get("repositories")
        if repositories:
            output.append(f"{indent_str}Repositories:")
            for name, repo in repositories.items():
                url = repo.get("url")
                branch = repo.get("branch")
                repo_details = f"{url}"
                if branch:
                    repo_details += f" (branch: {branch})"
                output.append(f"{indent_str}  - {name}: {repo_details}")
        python_dependencies = data.get("python_dependencies")
        if python_dependencies:
            output.append(f"{indent_str}Python Dependencies:")
            output.extend(f"{indent_str}  - {item}" for item in python_dependencies)

        return "\n" + "\n".join(output)

    def _format_value(self, value: any, indent: int = 0, inline: bool = False) -> str:
        """Formats a value for display, handling different types."""
        if isinstance(value, InstanceConfig):
            return self._format_instance_config_summary(asdict(value), indent)

        if is_dataclass(value):
            value = asdict(value)

        if isinstance(value, (dict, list)):
            if inline:
                return pformat(value, indent=0, width=60, compact=True)

            formatted_val = pformat(value, indent=2, width=80)
            return "\n" + "\n".join(
                " " * (indent + 2) + line for line in formatted_val.splitlines()
            )

        if isinstance(value, str) and "\n" in value:
            if inline:
                return repr(value)
            return '"""\n' + value + '\n"""'

        return str(value)
