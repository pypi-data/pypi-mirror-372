"""GitHub repository watch commands with webhook management."""

import click

from github.application.use_cases.list_repository_watch_github import (
    ListRepositoryWatchGitHubUseCase,
)
from github.application.use_cases.sync_repository_watch_github import (
    SyncRepositoryWatchGitHubUseCase,
)
from github.domain.services.watch_github_management_service import (
    WatchGitHubManagementService,
)
from github.domain.services.watch_github_webhook_sync_service import (
    WatchGitHubWebhookSyncService,
)
from github.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    github_config_context,
)


def _build_webhook_url(webhook_config: dict) -> str:
    """Build webhook URL from configuration."""
    host = webhook_config.get("host", "localhost")
    port = webhook_config.get("port", webhook_config.get("default_port", 7070))

    # Simple IP detection for 0.0.0.0
    if host == "0.0.0.0":  # noqa: S104
        import subprocess

        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                host = result.stdout.strip().split()[0]
        except (ValueError, OSError, AttributeError):
            host = "localhost"

    return f"http://{host}:{port}/webhooks/github"


@click.group(name="watch")
def watch_group():
    """Manage repository watchers for automatic sync."""


@watch_group.command(name="list")
@config_option()
@github_config_context
def watch_list(config: str):
    """List all repository watchers with webhook status."""
    try:
        config_context = click.get_current_context().obj

        # Check if GitHub is enabled
        if not config_context.is_github_enabled():
            click.echo("❌ GitHub integration is disabled in configuration")
            return

        # Check authentication
        if not config_context.login_use_case.is_authenticated():
            click.echo("❌ Not authenticated with GitHub")
            click.echo("💡 Run 'dooservice cli github login' to authenticate")
            return

        # Initialize services
        watch_service = WatchGitHubManagementService(config_context._config_service)
        webhook_sync_service = WatchGitHubWebhookSyncService(config_context._api_repo)

        # Get webhook server URL from configuration
        webhook_config = config_context.github_config_service.get_webhook_config()
        webhook_url = _build_webhook_url(webhook_config)

        # Initialize and execute use case
        use_case = ListRepositoryWatchGitHubUseCase(
            watch_service,
            webhook_sync_service,
            config_context._auth_repo,
            webhook_url,
        )

        watches_with_status = use_case.execute()

        if not watches_with_status:
            click.echo("❌ No repository watchers configured")
            click.echo(
                "💡 Configure auto-watch in your repositories or use "
                "'dooservice github watch add'"
            )
            return

        # Display results
        click.echo(f"\n👁️  Repository Watchers ({len(watches_with_status)} configured)")
        click.echo("━" * 80)

        healthy_count = 0
        error_count = 0

        for watch_with_status in watches_with_status:
            watch = watch_with_status.watch
            status = watch_with_status.status

            # Repository info
            click.echo(f"📁 {watch.repository_name}")
            click.echo(f"   🌐 {watch.repository_url}")
            click.echo(f"   🏠 Instance: {watch.instance_name}")

            # Actions
            actions_str = ", ".join([action.value for action in watch.actions])
            click.echo(f"   ⚡ Actions: {actions_str}")

            # Webhook status
            if status.error:
                click.echo(f"   🔒 Webhook: ❌ Error - {status.error}")
                error_count += 1
            elif status.exists:
                if status.active:
                    click.echo(f"   🔒 Webhook: ✅ Active (ID: {status.webhook_id})")
                    if status.last_delivery:
                        activity_str = status.last_delivery.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        click.echo(f"   📅 Last activity: {activity_str}")
                    healthy_count += 1
                else:
                    click.echo(f"   🔒 Webhook: ⚠️  Inactive (ID: {status.webhook_id})")
                    error_count += 1
            else:
                click.echo("   🔒 Webhook: ❌ Missing")
                error_count += 1

            # Additional info
            click.echo(f"   🔑 Secret: {'Yes' if status.secret_configured else 'No'}")
            watch_type_icon = "🤖" if watch.watch_type.value == "auto" else "👤"
            click.echo(f"   {watch_type_icon} Type: {watch.watch_type.value.title()}")
            click.echo(f"   🌿 Branch: {watch.branch}")

            click.echo("   " + "─" * 76)

        # Summary
        click.echo("\n📊 Summary:")
        click.echo(f"   Total watches: {len(watches_with_status)}")
        click.echo(f"   ✅ Healthy webhooks: {healthy_count}")
        if error_count > 0:
            click.echo(f"   ❌ Issues found: {error_count}")
            click.echo(
                "\n💡 Run 'dooservice cli github watch sync' to fix missing webhooks"
            )

    except (ValueError, OSError) as e:
        click.echo(f"❌ Error listing watchers: {e}")
        raise click.Abort() from e


