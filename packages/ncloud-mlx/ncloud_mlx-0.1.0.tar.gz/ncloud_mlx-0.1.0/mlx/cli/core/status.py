#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import os
from collections import OrderedDict

import typer
from rich import print as rich_print
from typing_extensions import Annotated

from mlx.cli.core.printer import pretty_yaml
from mlx.sdk.core.auth import Token, TokenType
from mlx.sdk.core.config import ConfigFile

REDACT = Annotated[
    bool,
    typer.Option("--redact/--no-redact", help="Hide sensitive values."),
]


def status(ctx: typer.Context, *, redact: REDACT = True):
    """Print MLX CLI status and configuration information."""

    gc = ctx.obj  # global_context
    config_file = ConfigFile()

    # Check for environment variables
    # TODO(hyojun.jeon): Use SDK constants for environment variable names
    env_workspace = os.environ.get("MLX_WORKSPACE")
    env_project = os.environ.get("MLX_PROJECT")
    env_endpoint_url = os.environ.get("MLX_ENDPOINT_URL")
    env_apikey = os.environ.get("MLX_APIKEY")

    # Basic information
    rich_print("[bold]MLX CLI Status[/bold]")
    rich_print()
    rich_print("[cyan]Configuration:[/cyan]")

    # Show endpoint URL with source
    endpoint_url_value = env_endpoint_url or config_file.endpoint_url
    endpoint_url_source = (
        " [dim](env)[/dim]"
        if env_endpoint_url
        else " [dim](config)[/dim]"
        if endpoint_url_value
        else ""
    )
    rich_print(
        f"  Endpoint URL      : {endpoint_url_value or 'Not set'}{endpoint_url_source}"
    )

    # Show workspace with source
    workspace_value = gc.safe_current_workspace
    workspace_source = (
        " [dim](env)[/dim]"
        if env_workspace
        else " [dim](config)[/dim]"
        if workspace_value
        else ""
    )
    rich_print(
        f"  Current workspace : {workspace_value or 'Not set'}{workspace_source}"
    )

    # Show project with source
    project_value = gc.safe_current_project
    project_source = (
        " [dim](env)[/dim]"
        if env_project
        else " [dim](config)[/dim]"
        if project_value
        else ""
    )
    rich_print(f"  Current project   : {project_value or 'Not set'}{project_source}")

    # Auth credentials information
    rich_print()
    rich_print("[cyan]Authentication:[/cyan]")

    auth_info = OrderedDict(
        {
            "Auth Type": "API_KEY",
            "Config Path": config_file.config_file_path(),
        }
    )

    # Display workspace with source annotation
    workspace_display = config_file.workspace or "Not configured"
    if env_workspace:
        workspace_display += " (from environment)"
    elif config_file.workspace:
        workspace_display += " (from config)"
    auth_info["Workspace"] = workspace_display

    # Display project with source annotation
    project_display = config_file.project or "Not configured"
    if env_project:
        project_display += " (from environment)"
    elif config_file.project:
        project_display += " (from config)"
    auth_info["Project"] = project_display

    # Display endpoint URL with source annotation
    if env_endpoint_url:
        endpoint_url_display = env_endpoint_url + " (from environment)"
    elif config_file.endpoint_url:
        endpoint_url_display = config_file.endpoint_url + " (from config)"
    else:
        endpoint_url_display = "Not configured"
    auth_info["Endpoint URL"] = endpoint_url_display

    # Display API Key with source annotation
    if config_file.apikey:
        apikey_t = Token(config_file.apikey, token_type=TokenType.MLX_API_KEY)
        apikey_display = apikey_t.display(no_redact=not redact)
        if env_apikey:
            apikey_display += " (from environment)"
        elif config_file.apikey:
            apikey_display += " (from config)"
        auth_info["API Key"] = apikey_display
    else:
        auth_info["API Key"] = "Not configured"

    # Print auth info in YAML format
    print(pretty_yaml(auth_info, initial_indent=2))

    # Show environment variable priority notice
    env_vars_set = [
        var
        for var in ["MLX_WORKSPACE", "MLX_PROJECT", "MLX_ENDPOINT_URL", "MLX_APIKEY"]
        if os.environ.get(var)
    ]
    if env_vars_set:
        rich_print()
        rich_print("[yellow]Environment Variables Override:[/yellow]")
        for var in env_vars_set:
            value = os.environ.get(var)
            if var == "MLX_APIKEY" and value:
                # Use Token.display() for consistent masking
                apikey_token = Token(value, token_type=TokenType.MLX_API_KEY)
                masked_value = apikey_token.display(no_redact=not redact)
                rich_print(f"  {var}={masked_value}")
            else:
                rich_print(f"  {var}={value}")
        rich_print(
            "  [dim]These values take precedence over config file settings.[/dim]"
        )
