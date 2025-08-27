<TAGS>
MERGE INTO <DATABASE_NAME>.pybrv_meta.pybrv_metadata AS target
USING (
    SELECT 
        <UNIQUE_RULE_IDENTIFIER> AS UNIQUE_RULE_IDENTIFIER,
        DATE '<BOOKMARK_START_DATE>' AS min_bookmark,
        DATE '<BOOKMARK_END_DATE>' AS max_bookmark
) AS source
ON target.UNIQUE_RULE_IDENTIFIER = source.UNIQUE_RULE_IDENTIFIER
WHEN MATCHED THEN
    UPDATE SET
        target.BOOKMARK_START_DATE = source.min_bookmark,
        target.BOOKMARK_END_DATE = source.max_bookmark,
        target.LAST_MODIFIED_TS = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (
        UNIQUE_RULE_IDENTIFIER,
        BOOKMARK_START_DATE,
        BOOKMARK_END_DATE,
        LAST_MODIFIED_TS
    ) VALUES (
        source.UNIQUE_RULE_IDENTIFIER,
        source.min_bookmark,
        source.max_bookmark,
        CURRENT_TIMESTAMP
    );