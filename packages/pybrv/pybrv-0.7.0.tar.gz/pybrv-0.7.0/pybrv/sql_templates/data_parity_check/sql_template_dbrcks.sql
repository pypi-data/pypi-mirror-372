-- Step 1: Drop the table if it already exists
DROP TABLE IF EXISTS <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>;
DROP TABLE IF EXISTS <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>_mismatch_details;


-- Step 2: Create the table with the result of the query
CREATE TABLE <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME> AS
SELECT
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    <EXECUTION_ID> AS execution_id,
    '<RULE_NAME>' AS rule_name,
    '<DATA_DOMAIN>' AS data_domain,
    '<TABLE_NAME>' AS table_name,
    '<BOOKMARK_COLUMN_NAME>' AS bookmark_column_name,
    <BOOKMARK_COLUMN_NAME> AS bookmark_column_value,
    to_json(join_key_values) AS join_key_values,
    to_json(metric_dim_values) AS metric_dim_values,
    lower(attribute_name) AS attribute_name,
    cast(attribute_value AS integer) as attribute_value,
    '<COMMENTS>' AS comments,
    last_modified_ts
FROM (
    SELECT * FROM (
        SELECT
            <REPEAT> SOURCE.<MANDATORY_COLUMNS>,
            -- Convert key-value pairs into JSON
            map(
                <REPEAT> '<JOIN_KEY>', SOURCE.<JOIN_KEY>
            ) AS join_key_values,
            
            map(
                <REPEAT_COL_CHECK> <DATABRICKS_REPEAT_COL_CHECK>'<METRIC_DIM_COL_ONLY>', coalesce(cast(SOURCE.<METRIC_DIM_COL_ONLY> as string),'NA')
            ) AS metric_dim_values,

            COUNT(1) AS source_total_count,
            COUNT(TARGET.<BOOKMARK_COLUMN_NAME>) AS target_total_count,

            -- Row match count
            SUM(CASE WHEN
                <REPEAT_COL_CHECK> md5(coalesce(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING), '')) = md5(coalesce(cast(TARGET.<COLUMN_TO_CHECK> AS STRING), ''))
                <NO_COLUMN_TO_CHECK> AND
                <REPEAT_COL_CHECK> md5(cast(SOURCE.<METRIC_DIM_COL> AS STRING)) = md5(cast(TARGET.<METRIC_DIM_COL> AS STRING)) 
                <NO_METRIC_DIM_COL> AND 
                AND md5(trim(cast(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) = md5(trim(cast(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                THEN 1 ELSE 0 END) AS row_matched_count,

            -- Metric dimension match count
            SUM(CASE WHEN
                <REPEAT_COL_CHECK> md5(trim(cast(SOURCE.<METRIC_DIM_COL> AS STRING))) = md5(trim(cast(TARGET.<METRIC_DIM_COL> AS STRING)))
                THEN 1 ELSE 0 END) AS target_dim_metric_matched_count,

            -- Bookmark column match count
            SUM(CASE 
                WHEN md5(trim(cast(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) = md5(trim(cast(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                THEN 1 ELSE 0 
            END) AS <BOOKMARK_COLUMN_NAME>_matched_count,

            -- Individual column match counts
            <REPEAT> SUM(CASE WHEN md5(coalesce(trim(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING)), '')) = md5(coalesce(trim(cast(TARGET.<COLUMN_TO_CHECK> AS STRING)), '')) THEN 1 ELSE 0 END) AS <COLUMN_TO_CHECK>_matched_count,

            current_timestamp() AS last_modified_ts

        FROM
            (<SOURCE_SQL>) AS SOURCE
        LEFT JOIN
            (<TARGET_SQL>) AS TARGET
        ON
            <REPEAT> SOURCE.<JOIN_KEY> = TARGET.<JOIN_KEY>
        WHERE SOURCE.<BOOKMARK_COLUMN_NAME> BETWEEN '<BOOKMARK_START_DATE>' AND '<BOOKMARK_END_DATE>'
        GROUP BY <REPEAT> SOURCE.<MANDATORY_COLUMNS>
    ) AS grouped_data
    -- Unpivot data in Databricks
    LATERAL VIEW explode(map(
        'source_total_count', source_total_count,
        'target_total_count', target_total_count,
        'row_matched_count', row_matched_count,
        <REPEAT> '<COLUMN_TO_CHECK>_matched_count', <COLUMN_TO_CHECK>_matched_count,
        'target_dim_metric_matched_count', target_dim_metric_matched_count,
        '<BOOKMARK_COLUMN_NAME>_matched_count', <BOOKMARK_COLUMN_NAME>_matched_count
    )) unpivoted as attribute_name, attribute_value
) AS final_query;



-- Step 3: Create detailed mismatch table with actual row data
CREATE TABLE <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>_mismatch_details AS
SELECT
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    <EXECUTION_ID> AS execution_id,
    '<RULE_NAME>' AS rule_name,
    '<DATA_DOMAIN>' AS data_domain,
    '<TABLE_NAME>' AS table_name,
    '<BOOKMARK_COLUMN_NAME>' AS bookmark_column_name,
    <BOOKMARK_COLUMN_NAME> AS bookmark_column_value,
    join_key_values,
    metric_dim_values,
    mismatch_type,
    source_values,
    target_values,
    column_mismatch_flags,
    mismatched_columns,
    '<COMMENTS>' AS comments,
    current_timestamp() AS last_modified_ts
FROM (
    SELECT * FROM (
        SELECT
            <REPEAT> SOURCE.<MANDATORY_COLUMNS>,
            
            -- Convert key-value pairs into JSON
            map(
                <REPEAT> '<JOIN_KEY>', SOURCE.<JOIN_KEY>
            ) AS join_key_values,
        
            -- Metric dimension values
            map(
                <REPEAT_COL_CHECK> <DATABRICKS_REPEAT_COL_CHECK> '<METRIC_DIM_COL_ONLY>', COALESCE(CAST(SOURCE.<METRIC_DIM_COL_ONLY> AS STRING), 'NA')
            ) AS metric_dim_values,

            -- Mismatch type categorization
            CASE 
                WHEN TARGET.<BOOKMARK_COLUMN_NAME> IS NULL THEN 'MISSING_IN_TARGET'
                WHEN NOT (
                    <REPEAT_COL_CHECK> md5(coalesce(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING), '')) = md5(coalesce(cast(TARGET.<COLUMN_TO_CHECK> AS STRING), ''))
                    <NO_COLUMN_TO_CHECK> AND
                    <REPEAT_COL_CHECK> md5(CAST(SOURCE.<METRIC_DIM_COL> AS STRING)) = md5(CAST(TARGET.<METRIC_DIM_COL> AS STRING))
                    <NO_METRIC_DIM_COL> AND
                    AND md5(TRIM(CAST(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) = md5(TRIM(CAST(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                ) THEN 'DATA_MISMATCH'
                ELSE 'MATCHED'
            END AS mismatch_type,

            -- Source data values
            map(
                <REPEAT> '<COLUMN_TO_CHECK>', CAST(SOURCE.<COLUMN_TO_CHECK> AS STRING),
                '<BOOKMARK_COLUMN_NAME>', CAST(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING)
            ) AS source_values,

            -- Target data values
            map(
                <REPEAT> '<COLUMN_TO_CHECK>', CAST(TARGET.<COLUMN_TO_CHECK> AS STRING),
                '<BOOKMARK_COLUMN_NAME>', CAST(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)
            ) AS target_values,

            -- Detailed column-by-column mismatch flags
            map( 
                <REPEAT> '<COLUMN_TO_CHECK>_mismatch', CASE WHEN md5(coalesce(trim(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING)), '')) != md5(coalesce(trim(cast(TARGET.<COLUMN_TO_CHECK> AS STRING)), '')) OR SOURCE.<COLUMN_TO_CHECK> IS DISTINCT FROM TARGET.<COLUMN_TO_CHECK> THEN true ELSE false END,

                '<BOOKMARK_COLUMN_NAME>_mismatch',
                CASE 
                    WHEN md5(TRIM(CAST(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) != md5(TRIM(CAST(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                        OR SOURCE.<BOOKMARK_COLUMN_NAME> IS DISTINCT FROM TARGET.<BOOKMARK_COLUMN_NAME>
                    THEN true ELSE false 
                END
            ) AS column_mismatch_flags,

            -- Concatenated list of mismatched columns for easy reading
            CASE 
                WHEN TARGET.<BOOKMARK_COLUMN_NAME> IS NULL THEN 'Row missing in target'
                ELSE trim(BOTH ',' FROM concat(
                    <REPEAT> CASE WHEN md5(coalesce(trim(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING)), '')) != md5(coalesce(trim(cast(TARGET.<COLUMN_TO_CHECK> AS STRING)), '')) OR SOURCE.<COLUMN_TO_CHECK> IS DISTINCT FROM TARGET.<COLUMN_TO_CHECK> THEN '<COLUMN_TO_CHECK>,' ELSE '' END,
                    CASE 
                        WHEN md5(TRIM(CAST(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) != md5(TRIM(CAST(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                             OR SOURCE.<BOOKMARK_COLUMN_NAME> IS DISTINCT FROM TARGET.<BOOKMARK_COLUMN_NAME>
                        THEN '<BOOKMARK_COLUMN_NAME>,' ELSE '' 
                    END
                ))
            END AS mismatched_columns

        FROM
            (<SOURCE_SQL>) AS SOURCE
        LEFT JOIN
            (<TARGET_SQL>) AS TARGET
        ON
            <REPEAT> SOURCE.<JOIN_KEY> = TARGET.<JOIN_KEY>
        WHERE 
            SOURCE.<BOOKMARK_COLUMN_NAME> BETWEEN '<BOOKMARK_START_DATE>' AND '<BOOKMARK_END_DATE>'
            AND (
                -- Only include rows that have mismatches or are missing in target
                TARGET.<BOOKMARK_COLUMN_NAME> IS NULL
                OR NOT (
                    <REPEAT_COL_CHECK> md5(coalesce(cast(SOURCE.<COLUMN_TO_CHECK> AS STRING), '')) = md5(coalesce(cast(TARGET.<COLUMN_TO_CHECK> AS STRING), ''))
                    <NO_COLUMN_TO_CHECK> AND
                    <REPEAT_COL_CHECK> md5(CAST(SOURCE.<METRIC_DIM_COL> AS STRING)) = md5(CAST(TARGET.<METRIC_DIM_COL> AS STRING))
                    <NO_METRIC_DIM_COL> AND
                    AND md5(TRIM(CAST(SOURCE.<BOOKMARK_COLUMN_NAME> AS STRING))) = md5(TRIM(CAST(TARGET.<BOOKMARK_COLUMN_NAME> AS STRING)))
                )
            )
    ) final_rows
);







-- Step 5: Your existing delete and insert logic for statistics
DELETE FROM <DATABASE_NAME>.<SCHEMA>.pydpc_record_results
WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
AND (
    bookmark_column_value IN (SELECT bookmark_column_value FROM <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME> GROUP BY bookmark_column_value)
    OR bookmark_column_name = 'TEMP_COL_FOR_BOOKMARK'
);




-- Step 2: Insert new data from stage table
INSERT INTO <DATABASE_NAME>.<SCHEMA>.pydpc_record_results (
    unique_rule_identifier,
    execution_id,
    rule_name,
    data_domain,
    table_name,
    bookmark_column_name,
    bookmark_column_value,
    join_key_values,
    metric_dim_values,
    attribute_name,
    attribute_value,
    comments,
    last_modified_ts
)
SELECT 
    unique_rule_identifier,
    execution_id,
    rule_name,
    data_domain,
    table_name,
    bookmark_column_name,
    bookmark_column_value,
    join_key_values,  
    metric_dim_values,
    attribute_name,
    attribute_value,
    comments,
    current_timestamp() AS last_modified_ts 
FROM <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>;


-- Step 6: Insert detailed mismatch data into a new table
-- Delete existing mismatch details for this execution
DELETE FROM <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_mismatch_details
WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
AND execution_id = <EXECUTION_ID>;

INSERT INTO <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_mismatch_details
SELECT * FROM <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>_mismatch_details;





INSERT INTO <DATABASE_NAME>.<SCHEMA>.pydpc_attribute_result (
    execution_id,
    unique_rule_identifier,
    data_domain,
    team_name,
    inventory,
    tool_name,
    test_case_type,
    test_name,
    execution_datetime,
    gpid,
    test_execution_link,
    status,
    remarks,
    bookmark_column_name,
    bookmark_start_date,
    bookmark_end_date,
    metadata,
    last_modified_ts,
    pos
)
SELECT 
    <EXECUTION_ID>,
    <UNIQUE_RULE_IDENTIFIER>,
    '<DATA_DOMAIN>',
    '<TEAM_NAME>',
    '<INVENTORY>',
    'Validation Framework - Data Parity',
    'Data Parity',
    concat('<RULE_NAME>', '_', FIELD_NAME),
    current_timestamp(), 
    '',
    '',
    CASE WHEN ATTRIBUTES_MATCHED_PERC >= <THRESHOLD> THEN 1 ELSE 0 END AS status,
    CASE 
        WHEN ATTRIBUTES_MATCHED_PERC < <THRESHOLD> 
        THEN concat(cast(ATTRIBUTES_MATCHED_PERC as string), '% attributes matched (Threshold: ', cast(<THRESHOLD> as string), '). ')
        ELSE '' 
    END AS remarks,
    '<BOOKMARK_COLUMN_NAME>',
    cast('<BOOKMARK_START_DATE>' as date),
    cast('<BOOKMARK_END_DATE>' as date),
    '',
    current_timestamp(),
    '<POS>'
FROM (
    select *,
    coalesce(round(target_attribute_count * 100.0 / nullif(target_total_records, 0), 2), 0.00) AS attributes_matched_perc
    FROM (
    SELECT 
        upper(result.data_domain) AS data_domain,
        upper(result.rule_name) AS rule_name,
        upper(result.table_name) AS table_name,
        lower(result.field_name) AS field_name,
        sum(result.source_records) over (partition by result.data_domain, result.rule_name, result.table_name) AS source_total_records,
        sum(result.target_records) over (partition by result.data_domain, result.rule_name, result.table_name) AS target_total_records,
        sum(result.target_rows_matched) over (partition by result.data_domain, result.rule_name, result.table_name) AS target_total_rows_matched,
        coalesce(target_attr_count, 0) AS target_attribute_count,
        result.comments
    FROM (
        SELECT 
            pr.data_domain, 
            pr.rule_name, 
            pr.table_name,
            CASE 
                WHEN pr.attribute_name IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
                THEN map_keys(from_json(pr.metric_dim_values, 'MAP<STRING, STRING>'))[0]
                WHEN pr.attribute_name NOT IN ('source_total_count', 'target_total_count', 'row_matched_count')
                THEN replace(replace(pr.attribute_name, '_total_count', ''), '_matched_count', '') 
            END AS field_name,
            sum(CASE WHEN pr.attribute_name = 'source_total_count' THEN pr.attribute_value END) AS source_records,
            sum(CASE WHEN pr.attribute_name = 'target_total_count' THEN pr.attribute_value END) AS target_records,
            sum(CASE WHEN pr.attribute_name = 'row_matched_count' THEN pr.attribute_value END) AS target_rows_matched,
            sum(CASE 
                WHEN pr.attribute_name NOT IN ('source_total_count', 'target_total_count', 'row_matched_count') 
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
            AND coalesce(cast(matched_result.metric_dim_values as string), '') = coalesce(cast(pr.metric_dim_values as string), '')
        WHERE pr.execution_id = <EXECUTION_ID> 
        AND pr.unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
        AND 1 = <CUST_EXP_TESTING>
        GROUP BY 1,2,3,4,9
        ) result
    ) perc
) AS final_result
WHERE field_name IS NOT NULL
AND upper(field_name) <> 'TEMP_COL_FOR_BOOKMARK'

UNION ALL

SELECT 
    '<EXECUTION_ID>',
    '<UNIQUE_RULE_IDENTIFIER>',
    '<DATA_DOMAIN>',
    '<TEAM_NAME>',
    '<INVENTORY>',
    'Validation Framework - Data Parity',
    'Data Parity',
    concat('<RULE_NAME>', '_', 'primary_key_match'),
    current_timestamp(),
    '',
    '',
    CASE WHEN keys_matched_perc >= <RECORD_THRESHOLD> THEN 1 ELSE 0 END AS status,
    CASE 
        WHEN keys_matched_perc < <RECORD_THRESHOLD> 
        THEN concat(cast(keys_matched_perc as string), '% primary keys found in target (Threshold: ', cast(<RECORD_THRESHOLD> as string), ').')
        ELSE '' 
    END AS remarks,
    '<BOOKMARK_COLUMN_NAME>',
    '<BOOKMARK_START_DATE>',
    '<BOOKMARK_END_DATE>',
    '',
    current_timestamp(),
    '<POS>'
FROM (
    SELECT 
    source_total_records, 
    target_total_records,
    round(target_total_records * 100.0 / nullif(source_total_records, 0), 2) AS keys_matched_perc
    FROM (
    SELECT
        sum(CASE WHEN attribute_name = 'source_total_count' THEN attribute_value ELSE 0 END) AS source_total_records,
        sum(CASE WHEN attribute_name = 'target_total_count' THEN attribute_value ELSE 0 END) AS target_total_records
    FROM <DATABASE_NAME>.<SCHEMA>.pydpc_record_results
    WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
    AND execution_id = <EXECUTION_ID>
    ) AS counts
) AS primary_key_result;


<SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE>;

-- Clean up temporary tables
DROP TABLE IF EXISTS <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>;
DROP TABLE IF EXISTS <DATABASE_NAME>.<SCHEMA>.<STAGE_TABLE_NAME>_mismatch_details;


