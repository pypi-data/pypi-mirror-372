INSERT INTO <SCHEMA>.pybrv_metadata (
    unique_rule_identifier,
    bookmark_start_date,
    bookmark_end_date,
    last_modified_ts
)
SELECT
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    MIN(bookmark_column_value) AS bookmark_start_date,
    MAX(bookmark_column_value) AS bookmark_end_date,
    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')  
FROM <STAGE_TABLE_NAME>
GROUP BY unique_rule_identifier
ON CONFLICT (unique_rule_identifier)  
DO UPDATE SET
    bookmark_start_date = EXCLUDED.bookmark_start_date,
    bookmark_end_date = EXCLUDED.bookmark_end_date,
    last_modified_ts = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC');  