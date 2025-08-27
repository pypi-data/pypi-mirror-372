from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from pytz import timezone
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import sys
import time
import json
import os
import logging
import re
import pandas as pd
from .email_notification import email_notification
from .utils import (
    execute_run_databricks,
    execute_run_postgres,
    DbConnections
)

class RuleManager:
    def __init__(
        self,
        *,
        spark: Optional[SparkSession] = None,
        dbutils=None,
        http_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.spark = spark
        self.dbutils = dbutils
        self.http_path = http_path

        self.server_hostname = (
            spark.conf.get("spark.databricks.workspaceUrl")
            if spark else None
        )

        self.access_token = (
            dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            if dbutils else None
        )

        self.databricks_client = WorkspaceClient()

        self.config: Dict[str, Any] = {}
        self.template: Dict[str, Any] = {}
        self.rules: Dict[str, List[Dict[str, Any]]] = {}
        self.execution_id: Optional[int] = None
        self.job_start_time: Optional[float] = None

        if base_dir:
            self.base_dir = base_dir
        elif os.getenv("BRV_BASE_DIR"):
            self.base_dir = os.getenv("BRV_BASE_DIR")
        else:
            self.base_dir = os.getcwd()
    
    def resolve_relative_path(self, raw_path: str) -> str:
        """
        Resolves a given relative or absolute file path using the base_dir.
        """
        raw_path = raw_path.strip().lstrip("/\\")
        return os.path.abspath(os.path.join(self.base_dir, raw_path))

    def load_config(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def split_config_object(self):
        if 'RULES' in self.config:
            self.template = {k: v for k, v in self.config.items() if k != 'RULES'}
            self.rules = {'RULES': self.config['RULES']}
            return self.template, self.rules
        else:
            self.logger.warning("Array 'RULES' not found in rule object.")
            return self.template, None

    def run_exe(self, s: str) -> int:
        # Use consistent hashing and ensure non-negative number
        return abs(hash(s)) % (sys.maxsize + 1)

    def init_other_variables(self):
        # Use UTC date to avoid timezone issues
        hash_string = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d%H%M%S")
        self.execution_id = self.run_exe(hash_string)
        self.job_start_time = time.time()

    def set_system_variables(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        self.init_other_variables()
        hash_string = f"{rule['TEAM_NAME']}{rule['DOMAIN_NAME']}{rule['RULE_CATEGORY_NAME']}{rule['RULE_ID']}"
        unique_rule_identifier = self.run_exe(hash_string)
        rule['EXECUTION_ID'] = self.execution_id
        rule['UNIQUE_RULE_IDENTIFIER'] = unique_rule_identifier
        rule['UNIQUE_TIMESTAMP'] = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return rule

    def get_file_text(self, file_path: str, is_local: bool = False) -> str:
        """Read file content from local filesystem or Databricks workspace.
        
        Args:
            file_path: Path to the file
            is_local: Whether the file is local or in Databricks workspace
            
        Returns:
            str: File contents
            
        Raises:
            FileNotFoundError: If local file not found
            Exception: For other errors
        """
        if is_local:
            try:
                # First, try to find SQL templates in the package directory
                package_dir = os.path.dirname(os.path.abspath(__file__))
                possible_paths = [
                    os.path.join(package_dir, 'sql_templates', file_path),  # Package sql_templates
                    os.path.join(os.getcwd(), 'sql_templates', file_path),  # Current directory sql_templates
                    os.path.join(self.base_dir, 'sql_templates', file_path),  # Base directory sql_templates
                    os.path.join(os.getcwd(), file_path),  # Current directory
                ]

                

                # Add user-specified templates path if available
                if hasattr(self, 'base_dir'):
                    possible_paths.append(os.path.join(self.base_dir, 'sql_templates', file_path))

                if hasattr(self, 'sql_templates_path'):
                    possible_paths.insert(0, os.path.join(self.sql_templates_path, file_path))

                for path in possible_paths:
                    if os.path.exists(path):
                        full_path = path
                        break
                else:
                    raise FileNotFoundError(f"SQL template not found: {file_path}")

                self.logger.info(f"Reading local file: {full_path}")
                try:
                    with open(full_path, 'r', encoding='utf-8') as file:
                        return file.read()
                except UnicodeDecodeError:
                    self.logger.warning(f"UTF-8 decoding failed, retrying with latin-1 for file: {full_path}")
                    with open(full_path, 'r', encoding='latin-1') as file:
                        return file.read()

            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {str(e)}")
                raise
        else:
            # Download file content from Databricks workspace
            try:
                with self.databricks_client.workspace.download(file_path) as f:
                    return f.read().decode("utf-8")
            except Exception as e:
                self.logger.error(f"Error downloading from Databricks: {str(e)}")
                raise

    def set_business_rule_check_templates(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Load SQL templates based on engine type.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with SQL templates
        """
        engine_type = rule.get('ENGINE_TYPE', '').lower()
        
        # First try package sql_templates directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(package_dir, 'sql_templates')
        
        if engine_type == 'databricks':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping.sql'),
                'TAGS': os.path.join('tags','tag.sql'),
            }
        elif engine_type == 'postgres':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select_postgres.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result_postgres.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update_postgres.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping_postgres.sql'),
                'TAGS': os.path.join('tags','tag.sql'),
            }
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        for key, path in paths.items():
            rule[key] = self.get_file_text(path, is_local=True)

        return rule

    def loader(self, rule: Dict[str, Any]):
        catalog = rule.get("DATABASE_NAME")
        schema = rule.get("SCHEMA")

        for file_info in rule.get("FILES", []):
            path = file_info['PATH']
            delimiter = file_info.get('DELIMITER', '|')
            header = file_info.get('HEADER', 'true')
            table_name = file_info['TEMP_TABLE_NAME']
            qualified_table_name = f"{catalog}.{schema}.{table_name}"

            self.logger.info(f"Loading file into: {qualified_table_name}")
            df = self.spark.read.option("header", header).option("delimiter", delimiter).option("inferSchema", "true").csv(path)
            df.write.mode("overwrite").saveAsTable(qualified_table_name)

    
    def set_data_parity_check_templates(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Load SQL templates for data parity check based on engine type.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with SQL templates
        """
        engine_type = rule.get('ENGINE_TYPE', '').lower()
        rule['STAGE_TABLE_NAME'] = f"VF_DATA_PARITY_RESULT_{rule['EXECUTION_ID']}_{rule['UNIQUE_TIMESTAMP']}"
        # First try package sql_templates directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(package_dir, 'sql_templates')

        if engine_type == 'databricks':
            paths = {
                'metadata_sql_text': os.path.join('data_parity_check', 'metadata_sql_text.sql'),
                'bookmark_sql_text': os.path.join('common', 'bookmark_select_dbrcks.sql'),
                'SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE': os.path.join('common', 'bookmark_update_dpc_dbrcks.sql'),
                'summary_report_sql_text': os.path.join('data_parity_check', 'summary_report_dbrcks.sql'),
                'attr_summary_report_sql_text': os.path.join('data_parity_check', 'attribute_summary_report_dbrcks.sql'),
                'load_summary_report_sql_text': os.path.join('data_parity_check', 'load_summary_report_dbrcks.sql'),
                'load_attr_summary_report_sql_text': os.path.join('data_parity_check', 'load_attribute_summary_report_dbrcks.sql'),
                'unit_test_clean_up_sql_text': os.path.join('common', 'clean_up_unit_test_dbrcks.sql'),
                'unique_rule_mapping_sql_text': os.path.join('common', 'unique_identifier_mapping_dbrcks.sql'),
                'comparison_stg_sql': os.path.join('data_parity_check', 'sql_template_dbrcks.sql'),
                'dashboard_sql': os.path.join('data_parity_check', 'dashboard_etl_dbrcks.sql'),
            }
        elif engine_type == 'postgres':
            paths = {
                'metadata_sql_text': os.path.join('data_parity_check', 'metadata_sql_text.sql'),
                'bookmark_sql_text': os.path.join('common', 'bookmark_select_postgres.sql'),
                'SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE': os.path.join('common', 'bookmark_update_dpc_postgres.sql'),
                'summary_report_sql_text': os.path.join('data_parity_check', 'summary_report_postgres.sql'),
                'attr_summary_report_sql_text': os.path.join('data_parity_check', 'attribute_summary_report_postgres.sql'),
                'load_summary_report_sql_text': os.path.join('data_parity_check', 'load_summary_report_postgres.sql'),
                'load_attr_summary_report_sql_text': os.path.join('data_parity_check', 'load_attribute_summary_report_postgres.sql'),
                'unit_test_clean_up_sql_text': os.path.join('common', 'clean_up_unit_test_pgrs.sql'),
                'unique_rule_mapping_sql_text': os.path.join('common', 'unique_identifier_mapping_postgres.sql'),
                'comparison_stg_sql': os.path.join('data_parity_check', 'sql_template_postgres.sql'),
                'dashboard_sql': os.path.join('data_parity_check', 'dashboard_etl_postgres.sql'),
            }
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        for key, path in paths.items():
            rule[key] = self.get_file_text(path, is_local=True)

        return rule


    def set_bookmark_value(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        try:
            rule['BOOKMARK_COLUMN'] = rule.get('BOOKMARK_COLUMN', 'TEMP_COL_FOR_BOOKMARK')
            rule['BOOKMARK_COLUMN_NAME'] = rule.get('BOOKMARK_COLUMN', 'TEMP_COL_FOR_BOOKMARK')
            rule['BOOKMARK_START_DATE'] = rule.get('DEFAULT_BOOKMARK_START_DATE', '1970-01-01')
            self.logger.info(f"Default bookmark start date: {rule['BOOKMARK_START_DATE']}")

            if rule['BOOKMARK_COLUMN'] == 'TEMP_COL_FOR_BOOKMARK':
                return self._handle_temp_bookmark(rule)

            return self._handle_actual_bookmark(rule)

        except Exception as e:
            self.logger.error(f"Error setting bookmark value: {str(e)}")
            raise

    def _handle_temp_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': True,
            'NEED_BOOKMARK_UPDATE': False,
            'BOOKMARK_END_DATE': '2099-01-01'
        })
        return rule

    def _handle_actual_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': False,
            'NEED_BOOKMARK_UPDATE': True,
            'BOOKMARK_END_DATE': rule.get('BOOKMARK_END_DATE', rule['BOOKMARK_START_DATE'])
        })

        if 'bookmark_sql_text' not in rule:
            return rule

        return self._process_bookmark_sql(rule)

    def _process_bookmark_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule['bookmark_sql_text'] = self.replace_common_variables(rule['bookmark_sql_text'], rule)
        engine_type = rule.get('ENGINE_TYPE', '').lower()

        if engine_type == 'databricks':
            result = execute_run_databricks(rule['bookmark_sql_text'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(rule['bookmark_sql_text'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        # Expecting result to be list with at least two elements (date range)
        if isinstance(result, list) and len(result) > 1 and len(result[1]) > 1:
            rule['BOOKMARK_START_DATE'] = result[1][0]
            rule['BOOKMARK_END_DATE'] = result[1][1]
            if rule['BOOKMARK_END_DATE'] < rule['BOOKMARK_START_DATE']:
                rule['BOOKMARK_END_DATE'] = rule['BOOKMARK_START_DATE']
        else:
            rule['BOOKMARK_END_DATE'] = (datetime.now(timezone('UTC')) - timedelta(days=1)).date().isoformat()

        return rule

    def get_dataframe(self, result: Any) -> pd.DataFrame:
        df = pd.DataFrame()
        if result:
            result_df = pd.DataFrame(result)
            if len(result_df) > 0:
                df_header = result_df.iloc[0]
                result_df = result_df[1:]
                result_df.columns = df_header
                df = result_df.reset_index(drop=True)
        return df

    def process_fail_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        fail_sql_path = rule.get('FAIL_SQL')
        
        if not fail_sql_path:
            rule['STATUS'] = True
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        rule['STATUS'] = False
        fail_sql_path = os.path.normpath(os.path.join(self.base_dir, fail_sql_path))
        self.logger.info(f"Reading fail SQL file from: {fail_sql_path}")

        try:
            rule['FAILED_QUERY'] = self.get_file_text(str(fail_sql_path), is_local=True).replace(';', '')
        except Exception as e:
            self.logger.error(f"Error reading fail SQL file: {e}")
            rule['FAILED_QUERY'] = ''
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        pass_sql_path = rule.get('PASS_SQL', '')
        if pass_sql_path:
            pass_sql_path = os.path.normpath(os.path.join(self.base_dir, pass_sql_path))
            try:
                rule['PASS_QUERY'] = self.get_file_text(str(pass_sql_path), is_local=True).replace(';', '')
            except Exception as e:
                self.logger.error(f"Error reading pass SQL file: {e}")
                rule['PASS_QUERY'] = ''
        else:
            rule['PASS_QUERY'] = ''

        rule['FAILED_QUERY'] = self.replace_common_variables(rule['FAILED_QUERY'], rule)

        engine_type = rule.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            fail_df_result = execute_run_databricks(rule['FAILED_QUERY'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            fail_df_result = execute_run_postgres(rule['FAILED_QUERY'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        fail_df = self.get_dataframe(fail_df_result)
        fail_df_count = fail_df.shape[0]
        rule['FAIL_RECORD_COUNT'] = fail_df_count

        if rule['FAIL_RECORD_COUNT'] == 0 and rule['PASS_QUERY'] == '':
            rule['STATUS'] = True

        try:
            fail_df_keys = fail_df.head(10).to_json(orient="records")
            fail_df_keys_parsed = json.loads(fail_df_keys)
            rule['FAILED_KEYS'] = json.dumps(fail_df_keys_parsed, indent=4)
        except Exception as e:
            self.logger.error(f"Error converting failed keys to JSON: {e}")
            rule['FAILED_KEYS'] = '{}'

        return rule
    
    def process_pass_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        if rule['PASS_QUERY'] != '':
            engine_type = rule.get('ENGINE_TYPE', '').lower()
            if engine_type == 'databricks':
                pass_df_result = execute_run_databricks(rule['PASS_QUERY'], True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            else:
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                pass_df_result = execute_run_postgres(rule['PASS_QUERY'], engine, True)
                
            pass_df = self.get_dataframe(pass_df_result)
            pass_df_count = pass_df.shape[0]
            rule['PASS_RECORD_COUNT'] = pass_df_count
                
            if (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT']) == 0:
                rule['PASS_PERCENTAGE'] = 0
            else:
                rule['PASS_PERCENTAGE'] = round(
                    (rule['PASS_RECORD_COUNT'] / (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT'])) * 100, 2
                )
                
            if int(rule['PASS_PERCENTAGE']) >= int(rule['PASS_THRESHOLD']):
                rule['STATUS'] = True
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}.'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD']
                )
            elif rule['PASS_PERCENTAGE'] == 0:
                rule['REMARKS'] = 'Both passed records count and failed records count are zero'
            else:
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}. Some failed keys are: {}'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD'], rule['FAILED_KEYS']
                )
        elif not rule['STATUS']:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = '{} number of records failed the test. Some failed keys are: {}'.format(
                rule['FAIL_RECORD_COUNT'], rule['FAILED_KEYS']
            )
        else:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = 'No record has failed the test'
        
        return rule

    def replace_common_variables(self,sql_str, rule):
        """
        Replaces placeholders in sql_str with corresponding values from the rule dictionary.
        Any placeholder in the format <PLACEHOLDER_NAME> will be dynamically replaced.
        """
        final_sql = sql_str
        for key, value in rule.items():
            placeholder = f'<{key}>'
            final_sql = final_sql.replace(placeholder, str(value))
        return final_sql

    def replace_special_variables(self, sql_str, rule):
        final_sql = ''
        for line in sql_str.splitlines():
            if not line.startswith('--') and not re.match(r'^\s*$', line):
                if "GROUP BY <REPEAT>" in line:
                    line = line.replace("<REPEAT>", "")
                    new_line = line.replace("<MANDATORY_COLUMNS>",
                                            ','.join(rule['mandatory_col_list']).replace(",", ', SOURCE.'))
                    final_sql = final_sql + ' \n' + new_line
                elif "<REPEAT>" in line:
                    line = line.replace("<REPEAT>", "")
                    if "<MANDATORY_COLUMNS>" in line:
                        for value in rule['mandatory_col_list']:
                            new_line = line.replace("<MANDATORY_COLUMNS>", value.strip())
                            final_sql = final_sql + ' \n' + new_line
                    if "<JOIN_KEY>" in line:
                        ending_string = ' AND'
                        if "<EMPTY_END>" in line:
                            ending_string = ''
                        for idx, value in enumerate(rule['join_dimensions_col_list']):
                            new_line = line.replace("<JOIN_KEY>", value.strip()).replace("<EMPTY_END>", "")
                            if idx < len(rule['join_dimensions_col_list']) - 1:
                                final_sql = final_sql + ' \n' + new_line + ending_string
                            else:
                                final_sql = final_sql + ' \n' + new_line
                    if "<COLUMN_TO_CHECK>" in line:
                        for value in rule['COLUMN_TO_CHECK']:
                            new_line = line.replace("<COLUMN_TO_CHECK>", value.strip())
                            final_sql = final_sql + ' \n' + new_line

                elif "<CONCAT> SOURCE." in line:
                    line = line.replace("<CONCAT>", "")
                    new_line = line.replace("<JOIN_KEY>",
                                            ','.join(rule['join_dimensions_col_list']).replace(",", ' || SOURCE.'))
                    new_line = new_line.replace("<MANDATORY_COLUMNS>",
                                                ','.join(rule['mandatory_col_list']).replace(",", ' || SOURCE.'))
                    new_line = new_line.replace("<METRIC_DIM_COL>",
                                                ','.join(rule['METRIC_DIM_COL']).replace(",", ' || SOURCE.'))
                    final_sql = final_sql + ' \n' + new_line

                elif "<CONCAT> TARGET." in line:
                    line = line.replace("<CONCAT>", "")
                    new_line = line.replace("<JOIN_KEY>",
                                            ','.join(rule['join_dimensions_col_list']).replace(",", ' || TARGET.'))
                    new_line = new_line.replace("<MANDATORY_COLUMNS>",
                                                ','.join(rule['mandatory_col_list']).replace(",", ' || TARGET.'))
                    final_sql = final_sql + ' \n' + new_line

                elif "<REPEAT_COL_CHECK>" in line:
                    line = line.replace("<REPEAT_COL_CHECK>", "")

                    if "<COLUMN_TO_CHECK>" in line:
                        for idx, value in enumerate(rule['COLUMN_TO_CHECK']):
                            new_line = line.replace("<COLUMN_TO_CHECK>", value.strip())
                            if idx < len(rule['COLUMN_TO_CHECK']) - 1:
                                final_sql = final_sql + ' \n' + new_line + ' AND'
                            else:
                                final_sql = final_sql + ' \n' + new_line

                    if "<MANDATORY_COLUMNS>" in line:
                        for idx, value in enumerate(rule['mandatory_col_list']):
                            new_line = line.replace("<MANDATORY_COLUMNS>", value.strip())
                            if idx < len(rule['mandatory_col_list']) - 1:
                                final_sql = final_sql + ' \n' + new_line + ' AND'
                            else:
                                final_sql = final_sql + ' \n' + new_line

                    if "<METRIC_DIM_COL>" in line or "<METRIC_DIM_COL_ONLY>" in line:
                        col_list = rule['METRIC_DIM_COL']
                        if "<METRIC_DIM_COL_ONLY>" in line:
                            col_list = rule['metric_dimensions_col_list']
                        ending_string = ' AND'
                        if "<POSTGRES_REPEAT_COL_CHECK>" in line:
                            line = line.replace("<POSTGRES_REPEAT_COL_CHECK>", "")
                            ending_string = ' AND'
                        elif "<DATABRICKS_REPEAT_COL_CHECK>" in line:
                            line = line.replace("<DATABRICKS_REPEAT_COL_CHECK>", "")
                            ending_string = ' AND'
                            
                        
                        if "<EMPTY_END>" in line:
                            ending_string = ''
                        for idx, value in enumerate(col_list):
                            new_line = line.replace("<METRIC_DIM_COL>", value.strip()).replace("<METRIC_DIM_COL_ONLY>",
                                                                                               value.strip()).replace(
                                "<EMPTY_END>", "")
                            if idx < len(col_list) - 1:
                                final_sql = final_sql + ' \n' + new_line + ending_string
                            else:
                                final_sql = final_sql + ' \n' + new_line
                
                elif "<NO_COLUMN_TO_CHECK>" in line:
                    line = line.replace("<NO_COLUMN_TO_CHECK>", "")
                    if len(rule['COLUMN_TO_CHECK']) == 0:
                        line = line.replace("AND", "")

                    final_sql = final_sql + ' \n' + line
                
                elif "<NO_METRIC_DIM_COL>" in line:
                    line = line.replace("<NO_METRIC_DIM_COL>", "")
                    if len(rule['METRIC_DIM_COL']) == 0:
                        line = line.replace("AND", "")
                
                elif "<REPEAT_UNION_ALL>" in line:
                    for idx, col in enumerate(rule['COLUMN_TO_CHECK']):
                        union_prefix = "\nUNION ALL\n"
                        line = f"""{union_prefix}SELECT {rule['UNIQUE_RULE_IDENTIFIER']}, {rule['EXECUTION_ID']}, '{rule['RULE_NAME']}', '{rule['DATA_DOMAIN']}', '{rule['TABLE_NAME']}', '{rule['BOOKMARK_COLUMN_NAME']}', {rule['BOOKMARK_COLUMN_NAME']}, join_key_values, metric_dim_values,
                        '{col}_matched_count', {col}_matched_count, '{rule['COMMENTS']}', last_modified_ts
                        FROM grouped_data"""

                    final_sql = final_sql + ' \n' + line

                else:
                    final_sql = final_sql + ' \n' + line
        return final_sql

    def get_query_metadata_col_list(self, sql):
        engine_type = self.template.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            result = execute_run_databricks(sql, True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            return [col.lower() for col in result[0]] 
        else:
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(sql, engine, True)
            if isinstance(result, list) and len(result) > 0:
                return [col.lower() for col in result[0]]
            else:
                self.logger.warning("No columns found in the result set.")
        return []
    
    def get_merged_list(self, *lists):
        result = []
        for lst in lists:
            result.extend(lst)
        return list(dict.fromkeys(col.lower() for col in result if col))
    
    def get_list_difference(self, list1, list2):
        return list(set(col.lower() for col in list1) - set(col.lower() for col in list2))
    

    def res_summary_report_df(self, sql_text):
        engine_type = self.template.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            result = execute_run_databricks(sql_text, True,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(sql_text, engine, True)
        return self.get_dataframe(result)
    
    def summary_report_df(self, sql_text):
        engine_type = self.template.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            result = execute_run_databricks(sql_text, False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(sql_text, engine, False)
        return self.get_dataframe(result)

    def set_business_rule_check_final_queries(self, rule: dict) -> dict:
        rule['unique_rule_mapping_sql'] = self.replace_common_variables(rule.get('unique_rule_mapping_sql', ''), rule)
        rule['result_sql_txt'] = self.replace_common_variables(rule.get('result_sql_txt', ''), rule)
        rule['update_bookmark_sql_text'] = self.replace_common_variables(rule.get('update_bookmark_sql_text', ''), rule)
        return rule

    def set_data_parity_check_final_queries(self, rule: dict) -> dict:
        rule['SOURCE_SQL'] = self.get_file_text(rule['SOURCE_SQL'], is_local=True).replace(';', '')
        rule['TARGET_SQL'] = self.get_file_text(rule['TARGET_SQL'], is_local=True).replace(';', '')
        
        if rule.get('SKIP_BOOKMARKING'):
            engine = rule.get('ENGINE_TYPE', '').lower()

            if engine == 'postgres':
                timestamp_expr = "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::DATE"

            elif engine == 'databricks':
                timestamp_expr = "CAST(CURRENT_TIMESTAMP AS DATE)"

            else:
                raise ValueError(f"Unsupported ENGINE_TYPE for bookmarking: {engine}")

            rule['SOURCE_SQL'] = f"SELECT *, {timestamp_expr} AS TEMP_COL_FOR_BOOKMARK FROM ({rule['SOURCE_SQL']})"

            rule['TARGET_SQL'] = f" SELECT *, {timestamp_expr} AS TEMP_COL_FOR_BOOKMARK FROM ({rule['TARGET_SQL']})"


        rule['metadata_sql_text'] = self.replace_common_variables(rule.get('metadata_sql_text', ''), rule)
        rule['SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE'] = self.replace_common_variables(rule.get('SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE', ''), rule)
        rule['summary_report_sql_text'] = self.replace_common_variables(rule.get('summary_report_sql_text', ''), rule)
        rule['attr_summary_report_sql_text'] = self.replace_common_variables(rule.get('attr_summary_report_sql_text', ''), rule)
        rule['load_summary_report_sql_text'] = self.replace_common_variables(rule.get('load_summary_report_sql_text', ''), rule)
        rule['load_attr_summary_report_sql_text'] = self.replace_common_variables(rule.get('load_attr_summary_report_sql_text', ''), rule)
        rule['unit_test_clean_up_sql_text'] = self.replace_common_variables(rule.get('unit_test_clean_up_sql_text', ''), rule)
        rule['unique_rule_mapping_sql_text'] = self.replace_common_variables(rule.get('unique_rule_mapping_sql_text', ''), rule)
        rule['comparison_stg_sql'] = self.replace_common_variables(rule.get('comparison_stg_sql', ''), rule)
        rule['dashboard_sql'] = self.replace_common_variables(rule.get('dashboard_sql', ''), rule)


        rule['metadata_sql_text'] = self.replace_special_variables(rule.get('metadata_sql_text', ''), rule)
        rule['SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE'] = self.replace_special_variables(rule.get('SQL_TO_UPDATE_BOOKMARK_IN_METADATA_TABLE', ''), rule)
        rule['unit_test_clean_up_sql_text'] = self.replace_special_variables(rule.get('unit_test_clean_up_sql_text', ''), rule)
        rule['unique_rule_mapping_sql_text'] = self.replace_special_variables(rule.get('unique_rule_mapping_sql_text', ''), rule)
        rule['final_sql_template_text'] = rule['unique_rule_mapping_sql_text']+ '\n' + rule['comparison_stg_sql'] + '\n' + rule['dashboard_sql']

        return rule


    def exec_business_rule_check_final_queries(self, rule):
        """Execute final SQL queries based on engine type (databricks or postgres)."""
        print("Executing final queries")
        engine_type = rule.get("ENGINE_TYPE").lower()
        print("exec_business_rule_check_final_queries", engine_type)
        
        try:
            def clean_sql(sql):
                if not sql:
                    return ""
                # Remove trailing semicolons, quotes, commas and normalize whitespace
                cleaned = sql.strip().rstrip(';').rstrip("'").rstrip(",").strip()
                return cleaned

            # Clean all SQL queries
            rule["unique_rule_mapping_sql"] = clean_sql(rule.get("unique_rule_mapping_sql", ""))
            rule["result_sql_txt"] = clean_sql(rule.get("result_sql_txt", ""))
            rule["update_bookmark_sql_text"] = clean_sql(rule.get("update_bookmark_sql_text", ""))

            if engine_type == 'databricks':
                print("Running Databricks...")
                execute_run_databricks(rule["unique_rule_mapping_sql"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
                execute_run_databricks(rule["result_sql_txt"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    execute_run_databricks(rule["update_bookmark_sql_text"], False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)

            else:  # Assume Postgres
                print("Running Postgres...")
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()

                try:
                    execute_run_postgres(rule["unique_rule_mapping_sql"], engine, False)
                except Exception as e:
                    print(f"Error executing unique_rule_mapping_sql: {str(e)}")

                try:
                    execute_run_postgres(rule["result_sql_txt"], engine, False)
                except Exception as e:
                    print(f"Error executing result_sql_txt: {str(e)}")

                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    try:
                        execute_run_postgres(rule["update_bookmark_sql_text"], engine, False)
                    except Exception as e:
                        print(f"Error executing update_bookmark_sql_text: {str(e)}")

        except Exception as e:
            print(f"Error executing final queries: {str(e)}")
            raise

        return rule

    def exec_data_parity_check_final_queries(self, rule: dict) -> dict:
        
        rule['join_dimensions_col_list'] = [col for col in rule['JOIN_DIMENSIONS'].replace(' ', '').split(',') if col]
        rule['metric_dimensions_col_list'] = [col for col in rule['METRIC_DIMENSIONS'].replace(' ', '').split(',') if col]

        try:
            rule['query_metadata_col_list'] = self.get_query_metadata_col_list(rule['metadata_sql_text'])
            logging.info(f"Metadata columns: {rule['query_metadata_col_list']}")


            rule['mandatory_col_list'] = self.get_merged_list(
                rule['join_dimensions_col_list'], rule['metric_dimensions_col_list'], [rule['BOOKMARK_COLUMN'].lower()]
            )
            logging.info("Mandatory column list generated")
            print(f"Mandatory columns: {rule['mandatory_col_list']}")

            rule['METRIC_DIM_COL'] = self.get_merged_list(
                rule['join_dimensions_col_list'], rule['metric_dimensions_col_list']
            )
            logging.info("Metric and Join column list generated")
            print(f"Metric and Join columns: {rule['METRIC_DIM_COL']}")

            rule['COLUMN_TO_CHECK'] = self.get_list_difference(
                rule['query_metadata_col_list'], rule['mandatory_col_list']
            )
            logging.info("Columns to check list generated")
            print(f"Columns to check: {rule['COLUMN_TO_CHECK']}")   

            rule['comparison_stg_sql'] = self.replace_special_variables(rule.get('comparison_stg_sql', ''), rule)
            ## Check if source query have all bookmark cols, join cols, and metric dimension cols or not.
            missing_cols = self.get_list_difference(rule['mandatory_col_list'], rule['query_metadata_col_list'])
            if missing_cols:
                raise Exception(f"Mandatory columns missing: {missing_cols}")

            final_sql = self.replace_special_variables(rule.get('final_sql_template_text', ''), rule)

            engine_type = rule.get('ENGINE_TYPE', '').lower()
            if engine_type == 'databricks':
                result = execute_run_databricks(final_sql, False,server_hostname=self.server_hostname, http_path=self.http_path, access_token=self.access_token)
            elif engine_type == 'postgres':
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                result = execute_run_postgres(final_sql, engine, False)
            print(result)
            logging.info("Executed final SQL successfully")
            
            # rule['summary_report_sql_text'] = self.replace_special_variables(rule.get('summary_report_sql_text', ''), rule)
            # rule['attr_summary_report_sql_text'] = self.replace_special_variables(rule.get('attr_summary_report_sql_text', ''), rule)
            # rule['summary_report_df'] = self.res_summary_report_df(rule['summary_report_sql_text'])
            # rule['attribute_summary_report_df'] = self.res_summary_report_df(rule['attr_summary_report_sql_text'])
            # logging.info("Generated report dataframes")

            rule['load_summary_report_sql_text'] = self.replace_special_variables(rule.get('load_summary_report_sql_text', ''), rule)
            rule['load_attr_summary_report_sql_text'] = self.replace_special_variables(rule.get('load_attr_summary_report_sql_text', ''), rule)
            
            self.summary_report_df(rule['load_summary_report_sql_text'])
            self.summary_report_df(rule['load_attr_summary_report_sql_text'])
            
            # safe_rule_name = rule['RULE_NAME'].replace(" ", "_").replace("/", "_")

            # summary_csv_path = f"summary_report_{safe_rule_name}.csv"
            # attr_summary_csv_path = f"attribute_summary_report_{safe_rule_name}.csv"

            # if not rule['summary_report_df'].empty:
            #     rule['summary_report_df'].to_csv(summary_csv_path, index=False)
            #     logging.info(f"Summary report saved to {summary_csv_path}")
            # else:
            #     logging.warning("Summary DataFrame is empty — skipping CSV write.")

            # if not rule['attribute_summary_report_df'].empty:
            #     rule['attribute_summary_report_df'].to_csv(attr_summary_csv_path, index=False)
            #     logging.info(f"Attribute summary report saved to {attr_summary_csv_path}")
            # else:
            #     logging.warning("Attribute Summary DataFrame is empty — skipping CSV write.")
            logging.info("Loaded reports to log tables")

            rule['STATUS'] = True

        except Exception as e:
            rule['STATUS'] = False
            rule['EXCEPTION_LOG'] = str(e)
            logging.exception(e)

        return rule

    def drop_temp_tables(self, rule: Dict[str, Any]):
        catalog = rule.get("DATABASE_NAME")
        schema = rule.get("SCHEMA")

        for file_info in rule.get("FILES", []):
            table_name = file_info['TEMP_TABLE_NAME']
            qualified_table_name = f"{catalog}.{schema}.{table_name}"
            self.logger.info(f"Dropping temp table: {qualified_table_name}")
            self.spark.sql(f"DROP TABLE IF EXISTS {qualified_table_name}")


    def business_rule_check(self) -> Dict[str, List[Dict[str, Any]]]:
        BATCH_ID = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        results = []
        current_time_et = datetime.now(timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S %Z")

        # Read config-driven email values
        email_enabled = self.template.get("Email_Notification", False)
        recipient_email = self.template.get("TEAM_EMAIL")
        email_api_url = self.template.get("URL")
        env = self.template.get("ENV", "DEV")

        try:
            if self.template.get("RULE_CATEGORY_NAME") == 'BUSINESS_RULE_CHECK':
                for idx, rule in enumerate(self.rules.get("RULES", [])):
                    rule = {**self.template, **rule}
                    rule['BATCH_ID'] = BATCH_ID
                    rule = self.set_system_variables(rule)
                    rule = self.set_business_rule_check_templates(rule)
                    rule = self.set_bookmark_value(rule)
                    rule = self.process_fail_sql(rule)
                    rule = self.process_pass_sql(rule)
                    rule = self.set_business_rule_check_final_queries(rule)
                    rule = self.exec_business_rule_check_final_queries(rule)

                    self.rules["RULES"][idx] = rule
                    self.logger.info(json.dumps(rule, indent=2))

                    rule_name = rule.get('RULE_NAME', 'Unknown')
                    rule_id = rule.get('RULE_ID', 'Unknown')

                    results.append({
                        "RULE_ID": rule_id,
                        "RULE_NAME": rule_name,
                        "DOMAIN_NAME": rule.get('DOMAIN_NAME'),
                        "TABLES_CHECKED": rule.get('TABLES_CHECKED'),
                        "TEAM_NAME": rule.get('TEAM_NAME'),
                        "SEVERITY": rule.get('SEVERITY'),
                        "RULE_CATEGORY": rule.get('RULE_CATEGORY'),
                        "STATUS": rule.get('STATUS'),
                        "FAIL_RECORD_COUNT": rule.get('FAIL_RECORD_COUNT'),
                        "PASS_RECORD_COUNT": rule.get('PASS_RECORD_COUNT'),
                        "COMMENTS": rule.get('COMMENTS'),
                        "TIME": rule.get('TIME', datetime.now(timezone('UTC')).isoformat())
                    })

                    if rule.get('STOP_ON_FAIL_STATUS') == 'TRUE' and not rule.get('STATUS'):
                        self.logger.warning(f"Rule {rule_name} (ID: {rule_id}) failed. Sending failure email and stopping.")

                        if email_enabled:
                            summary_df = self.spark.createDataFrame(results)
                            email_notification(
                                current_time_et=current_time_et,
                                recipient_name=recipient_email,
                                subject=f"Rule {rule_name} Failed",
                                env=env,
                                body_part=rule.get('COMMENTS', 'Rule failed'),
                                df=summary_df,
                                footer=f"Rule ID: {rule_id}",
                                is_failure=True,
                                file_name=rule.get("FILE_NAME"),
                                url=email_api_url
                            )
                        break

            elif self.template.get("RULE_CATEGORY_NAME") == 'DATA_PARITY_CHECK':
                for idx, rule in enumerate(self.rules.get("RULES", [])):
                    rule = {**self.template, **rule}
                    rule['BATCH_ID'] = BATCH_ID
                    rule = self.set_system_variables(rule)

                    if rule.get("LOAD_FILES", False):
                        self.logger.info(f"Loading files for rule: {rule['RULE_NAME']}")
                        self.loader(rule)

                    rule = self.set_data_parity_check_templates(rule)
                    rule = self.set_bookmark_value(rule)
                    rule = self.set_data_parity_check_final_queries(rule)
                    rule = self.exec_data_parity_check_final_queries(rule)

                    self.rules["RULES"][idx] = rule

                    results.append({
                        "RULE_ID": rule.get('RULE_ID'),
                        "RULE_NAME": rule.get('RULE_NAME'),
                        "DOMAIN_NAME": rule.get('DOMAIN_NAME'),
                        "TABLES_CHECKED": rule.get('TABLE_NAME'),
                        "TEAM_NAME": rule.get('TEAM_NAME'),
                        "STATUS": rule.get('STATUS'),
                        "COMMENTS": rule.get('COMMENTS'),
                        "TIME": rule.get('TIME', datetime.now(timezone('UTC')).isoformat())
                    })

                    if rule.get("DROP_TEMP_TABLES", False):
                        self.logger.info(f"Dropping temp tables for rule: {rule['RULE_NAME']}")
                        self.drop_temp_tables(rule)

                    if 'summary_report_df' in rule and not rule['summary_report_df'].empty:
                        if email_enabled:
                            email_notification(
                                current_time_et=current_time_et,
                                recipient_name=recipient_email,
                                subject=f"{rule.get('RULE_NAME')} Summary Report",
                                env=env,
                                body_part="failed records summary",
                                df=rule['summary_report_df'],
                                footer=f"Rule ID: {rule.get('RULE_ID')}",
                                url=email_api_url
                            )

                    self.logger.info(f"Rule {idx + 1} processed successfully")
                    

           
            if email_enabled:
                summary_df = self.spark.createDataFrame(results)
                email_notification(
                    current_time_et=current_time_et,
                    recipient_name=recipient_email,
                    subject="Business Rule Check Summary",
                    env=env,
                    body_part=f". {len(results)} rules processed successfully",
                    footer=f"BATCH_ID: {BATCH_ID}",
                    url=email_api_url,
                    df=summary_df
                )

            print(json.dumps({ "BATCH_ID": BATCH_ID, "RULES": results }, indent=2))
            return results

        except Exception as e:
            self.logger.error(f"Critical Error in business_rule_check: {str(e)}")
            if email_enabled:
                email_notification(
                    current_time_et=current_time_et,
                    recipient_name=recipient_email,
                    subject="Business Rule Check - Execution Error",
                    env=env,
                    body_part=str(e),
                    is_failure=True,
                    url=email_api_url
                )
            raise