@watch_group.command(name="sync")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option("--force", is_flag=True, help="Force recreation of existing webhooks")
@click.option("--webhook-secret", help="Webhook secret for verification")
@config_option()
@github_config_context
def watch_sync(config: str, dry_run: bool, force: bool, webhook_secret: str):
    """Synchronize GitHub webhooks based on configured watchers."""
    try:
        config_context = click.get_current_context().obj

        # Check if GitHub is enabled
        if not config_context.is_github_enabled():
            click.echo("❌ GitHub integration is disabled in configuration")
            return

        # Check authentication
        if not config_context.login_use_case.is_authenticated():
            click.echo("❌ Not authenticated with GitHub")
            click.echo("💡 Run 'dooservice cli github login' to authenticate")
            return

        click.echo("🔄 Synchronizing GitHub webhooks...")
        if dry_run:
            click.echo("🔍 DRY RUN - No changes will be made")

        # Initialize services
        watch_service = WatchGitHubManagementService(config_context._config_service)
        webhook_sync_service = WatchGitHubWebhookSyncService(config_context._api_repo)

        # Get webhook server URL from configuration
        webhook_config = config_context.github_config_service.get_webhook_config()
        webhook_url = _build_webhook_url(webhook_config)

        click.echo(f"📡 Webhook URL: {webhook_url}")

        # Use default webhook secret if not provided
        if not webhook_secret:
            webhook_secret = webhook_config.get("default_secret")

        # Initialize and execute use case
        use_case = SyncRepositoryWatchGitHubUseCase(
            watch_service,
            webhook_sync_service,
            config_context._auth_repo,
            webhook_url,
        )

        report = use_case.execute(
            dry_run=dry_run, force=force, webhook_secret=webhook_secret
        )

        # Display results
        if report.has_changes:
            click.echo("\n🔨 Changes:")

            for watch in report.created:
                action = "Would create" if dry_run else "Created"
                click.echo(
                    f"   ✅ {action} webhook for {watch.repository_name} -> "
                    f"{watch.instance_name}"
                )

            for watch in report.updated:
                action = "Would update" if dry_run else "Updated"
                click.echo(
                    f"   🔄 {action} webhook for {watch.repository_name} -> "
                    f"{watch.instance_name}"
                )

            for repo_name in report.deleted:
                action = "Would delete" if dry_run else "Deleted"
                click.echo(f"   🗑️  {action} webhook from {repo_name}")

        if report.errors:
            click.echo("\n❌ Errors:")
            for repo_name, error in report.errors:
                click.echo(f"   • {repo_name}: {error}")

        # Summary
        if not dry_run:
            if report.has_changes:
                click.echo("\n✅ Synchronization complete!")
                created_count = len(report.created)
                updated_count = len(report.updated)
                deleted_count = len(report.deleted)
                click.echo(
                    f"   📊 {created_count} created, {updated_count} updated, "
                    f"{deleted_count} deleted"
                )
            else:
                click.echo("\n✅ All webhooks are already synchronized!")
        elif report.has_changes:
            click.echo("\n📋 Summary of planned changes:")
            to_create = len(report.created)
            to_update = len(report.updated)
            to_delete = len(report.deleted)
            click.echo(
                f"   📊 {to_create} to create, {to_update} to update, "
                f"{to_delete} to delete"
            )
            click.echo("\n💡 Run without --dry-run to apply these changes")
        else:
            click.echo("\n✅ No changes needed - all webhooks are synchronized!")

        if report.errors:
            raise click.Abort()

    except (ValueError, OSError) as e:
        click.echo(f"❌ Error syncing webhooks: {e}")
        raise click.Abort() from e


