# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Literal

from jinja2 import Template

from .conf import config
from .exceptions import (
    TemplateNotSet,
    TemplateNotSupport,
    TemplateVersionNotFound,
)
from .utils import get_env, remove_sql_comment


def trim(value: str) -> str:
    return value.strip().strip("\n")


Rule = Literal["contain", "validate"]


@dataclass(frozen=True)
class Check:
    rule: Rule | str
    cols: list[str]
    condition: str


class SQLPlate:
    """A SQLPlate object for render any SQL template that prepare by Jinja
    template.

        This object cas pass an option with dot pattern like func-programing.
    """

    def __init__(self, name: str, path: Path) -> None:
        self.name: str = name

        if not path.exists():
            raise FileNotFoundError(f"Path {path} does not exists.")

        if not (path / self.name).exists():
            raise FileNotFoundError(f"Format {self.name!r} does not implement.")

        self.path: Path = path

        # NOTE: Make default arguments.
        self._template_name: str | None = None
        self._template_type: str | None = None
        self._template: Template | None = None
        self._version: str = "latest"
        self._option: dict[str, Any] = {}

    @staticmethod
    def list_formats(path: Path | None = None) -> list[str]:
        """Return supported formats with list of format value.

        Arges:
            path (Path | None): A template path that want to search.

        :rtype: list[str]
        """
        if path is None:
            path: Path = Path("./templates")
        return [
            fmt.name
            for fmt in path.glob(pattern="*")
            if fmt.is_dir() and fmt.name != "utils"
        ]

    @staticmethod
    def list_versions(fmt: str, path: Path | None = None) -> list[str]:
        """Return supported version of specific format with list of version
        string value.

        Arges:
            path (Path | None): A template path that want to search.

        :rtype: list[str]
        """
        if path is None:
            path: Path = Path("./templates")
        return [f.name for f in (path / fmt).glob(pattern="*") if f.is_dir()]

    @classmethod
    def format(cls, name: str, path: Path | None = None) -> "SQLPlate":
        """Construction this class from a system value name.

        Args:
            name (str): A system name of the SQLPlate template.
            path (Path | None): A template path.
        """
        if path is None:
            path: Path = Path("./templates")
        return cls(name=name, path=path)

    def template(self, name: str) -> "SQLPlate":
        """Create template object attribute on this instance."""
        self._template_name: str = name

        if "." in name and name.count(".") == 1:
            self._template_type, _ = name.split(".", maxsplit=1)

        self._template: Template = get_env(self.path).get_template(
            f"{self.name}/{self._version}/{name}.sql"
        )
        return self

    def version(self, tag: str) -> "SQLPlate":
        """Pass a version for getting specific or time-travel template.

        Args:
            tag (str): A tag version.
        """
        if all(
            tag != f.name
            for f in (self.path / self.name).iterdir()
            if f.is_dir()
        ):
            raise TemplateVersionNotFound(
                f"Version: {tag!r} does not found on this {self.name!r} format."
            )

        self._version: str = tag
        return self

    def option(self, key: str, value: Any) -> "SQLPlate":
        """Pass an option key-value pair before generate template.

        Args:
            key (str): A key name of this option.
            value (Any): A value of this key option.
        """
        self._option[key] = value
        return self

    def options(self, values: dict[str, Any]) -> "SQLPlate":
        """Pass an option mapping with multiple key-value pairs before generate
        template.

        Args:
            values (dict[str, Any]): A mapping of multiple key-value pairs.
        """
        self._option = self._option | values
        return self

    def load(self, remove_comment: bool = False, **kwargs) -> str:
        """Generate the SQL statement from its template setup.

        Args:
            - remove_comment (bool): Remove comment after the template render.
        """
        if self._template_name is None or self._template is None:
            raise TemplateNotSet(
                "Template object does not create before load, you should use "
                "`.template(name=?)`."
            )
        render: str = trim(
            self._template.render(
                **(
                    {
                        "_system": self.name,
                        "_template": self._template_name,
                        "_version": self._version,
                    }
                    | config().export(self._template_type)
                    | self._option
                    | kwargs
                ),
            )
        )
        if remove_comment:
            return remove_sql_comment(render)
        return render

    def stream(
        self, remove_comment: bool = False, split_char: str = ";", **kwargs
    ) -> Iterator[str]:
        """Return the iterator of sub-statement that split with ';' charactor.

        Args:
            - remove_comment (bool): Remove comment after the template render.
            - split_char (str): A charactor that want to split from the full
                statement. Default is ';'.
        """
        yield from (
            trim(s)
            for s in (
                self.load(remove_comment=remove_comment, **kwargs).split(
                    split_char
                )
            )
            if trim(s) != ""
        )

    def check(
        self,
        name: Rule | str,
        cols: str | list[str],
        condition: str,
    ) -> "SQLPlate":
        """Passing the check object to the validates key option.

        Args:
            - name (Rule | str): A validation name.
            - cols (str | list[str]): A list of column name.
            - condition (str): A condition string of this validation.
        """
        if "validates" not in self._option:
            self._option["validates"] = []

        if self._template_name and self._template_type != "quality":
            raise TemplateNotSupport(
                "The check method does not support the none-quality template."
            )

        if isinstance(cols, str):
            cols: list[str] = [cols]
        elif not isinstance(cols, list) or any(
            not isinstance(c, str) for c in cols
        ):
            raise TypeError(
                f"The cols parameter does not support for type: {type(cols)}."
            )

        self._option["validates"].append(
            Check(rule=name, cols=cols, condition=condition)
        )
        return self
