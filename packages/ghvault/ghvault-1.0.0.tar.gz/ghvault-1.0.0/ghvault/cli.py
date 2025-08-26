# ghvault/cli.py
import json
import os
from pathlib import Path

import typer

from .api import (
    create_or_update_secret,
    delete_environment_secret,
    delete_multiple_secrets,
    list_environment_secrets,
    set_github_token,
    validate_github_token,
    write_env_to_github,
)

app = typer.Typer(help="ghvault - Manage GitHub environment secrets securely.")


def ensure_github_token():
    """
    Ensure GitHub token is available, prompt user if not found in environment.
    Sets the token in environment variables once validated.
    """
    # Check if token is already available in environment
    if os.getenv("GH_TOKEN"):
        return

    # Prompt user for token
    typer.echo("🔑 GitHub token not found in environment variables.")
    typer.echo("You can set it permanently with: export GH_TOKEN=your_token_here")
    typer.echo("Or provide it now (will be set for this session):")

    token = typer.prompt("Enter your GitHub token", hide_input=True)

    if not token.strip():
        typer.echo("❌ Empty token provided", err=True)
        raise typer.Exit(code=1)

    # Validate the token
    typer.echo("🔍 Validating GitHub token...")
    if not validate_github_token(token):
        typer.echo("❌ Invalid GitHub token. Please check your token and try again.", err=True)
        raise typer.Exit(code=1)

    # Set the token in environment variables for this session
    os.environ["GH_TOKEN"] = token
    set_github_token(token)
    typer.echo("✅ GitHub token validated and set for this session")
    typer.echo("💡 The token will be available for all subsequent commands in this session")