@watch_group.command(name="add")
@click.argument("repository")
@click.argument("instance")
@click.option(
    "--action",
    "-a",
    type=click.Choice(["pull", "restart", "pull+restart", "backup", "snapshot"]),
    default="pull+restart",
    help="Action to trigger on push",
)
@click.option("--branch", "-b", default="main", help="Branch to watch")
@click.option("--webhook-secret", help="Webhook secret for verification")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@config_option()
@github_config_context
def watch_add(
    config: str,
    repository: str,
    instance: str,
    action: str,
    branch: str,
    webhook_secret: str,
    dry_run: bool,
):
    """Add a repository watcher and create GitHub webhook."""
    try:
        config_context = click.get_current_context().obj

        # Check if GitHub is enabled
        if not config_context.is_github_enabled():
            click.echo("❌ GitHub integration is disabled in configuration")
            return

        # Check authentication
        if not config_context.login_use_case.is_authenticated():
            click.echo("❌ Not authenticated with GitHub")
            click.echo("💡 Run 'dooservice cli github login' to authenticate")
            return

        click.echo("⚠️  Manual watch addition is not yet implemented")
        click.echo("📝 This feature will allow you to:")
        click.echo(f"   • Add {repository} -> {instance} watch")
        click.echo(f"   • Configure {action} action")
        click.echo(f"   • Monitor {branch} branch")
        click.echo(
            f"   • {'Create' if not dry_run else 'Plan to create'} GitHub webhook"
        )
        click.echo("\n💡 For now, use auto-watch configuration in your dooservice.yml")
        click.echo(
            "   Or run 'dooservice cli github watch sync' to create webhooks "
            "for existing config"
        )

    except (ValueError, OSError) as e:
        click.echo(f"❌ Error adding watcher: {e}")
        raise click.Abort() from e


@watch_group.command(name="remove")
@click.argument("repository")
@click.argument("instance")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--keep-webhook",
    is_flag=True,
    help="Keep GitHub webhook (only remove local config)",
)
@config_option()
@github_config_context
def watch_remove(
    config: str, repository: str, instance: str, yes: bool, keep_webhook: bool
):
    """Remove a repository watcher and optionally delete GitHub webhook."""
    try:
        config_context = click.get_current_context().obj

        # Check if GitHub is enabled
        if not config_context.is_github_enabled():
            click.echo("❌ GitHub integration is disabled in configuration")
            return

        if not yes:
            webhook_action = "keep" if keep_webhook else "delete"
            click.echo(
                f"⚠️  This will remove the watcher for {repository} -> {instance}"
            )
            click.echo(f"   GitHub webhook will be {webhook_action}d")
            if not click.confirm("Are you sure you want to continue?"):
                click.echo("❌ Remove cancelled")
                return

        click.echo("⚠️  Manual watch removal is not yet implemented")
        click.echo("📝 This feature will allow you to:")
        click.echo(f"   • Remove {repository} -> {instance} watch")
        click.echo(f"   • {'Keep' if keep_webhook else 'Delete'} GitHub webhook")
        click.echo("\n💡 For now, modify your dooservice.yml configuration")
        click.echo("   Then run 'dooservice cli github watch sync' to update webhooks")

    except (ValueError, OSError) as e:
        click.echo(f"❌ Error removing watcher: {e}")
        raise click.Abort() from e
