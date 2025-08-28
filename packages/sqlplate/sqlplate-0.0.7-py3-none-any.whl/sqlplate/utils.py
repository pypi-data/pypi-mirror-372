# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader
from jinja2.exceptions import UndefinedError


def map_fmt(value: list[str], fmt: str) -> list[str]:
    """Prepare string value with formatting string.

    Example:
        >>> map_fmt(['col01', 'col02'], fmt='src.{0} = tgt.{0}')
        ['src.col01 = tgt.col01', 'src.col02 = tgt.col02']
    """
    return [fmt.format(i) for i in value]


def raise_undefined(value: str) -> None:
    """Raise with UndefinedError for a needed variable on the Jinja template."""
    if len(value.split("|")) > 1:
        value: str = "' or '".join(value.split("|"))
    raise UndefinedError(f"The '{value}' is undefined")


def dt_fmt(value: datetime, fmt: str) -> str:
    """Format a datetime object to string value."""
    return value.strftime(fmt)


def get_env(
    path: Path,
    *,
    trim_blocks: bool = True,
    lstrip_blocks: bool = True,
) -> Environment:
    """Get jinja environment object for the SQL template files.

    Args:
        path (Path): A package path.
        trim_blocks (bool):
        lstrip_blocks (bool):
    """
    env = Environment(
        loader=PackageLoader(
            package_name="templates",
            package_path=str(path),
        ),
        trim_blocks=trim_blocks,
        lstrip_blocks=lstrip_blocks,
    )
    env.filters["map_fmt"] = map_fmt
    env.filters["dt_fmt"] = dt_fmt
    env.globals["raise_undefined"] = raise_undefined
    return env


def remove_sql_comment(statement: str):
    """Remove comment statement in a SQL template.

    Args:
        statement (str): A SQL statement.

    Example:

        >>> remove_sql_comment("SELECT * FROM table -- this is comment")
        'SELECT * FROM table'

        >>> remove_sql_comment(
        ...     "SELECT /* comment\\n"
        ...     "more comment */ FROM table"
        ... )
        'SELECT\\nFROM table'

    """
    statement: str = re.sub(r"^\s*--.*\n?", "", statement, flags=re.MULTILINE)
    statement: str = re.sub(r"\s*--.*\n?", "", statement, flags=re.MULTILINE)

    comment_re = re.compile(
        r"(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?",
        re.DOTALL | re.MULTILINE,
    )

    def comment_replacer(match):
        start, mid, end = match.group(1, 2, 3)
        if mid is None:
            # NOTE: single line comment
            return ""
        elif start is not None or end is not None:
            # NOTE: multi line comment at start or end of a line
            return ""
        elif "\n" in mid:
            # NOTE: multi line comment with line break
            return "\n"
        else:
            # NOTE: multi line comment without line break
            return " "

    statement = comment_re.sub(comment_replacer, statement)
    return statement
