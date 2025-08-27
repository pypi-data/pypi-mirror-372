-- Step 1: Drop the table if it already exists
DROP TABLE IF EXISTS <STAGE_TABLE_NAME>;
DROP TABLE IF EXISTS <STAGE_TABLE_NAME>_mismatch_details;

-- Step 2: Create the table with the result of the query
CREATE TABLE <STAGE_TABLE_NAME> AS
SELECT
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    <EXECUTION_ID> AS execution_id,
    '<RULE_NAME>' AS rule_name,
    '<DATA_DOMAIN>' AS data_domain,
    '<TABLE_NAME>' AS table_name,
    '<BOOKMARK_COLUMN_NAME>' AS bookmark_column_name,
    <BOOKMARK_COLUMN_NAME> AS bookmark_column_value,
    join_key_values::jsonb,  -- PostgreSQL uses JSONB instead of Snowflake's `parse_json`
    metric_dim_values::jsonb,
    lower(attribute_name) AS attribute_name,
    attribute_value::integer as attribute_value,
    '<COMMENTS>' AS comments,
    last_modified_ts
FROM (
    SELECT * FROM (
        SELECT
            <REPEAT> SOURCE.<MANDATORY_COLUMNS>,
            -- Convert key-value pairs into JSONB
            jsonb_build_object(
                <REPEAT> '<JOIN_KEY>', SOURCE.<JOIN_KEY>
            ) AS join_key_values,
            
            jsonb_build_object(
                <REPEAT_COL_CHECK> <POSTGRES_REPEAT_COL_CHECK>'<METRIC_DIM_COL_ONLY>', SOURCE.<METRIC_DIM_COL_ONLY>
            ) AS metric_dim_values,

            COUNT(1)::INTEGER AS source_total_count,
            COUNT(TARGET.<BOOKMARK_COLUMN_NAME>)::INTEGER AS target_total_count,

            -- Row match count
                   SUM(CASE WHEN
                   <REPEAT_COL_CHECK> md5(SOURCE.<COLUMN_TO_CHECK>::text) = md5(TARGET.<COLUMN_TO_CHECK>::text) 
                   <NO_COLUMN_TO_CHECK> AND
                   <REPEAT_COL_CHECK> md5(SOURCE.<METRIC_DIM_COL>::text) = md5(TARGET.<METRIC_DIM_COL>::text) 
                   <NO_METRIC_DIM_COL> AND 
                    AND md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) = md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
                     THEN 1 ELSE 0 END)::INTEGER AS row_matched_count,

            -- Metric dimension match count
                   SUM(CASE WHEN
                   <REPEAT_COL_CHECK> md5(TRIM(SOURCE.<METRIC_DIM_COL>::text)) = md5(TRIM(TARGET.<METRIC_DIM_COL>::text))
                   THEN 1 ELSE 0 END)::INTEGER target_dim_metric_matched_count,

            -- Bookmark column match count
            SUM(CASE 
                WHEN md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) = md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
                THEN 1 ELSE 0 
            END)::INTEGER AS <BOOKMARK_COLUMN_NAME>_matched_count,

            -- Individual column match counts

            <REPEAT> SUM(CASE WHEN md5(TRIM(SOURCE.<COLUMN_TO_CHECK>::text)) = md5(TRIM(TARGET.<COLUMN_TO_CHECK>::text)) THEN 1 ELSE 0 END)::INTEGER AS <COLUMN_TO_CHECK>_matched_count,

            (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AS last_modified_ts

        FROM
            (<SOURCE_SQL>) AS SOURCE
        LEFT JOIN
            (<TARGET_SQL>) AS TARGET
        ON
            <REPEAT> SOURCE.<JOIN_KEY> = TARGET.<JOIN_KEY>
        WHERE SOURCE.<BOOKMARK_COLUMN_NAME> BETWEEN '<BOOKMARK_START_DATE>' AND '<BOOKMARK_END_DATE>'
        GROUP BY <REPEAT> SOURCE.<MANDATORY_COLUMNS>
    ) AS grouped_data
    -- Unpivot data (PostgreSQL does not support UNPIVOT natively, so we use `jsonb_each`)
    CROSS JOIN LATERAL jsonb_each(jsonb_build_object(
        'source_total_count', source_total_count,
        'target_total_count', target_total_count,
        'row_matched_count', row_matched_count,
        <REPEAT> '<COLUMN_TO_CHECK>_matched_count', <COLUMN_TO_CHECK>_matched_count,
        'target_dim_metric_matched_count', target_dim_metric_matched_count,
        '<BOOKMARK_COLUMN_NAME>_matched_count', <BOOKMARK_COLUMN_NAME>_matched_count
    )) AS unpivoted(attribute_name, attribute_value)
) AS final_query;

