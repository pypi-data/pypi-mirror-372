#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import logging
import resource
from typing import List

from yamlpath import Processor


def override_yaml_values(data: dict, override_values: List[str]):
    processor = Processor(logging.getLogger(__name__), data)
    for o in override_values:
        yaml_path, value = o.rsplit("=", 1)
        processor.set_value(
            yaml_path,
            value,
            mustexist=True,
        )


def select_with_fzf(candidates):
    from shutil import which

    import typer
    from pyfzf.pyfzf import FzfPrompt

    selected = ""

    if not candidates:
        return selected

    if not which("fzf"):
        typer.echo("Install 'fzf' to enable interactive selection")
        return selected

    fzf = FzfPrompt()
    res = fzf.prompt(candidates)
    if res:
        selected = res[0]

    return selected


def increase_soft_rlimit_nofile(debug: bool):
    soft = 0
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
        return soft, hard
    except Exception as e:
        # Keep going when it fail to increase RLIMIT_NOFILE value.
        if debug:
            print(e)
        return soft, soft


def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    # Capitalize the first letter of each component except the first one
    return components[0] + "".join(x.capitalize() for x in components[1:])


def convert_keys_to_camel_case(d: dict, recurse: bool = False) -> dict:
    converted_dict = {}
    for k, v in d.items():
        converted_key = snake_to_camel(k)
        if recurse:
            converted_dict[converted_key] = convert_keys_to_camel_case(v)
        else:
            converted_dict[converted_key] = v
    return converted_dict
