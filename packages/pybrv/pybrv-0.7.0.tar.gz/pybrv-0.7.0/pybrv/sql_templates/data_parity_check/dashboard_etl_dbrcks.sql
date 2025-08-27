
DELETE FROM <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_stats
WHERE EXECUTION_ID = <EXECUTION_ID>;


INSERT INTO <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_stats
SELECT 
    pr.EXECUTION_ID,
    pr.UNIQUE_RULE_IDENTIFIER,
    pr.DATA_DOMAIN,
    pr.RULE_NAME,
    pr.TABLE_NAME,
    CAST(pr.LAST_MODIFIED_TS AS DATE) AS execution_date,
    pr.BOOKMARK_COLUMN_NAME AS key_date_column,
    pr.BOOKMARK_COLUMN_VALUE AS key_date_value,

    CASE 
        WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
             AND pr.metric_dim_values IS NOT NULL
        THEN element_at(map_keys(from_json(COALESCE(pr.metric_dim_values, '{}'), 'MAP<STRING, STRING>')), 1)
        WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
            AND pr.metric_dim_values IS NULL THEN NULL
        WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count', 'target_total_count', 'row_matched_count') 
        THEN regexp_replace(regexp_replace(pr.ATTRIBUTE_NAME, '_total_count', ''), '_matched_count', '')

    END AS FIELD_NAME,


    pr.comments AS comments,

    SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'source_total_count' THEN pr.ATTRIBUTE_VALUE END) AS SOURCE_RECORDS,
    SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'target_total_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_RECORDS,
    SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'row_matched_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_ROWS_MATCHED,

    SUM(CASE 
        WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count') 
             AND matched_result.DATA_DOMAIN IS NOT NULL 
             AND pr.ATTRIBUTE_NAME LIKE '%_total_count'
        THEN pr.ATTRIBUTE_VALUE 
    END) AS SOURCE_ATTRIBUTE_COUNT,

    SUM(CASE 
        WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count') 
             AND matched_result.DATA_DOMAIN IS NOT NULL 
             AND pr.ATTRIBUTE_NAME LIKE '%_matched_count'
        THEN pr.ATTRIBUTE_VALUE 
    END) AS TARGET_ATTRIBUTE_COUNT

FROM <DATABASE_NAME>.<SCHEMA>.pydpc_record_results pr
LEFT JOIN <DATABASE_NAME>.<SCHEMA>.pydpc_record_results matched_result
    ON matched_result.ATTRIBUTE_NAME = 'target_total_count'
    AND matched_result.ATTRIBUTE_VALUE > 0
    AND matched_result.DATA_DOMAIN = pr.DATA_DOMAIN
    AND matched_result.RULE_NAME = pr.RULE_NAME
    AND matched_result.TABLE_NAME = pr.TABLE_NAME
    AND matched_result.JOIN_KEY_VALUES = pr.JOIN_KEY_VALUES
    AND matched_result.BOOKMARK_COLUMN_VALUE = pr.BOOKMARK_COLUMN_VALUE
    AND COALESCE(CAST(matched_result.metric_dim_values AS STRING), '') = COALESCE(CAST(pr.metric_dim_values AS STRING), '')

WHERE pr.EXECUTION_ID = <EXECUTION_ID>

GROUP BY 
    pr.EXECUTION_ID,
    pr.UNIQUE_RULE_IDENTIFIER,
    pr.DATA_DOMAIN,
    pr.RULE_NAME,
    pr.TABLE_NAME,
    CAST(pr.LAST_MODIFIED_TS AS DATE),
    pr.BOOKMARK_COLUMN_NAME,
    pr.BOOKMARK_COLUMN_VALUE,
    CASE 
        WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
            AND pr.metric_dim_values IS NOT NULL
        THEN element_at(map_keys(from_json(COALESCE(pr.metric_dim_values, '{}'), 'MAP<STRING, STRING>')), 1)
        WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
            AND pr.metric_dim_values IS NULL THEN NULL
        WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count', 'target_total_count', 'row_matched_count') 
        THEN regexp_replace(regexp_replace(pr.ATTRIBUTE_NAME, '_total_count', ''), '_matched_count', '')
    END,
    pr.comments;