-- Step 3: Create detailed mismatch table with actual row data
CREATE TABLE <STAGE_TABLE_NAME>_mismatch_details AS
SELECT
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    <EXECUTION_ID> AS execution_id,
    '<RULE_NAME>' AS rule_name,
    '<DATA_DOMAIN>' AS data_domain,
    '<TABLE_NAME>' AS table_name,
    '<BOOKMARK_COLUMN_NAME>' AS bookmark_column_name,
    SOURCE.<BOOKMARK_COLUMN_NAME> AS bookmark_column_value,
    
    -- Join key values for identification
    jsonb_build_object(
        <REPEAT> '<JOIN_KEY>', SOURCE.<JOIN_KEY>
    ) AS join_key_values,
    
    -- Metric dimension values
    jsonb_build_object(
        <REPEAT_COL_CHECK> <POSTGRES_REPEAT_COL_CHECK>'<METRIC_DIM_COL_ONLY>', SOURCE.<METRIC_DIM_COL_ONLY>
    ) AS metric_dim_values,
    
    -- Mismatch type categorization
    CASE 
        WHEN TARGET.<BOOKMARK_COLUMN_NAME> IS NULL THEN 'MISSING_IN_TARGET'
        WHEN NOT (
            <REPEAT_COL_CHECK> md5(SOURCE.<COLUMN_TO_CHECK>::text) = md5(TARGET.<COLUMN_TO_CHECK>::text) 
            <NO_COLUMN_TO_CHECK> AND
            <REPEAT_COL_CHECK> md5(SOURCE.<METRIC_DIM_COL>::text) = md5(TARGET.<METRIC_DIM_COL>::text) 
            <NO_METRIC_DIM_COL> AND 
            AND md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) = md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
        ) THEN 'DATA_MISMATCH'
        ELSE 'MATCHED'
    END AS mismatch_type,
    
    -- Source data values
    jsonb_build_object(
        <REPEAT> '<COLUMN_TO_CHECK>', SOURCE.<COLUMN_TO_CHECK>,
        '<BOOKMARK_COLUMN_NAME>', SOURCE.<BOOKMARK_COLUMN_NAME>
    ) AS source_values,
    
    -- Target data values
    jsonb_build_object(
        <REPEAT> '<COLUMN_TO_CHECK>', TARGET.<COLUMN_TO_CHECK>,
        '<BOOKMARK_COLUMN_NAME>', TARGET.<BOOKMARK_COLUMN_NAME>
    ) AS target_values,

    -- Detailed column-by-column mismatch flags
    jsonb_build_object(
        <REPEAT> '<COLUMN_TO_CHECK>_mismatch', CASE WHEN md5(TRIM(SOURCE.<COLUMN_TO_CHECK>::text)) != md5(TRIM(TARGET.<COLUMN_TO_CHECK>::text)) OR (SOURCE.<COLUMN_TO_CHECK> IS NULL AND TARGET.<COLUMN_TO_CHECK> IS NOT NULL) OR (SOURCE.<COLUMN_TO_CHECK> IS NOT NULL AND TARGET.<COLUMN_TO_CHECK> IS NULL) THEN true ELSE false END,
        
        '<BOOKMARK_COLUMN_NAME>_mismatch',
        CASE WHEN md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) != md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
             OR (SOURCE.<BOOKMARK_COLUMN_NAME> IS NULL AND TARGET.<BOOKMARK_COLUMN_NAME> IS NOT NULL)
             OR (SOURCE.<BOOKMARK_COLUMN_NAME> IS NOT NULL AND TARGET.<BOOKMARK_COLUMN_NAME> IS NULL)
             THEN true ELSE false END
    ) AS column_mismatch_flags,
    

    
    -- Concatenated list of mismatched columns for easy reading
    CASE 
        WHEN TARGET.<BOOKMARK_COLUMN_NAME> IS NULL THEN 'Row missing in target'
        ELSE 
            TRIM(BOTH ',' FROM 
                CONCAT(
                    <REPEAT> CASE WHEN md5(TRIM(SOURCE.<COLUMN_TO_CHECK>::text)) != md5(TRIM(TARGET.<COLUMN_TO_CHECK>::text)) OR (SOURCE.<COLUMN_TO_CHECK> IS NULL AND TARGET.<COLUMN_TO_CHECK> IS NOT NULL) OR (SOURCE.<COLUMN_TO_CHECK> IS NOT NULL AND TARGET.<COLUMN_TO_CHECK> IS NULL) THEN '<COLUMN_TO_CHECK>,' ELSE '' END,
                    
                    CASE WHEN md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) != md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
                              OR (SOURCE.<BOOKMARK_COLUMN_NAME> IS NULL AND TARGET.<BOOKMARK_COLUMN_NAME> IS NOT NULL)
                              OR (SOURCE.<BOOKMARK_COLUMN_NAME> IS NOT NULL AND TARGET.<BOOKMARK_COLUMN_NAME> IS NULL)
                         THEN '<BOOKMARK_COLUMN_NAME>,' ELSE '' END
                )
            )
    END AS mismatched_columns,
    
    '<COMMENTS>' AS comments,
    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AS last_modified_ts

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
        TARGET.<BOOKMARK_COLUMN_NAME> IS NULL  -- Missing in target
        OR NOT (
            <REPEAT_COL_CHECK> md5(SOURCE.<COLUMN_TO_CHECK>::text) = md5(TARGET.<COLUMN_TO_CHECK>::text) 
            <NO_COLUMN_TO_CHECK> AND
            <REPEAT_COL_CHECK> md5(SOURCE.<METRIC_DIM_COL>::text) = md5(TARGET.<METRIC_DIM_COL>::text) 
            <NO_METRIC_DIM_COL> AND 
            AND md5(TRIM(SOURCE.<BOOKMARK_COLUMN_NAME>::TEXT)) = md5(TRIM(TARGET.<BOOKMARK_COLUMN_NAME>::TEXT))
        ) -- Data mismatch
    );






