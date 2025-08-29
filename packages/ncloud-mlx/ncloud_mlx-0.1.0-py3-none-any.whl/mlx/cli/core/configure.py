#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import os

import typer

from mlx.sdk.core.auth import Token, TokenType
from mlx.sdk.core.config import ConfigFile


def configure(ctx: typer.Context):
    """Configure MLX credentials (workspace, project, apikey)."""
    config_file = ConfigFile()

    typer.echo("MLX CLI Configuration")
    typer.echo("Please enter the following information:")
    typer.echo()

    # Check for environment variables
    # TODO(hyojun.jeon): Use SDK constants for environment variable names
    env_workspace = os.environ.get("MLX_WORKSPACE")
    env_project = os.environ.get("MLX_PROJECT")
    env_apikey = os.environ.get("MLX_APIKEY")
    env_endpoint_url = os.environ.get("MLX_ENDPOINT_URL")

    # Show environment variable info if any are set
    if any([env_workspace, env_project, env_apikey, env_endpoint_url]):
        typer.echo("⚠️  Environment variables detected:")
        if env_workspace:
            typer.echo(f"   MLX_WORKSPACE={env_workspace}")
        if env_project:
            typer.echo(f"   MLX_PROJECT={env_project}")
        if env_endpoint_url:
            typer.echo(f"   MLX_ENDPOINT_URL={env_endpoint_url}")
        if env_apikey:
            # Use Token.display() for consistent masking
            env_apikey_token = Token(env_apikey, token_type=TokenType.MLX_API_KEY)
            masked_env_key = env_apikey_token.display(no_redact=False)
            typer.echo(f"   MLX_APIKEY={masked_env_key}")
        typer.echo("   Environment variables will override config file values.")
        typer.echo()

    # Get endpoint URL input
    current_endpoint_url = config_file.endpoint_url or "None"
    endpoint_url_source = "(from env)" if env_endpoint_url else "(from config)"
    config_endpoint_url = config_file.current_context_object.endpoint_url or ""
    endpoint_url = typer.prompt(
        f"Endpoint URL [{current_endpoint_url} {endpoint_url_source}]",
        default=config_endpoint_url,
        show_default=False,
    )

    # Get workspace input
    current_workspace = config_file.workspace or "None"
    workspace_source = "(from env)" if env_workspace else "(from config)"
    config_workspace = config_file.current_context_object.workspace or ""
    workspace = typer.prompt(
        f"Workspace name [{current_workspace} {workspace_source}]",
        default=config_workspace,
        show_default=False,
    )

    # Get project input
    current_project = config_file.project or "None"
    project_source = "(from env)" if env_project else "(from config)"
    config_project = config_file.current_context_object.project or ""
    project = typer.prompt(
        f"Project name [{current_project} {project_source}]",
        default=config_project,
        show_default=False,
    )

    # Get API Key input
    current_apikey = config_file.apikey or "None"
    apikey_source = "(from env)" if env_apikey else "(from config)"
    config_apikey = config_file.current_context_object.apikey or ""

    if current_apikey != "None" and not env_apikey:
        # Use Token.display() for consistent masking
        current_apikey_token = Token(current_apikey, token_type=TokenType.MLX_API_KEY)
        masked_apikey = current_apikey_token.display(no_redact=False)
        apikey_display = f"{masked_apikey} {apikey_source}"
    else:
        apikey_display = f"{current_apikey} {apikey_source}"

    apikey = typer.prompt(
        f"API Key [{apikey_display}]",
        default=config_apikey,
        hide_input=True,
        show_default=False,
    )

    # Warn about environment variables
    if any([env_workspace, env_project, env_endpoint_url, env_apikey]):
        typer.echo()
        typer.echo("⚠️  Note: Environment variables will override these config values.")
        typer.echo("   To use config values, unset the environment variables:")
        if env_workspace:
            typer.echo("   unset MLX_WORKSPACE")
        if env_project:
            typer.echo("   unset MLX_PROJECT")
        if env_endpoint_url:
            typer.echo("   unset MLX_ENDPOINT_URL")
        if env_apikey:
            typer.echo("   unset MLX_APIKEY")

    # Save configuration (property setters auto-save)
    if workspace:
        config_file.workspace = workspace
    if project:
        config_file.project = project
    if endpoint_url:
        config_file.endpoint_url = endpoint_url
    if apikey:
        config_file.apikey = apikey

    typer.echo()
    typer.echo("✅ Configuration saved successfully!")
    typer.echo(f"   Endpoint URL: {endpoint_url}")
    typer.echo(f"   Workspace: {workspace}")
    typer.echo(f"   Project: {project}")
    typer.echo(f"   API Key: {'*' * len(apikey) if apikey else ''}")
    typer.echo(f"   Config file: {config_file.config_file_path()}")
