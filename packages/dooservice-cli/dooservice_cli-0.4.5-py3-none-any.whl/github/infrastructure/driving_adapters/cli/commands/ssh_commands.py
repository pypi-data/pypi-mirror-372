"""GitHub SSH key management commands."""

from pathlib import Path

import click

from github.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    github_config_context,
)


@click.group(name="key")
def key_group():
    """Manage GitHub SSH keys."""


@key_group.command(name="list")
@config_option()
@github_config_context
def key_list(config: str):
    """List SSH keys managed by dooservice."""
    try:
        config_context = click.get_current_context().obj
        ssh_keys_use_case = config_context.ssh_keys_use_case

        keys = ssh_keys_use_case.list_keys()

        if not keys:
            click.secho("No SSH keys managed by dooservice", fg="yellow")
            click.secho(
                "💡 Note: Only SSH keys added through dooservice are shown here "
                "for security.",
                fg="blue",
            )
            click.secho(
                "   Use 'uv run dooservice cli github key add' to add a new key.",
                fg="blue",
            )
            return

        click.secho("\n🔑 SSH Keys Managed by dooservice", bold=True)
        click.secho("-" * 60)

        for key in keys:
            click.secho(f"ID: {key.id}")
            click.secho(f"Title: {key.title}")
            click.secho(f"Fingerprint: {key.fingerprint}")
            click.secho(f"Created: {key.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            click.secho(f"Read-only: {'Yes' if key.read_only else 'No'}")
            click.secho(f"Key: {key.key[:50]}...")
            click.secho("-" * 60)

        click.secho(f"\nTotal: {len(keys)} managed SSH key(s)")
        click.secho(
            "💡 Note: Only SSH keys added through dooservice are shown for security.",
            fg="blue",
        )

    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
    except OSError as e:
        click.secho(f"Error listing SSH keys: {e}", fg="red")


@key_group.command(name="add")
@click.argument("title")
@click.argument("key_file", type=click.Path(exists=True, path_type=Path))
@config_option()
@github_config_context
def key_add(config: str, title: str, key_file: Path):
    """
    Add SSH key to your GitHub account.

    Args:
        config: Configuration file path
        title: Title/name for the SSH key
        key_file: Path to the public key file (e.g., ~/.ssh/id_rsa.pub)
    """
    try:
        # Read public key content
        with open(key_file) as f:
            key_content = f.read().strip()

        config_context = click.get_current_context().obj
        ssh_keys_use_case = config_context.ssh_keys_use_case

        # Add the key
        new_key = ssh_keys_use_case.add_key(title, key_content)

        click.secho("✓ SSH key added successfully!", fg="green", bold=True)
        click.secho(f"  ID: {new_key.id}")
        click.secho(f"  Title: {new_key.title}")
        click.secho(f"  Fingerprint: {new_key.fingerprint}")

    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
    except FileNotFoundError:
        click.secho(f"Error: Key file '{key_file}' not found", fg="red")
    except OSError as e:
        click.secho(f"Error adding SSH key: {e}", fg="red")


@key_group.command(name="remove")
@click.argument("key_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@config_option()
@github_config_context
def key_remove(config: str, key_id: int, yes: bool):
    """
    Remove SSH key from your GitHub account.

    Args:
        config: Configuration file path
        key_id: ID of the SSH key to remove
        yes: Skip confirmation prompt
    """
    try:
        config_context = click.get_current_context().obj
        ssh_keys_use_case = config_context.ssh_keys_use_case

        # Confirmation
        if not yes:
            click.secho(
                f"⚠️  This will permanently remove SSH key {key_id} from your "
                "GitHub account!",
                fg="yellow",
                bold=True,
            )
            if not click.confirm("Are you sure you want to continue?"):
                click.secho("Remove cancelled.", fg="yellow")
                return

        # Remove the key
        ssh_keys_use_case.remove_key(key_id)

        click.secho(f"✓ SSH key {key_id} removed successfully!", fg="green", bold=True)

    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
    except OSError as e:
        click.secho(f"Error removing SSH key: {e}", fg="red")


@key_group.command(name="import")
@click.argument("key_id", type=int)
@config_option()
@github_config_context
def key_import(config: str, key_id: int):
    """
    Import an existing GitHub SSH key to be managed by dooservice.

    This allows you to manage SSH keys that were created outside of dooservice.

    Args:
        config: Configuration file path
        key_id: ID of the existing SSH key in GitHub
    """
    try:
        config_context = click.get_current_context().obj
        ssh_keys_use_case = config_context.ssh_keys_use_case

        # We need to access the internal components to do this
        auth = ssh_keys_use_case.oauth_service.get_current_auth()
        if not auth:
            click.secho("Error: Not authenticated with GitHub", fg="red")
            return

        # Get all keys from GitHub (the raw API call)
        all_keys = ssh_keys_use_case.api_repository.list_ssh_keys(auth.access_token)

        # Find the specific key
        target_key = None
        for key in all_keys:
            if key.id == key_id:
                target_key = key
                break

        if not target_key:
            click.secho(
                f"Error: SSH key {key_id} not found in your GitHub account", fg="red"
            )
            return

        # Check if already managed
        if ssh_keys_use_case.managed_keys_repo.is_managed_key(key_id):
            click.secho(
                f"SSH key {key_id} is already managed by dooservice", fg="yellow"
            )
            return

        # Register as managed
        ssh_keys_use_case.managed_keys_repo.register_managed_key(target_key, "imported")

        click.secho("✓ SSH key imported successfully!", fg="green", bold=True)
        click.secho(f"  ID: {target_key.id}")
        click.secho(f"  Title: {target_key.title}")
        click.secho(f"  Fingerprint: {target_key.fingerprint}")
        click.secho("  The key is now managed by dooservice.")

    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
    except OSError as e:
        click.secho(f"Error importing SSH key: {e}", fg="red")