-- Step 5: Your existing delete and insert logic for statistics
DELETE FROM <SCHEMA>.pybrv_data_parity_result
WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
AND (
    bookmark_column_value IN (SELECT bookmark_column_value FROM <STAGE_TABLE_NAME> GROUP BY bookmark_column_value)
    OR bookmark_column_name = 'TEMP_COL_FOR_BOOKMARK'
);



-- Step 2: Insert new data from stage table
INSERT INTO <SCHEMA>.pybrv_data_parity_result (
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
    join_key_values::jsonb,  
    metric_dim_values::jsonb,
    attribute_name,
    attribute_value,
    comments,
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' AS last_modified_ts 
FROM <STAGE_TABLE_NAME>;


-- Step 6: Insert detailed mismatch data into a new table
-- Delete existing mismatch details for this execution
DELETE FROM <SCHEMA>.pybrv_data_parity_mismatch_details
WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
AND execution_id = <EXECUTION_ID>;


-- Insert new mismatch details
INSERT INTO <SCHEMA>.pybrv_data_parity_mismatch_details
SELECT * FROM <STAGE_TABLE_NAME>_mismatch_details;




INSERT INTO <SCHEMA>.sgp_test_result (
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
    '<DATA_DOMAIN>',
    '<TEAM_NAME>',
    '<INVENTORY>',
    'Validation Framework - Data Parity',
    'Data Parity',
    CONCAT('<RULE_NAME>', '_', FIELD_NAME),
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC', 
    '',
    '',
    CASE WHEN ATTRIBUTES_MATCHED_PERC >= <THRESHOLD> THEN 1 ELSE 0 END AS status,
    CASE 
        WHEN ATTRIBUTES_MATCHED_PERC < <THRESHOLD> 
        THEN CONCAT(ATTRIBUTES_MATCHED_PERC::TEXT, '% attributes matched (Threshold: ', <THRESHOLD>, '). ')
        ELSE '' 
    END AS remarks,
    '<BOOKMARK_COLUMN_NAME>',
    '<BOOKMARK_START_DATE>'::DATE,
    '<BOOKMARK_END_DATE>'::DATE,
    '',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
    '<POS>'
FROM (
    select *,
    COALESCE(ROUND(target_attribute_count * 100.0 / NULLIF(target_total_records, 0), 2), 0.00) AS attributes_matched_perc
    FROM (
    SELECT 
        UPPER(result.data_domain) AS data_domain,
        UPPER(result.rule_name) AS rule_name,
        UPPER(result.table_name) AS table_name,
        LOWER(result.field_name) AS field_name,
        SUM(result.source_records) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name)  AS source_total_records,
        SUM(result.target_records) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name)  AS target_total_records,
        SUM(result.target_rows_matched) OVER (PARTITION BY result.data_domain, result.rule_name, result.table_name)  AS target_total_rows_matched,
        COALESCE(target_attr_count, 0) AS target_attribute_count,
        result.comments
    FROM (
        SELECT 
            pr.data_domain, 
            pr.rule_name, 
            pr.table_name,
            CASE 
                WHEN pr.attribute_name IN ('target_dim_metric_matched_count', 'target_dim_metric_total_count')
                THEN ( SELECT REPLACE(REPLACE(REPLACE(key, '"', ''), '[', ''), ']', '') FROM jsonb_each_text(pr.metric_dim_values) LIMIT 1 )
                WHEN pr.attribute_name NOT IN ('source_total_count', 'target_total_count', 'row_matched_count')
                THEN REPLACE(REPLACE(pr.attribute_name, '_total_count', ''), '_matched_count', '') 
            END AS field_name,
            SUM(CASE WHEN pr.attribute_name = 'source_total_count' THEN pr.attribute_value END) AS source_records,
            SUM(CASE WHEN pr.attribute_name = 'target_total_count' THEN pr.attribute_value END) AS target_records,
            SUM(CASE WHEN pr.attribute_name = 'row_matched_count' THEN pr.attribute_value END) AS target_rows_matched,
            SUM(CASE 
                WHEN pr.attribute_name NOT IN ('source_total_count', 'target_total_count', 'row_matched_count') 
                AND matched_result.data_domain IS NOT NULL
                AND pr.attribute_name LIKE '%_matched_count' 
                THEN pr.attribute_value 
            END) AS target_attr_count,
            pr.comments
        FROM <SCHEMA>.pybrv_data_parity_result pr
        LEFT JOIN <SCHEMA>.pybrv_data_parity_result matched_result 
            ON matched_result.attribute_name = 'target_total_count'
            AND matched_result.attribute_value > 0
            AND matched_result.execution_id = <EXECUTION_ID>
            AND matched_result.unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
            AND matched_result.data_domain = pr.data_domain
            AND matched_result.rule_name = pr.rule_name
            AND matched_result.table_name = pr.table_name
            AND matched_result.join_key_values = pr.join_key_values
            AND matched_result.bookmark_column_value = pr.bookmark_column_value
            AND COALESCE(matched_result.metric_dim_values::TEXT, '') = COALESCE(pr.metric_dim_values::TEXT, '')
        WHERE pr.execution_id = <EXECUTION_ID> 
        AND pr.unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
        AND 1 = <CUST_EXP_TESTING>
        GROUP BY 1,2,3,4,9
        ) result
    ) perc
) AS final_result
WHERE field_name IS NOT NULL
AND UPPER(field_name) <> 'TEMP_COL_FOR_BOOKMARK'


