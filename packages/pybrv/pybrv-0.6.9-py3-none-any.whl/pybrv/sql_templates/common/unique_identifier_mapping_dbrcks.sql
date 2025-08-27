MERGE INTO <DATABASE_NAME>.<SCHEMA>.PYBRV_unique_rule_mapping AS target
USING (
  SELECT 
    <UNIQUE_RULE_IDENTIFIER> AS unique_rule_identifier,
    '<TEAM_NAME>' AS team_name,
    '<DATA_DOMAIN>' AS data_domain,
    '<RULE_CATEGORY_NAME>' AS rule_category,
    <RULE_ID> AS rule_id,
    '<RULE_NAME>' AS rule_name,
    current_timestamp() AS last_modified_ts
) AS source
ON target.unique_rule_identifier = source.unique_rule_identifier

WHEN MATCHED THEN UPDATE SET
    target.team_name = source.team_name,
    target.data_domain = source.data_domain,
    target.rule_category = source.rule_category,
    target.rule_id = source.rule_id,
    target.rule_name = source.rule_name,
    target.last_modified_ts = source.last_modified_ts

WHEN NOT MATCHED THEN INSERT (
    unique_rule_identifier,
    team_name,
    data_domain,
    rule_category,
    rule_id,
    rule_name,
    last_modified_ts
) VALUES (
    source.unique_rule_identifier,
    source.team_name,
    source.data_domain,
    source.rule_category,
    source.rule_id,
    source.rule_name,
    source.last_modified_ts
);
