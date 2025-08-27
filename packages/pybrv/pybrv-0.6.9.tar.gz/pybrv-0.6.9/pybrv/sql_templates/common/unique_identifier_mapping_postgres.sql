INSERT INTO <SCHEMA>.pybrv_unique_rule_mapping (
    unique_rule_identifier,
    team_name,
    data_domain,
    rule_category,
    rule_id,
    rule_name,
    last_modified_ts
)
VALUES (
    <UNIQUE_RULE_IDENTIFIER>,
    '<TEAM_NAME>',
    '<DATA_DOMAIN>',
    '<RULE_CATEGORY_NAME>',
    <RULE_ID>,
    '<RULE_NAME>',
    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')  -- Convert to UTC in PostgreSQL
)
ON CONFLICT (unique_rule_identifier)  -- Match on unique identifier
DO UPDATE SET
    team_name = EXCLUDED.team_name,
    data_domain = EXCLUDED.data_domain,
    rule_category = EXCLUDED.rule_category,
    rule_id = EXCLUDED.rule_id,
    rule_name = EXCLUDED.rule_name,
    last_modified_ts = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC');

