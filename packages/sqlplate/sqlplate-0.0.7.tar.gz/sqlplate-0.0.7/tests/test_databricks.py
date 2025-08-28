from datetime import datetime
from functools import partial
from textwrap import dedent
from typing import Callable

import pytest
from jinja2.exceptions import UndefinedError

from src.sqlplate import SQLPlate
from tests.utils import prepare


@pytest.fixture(scope="module")
def respect_databricks(
    respect_sql: Callable[[str, str], str],
) -> Callable[[str], str]:
    return partial(respect_sql, fmt="databricks")


def test_sql_select(template_path):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("select")
        .option("schema", "schema-name")
        .option("table", "table-name")
    )
    statement: str = select_sql.load()
    assert statement == ("SELECT *\nFROM schema-name.table-name")

    statement: str = select_sql.option("catalog", "catalog-name").load()
    assert statement == ("SELECT *\nFROM catalog-name.schema-name.table-name")

    statement: str = select_sql.option("limit", 100).load()
    assert statement == (
        "SELECT *\nFROM catalog-name.schema-name.table-name\nLIMIT 100"
    )

    statement: str = select_sql.option("columns", ["col01", "col02"]).load()
    assert statement == (
        "SELECT col01, col02\nFROM catalog-name.schema-name.table-name\n"
        "LIMIT 100"
    )


def test_sql_delta(template_path, respect_databricks):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.delta")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("pk", "pk_col")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )

    with pytest.raises(UndefinedError):
        select_sql.load()

    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert prepare(statement) == respect_databricks("etl.delta.query")

    statement: str = (
        select_sql.option("pk", ["pk_col01", "pk_col02"])
        .option("source", "catalog-name.schema-name.source-name")
        .load()
    )
    assert prepare(statement) == respect_databricks("etl.delta")


def test_sql_scd1_soft_delete(template_path, respect_databricks):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.scd1-soft-delete")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("pk", "pk_col")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert prepare(statement) == respect_databricks("etl.scd1-soft-delete")

    assert len(list(select_sql.stream())) == 3

    statement: str = select_sql.option("only_main", True).load()
    assert prepare(statement) == respect_databricks(
        "etl.scd1-soft-delete.only-main"
    )

    assert len(list(select_sql.stream())) == 1


def test_sql_scd2(template_path, respect_databricks):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.scd2")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("pk", "pk_col")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert prepare(statement) == respect_databricks("etl.scd2")


def test_sql_scd2_delete_src(template_path, respect_databricks):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.scd2-delete-src")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("pk", "pk_col")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert prepare(statement) == respect_databricks("etl.scd2-delete-src")


def test_sql_scd2_transaction(template_path):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.scd2-transaction")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert (
        prepare(statement)
        == dedent(
            """
        DELETE FROM catalog-name.schema-name.table-name
        WHERE load_src  = 'SOURCE_FOO'
        AND   load_date = 20250201
        ;
        INSERT INTO catalog-name.schema-name.table-name
        PARTITION ( load_date = 20250201 )
            ( col01, col02, start_date, end_date, delete_f, load_src, load_id, updt_load_src, updt_load_id, updt_load_date )
        SELECT
            col01
        ,col02
            ,   to_timestamp('20250201', 'yyyyMMdd')  AS start_date
            ,   to_timestamp('9999-12-31', 'yyyy-MM-dd')                        AS end_date
            ,   'SOURCE_FOO'                                                AS load_src
            ,   1                                                   AS load_id
            ,   'SOURCE_FOO'                                                AS updt_load_src
            ,   1                                                   AS updt_load_id
            ,   to_timestamp('20250201', 'yyyyMMdd')  AS updt_load_date
        FROM ( SELECT * FROM catalog-name.schema-name.source-name ) AS sub_query
        ;
        """
        ).strip("\n")
    )


def test_sql_transaction(template_path):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.transaction")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert (
        prepare(statement)
        == dedent(
            """
        DELETE FROM catalog-name.schema-name.table-name
        WHERE load_src  = 'SOURCE_FOO'
        AND   load_date = 20250201
        ;
        INSERT INTO catalog-name.schema-name.table-name
        PARTITION ( load_date = 20250201 )
            ( col01, col02, load_src, load_id, updt_load_src, updt_load_id, updt_load_date )
        SELECT
            col01
        ,col02
            ,   'SOURCE_FOO'                                                AS load_src
            ,   1                                                   AS load_id
            ,   'SOURCE_FOO'                                                AS updt_load_src
            ,   1                                                   AS updt_load_id
            ,   to_timestamp('20250201', 'yyyyMMdd')  AS updt_load_date
        FROM ( SELECT * FROM catalog-name.schema-name.source-name ) AS sub_query
        ;
        """
        ).strip("\n")
    )


def test_sql_full_dump(template_path):
    select_sql: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("etl.fulldump")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("load_src", "SOURCE_FOO")
        .option("load_id", 1)
        .option("load_date", datetime(2025, 2, 1, 10))
    )
    statement: str = (
        select_sql.option("columns", ["col01", "col02"])
        .option("query", "SELECT * FROM catalog-name.schema-name.source-name")
        .load()
    )
    assert (
        prepare(statement)
        == dedent(
            """
        DELETE FROM catalog-name.schema-name.table-name
        WHERE load_src = 'SOURCE_FOO'
        ;
        INSERT INTO catalog-name.schema-name.table-name
            ( col01, col02, load_src, load_id, load_date, updt_load_src, updt_load_id, updt_load_date )
        SELECT
            col01
        ,col02
            ,   'SOURCE_FOO'                                                AS load_src
            ,   1                                                   AS load_id
            ,   20250201                              AS load_date
            ,   'SOURCE_FOO'                                                AS updt_load_src
            ,   1                                                   AS updt_load_id
            ,   to_timestamp('20250201', 'yyyyMMdd')  AS updt_load_date
        FROM ( SELECT * FROM catalog-name.schema-name.source-name ) AS sub_query
        ;
        """
        ).strip("\n")
    )


def test_quality_check(template_path):
    statement: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("quality.check")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("filter", "load_date >= to_timestamp('20250201', 'yyyyMMdd')")
        .option("unique", ["pk_col"])
        .option("notnull", ["col01", "col02"])
        .check("contain", ["col01"], "IN ['A', 'B', 'C']")
        .check("gt_10000", ["col03"], "> 10000")
        .load()
    )
    print(statement)


def test_quality_metrix(template_path):
    statement: SQLPlate = (
        SQLPlate.format("databricks", path=template_path)
        .template("quality.matrix")
        .option("catalog", "catalog-name")
        .option("schema", "schema-name")
        .option("table", "table-name")
        .option("filter", "load_date >= to_timestamp('20250201', 'yyyyMMdd')")
        .option("columns", ["col01", "col02"])
        .load()
    )
    print(statement)
