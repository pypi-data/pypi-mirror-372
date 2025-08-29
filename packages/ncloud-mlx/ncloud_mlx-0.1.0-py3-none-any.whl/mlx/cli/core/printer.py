#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import datetime
import re
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

import timeago
import yaml
from rich.box import Box
from rich.table import Table
from rich.text import TextType
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class Dictable(Protocol):
    def to_dict(self) -> dict: ...


class DictNormalizer:
    def __init__(
        self,
        remove_none: bool = False,
        titlize_key: bool = False,
        title_depth: int = 2,
        high_prior: List[str] = [],
        omit: List[str] = [],
    ) -> None:
        self.remove_none = remove_none
        self.titlize_key = titlize_key
        self.title_depth = title_depth
        self.high_prior = high_prior
        self.high_prior = high_prior
        self.omit = omit

    def normalize(self, d: dict) -> dict:
        if not self.remove_none and not self.titlize_key:
            return d

        return self._normalize(d, self.title_depth)

    def _normalize(
        self,
        o: Any,
        title_depth: int,
    ) -> Any:
        def _is_title():
            return self.titlize_key and title_depth > 0

        if isinstance(o, dict):
            ret = {}
            for key in self.high_prior:
                value = o.get(key)
                if value:
                    new_value = self._normalize(value, title_depth - 1)
                    if self.remove_none and not new_value:
                        continue
                    new_key = key.title().replace("_", " ") if _is_title() else key
                    ret[new_key] = new_value

            for key, value in o.items():
                if key in self.high_prior:
                    continue
                if key in self.omit:
                    continue
                new_value = self._normalize(value, title_depth - 1)
                if self.remove_none and not new_value:
                    continue
                new_key = key.title().replace("_", " ") if _is_title() else key
                ret[new_key] = new_value

            return ret
        elif isinstance(o, list):
            ret_list = []
            for i in o:
                new_value = self._normalize(i, title_depth - 1)
                if self.remove_none and not new_value:
                    continue
                ret_list.append(new_value)
            return ret_list
        return o


FIRST_OF_LINE = re.compile("^", re.MULTILINE)
TITLE_DEPTH_MAX = 1000


def pretty_yaml(
    data: Union[dict, Dictable],
    omit_empty: bool = True,
    initial_indent: int = 0,
    indent: int = 2,
    titlize_key: bool = True,
    title_depth: int = 2,
    padding_key: bool = True,
    sort_keys=False,
    high_prior: List[str] = [],
    omit: List[str] = [],
) -> str:
    if isinstance(data, Dictable):
        data = data.to_dict()

    def dict_representer(dumper, data):
        keyWidth = 0
        if data and padding_key:
            keyWidth = max(len(k) for k in data)
        aligned = {f"{k:{keyWidth + 2}}": convert_timezone(v) for k, v in data.items()}
        return dumper.represent_mapping("tag:yaml.org,2002:map", aligned)

    yaml.add_representer(dict, dict_representer)

    # https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)

    result = yaml.dump(
        DictNormalizer(
            remove_none=omit_empty,
            titlize_key=titlize_key,
            title_depth=title_depth,
            high_prior=high_prior,
            omit=omit,
        ).normalize(data),
        indent=indent,
        sort_keys=sort_keys,
    ).replace("'", "")

    if initial_indent == 0:
        return result

    return re.sub(FIRST_OF_LINE, " " * initial_indent, result)


def pretty_table(
    data: Union[List[dict], List[Dictable]],
    headers: Dict[str, str] = None,
    omits: List[str] = [],
    high_prior: List[str] = [],
    box: Optional[Box] = None,
    title: Optional[TextType] = None,
) -> Union[Table, str]:
    if len(data) == 0:
        return ""

    data_temp = []
    for d in data:
        if isinstance(d, Dictable):
            data_temp.append(d.to_dict())
        elif isinstance(d, dict):
            data_temp.append(d)
        else:
            raise RuntimeError("unknown type", type(d))

    data = data_temp

    fields = list(data[0].keys())
    if len(omits) > 0:
        fields = [f for f in fields if f not in omits]

    if len(high_prior) > 0:
        fields = [f for f in fields if f not in high_prior]
        fields = high_prior + fields

    data_internal = []

    for d in data:
        di = OrderedDict()
        for f in fields:
            di[f] = convert_timezone(d[f], use_ago=True)

        data_internal.append(di)

    if not headers:
        headers = dict()
        hs = data_internal[0].keys()
        for h in hs:
            headers[h] = h.upper()

    table = Table(
        box=box,
        title=title,
        title_style="bold",
        title_justify="left",
        *headers,
    )
    for d in data_internal:
        table.add_row(*[d[h] for h in headers])

    return table


def parse_from_utcformat(s: str) -> datetime.datetime:
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for format in formats:
        try:
            return datetime.datetime.strptime(s, format)
        except ValueError:
            pass
    raise ValueError(f"time data '{s}' does not match formats {formats}")


def convert_timezone(obj: object, use_ago=False) -> object:
    if not isinstance(obj, str) and not isinstance(obj, datetime.datetime):
        return obj

    if isinstance(obj, datetime.datetime):
        if use_ago:
            return timeago.format(obj, datetime.datetime.now(obj.tzinfo))
        return obj.astimezone()

    try:
        dateobj = parse_from_utcformat(obj)
        if use_ago:
            return timeago.format(dateobj, datetime.datetime.now(datetime.timezone.utc))
        return dateobj.astimezone()
    except ValueError:
        # return original date if it fail to convert
        pass
    return obj


def applied_message(target: Any, kind: str = "", name: str = ""):
    return result_message("applied", target, kind, name)


def created_message(target: Any, kind: str = "", name: str = ""):
    return result_message("created", target, kind, name)


def deleted_message(target: Any, kind: str = "", name: str = ""):
    return result_message("deleted", target, kind, name)


def result_message(verb: str, target: Any, kind: str = "", name: str = "") -> str:
    if not kind and hasattr(target, "kind"):
        kind = target.kind

    if not name and hasattr(target, "metadata") and hasattr(target.metadata, "name"):
        name = target.metadata.name

    if not kind or not name:
        raise RuntimeError("kind and name are required")

    return f"{kind}/{name} {verb}"
