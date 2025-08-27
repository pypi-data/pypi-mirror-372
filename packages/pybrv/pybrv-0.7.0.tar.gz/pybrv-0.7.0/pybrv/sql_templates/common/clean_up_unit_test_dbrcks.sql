DELETE FROM <DATABASE_NAME>.<SCHEMA>.pybrv_METADATA
WHERE unique_rule_identifier IN (
 SELECT unique_rule_identifier
 FROM <SCHEMA>.pybrv_UNIQUE_RULE_MAPPING
 WHERE upper(data_domain) like '%_TEST'
);

DELETE FROM <DATABASE_NAME>.<SCHEMA>.pybrv_UNIQUE_RULE_MAPPING
WHERE upper(data_domain) like '%_TEST'
;

DELETE FROM <DATABASE_NAME>.<SCHEMA>.pydpc_record_results
WHERE upper(data_domain) like '%_TEST'
;