UNION ALL

SELECT 
    '<DATA_DOMAIN>',
    '<TEAM_NAME>',
    '<INVENTORY>',
    'Validation Framework - Data Parity',
    'Data Parity',
    CONCAT('<RULE_NAME>', '_', 'primary_key_match'),
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
    '',
    '',
    CASE WHEN keys_matched_perc >= <RECORD_THRESHOLD> THEN 1 ELSE 0 END AS status,
    CASE 
        WHEN keys_matched_perc < <RECORD_THRESHOLD> 
        THEN CONCAT(keys_matched_perc::TEXT, '% primary keys found in target (Threshold: ', <RECORD_THRESHOLD>, ').')
        ELSE '' 
    END AS remarks,
    '<BOOKMARK_COLUMN_NAME>',
    '<BOOKMARK_START_DATE>',
    '<BOOKMARK_END_DATE>',
    '',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
    '<POS>'
FROM (
    SELECT 
    source_total_records, 
    target_total_records,
    ROUND(target_total_records * 100.0 / NULLIF(source_total_records, 0), 2) AS keys_matched_perc
    FROM (
    SELECT
        SUM(CASE WHEN attribute_name = 'source_total_count' THEN attribute_value ELSE 0 END) AS source_total_records,
        SUM(CASE WHEN attribute_name = 'target_total_count' THEN attribute_value ELSE 0 END) AS target_total_records
    FROM <SCHEMA>.pybrv_data_parity_result
    WHERE unique_rule_identifier = <UNIQUE_RULE_IDENTIFIER>
    AND execution_id = <EXECUTION_ID>
    ) AS counts
) AS primary_key_result;



<SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE>;

-- Clean up temporary tables
DROP TABLE IF EXISTS <STAGE_TABLE_NAME>;
DROP TABLE IF EXISTS <STAGE_TABLE_NAME>_mismatch_details;


