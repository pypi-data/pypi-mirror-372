"""Instance-focused repository management commands."""

import json
from pathlib import Path

import click

from repository.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    repository_config_context,
)


@click.command("list", help="List repositories configured for a specific instance")
@config_option()
@click.argument("instance_name", required=True)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@repository_config_context
def list_instance_repos(config: str, instance_name: str, format: str):
    """List repositories configured for a specific instance."""
    try:
        ctx = click.get_current_context()
        config_context = ctx.obj

        # Get instance configuration
        try:
            instance_config = config_context.resolved_instances[instance_name]
        except KeyError as e:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            ) from e

        if (
            not hasattr(instance_config, "repositories")
            or not instance_config.repositories
        ):
            click.echo(f"Instance '{instance_name}' has no repositories configured.")
            return

        repos = instance_config.repositories
        addons_path = instance_config.paths.get("addons", "N/A")

        if format == "json":
            repo_list = []
            for repo_name, repo_config in repos.items():
                repo_path = (
                    Path(addons_path) / repo_name
                    if addons_path != "N/A"
                    else Path("N/A")
                )

                repo_list.append(
                    {
                        "name": repo_name,
                        "url": repo_config.url,
                        "branch": repo_config.branch,
                        "path": str(repo_path),
                        "exists": repo_path.exists() if addons_path != "N/A" else False,
                        "is_git": (repo_path / ".git").exists()
                        if repo_path.exists()
                        else False,
                    }
                )

            click.echo(
                json.dumps(
                    {
                        "instance": instance_name,
                        "addons_path": addons_path,
                        "repositories": repo_list,
                    },
                    indent=2,
                )
            )

        else:
            click.echo(f"\n📋 Repositories for instance: {instance_name}")
            click.echo("=" * 60)
            click.echo(f"Addons path: {addons_path}")
            click.echo()

            for repo_name, repo_config in repos.items():
                repo_path = (
                    Path(addons_path) / repo_name if addons_path != "N/A" else None
                )

                status_icon = "❓"
                status_text = "unknown"

                if repo_path and repo_path.exists():
                    if (repo_path / ".git").exists():
                        status_icon = "✅"
                        status_text = "cloned"
                    else:
                        status_icon = "⚠️ "
                        status_text = "exists (not git)"
                else:
                    status_icon = "❌"
                    status_text = "not cloned"

                click.echo(f"📁 {repo_name}")
                click.echo(f"   URL: {repo_config.url}")
                click.echo(f"   Branch: {repo_config.branch}")
                click.echo(f"   Status: {status_icon} {status_text}")
                if repo_path:
                    click.echo(f"   Path: {repo_path}")
                click.echo()

            click.echo(f"Total: {len(repos)} repositories")

    except (ValueError, OSError, RuntimeError) as e:
        click.secho(f"Error listing instance repositories: {e}", fg="red")
        raise click.Abort() from e


@click.command(
    "status", help="Show detailed status of repositories for a specific instance"
)
@config_option()
@click.argument("instance_name", required=True)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@repository_config_context
def status_instance_repos(config: str, instance_name: str, format: str):
    """Show detailed status of repositories for a specific instance."""
    try:
        ctx = click.get_current_context()
        config_context = ctx.obj

        # Get instance configuration
        try:
            instance_config = config_context.resolved_instances[instance_name]
        except KeyError as e:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            ) from e

        if (
            not hasattr(instance_config, "repositories")
            or not instance_config.repositories
        ):
            click.echo(f"Instance '{instance_name}' has no repositories configured.")
            return

        repos = instance_config.repositories
        addons_path = instance_config.paths.get("addons")

        if not addons_path:
            raise click.ClickException(
                f"Instance '{instance_name}' has no addons path configured"
            )

        status_info = []

        for repo_name, repo_config in repos.items():
            repo_info = config_context.create_repository_info_for_instance(
                repo_name, instance_name
            )

            # Check repository status using use case
            is_sync = config_context.check_repository_status_use_case.execute(repo_info)
            current_commit = (
                config_context._repo_management_service.get_repository_commit(repo_info)
            )

            repo_status = {
                "name": repo_name,
                "url": repo_config.url,
                "branch": repo_config.branch,
                "path": str(repo_info.local_path),
                "exists": repo_info.local_path.exists(),
                "is_git": (repo_info.local_path / ".git").exists()
                if repo_info.local_path.exists()
                else False,
                "synchronized": is_sync,
                "current_commit": current_commit[:12] if current_commit else None,
            }
            status_info.append(repo_status)

        if format == "json":
            click.echo(
                json.dumps(
                    {
                        "instance": instance_name,
                        "addons_path": addons_path,
                        "status": status_info,
                    },
                    indent=2,
                )
            )

        else:
            click.echo(f"\n📊 Repository status for instance: {instance_name}")
            click.echo("=" * 60)
            click.echo(f"Addons path: {addons_path}")
            click.echo()

            for repo in status_info:
                # Status icons
                clone_icon = (
                    "✅" if repo["is_git"] else ("⚠️ " if repo["exists"] else "❌")
                )
                sync_icon = "✅" if repo["synchronized"] else "❌"

                click.echo(f"📁 {repo['name']}")
                click.echo(f"   URL: {repo['url']}")
                click.echo(f"   Branch: {repo['branch']}")
                click.echo(f"   Cloned: {clone_icon}")
                click.echo(f"   Synchronized: {sync_icon}")
                if repo["current_commit"]:
                    click.echo(f"   Current commit: {repo['current_commit']}")
                click.echo(f"   Path: {repo['path']}")
                click.echo()

            # Summary
            total = len(status_info)
            cloned = sum(1 for r in status_info if r["is_git"])
            synced = sum(1 for r in status_info if r["synchronized"])

            click.echo("📈 Summary:")
            click.echo(f"   Total repositories: {total}")
            click.echo(f"   Cloned: {cloned}/{total}")
            click.echo(f"   Synchronized: {synced}/{total}")

    except (ValueError, OSError, RuntimeError) as e:
        click.secho(f"Error getting repository status: {e}", fg="red")
        raise click.Abort() from e


