SELECT 
    MIN(DATA_DOMAIN) AS "DATA DOMAIN",
    MIN(RULE_NAME) AS "RULE NAME",
    MIN(TABLE_NAME) AS "TABLE NAME",
    STRING_AGG(FIELD_NAME, ', ') AS "FIELD NAME", 
    TO_CHAR(MIN(SOURCE_TOTAL_RECORDS), 'FM999,999,999') AS "SOURCE: # RECORDS",  
    TO_CHAR(MIN(TARGET_TOTAL_RECORDS), 'FM999,999,999') AS "TARGET: # RECORDS",
    TO_CHAR(MIN(TARGET_ATTRIBUTE_COUNT), 'FM999,999,999') AS "TARGET: # ATTRIBUTE FOUND",
    CASE 
        WHEN (ATTRIBUTES_MATCHED_PERC = 'NA') THEN ATTRIBUTES_MATCHED_PERC
        ELSE ATTRIBUTES_MATCHED_PERC || '%'
    END AS "% ATTRIBUTES MATCHED",
    <THRESHOLD> AS "THRESHOLD"
FROM (
       SELECT *, COALESCE(ROUND(TARGET_ATTRIBUTE_COUNT * 100.0 / NULLIF(TARGET_TOTAL_RECORDS, 0), 2)::VARCHAR, 'NA') AS ATTRIBUTES_MATCHED_PERC
       FROM (
              SELECT 
              UPPER(result.DATA_DOMAIN) AS DATA_DOMAIN,
              UPPER(result.RULE_NAME) AS RULE_NAME,
              UPPER(result.TABLE_NAME) AS TABLE_NAME,
              LOWER(result.FIELD_NAME) AS FIELD_NAME,
              SUM(result.SOURCE_RECORDS) OVER (PARTITION BY result.DATA_DOMAIN, result.RULE_NAME, result.TABLE_NAME) AS SOURCE_TOTAL_RECORDS,
              SUM(result.TARGET_RECORDS) OVER (PARTITION BY result.DATA_DOMAIN, result.RULE_NAME, result.TABLE_NAME) AS TARGET_TOTAL_RECORDS,
              SUM(result.TARGET_ROWS_MATCHED) OVER (PARTITION BY result.DATA_DOMAIN, result.RULE_NAME, result.TABLE_NAME) AS TARGET_TOTAL_ROWS_MATCHED,
              COALESCE(TARGET_ATTR_COUNT, 0) AS TARGET_ATTRIBUTE_COUNT,
              result.comments
              FROM (
                     SELECT 
                     pr.DATA_DOMAIN, 
                     pr.RULE_NAME, 
                     pr.TABLE_NAME,
                     CASE 
                            WHEN pr.ATTRIBUTE_NAME IN ('target_dim_metric_matched_count','target_dim_metric_total_count')
                            THEN (SELECT jsonb_object_keys(pr.METRIC_DIM_VALUES) LIMIT 1)  
                            WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count')
                            THEN REPLACE(REPLACE(pr.ATTRIBUTE_NAME, '_total_count', ''), '_matched_count', '') 
                     END AS FIELD_NAME,
                     
                     SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'source_total_count' THEN pr.ATTRIBUTE_VALUE END) AS SOURCE_RECORDS,
                     SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'target_total_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_RECORDS,
                     SUM(CASE WHEN pr.ATTRIBUTE_NAME = 'row_matched_count' THEN pr.ATTRIBUTE_VALUE END) AS TARGET_ROWS_MATCHED,
                     SUM(CASE 
                            WHEN pr.ATTRIBUTE_NAME NOT IN ('source_total_count','target_total_count','row_matched_count') 
                            AND matched_result.DATA_DOMAIN IS NOT NULL
                            AND pr.ATTRIBUTE_NAME LIKE '%_matched_count' 
                            THEN pr.ATTRIBUTE_VALUE 
                     END) AS TARGET_ATTR_COUNT,
                     pr.COMMENTS
                     FROM <SCHEMA>.pybrv_DATA_PARITY_RESULT pr
                     LEFT JOIN <SCHEMA>.pybrv_DATA_PARITY_RESULT matched_result 
                     ON matched_result.ATTRIBUTE_NAME = 'target_total_count'
                     AND matched_result.ATTRIBUTE_VALUE > 0
                     AND matched_result.EXECUTION_ID = <EXECUTION_ID>
                     AND matched_result.UNIQUE_RULE_IDENTIFIER = <UNIQUE_RULE_IDENTIFIER>
                     AND matched_result.DATA_DOMAIN = pr.DATA_DOMAIN
                     AND matched_result.RULE_NAME = pr.RULE_NAME
                     AND matched_result.TABLE_NAME = pr.TABLE_NAME
                     AND matched_result.JOIN_KEY_VALUES = pr.JOIN_KEY_VALUES
                     AND matched_result.BOOKMARK_COLUMN_VALUE = pr.BOOKMARK_COLUMN_VALUE
                     AND COALESCE(matched_result.METRIC_DIM_VALUES::TEXT, '') = COALESCE(pr.METRIC_DIM_VALUES::TEXT, '')

                     WHERE pr.EXECUTION_ID = <EXECUTION_ID>
                     AND pr.UNIQUE_RULE_IDENTIFIER = <UNIQUE_RULE_IDENTIFIER>
                     GROUP BY 1,2,3,4,9
              ) result
       ) report_perc
) 
WHERE FIELD_NAME IS NOT NULL
AND UPPER(FIELD_NAME) <> 'TEMP_COL_FOR_BOOKMARK'
GROUP BY 8,9
ORDER BY ROUND(MIN(TARGET_ATTRIBUTE_COUNT) * 100 / NULLIF(MIN(TARGET_TOTAL_RECORDS),0), 2) ASC;
