#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import importlib

import typer


def load_extension(
    app: typer.Typer,
    pakcage_name: str,
    is_debug=False,
):
    try:
        pkg = importlib.import_module(pakcage_name)

        exts = pkg.mlx_app

        if isinstance(exts, list):
            pass
        else:
            exts = [exts]

        for ext in exts:
            app.add_typer(
                ext,
                name=ext.info.name,
                short_help=ext.info.short_help,
            )

    except ModuleNotFoundError as e:
        if is_debug:
            print(f"Missing package : {e}")
