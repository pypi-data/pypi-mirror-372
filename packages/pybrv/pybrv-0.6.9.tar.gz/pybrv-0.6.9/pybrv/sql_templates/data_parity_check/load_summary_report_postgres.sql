INSERT INTO <SCHEMA>.data_parity_summary (
    start_date,
    end_date,
    data_domain,
    rule_name,
    table_name,
    source_records,
    target_found,
    percent_records_found,
    target_rows_matched,
    percent_rows_matched,
    attributes_checked,
    attributes_matched,
    comments,
    execution_id,  
    unique_rule_identifier
)
SELECT
    '<BOOKMARK_START_DATE>'::VARCHAR AS "START DATE",
    '<BOOKMARK_END_DATE>'::VARCHAR AS "END DATE",
    DATA_DOMAIN AS "DATA DOMAIN", 
    RULE_NAME AS "RULE NAME",
    TABLE_NAME AS "TABLE NAME",
    TO_CHAR(SOURCE_TOTAL_RECORDS, 'FM999,999,999') AS "SOURCE: # RECORDS",  
    TO_CHAR(TARGET_TOTAL_RECORDS, 'FM999,999,999') AS "TARGET: # FOUND", 
    ROUND(TARGET_TOTAL_RECORDS * 100.0 / NULLIF(SOURCE_TOTAL_RECORDS, 0), 2)::VARCHAR || '%' AS "% RECORDS FOUND",
    TO_CHAR(TARGET_TOTAL_ROWS_MATCHED, 'FM999,999,999') AS "TARGET: # ROWS MATCHED", 
    ROUND(TARGET_TOTAL_ROWS_MATCHED * 100.0 / NULLIF(SOURCE_TOTAL_RECORDS, 0), 2)::VARCHAR || '%' AS "% ROWS MATCHED",
    TO_CHAR(COUNT(DISTINCT FIELD_NAME), 'FM999,999,999') AS "# ATTRIBUTES CHECKED",  
    TO_CHAR(COUNT(DISTINCT CASE WHEN ATTRIBUTES_MATCHED_PERC >= <THRESHOLD> THEN FIELD_NAME END), 'FM999,999,999') AS "ATTRIBUTES MATCHED (%>=<THRESHOLD>)",
    COMMENTS AS "COMMENTS",
    '<EXECUTION_ID>' AS "execution_id", 
    '<UNIQUE_RULE_IDENTIFIER>' AS "unique_rule_identifier"
FROM (
       SELECT *,
	COALESCE(ROUND(TARGET_ATTRIBUTE_COUNT * 100.0 / NULLIF(TARGET_TOTAL_RECORDS, 0), 2), 0.00) AS ATTRIBUTES_MATCHED_PERC
	from (
              SELECT 
              UPPER(result.DATA_DOMAIN) AS DATA_DOMAIN,
              UPPER(result.RULE_NAME) AS RULE_NAME,
              UPPER(result.TABLE_NAME) AS TABLE_NAME,
              result.FIELD_NAME,
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
        AND UPPER(pr.ATTRIBUTE_NAME) <> 'TEMP_COL_FOR_BOOKMARK_MATCHED_COUNT'
        GROUP BY 1,2,3,4,9
           ) result
       ) report_perc
) 
GROUP BY 1,2,3,4,5,6,7,8,9,10,13;
