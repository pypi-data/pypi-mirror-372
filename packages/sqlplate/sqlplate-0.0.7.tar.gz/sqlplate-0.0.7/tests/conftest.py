from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture(scope="session")
def test_path() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session")
def template_path(test_path) -> Path:
    return test_path.parent / "templates"


@pytest.fixture(scope="session")
def respect_sql(test_path: Path) -> Callable[[str, str], str]:
    from tests.utils import load_respect_file

    def wrap_respect(template: str, fmt: str) -> str:
        return load_respect_file(test_path / f"templates/{fmt}.{template}.sql")

    return wrap_respect
