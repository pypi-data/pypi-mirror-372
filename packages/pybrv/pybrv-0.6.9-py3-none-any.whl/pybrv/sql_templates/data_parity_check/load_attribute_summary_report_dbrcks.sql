INSERT INTO <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_summary (
    data_domain, 
    rule_name, 
    table_name, 
    field_name,  
    source_total_records, 
    target_total_records, 
    target_attribute_found, 
    attributes_matched_perc, 
    threshold, 
    execution_id, 
    unique_rule_identifier
)
SELECT  
    MIN(data_domain) AS data_domain,
    MIN(rule_name) AS rule_name,
    MIN(table_name) AS table_name,
    CONCAT_WS(', ', COLLECT_LIST(field_name)) AS field_name,
    FORMAT_NUMBER(MIN(source_total_records), '#,###') AS source_total_records,
    FORMAT_NUMBER(MIN(target_total_records_value), '#,###') AS target_total_records,
    FORMAT_NUMBER(MIN(target_attribute_count), '#,###') AS target_attribute_found,
    ANY_VALUE(
        CASE  
            WHEN attributes_matched_perc = 'NA' THEN 'NA'
            ELSE CONCAT(attributes_matched_perc, '%')
        END
    ) AS attributes_matched_perc,
    <THRESHOLD> AS threshold,
    <EXECUTION_ID> AS execution_id,
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier
FROM (
    SELECT 
        data_domain,
        rule_name,
        table_name,
        field_name,
        source_total_records,
        target_total_records_value,
        target_total_rows_matched,
        target_attribute_count,
        comments,
        COALESCE(
            CAST(ROUND(target_attribute_count * 100.0 / NULLIF(target_total_records_value, 0), 2) AS STRING),
            'NA'
        ) AS attributes_matched_perc
    FROM (
        SELECT  
            UPPER(result.data_domain) AS data_domain,
            UPPER(result.rule_name) AS rule_name,
            UPPER(result.table_name) AS table_name,
            LOWER(result.field_name) AS field_name,
            SUM(result.source_records) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name) AS source_total_records,
            SUM(result.target_records) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name) AS target_total_records_value,
            SUM(result.target_rows_matched) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name) AS target_total_rows_matched,
            COALESCE(target_attr_count, 0) AS target_attribute_count,
            result.comments
        FROM (
            SELECT  
                pr.data_domain,  
                pr.rule_name,  
                pr.table_name,
                CASE  
                    WHEN pr.attribute_name IN ('target_dim_metric_matched_count','target_dim_metric_total_count') THEN
                        element_at(map_keys(from_json(pr.metric_dim_values, 'MAP<STRING, STRING>')), 1)
                    WHEN pr.attribute_name NOT IN ('source_total_count','target_total_count','row_matched_count') THEN
                        REGEXP_REPLACE(pr.attribute_name, '_(total|matched)_count$', '')
                END AS field_name,
                SUM(CASE WHEN pr.attribute_name = 'source_total_count' THEN pr.attribute_value END) AS source_records,
                SUM(CASE WHEN pr.attribute_name = 'target_total_count' THEN pr.attribute_value END) AS target_records,
                SUM(CASE WHEN pr.attribute_name = 'row_matched_count' THEN pr.attribute_value END) AS target_rows_matched,
                SUM(CASE  
                    WHEN pr.attribute_name NOT IN ('source_total_count','target_total_count','row_matched_count')  
                         AND matched_result.data_domain IS NOT NULL
                         AND pr.attribute_name LIKE '%_matched_count'  
                    THEN pr.attribute_value  
                END) AS target_attr_count,
                pr.comments
            FROM <DATABASE_NAME>.<SCHEMA>.pydpc_record_results pr
            LEFT JOIN <DATABASE_NAME>.<SCHEMA>.pydpc_record_results matched_result  
                ON matched_result.attribute_name = 'target_total_count'
                AND matched_result.attribute_value > 0
                AND matched_result.execution_id = <EXECUTION_ID>
                AND matched_result.unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
                AND matched_result.data_domain = pr.data_domain
                AND matched_result.rule_name = pr.rule_name
                AND matched_result.table_name = pr.table_name
                AND matched_result.join_key_values = pr.join_key_values
                AND matched_result.bookmark_column_value = pr.bookmark_column_value
                AND COALESCE(CAST(matched_result.metric_dim_values AS STRING), '') = COALESCE(CAST(pr.metric_dim_values AS STRING), '')
            WHERE pr.execution_id = <EXECUTION_ID>
              AND pr.unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
            GROUP BY 1, 2, 3, 4, 9
        ) result
    ) report_perc
) final_summary
WHERE field_name IS NOT NULL
  AND UPPER(field_name) <> 'TEMP_COL_FOR_BOOKMARK'
GROUP BY execution_id, unique_rule_identifier
ORDER BY ROUND(
    COALESCE(MIN(target_attribute_count), 0) * 100.0 /
    NULLIF(COALESCE(MIN(target_total_records_value), 0), 0), 2
) ASC;