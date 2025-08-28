import pytest

from src.sqlplate import SQLPlate
from src.sqlplate.exceptions import TemplateNotSupport, TemplateVersionNotFound


def test_sqlplate_raise(template_path):
    with pytest.raises(FileNotFoundError):
        SQLPlate.format(name="not-exists", path=template_path / "not-exists")

    with pytest.raises(FileNotFoundError):
        SQLPlate.format(name="not-exists", path=template_path)


def test_sqlplate_formats(template_path):
    formats: list[str] = SQLPlate.list_formats(path=template_path)
    assert isinstance(formats, list)
    assert len(formats) > 0
    assert "utils" not in formats


def test_sqlplate_version(template_path):
    fmt: SQLPlate = SQLPlate.format("databricks", path=template_path)

    with pytest.raises(TemplateVersionNotFound):
        fmt.version("test")

    fmt.version("latest")


def test_sqlplate_versions(template_path):
    versions: list[str] = SQLPlate.list_versions(
        fmt="databricks", path=template_path
    )
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert "latest" in versions


def test_sqlplate_check(template_path):
    fmt: SQLPlate = SQLPlate.format("databricks", path=template_path)

    with pytest.raises(TemplateNotSupport):
        (
            fmt.template("etl.delta")
            .option("catalog", "catalog-name")
            .option("schema", "schema-name")
            .option("table", "table-name")
            .check("contain", ["col01"], "IN ['A', 'B', 'C']")
        )
