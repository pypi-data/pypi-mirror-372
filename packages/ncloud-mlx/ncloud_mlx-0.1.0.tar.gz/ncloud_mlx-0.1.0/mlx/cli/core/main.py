#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from typing import Optional

import typer
from typing_extensions import Annotated

from mlx.sdk.core.config import GlobalContext

from .configure import configure as configure_command
from .extension import load_extension
from .status import status as status_command

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

app = typer.Typer(
    name="mlx",
    help="MLX CLI/SDK",
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
app.command(context_settings=CONTEXT_SETTINGS)(status_command)
app.command(context_settings=CONTEXT_SETTINGS)(configure_command)

load_extension(app, "mlx.cli.model_registry")


def print_package_version(extension_name: str):
    try:
        import sys

        if sys.version_info >= (3, 8):
            from importlib import metadata
        else:
            import importlib_metadata as metadata

        print(f"{extension_name} {metadata.version(extension_name)}")
    except Exception:
        pass


def version_callback(value: bool):
    if not value:
        return

    print_package_version("ncloud-mlx")
    print_package_version("ncloud-mlx-model-registry")
    raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    debug: Annotated[
        Optional[bool],
        typer.Option("--debug", "-d", envvar="MLX_DEBUG", help="Print debug log."),
    ] = False,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            "--verbose",
            "-V",
            envvar="MLX_VERBOSE",
            help="Print detailed command output.",
        ),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Print version info.",
            is_eager=True,
            callback=version_callback,
        ),
    ] = None,
):
    ctx.obj = app.global_context = GlobalContext(verbose=verbose, debug=debug)
    if debug:
        app.pretty_exceptions_short = False
    else:
        app.pretty_exceptions_show_locals = False


def run():
    try:
        app()
    except Exception as e:
        import sys

        from .console import console_err

        debug = app.global_context.debug
        console_err.print("Error : ", style="red", end="")
        console_err.print(f"{e}")

        if debug:
            console_err.print("Stack trace :", style="red")
            # below re-raise will print traceback and return non-zero exit code
            raise
        else:
            console_err.print(
                "\nFor more information, try to add `--debug` option. Like this : ",
                style="yellow",
            )
            console_err.print(
                f"    mlx --debug {' '.join(sys.argv[1:])}",
                style="yellow",
            )
            sys.exit(1)


if __name__ == "__main__":
    run()