@app.command()
def set(
    environment: str = typer.Argument(..., help="The GitHub environment (e.g., staging, production)."),
    name: str = typer.Argument(..., help="The name of the secret."),
    value: str = typer.Argument(None, help="The secret value (optional if --file is used)."),
    file: Path = typer.Option(None, "--file", "-f", help="Path to a file containing the secret value."),
    owner: str = typer.Option(None, "--owner", help="GitHub repo owner (defaults to GH_OWNER env var)."),
    repo: str = typer.Option(None, "--repo", help="GitHub repo name (defaults to GH_REPO env var)."),
):
    """
    Create or update a GitHub environment secret.
    """
    # Ensure GitHub token is available
    ensure_github_token()

    repo_owner = owner or os.getenv("GH_OWNER")
    repo_name = repo or os.getenv("GH_REPO")

    if not repo_owner or not repo_name:
        typer.echo("❌ Missing repo info. Set GH_OWNER/GH_REPO env vars or use --owner/--repo")
        raise typer.Exit(code=1)

    # Load secret value
    if file:
        with open(file, "r", encoding="utf-8") as f:
            raw_value = f.read().strip()

        # Try to JSON-serialize if possible
        try:
            parsed = json.loads(raw_value)
            value = json.dumps(parsed)
        except Exception:
            value = raw_value

    if not value:
        typer.echo("❌ Error: You must provide either a value or a --file", err=True)
        raise typer.Exit(code=1)

    # Call API
    try:
        create_or_update_secret(repo_owner, repo_name, environment, name, value)
        typer.echo(f"✅ Secret '{name}' updated in environment '{environment}'")
    except Exception as e:
        typer.echo(f"❌ Failed to set secret: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def bulk(
    environment: str = typer.Argument(..., help="The GitHub environment (e.g., staging, production)."),
    env_file: Path = typer.Option(..., "--file", "-f", help="Path to .env file containing secrets."),
    owner: str = typer.Option(None, "--owner", help="GitHub repo owner (defaults to GH_OWNER env var)."),
    repo: str = typer.Option(None, "--repo", help="GitHub repo name (defaults to GH_REPO env var)."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be uploaded without actually doing it.",
    ),
):
    """
    Upload multiple secrets from a .env file to GitHub environment.
    """
    # Ensure GitHub token is available (skip for dry-run)
    if not dry_run:
        ensure_github_token()

    repo_owner = owner or os.getenv("GH_OWNER")
    repo_name = repo or os.getenv("GH_REPO")

    if not repo_owner or not repo_name:
        typer.echo("❌ Missing repo info. Set GH_OWNER/GH_REPO env vars or use --owner/--repo")
        raise typer.Exit(code=1)

    if not env_file.exists():
        typer.echo(f"❌ .env file not found: {env_file}", err=True)
        raise typer.Exit(code=1)

    try:
        results = write_env_to_github(
            repo_owner=repo_owner,
            repo_name=repo_name,
            environment=environment,
            file_path=str(env_file),
            dry_run=dry_run,
        )

        if dry_run:
            typer.echo(f"🔍 Dry run completed. Found {len(results['variables'])} variables.")
        else:
            success_count = len(results["success"])
            failed_count = len(results["failed"])

            if failed_count == 0:
                typer.echo(f"🎉 All {success_count} secrets uploaded successfully!")
            else:
                typer.echo(f"⚠️  Upload completed with {failed_count} failures out of {results['total']} secrets.")
                raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"❌ Bulk upload failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def list(
    environment: str = typer.Argument(..., help="The GitHub environment (e.g., staging, production)."),
    owner: str = typer.Option(None, "--owner", help="GitHub repo owner (defaults to GH_OWNER env var)."),
    repo: str = typer.Option(None, "--repo", help="GitHub repo name (defaults to GH_REPO env var)."),
):
    """
    List all secrets in a GitHub environment.
    """
    # Ensure GitHub token is available
    ensure_github_token()

    repo_owner = owner or os.getenv("GH_OWNER")
    repo_name = repo or os.getenv("GH_REPO")

    if not repo_owner or not repo_name:
        typer.echo("❌ Missing repo info. Set GH_OWNER/GH_REPO env vars or use --owner/--repo")
        raise typer.Exit(code=1)

    try:
        secrets = list_environment_secrets(repo_owner, repo_name, environment)

        if not secrets:
            typer.echo(f"📭 No secrets found in environment '{environment}'")
        else:
            typer.echo(f"🔐 Found {len(secrets)} secrets in environment '{environment}':")
            for secret in sorted(secrets):
                typer.echo(f"  • {secret}")

    except Exception as e:
        typer.echo(f"❌ Failed to list secrets: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def delete(
    environment: str = typer.Argument(..., help="The GitHub environment (e.g., staging, production)."),
    secret_name: str = typer.Argument(..., help="The name of the secret to delete."),
    owner: str = typer.Option(None, "--owner", help="GitHub repo owner (defaults to GH_OWNER env var)."),
    repo: str = typer.Option(None, "--repo", help="GitHub repo name (defaults to GH_REPO env var)."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
):
    """
    Delete a single secret from a GitHub environment.
    """
    # Ensure GitHub token is available
    ensure_github_token()

    repo_owner = owner or os.getenv("GH_OWNER")
    repo_name = repo or os.getenv("GH_REPO")

    if not repo_owner or not repo_name:
        typer.echo("❌ Missing repo info. Set GH_OWNER/GH_REPO env vars or use --owner/--repo")
        raise typer.Exit(code=1)

    # Confirmation prompt unless --force is used
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to delete secret '{secret_name}' from environment '{environment}'?"
        )
        if not confirm:
            typer.echo("❌ Deletion cancelled.")
            raise typer.Exit(code=1)

    try:
        delete_environment_secret(repo_owner, repo_name, environment, secret_name)
        typer.echo(f"✅ Secret '{secret_name}' deleted from environment '{environment}'")

    except Exception as e:
        typer.echo(f"❌ Failed to delete secret: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def delete_bulk(
    environment: str = typer.Argument(..., help="The GitHub environment (e.g., staging, production)."),
    secrets_file: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to file containing secret names (one per line).",
    ),
    secrets: str = typer.Option(None, "--names", help="Comma-separated list of secret names to delete."),
    owner: str = typer.Option(None, "--owner", help="GitHub repo owner (defaults to GH_OWNER env var)."),
    repo: str = typer.Option(None, "--repo", help="GitHub repo name (defaults to GH_REPO env var)."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
):
    """
    Delete multiple secrets from a GitHub environment.
    Provide secret names via --file (one per line) or --names (comma-separated).
    """
    # Ensure GitHub token is available
    ensure_github_token()

    repo_owner = owner or os.getenv("GH_OWNER")
    repo_name = repo or os.getenv("GH_REPO")

    if not repo_owner or not repo_name:
        typer.echo("❌ Missing repo info. Set GH_OWNER/GH_REPO env vars or use --owner/--repo")
        raise typer.Exit(code=1)

    # Get secret names from file or command line
    secret_names = []

    if secrets_file:
        if not secrets_file.exists():
            typer.echo(f"❌ File not found: {secrets_file}", err=True)
            raise typer.Exit(code=1)

        with open(secrets_file, "r", encoding="utf-8") as f:
            secret_names = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    elif secrets:
        secret_names = [name.strip() for name in secrets.split(",") if name.strip()]

    else:
        typer.echo("❌ You must provide either --file or --names", err=True)
        raise typer.Exit(code=1)

    if not secret_names:
        typer.echo("❌ No valid secret names found", err=True)
        raise typer.Exit(code=1)

    # Confirmation prompt unless --force is used
    if not force:
        typer.echo(f"🗑️  About to delete {len(secret_names)} secrets from environment '{environment}':")
        for name in secret_names[:10]:  # Show first 10
            typer.echo(f"  • {name}")
        if len(secret_names) > 10:
            typer.echo(f"  ... and {len(secret_names) - 10} more")

        confirm = typer.confirm("Are you sure you want to proceed?")
        if not confirm:
            typer.echo("❌ Deletion cancelled.")
            raise typer.Exit(code=1)

    try:
        results = delete_multiple_secrets(
            repo_owner=repo_owner,
            repo_name=repo_name,
            environment=environment,
            secret_names=secret_names,
            confirm=True,
        )

        failed_count = len(results["failed"])
        if failed_count == 0:
            typer.echo(f"🎉 All {len(results['success'])} secrets deleted successfully!")
        else:
            typer.echo(f"⚠️  Deletion completed with {failed_count} failures out of {results['total']} secrets.")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"❌ Bulk deletion failed: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
