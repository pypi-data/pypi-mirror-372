DELETE FROM catalog-name.schema-name.table-name
WHERE
    load_date >= 20250201,
    AND load_src = 'SOURCE_FOO'
;
UPDATE catalog-name.schema-name.table-name
    SET delete_f        = 0
    ,   updt_load_src   = 'SOURCE_FOO'
    ,   updt_load_id    = 1
    ,   updt_load_date  = to_timestamp('20250201', 'yyyyMMdd')
WHERE
    delete_f            = 1
    AND updt_load_src   = 'SOURCE_FOO'
    AND updt_load_date  >= to_timestamp('20250201', 'yyyyMMdd')
;
MERGE INTO catalog-name.schema-name.table-name AS target
USING (
    WITH change_query AS (
        SELECT
            src.*,
            CASE WHEN tgt.pk_col IS NULL THEN 99
                WHEN hash(src.col01, src.col02) <> hash(tgt.col01, tgt.col02) THEN 1
                ELSE 0 END                                        AS data_change
        FROM ( SELECT * FROM catalog-name.schema-name.source-name ) AS src
        LEFT JOIN catalog-name.schema-name.table-name          AS tgt
            ON  tgt.col01 = src.col01
AND tgt.col02 = src.col02
    )
    SELECT * FROM change_query
) AS source
    ON  target.pk_col = source.pk_col
WHEN MATCHED AND data_change = 1
THEN UPDATE
    SET target.col01= source.col01
,target.col02= source.col02
    ,   target.delete_f         = 0
    ,   target.updt_load_src    = 'SOURCE_FOO'
    ,   target.updt_load_id     = 1
    ,   target.updt_load_date   = to_timestamp('20250201', 'yyyyMMdd')
WHEN MATCHED AND data_change = 0 AND target.delete_f = 1
THEN UPDATE
    SET target.delete_f         = 0
    ,   target.updt_load_src    = 'SOURCE_FOO'
    ,   target.updt_load_id     = 1
    ,   target.updt_load_date   = to_timestamp('20250201', 'yyyyMMdd')
WHEN NOT MATCHED AND data_change = 99
THEN INSERT
    (
        col01, col02, pk_col, delete_f, load_src, load_id, load_date, updt_load_src, updt_load_id, updt_load_date
    )
    VALUES (
        source.col01,
        source.col02,
        source.pk_col,
        0,
        'SOURCE_FOO',
        1,
        20250201,
        'SOURCE_FOO',
        1,
        to_timestamp('20250201', 'yyyyMMdd')
    )
WHEN NOT MATCHED BY SOURCE AND target.delete_f = 0
THEN UPDATE
    SET target.delete_f         = 1
    ,   target.updt_load_src    = 'SOURCE_FOO'
    ,   target.updt_load_id     = 1
    ,   target.updt_load_date   = to_timestamp('20250201', 'yyyyMMdd')
;
