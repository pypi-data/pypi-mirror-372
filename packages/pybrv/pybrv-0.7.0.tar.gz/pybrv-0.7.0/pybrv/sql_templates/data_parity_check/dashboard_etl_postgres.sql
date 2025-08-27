DELETE FROM <SCHEMA>.SGP_DATA_PARITY_STATS WHERE UNIQUE_RULE_IDENTIFIER = <UNIQUE_RULE_IDENTIFIER>;

INSERT INTO <SCHEMA>.SGP_DATA_PARITY_STATS
SELECT pr.UNIQUE_RULE_IDENTIFIER,
pr.DATA_DOMAIN,
pr.RULE_NAME,
pr.TABLE_NAME,
pr.LAST_MODIFIED_TS::DATE AS execution_date ,
pr.BOOKMARK_COLUMN_NAME as key_date_column,
pr.BOOKMARK_COLUMN_VALUE as key_date_value,
CASE WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count','target_dim_metric_total_count')
     THEN (SELECT REPLACE(REPLACE(REPLACE(jsonb_object_keys(pr.METRIC_DIM_VALUES)::TEXT, '"', ''), '[', ''), ']', '') LIMIT 1 )
     WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count')
     THEN REPLACE(REPLACE(pr.ATTRIBUTE_NAME,'_total_count',''),'_matched_count','') END AS FIELD_NAME,
pr.comments as comments ,
SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'source_total_count' THEN pr.ATTRIBUTE_VALUE END) AS SOURCE_RECORDS,
SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'target_total_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_RECORDS,
SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'row_matched_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_ROWS_MATCHED,
SUM(CASE WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count') AND matched_result.DATA_DOMAIN IS NOT NULL AND pr.ATTRIBUTE_NAME LIKE '%_total_count' THEN pr.ATTRIBUTE_VALUE END) AS SOURCE_ATTRIBUTE_COUNT,
SUM(CASE WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count') AND matched_result.DATA_DOMAIN IS NOT NULL AND pr.ATTRIBUTE_NAME LIKE '%_matched_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_ATTRIBUTE_COUNT
FROM <SCHEMA>.pybrv_DATA_PARITY_RESULT pr
LEFT JOIN <SCHEMA>.pybrv_DATA_PARITY_RESULT matched_result ON
                matched_result.ATTRIBUTE_NAME = 'target_total_count'
                AND matched_result.ATTRIBUTE_VALUE > 0
                AND matched_result.DATA_DOMAIN = pr.DATA_DOMAIN
                AND matched_result.RULE_NAME = pr.RULE_NAME
                AND matched_result.TABLE_NAME = pr.TABLE_NAME
                AND matched_result.JOIN_KEY_VALUES = pr.JOIN_KEY_VALUES
                AND matched_result.BOOKMARK_COLUMN_VALUE = pr.BOOKMARK_COLUMN_VALUE
               AND COALESCE(matched_result.metric_dim_values::TEXT, '') = COALESCE(pr.metric_dim_values::TEXT, '')
WHERE pr.UNIQUE_RULE_IDENTIFIER = <UNIQUE_RULE_IDENTIFIER>
GROUP BY 1,2,3,4,5,6,7,8,9;
