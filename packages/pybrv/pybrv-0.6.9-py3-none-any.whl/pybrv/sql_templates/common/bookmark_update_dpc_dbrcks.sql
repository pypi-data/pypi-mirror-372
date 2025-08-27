MERGE INTO <DATABASE_NAME>.<SCHEMA>.pybrv_metadata AS target
USING (
    SELECT
        <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
        MIN(bookmark_column_value) AS bookmark_start_date,
        MAX(bookmark_column_value) AS bookmark_end_date,
        current_timestamp() AS last_modified_ts
    FROM <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>
    GROUP BY <UNIQUE_RULE_IDENTIFIER>
) AS source
ON target.unique_rule_identifier = source.unique_rule_identifier

WHEN MATCHED THEN
  UPDATE SET
    target.bookmark_start_date = source.bookmark_start_date,
    target.bookmark_end_date = source.bookmark_end_date,
    target.last_modified_ts = source.last_modified_ts

WHEN NOT MATCHED THEN
  INSERT (
    unique_rule_identifier,
    bookmark_start_date,
    bookmark_end_date,
    last_modified_ts
  )
  VALUES (
    source.unique_rule_identifier,
    source.bookmark_start_date,
    source.bookmark_end_date,
    source.last_modified_ts
  );
