from pathlib import Path
from textwrap import dedent


def prepare(statement: str) -> str:
    return statement.replace("\t", "").strip().strip("\n")


def load_respect_file(template: Path) -> str:
    with template.open(mode="rt", encoding="utf-8") as f:
        return dedent(f.read()).strip("\n")
