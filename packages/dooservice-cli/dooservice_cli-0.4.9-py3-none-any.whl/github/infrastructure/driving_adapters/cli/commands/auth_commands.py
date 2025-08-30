"""GitHub authentication commands."""

import click

from github.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    github_config_context,
)


@click.command(name="login")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@config_option()
@github_config_context
def github_login(config: str, no_browser: bool):
    """
    Authenticate with GitHub using OAuth.

    This command will open your browser and redirect you to GitHub
    to authorize the DooService CLI application.
    """
    try:
        config_context = click.get_current_context().obj

        # Check if GitHub is enabled
        if not config_context.is_github_enabled():
            click.secho("✗ GitHub integration is disabled in configuration", fg="red")
            click.secho(
                "Enable it in your dooservice.yml file under 'github.enabled'",
                fg="yellow",
            )
            return

        login_use_case = config_context.login_use_case

        # Check if already authenticated
        if login_use_case.is_authenticated():
            auth = login_use_case.get_current_auth()
            click.secho(f"✓ Already authenticated as {auth.user.login}", fg="green")
            return

        click.secho("🔐 Starting GitHub authentication...", bold=True)

        # Get callback URL
        callback_url = config_context.get_oauth_redirect_uri()

        click.secho("Starting temporary server to receive OAuth callback...", fg="blue")
        click.secho(f"Callback server listening on: {callback_url}", fg="blue")

        if no_browser:
            click.secho(
                "Manual OAuth flow (browser will not open automatically):",
                fg="yellow",
            )
        else:
            click.secho("Opening browser for authentication...", fg="green")

        click.secho("\n📝 OAuth Flow Instructions:", bold=True, fg="cyan")
        click.secho("1. Authorize the application in the browser", fg="cyan")
        click.secho(
            "2. If you see 'You are being redirected...' page, manually navigate to:",
            fg="cyan",
        )
        click.secho(f"   {callback_url}", fg="blue", bold=True)
        click.secho("3. The login will complete automatically", fg="cyan")
        click.secho("", fg="cyan")

        try:
            # Execute complete OAuth flow
            auth = login_use_case.execute(open_browser=not no_browser)

            click.secho(
                "✓ Successfully authenticated with GitHub!",
                fg="green",
                bold=True,
            )
            click.secho(f"  Welcome, {auth.user.login}!", fg="green")
            click.secho(f"  Scopes: {', '.join(auth.scopes)}", fg="blue")

        except ValueError as e:
            error_msg = str(e)
            if "port_" in error_msg and "_in_use" in error_msg:
                click.secho("✗ OAuth callback port is already in use", fg="red")
                click.secho(
                    "Please stop any service using that port and try again",
                    fg="yellow",
                )
            elif "timed out" in error_msg:
                click.secho("✗ OAuth flow timed out", fg="red")
                click.secho(
                    "You have 5 minutes to complete the authorization.",
                    fg="yellow",
                )
                click.secho(
                    f"If needed, manually navigate to: {callback_url}",
                    fg="blue",
                )
            elif "client_id" in error_msg or "client_secret" in error_msg:
                click.secho("✗ GitHub OAuth configuration incomplete", fg="red")
                click.secho("Please check your dooservice.yml file:", fg="yellow")
                click.secho("  - github.oauth.client_id", fg="yellow")
                click.secho("  - github.oauth.client_secret", fg="yellow")
            else:
                click.secho(f"✗ OAuth flow failed: {error_msg}", fg="red")
            return

    except (ValueError, OSError) as e:
        click.secho(f"Error during GitHub login: {e}", fg="red")


@click.command(name="logout")
@config_option()
@github_config_context
def github_logout(config: str):
    """Logout from GitHub and clear stored credentials."""
    try:
        config_context = click.get_current_context().obj
        login_use_case = config_context.login_use_case

        if not login_use_case.is_authenticated():
            click.secho("Not currently authenticated with GitHub", fg="yellow")
            return

        login_use_case.logout()
        click.secho("✓ Successfully logged out from GitHub", fg="green")

    except (ValueError, OSError) as e:
        click.secho(f"Error during GitHub logout: {e}", fg="red")


@click.command(name="status")
@config_option()
@github_config_context
def github_status(config: str):
    """Show GitHub authentication status."""
    try:
        config_context = click.get_current_context().obj
        login_use_case = config_context.login_use_case

        if login_use_case.is_authenticated():
            auth = login_use_case.get_current_auth()
            click.secho("✓ Authenticated with GitHub", fg="green", bold=True)
            click.secho(f"  User: {auth.user.login}")
            click.secho(f"  Name: {auth.user.name or 'N/A'}")
            click.secho(f"  Email: {auth.user.email or 'N/A'}")
            click.secho(f"  Scopes: {', '.join(auth.scopes)}")

            if auth.expires_at:
                click.secho(
                    f"  Expires: {auth.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                )
        else:
            click.secho("✗ Not authenticated with GitHub", fg="red", bold=True)
            click.secho(
                "Run 'uv run dooservice cli github login' to authenticate",
                fg="yellow",
            )

    except (ValueError, OSError) as e:
        click.secho(f"Error checking GitHub status: {e}", fg="red")