@click.command("sync", help="Synchronize repositories for a specific instance")
@config_option()
@click.argument("instance_name", required=True)
@click.option("--repo-name", help="Sync only specific repository")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without actually doing it"
)
@repository_config_context
def sync_instance_repos(config: str, instance_name: str, repo_name: str, dry_run: bool):
    """Synchronize repositories for a specific instance."""
    try:
        ctx = click.get_current_context()
        config_context = ctx.obj

        # Get instance configuration
        try:
            instance_config = config_context.resolved_instances[instance_name]
        except KeyError as e:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            ) from e

        if (
            not hasattr(instance_config, "repositories")
            or not instance_config.repositories
        ):
            click.echo(f"Instance '{instance_name}' has no repositories configured.")
            return

        repos = instance_config.repositories
        addons_path = instance_config.paths.get("addons")

        if not addons_path:
            raise click.ClickException(
                f"Instance '{instance_name}' has no addons path configured"
            )

        # Filter repositories if specific repo requested
        repos_to_sync = (
            {repo_name: repos[repo_name]} if repo_name and repo_name in repos else repos
        )

        if repo_name and repo_name not in repos:
            raise click.ClickException(
                f"Repository '{repo_name}' not found in instance '{instance_name}'"
            )

        if dry_run:
            click.echo(
                f"🧪 Dry run - showing what would be synchronized for instance: "
                f"{instance_name}"
            )
        else:
            click.echo(f"🔄 Synchronizing repositories for instance: {instance_name}")

        click.echo(f"Addons path: {addons_path}")
        click.echo()

        results = []
        for sync_repo_name, repo_config in repos_to_sync.items():
            if dry_run:
                click.echo(f"📁 Would sync: {sync_repo_name}")
                click.echo(f"   URL: {repo_config.url}")
                click.echo(f"   Branch: {repo_config.branch}")
                continue

            # Use the repository use case to ensure repository
            # (now always pulls if exists)
            repo_info = config_context.create_repository_info_for_instance(
                sync_repo_name, instance_name
            )

            click.echo(f"📁 Syncing: {sync_repo_name}")
            result = config_context.ensure_repository_use_case.execute(repo_info)
            results.append((sync_repo_name, result))

            if result.success:
                operation = result.operation_performed
                if operation == "clone":
                    click.secho("   ✅ Cloned successfully", fg="green")
                elif operation == "pull":
                    click.secho("   ✅ Updated successfully", fg="green")
                    if result.old_commit and result.new_commit:
                        click.echo(
                            f"      {result.old_commit[:7]} → {result.new_commit[:7]}"
                        )
                elif operation == "no_change":
                    click.secho("   ✅ Already up to date", fg="green")
            else:
                click.secho(f"   ❌ Failed: {result.error_message}", fg="red")

            click.echo()

        if not dry_run:
            # Summary
            total = len(results)
            successful = sum(1 for _, result in results if result.success)

            click.echo("📈 Synchronization Summary:")
            click.echo(f"   Total repositories: {total}")
            click.echo(f"   Successful: {successful}/{total}")

            if successful == total:
                click.secho(
                    "🎉 All repositories synchronized successfully!", fg="green"
                )
            elif successful > 0:
                failed = total - successful
                click.secho(f"⚠️  {successful} succeeded, {failed} failed", fg="yellow")
            else:
                click.secho("❌ All synchronization attempts failed", fg="red")

    except (ValueError, OSError, RuntimeError) as e:
        click.secho(f"Error synchronizing repositories: {e}", fg="red")
        raise click.Abort() from e
