# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from git import Commit, Diff, DiffIndex
from pyforgejo import PullRequest, PyforgejoApi
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

CC_LINE_IN_BODY_RE = re.compile(r"^CC:\s*(.*)$", re.IGNORECASE)


@dataclass
class LocalRepoPrInformation:
    """Local repository information for a PR."""

    real_head_sha: str
    real_base_sha: str
    base_gcc_descr: str | None
    head_gcc_desc: str | None
    diff: DiffIndex[Diff]
    commits: list[Commit]


@dataclass
class PatchPosting:
    """Map a single git commit to its corresponding message ID for tracking."""

    pull_request_url: str
    version: int
    cover_msgid: str
    patch_msgid: str


@dataclass
class PullRequestData:
    """Wrap metadata and Forgejo client related to a specific pull request."""

    url: str
    owner: str
    repo: str
    index: int
    client: PyforgejoApi
    pr_data: PullRequest
    pr_body: str
    cc: list[str]


@dataclass
class PullRequestVersion:
    """Track patch version metadata for a pull request."""

    version: int = 0
    base_ref: str = ""
    head_ref: str = ""


class RetryException(Exception):
    """Exception used to signal a recoverable operation that
    should be retried by celery workers."""

    pass


def convert_multiline_strings(data):
    """Recursively convert strings with newlines to YAML block scalars."""
    if isinstance(data, dict):
        return {k: convert_multiline_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_multiline_strings(i) for i in data]
    elif isinstance(data, str) and "\n" in data:
        return LiteralScalarString(data)
    return data


def deep_get(path: str, obj: Any) -> str | int | list | dict | datetime:
    """
    Recursively retrieve a deeply nested attribute or dictionary key.

    Raises:
        ValueError: if the path is not found or the type is unsupported.
    """
    parts = path.split(".")
    current = obj
    for i, part in enumerate(parts):
        try:
            if isinstance(current, dict):
                current = current[part]
            else:
                current = getattr(current, part)
        except (KeyError, AttributeError) as e:
            missing_path = ".".join(parts[: i + 1])
            raise ValueError(f"Missing key or attribute at '{missing_path}'") from e
    if not isinstance(current, (str, list, dict, int, datetime)):
        raise ValueError(f"Invalid type for {path}: {type(current)}")
    return current


def deep_get_datetime(path: str, obj: Any) -> datetime:
    """
    Retrieve a nested datetime object using the deep_get utility.

    Raises:
        ValueError: if the result is not a datetime instance.
    """
    r = deep_get(path, obj)
    if not isinstance(r, datetime):
        raise ValueError(f"Invalid type for {path}: {type(r)}")
    return r


def deep_get_int(path: str, obj: Any) -> int:
    """
    Retrieve a nested value and convert it to an integer.

    Raises:
        ValueError: if conversion fails or path is missing.
    """
    r = deep_get(path, obj)
    try:
        return int(r)  # type: ignore[arg-type]
    except TypeError:
        raise ValueError(f"Invalid type for {path}: {type(r)}")


def deep_get_str(path: str, obj: Any) -> str:
    """
    Retrieve a nested string using the deep_get utility.

    Raises:
        ValueError: if the result is not a string.
    """
    r = deep_get(path, obj)
    if not isinstance(r, str):
        raise ValueError(f"Invalid type for {path}: {type(r)}")
    return r


def dump(something: list | dict | None, stream: Any = sys.stdout):
    """
    Dump a Python object to YAML, formatting multiline strings as block scalars.

    Args:
        something: The object to serialize.
        stream: Output stream to write to (defaults to stdout).
    """
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 80
    yaml.dump(convert_multiline_strings(something), stream)


# Helper tool to convert JSON to YAML format with a specific block style.
def json2yaml(file: str):
    """Convert a JSON file to YAML format and print to stdout."""
    with open(file) as f:
        dump(json.load(f))


def read_pr_body(body: str) -> tuple[str, list[str]]:
    remaining = []
    cc: list[str] = []
    lines = body.splitlines()
    for idx, line in enumerate(reversed(lines)):
        if m := CC_LINE_IN_BODY_RE.match(line):
            cc.extend([address.strip() for address in m.group(1).split(",")])
        elif not line.strip():
            continue
        else:
            if idx:
                remaining = lines[0:-idx]
            else:
                remaining = lines
            break
    remaining_body = "\n".join(remaining) + "\n" if remaining else ""
    return remaining_body, cc
