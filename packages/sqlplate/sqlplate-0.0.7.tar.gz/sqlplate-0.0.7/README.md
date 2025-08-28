# SQL Template

[![test](https://github.com/korawica/sqlplate/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/sqlplate/actions/workflows/tests.yml)
[![pypi version](https://img.shields.io/pypi/v/sqlplate)](https://pypi.org/project/sqlplate/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlplate?logo=pypi)](https://pypi.org/project/sqlplate/)
[![size](https://img.shields.io/github/languages/code-size/korawica/sqlplate)](https://github.com/korawica/sqlplate)
[![gh license](https://img.shields.io/github/license/korawica/sqlplate)](https://github.com/korawica/sqlplate/blob/main/LICENSE)

A **SQL Template Generator** (aka `SqlPlate`) provide the generator object for
SQL template statements via Python API object.
All SQL template files are store in the [Jinja template](https://jinja.palletsprojects.com/en/stable/templates/)
format that is the powerful template tool package.

> [!NOTE]
> This project keep all SQL use-case that use on Data Engineer works like SCD2
> with `MERGE` operator.

**The layer of SQL template files will be:**

```text
templates/
   ├─ databricks/
   │     ├─ 📂macros/
   │     │     ╰─ ⚙️ delta.jinja
   │     ╰─ 📂latest/
   │           ├─ 📜 etl.delta.sql
   │           ├─ 📜 etl.scd2.sql
   │           ╰─ 📜 select.sql
   ├─ sqlite/
   │     ╰─ 📂latest/
   │           ╰─📜 etl.delta.sql
   ├─ synapse/
   │     ╰─ 📂latest/
   │           ╰─📜 etl.delta.sql
   ╰─ utils/
         ╰─ ⚙️ etl_vars.jinja
```

> [!IMPORTANT]
> The first object of this project is generate ETL statements for dynamic service
> change. You can change the SQL compute service while the SQL statement does not
> change.

## :package: Installation

```shell
pip install -U sqlplate
```

## :fork_and_knife: Usage

### Generate SQL template

Start passing option parameters before generate the Delta ETL SQL statement that
will use on the Azure Databricks service.

```python
from datetime import datetime
from sqlplate import SQLPlate

statement: str = (
    SQLPlate.format('databricks')
    .template('etl.delta')
    .option('catalog', 'catalog-name')
    .option('schema', 'schema-name')
    .option('table', 'table-name')
    .option('pk', 'pk_col')
    .option('columns', ['col01', 'col02'])
    .option('query', 'SELECT * FROM catalog-name.schema-name.source-name')
    .option('load_src', 'SOURCE_FOO')
    .option('load_id', 1)
    .option('load_date', datetime(2025, 2, 1, 10))
    .option('only_main', True)
    .load()
)
print(statement.strip().strip('\n'))
```

The result SQL statement:

```sql
MERGE INTO catalog-name.schema-name.table-name AS target
USING (
    WITH change_query AS (
        SELECT
            src.*,
        CASE WHEN tgt.pk_col IS NULL THEN 99
             WHEN hash(src.col01, src.col02) <> hash(tgt.col01, tgt.col02) THEN 1
             ELSE 0 END AS data_change
        FROM ( SELECT * FROM catalog-name.schema-name.source-name ) AS src
        LEFT JOIN catalog-name.schema-name.table-name AS tgt
            ON  tgt.col01 = src.col01
AND tgt.col02 = src.col02
    )
    SELECT * EXCEPT( data_change ) FROM change_query WHERE data_change IN (99, 1)
) AS source
    ON  target.pk_col = source.pk_col
WHEN MATCHED THEN UPDATE
    SET target.col01            = source.col01
    ,   target.col02            = source.col02
    ,   target.updt_load_src    = 'SOURCE_FOO'
    ,   target.updt_load_id     = 1
    ,   target.updt_load_date   = to_timestamp('20250201', 'yyyyMMdd')
WHEN NOT MATCHED THEN INSERT
    (
        col01, col02, pk_col, load_src, load_id, load_date, updt_load_src, updt_load_id, updt_load_date
    )
    VALUES (
        source.col01,
        source.col02,
        source.pk_col,
        'SOURCE_FOO',
        1,
        20250201,
        'SOURCE_FOO',
        1,
        to_timestamp('20250201', 'yyyyMMdd')
    )
;
```

### Data Quality

This package handle generate SQL statement only.
For the data quality part, this package can use quality templates instead.

```python
from sqlplate import SQLPlate

statement: str = (
    SQLPlate.format('databricks')
    .template('quality.check')
    .option('catalog', 'catalog-name')
    .option('schema', 'schema-name')
    .option('table', 'table-name')
    .option('filter', "load_date >= to_timestamp('20250201', 'yyyyMMdd')")
    .option('unique', ['pk_col'])
    .option('notnull', ['col01', 'col02'])
    .check("contain", ["col01"], "IN ['A', 'B', 'C']")
    .check("gt_10000", ["col03"], "> 10000")
    .load()
)
print(statement.strip().strip('\n'))
```

The result SQL statement:

```sql
WITH source AS (
    SELECT
        *
    FROM
        catalog-name.schema-name.table-name
    WHERE load_date >= to_timestamp('20250201', 'yyyyMMdd')
)
, records AS (
    SELECT COUNT(1) AS table_records FROM source
)
SELECT
    (SELECT table_records FROM records) AS table_records
    , (SELECT COUNT( DISTINCT pk_col ) FROM source) = table_records AS unique_pk_col
    , (SELECT COUNT_IF( col01 IS NULL ) FROM source) = 0 AS notnull_col01
    , (SELECT COUNT_IF( col02 IS NULL ) FROM source) = 0 AS notnull_col02
    , (SELECT COUNT(1) FILTER(WHERE col01 IN ['A', 'B', 'C']) FROM source) = table_records AS contain_col01
    , (SELECT COUNT(1) FILTER(WHERE col03 > 10000) FROM source) = table_records AS gt_10000_col03
FROM records
```

## :chains: Support Systems

| System             | Progress Status  | System Integration Test | Remark                            |
|:-------------------|:----------------:|:-----------------------:|:----------------------------------|
| databricks         |        🟢        |           🟡            | Azure Databricks                  |
| postgres           |        🔴        |           🔴            |                                   |
| mysql              |        🔴        |           🔴            |                                   |
| mssql              |        🔴        |           🔴            | Microsoft SQL Server              |
| synapse            |        🔴        |           🔴            | Azure Synapse Dedicate SQL Pool   |
| synapse-serverless |        🔴        |           🔴            | Azure Synapse Serverless SQL Pool |
| bigquery           |        🟡        |           🔴            | Google BigQuery                   |
| snowflake          |        🔴        |           🔴            |                                   |
| sqlite             |        🟡        |           🟡            |                                   |
| duckdb             |        🟡        |           🟡            |                                   |
| redshift           |        🔴        |           🔴            | Amazon RedShift                   |
| athena             |        🔴        |           🔴            | Amazon Athena                     |
| trino              |        🔴        |           🔴            | Trino                             |

> [!NOTE]
> - 🟢 Complete
> - 🟡 In progress
> - 🔴 Does not develop yet
> - 🟣 Does not plan to support

## :speech_balloon: Contribute

I do not think this project will go around the world because it has specific propose,
and you can create by your coding without this project dependency for long term
solution. So, on this time, you can open [the GitHub issue on this project :raised_hands:](https://github.com/korawica/sqlplate/issues)
for fix bug or request new feature if you want it.
