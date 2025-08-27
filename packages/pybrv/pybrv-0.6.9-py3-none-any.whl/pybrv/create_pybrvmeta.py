from pyspark.sql import SparkSession
import os
import json

class DatabricksPybrvmeta:
    def __init__(self, spark: SparkSession = None):
        """
        Initialize with or without Spark.
        If Spark is provided → Databricks mode.
        If not → Local mode.
        """
        if spark is not None:
            self.spark = spark.getActiveSession()
            self.engine_type = "databricks"
        else:
            self.spark = None
            self.engine_type = "local"

    def setup_pybrv_meta(self, database: str):
        """
        Create database, 'pybrv_meta' schema, and required tables for business rule validation metadata.
        """
        
        # Create database and schema
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {database}.pybrv_meta")

        # Drop if exists
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_business_rule_check_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_data_parity_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_metadata")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_unique_rule_mapping")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_mismatch_details")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_stats")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_record_results")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_rule_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.sgp_test_result")

        # Create tables
        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_business_rule_check_result (
            batch_id Decimal (20, 0),
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            team_name STRING,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            severity STRING,
            rule_category STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            status STRING,
            pass_record_count INT,
            fail_record_count INT,
            pass_percentage INT,
            threshold INT,
            failed_keys STRING,
            failed_query STRING,
            test_case_comments STRING,
            remarks STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_data_parity_result (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value INT,
            comments STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_metadata (
            unique_rule_identifier BIGINT NOT NULL,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_unique_rule_mapping (
            unique_rule_identifier BIGINT NOT NULL,
            team_name STRING,
            data_domain STRING,
            rule_category STRING,
            rule_id INT,
            rule_name STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_mismatch_details (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value STRING,
            join_key_values MAP<STRING, STRING>,
            metric_dim_values MAP<STRING, STRING>,
            mismatch_type STRING,
            column_mismatch_flags MAP<STRING, STRING>,
            source_values MAP<STRING, STRING>,
            target_values MAP<STRING, STRING>,
            mismatched_columns STRING,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_result (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_stats (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            rule_name STRING,
            table_checked STRING,
            execution_date DATE,
            key_date_column STRING,
            key_date_value DATE,
            field_name STRING,
            comments STRING,
            source_records BIGINT,
            target_records BIGINT,
            target_rows_matched BIGINT,
            source_attribute_count BIGINT,
            target_attribute_count BIGINT 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_summary (
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            field_name STRING,
            source_total_records STRING,
            target_total_records STRING,
            target_attribute_found STRING,
            attributes_matched_perc STRING,
            threshold STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_record_results (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value BIGINT,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_rule_summary (
            batch_id Decimal (20, 0),
            start_date STRING,
            end_date STRING,
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            status STRING,
            source_records STRING,
            target_found STRING,
            percent_records_found STRING,
            target_rows_matched STRING,
            percent_rows_matched STRING,
            attributes_checked STRING,
            attributes_matched STRING,
            comments STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.sgp_test_result (
            id INT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


   
        print(f"✅ All tables in `{database}.pybrv_meta` created successfully.")


    def create_business_rules_structure(self, base_path: str):
        """
        Creates the Business Rules folder and JSON file at given base_path.
        """
        structure = {
            "PYBRV": {
                "Configs": {
                    "json": {
                        "business_rules.json": {
                            "TEAM_NAME": "Data",
                            "TEAM_EMAIL": "team@xyzcompany.com",
                            "DOMAIN_NAME": "Transactions",
                            "RULE_CATEGORY_NAME": "BUSINESS_RULE_CHECK",
                            "DATABASE_NAME": "pybrv",
                            "ENGINE_TYPE": "databricks",
                            "RULES": [
                                {
                                    "RULE_ID": 1,
                                    "RULE_NAME": "unique_transactions_id_check",
                                    "RULE_CATEGORY": "Uniqueness",
                                    "SEVERITY": "Critical",
                                    "STOP_ON_FAIL_STATUS": "False",
                                    "FAIL_SQL": f"{base_path}/PYBRV/Configs/sql/business_rules_sql/unique_transactionsid_fail.sql",
                                    "PASS_SQL": f"{base_path}/PYBRV/Configs/sql/business_rules_sql/unique_transactionsid_pass.sql",
                                    "TABLES_CHECKED": "sales_transactions",
                                    "INVENTORY": "Transactions Validator Rules",
                                    "COMMENTS": "Check if transactionID is unique.",
                                    "PASS_THRESHOLD": 100,
                                    "BOOKMARK_START_DATE": "2025-04-10",
                                    "DEFAULT_BOOKMARK_START_DATE": "2025-03-20"
                                }
                            ]
                        }
                    },
                    "sql": {
                        "business_rules_sql": {
                            "unique_transactionsid_fail.sql": """SELECT transactionID, COUNT(*) FROM samples.bakehouse.sales_transactions GROUP BY transactionID HAVING COUNT(*) > 1;""",
                            "unique_transactionsid_pass.sql": """SELECT transactionID, COUNT(*) FROM samples.bakehouse.sales_transactions GROUP BY transactionID HAVING COUNT(*) = 1;"""
                        }
                    }
                }
            }
        }

        self._create_items(base_path, structure)
        print(f"✅ Business Rules structure created at: {base_path}")

    def create_data_parity_structure(self, base_path: str):
        """
        Creates the Data Parity folder with JSON and SQL files.
        """
        structure = {
            "PYBRV": {
                "Configs": {
                    "json": {
                        "parity_checks.json": {
                            "TEAM_NAME": "DATA",
                            "TEAM_EMAIL": "team@xyzcompany.com",
                            "RULE_CATEGORY_NAME": "DATA_PARITY_CHECK",
                            "ENGINE_TYPE": "databricks",
                            "DATA_DOMAIN": "DATA",
                            "DOMAIN_NAME": "DATA",
                            "DATABASE_NAME": "pybrv",
                            "SCHEMA": "pybrv_meta",
                            "RULES": [
                                {
                                    "RULE_ID": 1,
                                    "RULE_NAME": "DEMO-EMP-DATA-CHECK",
                                    "SOURCE_SQL": f"{base_path}/PYBRV/Configs/sql/data_parity_sql/source.sql",
                                    "TARGET_SQL": f"{base_path}/PYBRV/Configs/sql/data_parity_sql/target.sql",
                                    "JOIN_DIMENSIONS": "transactionId",
                                    "INVENTORY": "Demo Tables",
                                    "TABLE_NAME": "sales_transactions",
                                    "COMMENTS": "Running only Demo tables",
                                    "METRIC_DIMENSIONS": "transactionId",
                                    "THRESHOLD": 95,
                                    "POS": "Demo",
                                    "CUST_EXP_TESTING": 1,
                                    "RECORD_THRESHOLD": 95
                                }
                            ]
                        }
                    },
                    "sql": {
                        "data_parity_sql": {
                            "source.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;""",
                            "target.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;"""
                        }
                    }
                }
            }
        }

        # ✅ Create actual folders/files
        self._create_items(base_path, structure)
        print(f"✅ Data Parity structure created at: {os.path.abspath(base_path)}")

    def create_dashboard(self,base_path: str):
        structure = {
            "PYBRV": {
                "Configs": {
                    "dashboard": {
                        "PYBRV_Dashboard.lvdash.json": {
                            "datasets": [
                                {
                                "name": "67b76837",
                                "displayName": "Pybrv_Result",
                                "queryLines": [
                                    "SELECT *,\r\n",
                                    "       CASE WHEN rule_category = 'completeness' THEN 'Completeness' ELSE rule_category END AS rule_Category,\r\n",
                                    "       CASE WHEN status = 'True' THEN 'Passed' ELSE 'Failed' END AS Test_Status,\r\n",
                                    "       CASE WHEN status = 'True' THEN 1 ELSE 0 END AS passed_test,\r\n",
                                    "       CASE WHEN status = 'False' THEN 1 ELSE 0 END AS failed_test,\r\n",
                                    "       ROUND(\r\n",
                                    "         CASE \r\n",
                                    "           WHEN (CASE WHEN status = 'True' THEN 1 ELSE 0 END + CASE WHEN status = 'False' THEN 1 ELSE 0 END) > 0\r\n",
                                    "           THEN (CASE WHEN status = 'True' THEN 1 ELSE 0 END) * 100/ \r\n",
                                    "                (CASE WHEN status = 'True' THEN 1 ELSE 0 END + CASE WHEN status = 'False' THEN 1 ELSE 0 END)\r\n",
                                    "           ELSE 0\r\n",
                                    "         END, 2\r\n",
                                    "       ) AS passed_percentage\r\n",
                                    "FROM pybrv.pybrv_meta.pybrv_business_rule_check_result;\r\n"
                                ]
                                },
                                {
                                "name": "f411e3c1",
                                "displayName": "Pydpc_Result",
                                "queryLines": [
                                    "WITH attribute_result_agg AS (\r\n",
                                    "  SELECT   \r\n",
                                    "    unique_rule_identifier,  \r\n",
                                    "    execution_id,\r\n",
                                    "    MAX(last_modified_ts) AS execution_date,\r\n",
                                    "    ARRAY_AGG(\r\n",
                                    "        CASE \r\n",
                                    "            WHEN status = 1 THEN NULL\r\n",
                                    "            ELSE split(test_name, '_')[1] || ': ' || remarks\r\n",
                                    "        END\r\n",
                                    "    ) AS remarks\r\n",
                                    "  FROM pybrv.pybrv_meta.pydpc_attribute_result \r\n",
                                    "  GROUP BY \r\n",
                                    "    unique_rule_identifier,\r\n",
                                    "    execution_id\r\n",
                                    ")\r\n",
                                    "SELECT \r\n",
                                    "  summ.*,\r\n",
                                    "  try_cast(summ.attributes_matched AS int) AS attributes_match,\r\n",
                                    "  try_cast(attributes_checked AS int) AS attributes_check,\r\n",
                                    "  try_cast(attributes_checked AS int) - try_cast(attributes_matched AS int) AS attributes_not_matched,\r\n",
                                    "  try_cast(target_rows_matched AS int) AS records_matched,\r\n",
                                    "  try_cast(target_found AS int) - try_cast(target_rows_matched AS int) AS records_not_matched,\r\n",
                                    "  ROUND(\r\n",
                                    "    CASE \r\n",
                                    "      WHEN try_cast(summ.attributes_checked AS int) = 0 THEN NULL\r\n",
                                    "      ELSE (try_cast(summ.attributes_matched AS float) * 100) / try_cast(summ.attributes_checked AS float)\r\n",
                                    "    END, \r\n",
                                    "    2\r\n",
                                    "  ) AS attributes_matched_percentage,\r\n",
                                    "  CASE \r\n",
                                    "    WHEN summ.status = True THEN 100.0\r\n",
                                    "    WHEN summ.status = False THEN 0.0\r\n",
                                    "    ELSE NULL\r\n",
                                    "  END AS pass_test_percentage,\r\n",
                                    "  agg.remarks,\r\n",
                                    "  agg.execution_date,\r\n",
                                    "  CASE \r\n",
                                    "    WHEN summ.status = False THEN 1 \r\n",
                                    "    ELSE 0 \r\n",
                                    "  END AS fail_records,\r\n",
                                    "  CASE \r\n",
                                    "    WHEN summ.status = True THEN 1 \r\n",
                                    "    ELSE 0 \r\n",
                                    "  END AS pass_records\r\n",
                                    "FROM pybrv.pybrv_meta.pydpc_rule_summary summ\r\n",
                                    "LEFT JOIN attribute_result_agg agg ON agg.execution_id = summ.execution_id;"
                                ]
                                }
                            ],
                            "pages": [
                                {
                                "name": "e8b3d010",
                                "displayName": "Business Rule Check Result",
                                "layout": [
                                    {
                                    "widget": {
                                        "name": "62b8e694",
                                        "multilineTextboxSpec": {
                                        "lines": [
                                            "# Business Rule Check Result"
                                        ]
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 0,
                                        "width": 6,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "15ce5df3",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "Test_Status",
                                                "expression": "`Test_Status`"
                                                },
                                                {
                                                "name": "daily(last_modified_ts)",
                                                "expression": "DATE_TRUNC(\"DAY\", `last_modified_ts`)"
                                                },
                                                {
                                                "name": "count(Test_Status)",
                                                "expression": "COUNT(`Test_Status`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "daily(last_modified_ts)",
                                            "format": {
                                                "type": "date-time",
                                                "date": "locale-short-month",
                                                "time": "locale-hour-minute",
                                                "leadingZeros": False
                                            },
                                            "axis": {
                                                "labelAngle": 0
                                            },
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "natural-order-reversed"
                                                }
                                            },
                                            "displayName": "Execution Date"
                                            },
                                            "y": {
                                            "fieldName": "count(Test_Status)",
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "displayName": "# Tests"
                                            },
                                            "color": {
                                            "fieldName": "Test_Status",
                                            "scale": {
                                                "type": "categorical",
                                                "mappings": [
                                                {
                                                    "value": "Failed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 4
                                                    }
                                                },
                                                {
                                                    "value": "Passed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 3
                                                    }
                                                }
                                                ]
                                            },
                                            "displayName": "Status"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Test Cases Execution Over time",
                                            "headerAlignment": "center"
                                        },
                                        "mark": {
                                            "colors": [
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 5
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 6
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 7
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 8
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 9
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            }
                                            ]
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 5,
                                        "width": 6,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "7653cdeb",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_team_name",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "team_name",
                                                "expression": "`team_name`"
                                                },
                                                {
                                                "name": "team_name_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "team_name",
                                                "displayName": "team_name",
                                                "queryName": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_team_name"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Team Name",
                                            "showDescription": False,
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 1,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "c3444509",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_data_domain",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "data_domain",
                                                "expression": "`data_domain`"
                                                },
                                                {
                                                "name": "data_domain_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "data_domain",
                                                "displayName": "data_domain",
                                                "queryName": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_data_domain"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Data Domain",
                                            "showDescription": False,
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 2,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "e6f5e337",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_table_checked",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "table_checked",
                                                "expression": "`table_checked`"
                                                },
                                                {
                                                "name": "table_checked_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "table_checked",
                                                "displayName": "table_checked",
                                                "queryName": "dashboards/01f035708823138c90cd50bec36e2954/datasets/01f03572ff6e1956bd67705b244e3448_table_checked"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Table Name",
                                            "showDescription": False,
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 2,
                                        "y": 1,
                                        "width": 2,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "2d515e90",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "unique_rule_identifier",
                                                "expression": "`unique_rule_identifier`"
                                                },
                                                {
                                                "name": "team_name",
                                                "expression": "`team_name`"
                                                },
                                                {
                                                "name": "rule_name",
                                                "expression": "`rule_name`"
                                                },
                                                {
                                                "name": "data_domain",
                                                "expression": "`data_domain`"
                                                },
                                                {
                                                "name": "Test_Status",
                                                "expression": "`Test_Status`"
                                                },
                                                {
                                                "name": "severity",
                                                "expression": "`severity`"
                                                },
                                                {
                                                "name": "rule_category",
                                                "expression": "`rule_category`"
                                                },
                                                {
                                                "name": "table_checked",
                                                "expression": "`table_checked`"
                                                },
                                                {
                                                "name": "bookmark_column_name",
                                                "expression": "`bookmark_column_name`"
                                                },
                                                {
                                                "name": "bookmark_start_date",
                                                "expression": "`bookmark_start_date`"
                                                },
                                                {
                                                "name": "bookmark_end_date",
                                                "expression": "`bookmark_end_date`"
                                                },
                                                {
                                                "name": "pass_record_count",
                                                "expression": "`pass_record_count`"
                                                },
                                                {
                                                "name": "fail_record_count",
                                                "expression": "`fail_record_count`"
                                                },
                                                {
                                                "name": "failed_keys",
                                                "expression": "`failed_keys`"
                                                },
                                                {
                                                "name": "failed_query",
                                                "expression": "`failed_query`"
                                                },
                                                {
                                                "name": "test_case_comments",
                                                "expression": "`test_case_comments`"
                                                },
                                                {
                                                "name": "remarks",
                                                "expression": "`remarks`"
                                                },
                                                {
                                                "name": "last_modified_ts",
                                                "expression": "`last_modified_ts`"
                                                }
                                            ],
                                            "disaggregated": True
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 1,
                                        "widgetType": "table",
                                        "encodings": {
                                            "columns": [
                                            {
                                                "fieldName": "unique_rule_identifier",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 0,
                                                "title": "Unique Rule Identifier",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "unique_rule_identifier"
                                            },
                                            {
                                                "fieldName": "team_name",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 2,
                                                "title": "Team Name",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "team_name"
                                            },
                                            {
                                                "fieldName": "rule_name",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 3,
                                                "title": "Rule Name",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "rule_name"
                                            },
                                            {
                                                "fieldName": "data_domain",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 4,
                                                "title": "Data Domain",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "data_domain"
                                            },
                                            {
                                                "fieldName": "Test_Status",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 5,
                                                "title": "Test Status",
                                                "allowSearch": False,
                                                "alignContent": "left",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "Test_Status"
                                            },
                                            {
                                                "fieldName": "severity",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 6,
                                                "title": "Severity",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "severity"
                                            },
                                            {
                                                "fieldName": "rule_category",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 7,
                                                "title": "Rule Category",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "rule_category"
                                            },
                                            {
                                                "fieldName": "table_checked",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 8,
                                                "title": "Table Checked",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "table_checked"
                                            },
                                            {
                                                "fieldName": "bookmark_column_name",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 9,
                                                "title": "Bookmark Column Name",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "bookmark_column_name"
                                            },
                                            {
                                                "fieldName": "bookmark_start_date",
                                                "dateTimeFormat": "YYYY-MM-DD",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "date",
                                                "displayAs": "datetime",
                                                "visible": True,
                                                "order": 10,
                                                "title": "Bookmark Start Date",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "bookmark_start_date"
                                            },
                                            {
                                                "fieldName": "bookmark_end_date",
                                                "dateTimeFormat": "YYYY-MM-DD",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "date",
                                                "displayAs": "datetime",
                                                "visible": True,
                                                "order": 11,
                                                "title": "Bookmark End Date",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "bookmark_end_date"
                                            },
                                            {
                                                "fieldName": "pass_record_count",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 13,
                                                "title": "Pass Records",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "pass_record_count"
                                            },
                                            {
                                                "fieldName": "fail_record_count",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 14,
                                                "title": "Fail Records",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "fail_record_count"
                                            },
                                            {
                                                "fieldName": "failed_keys",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 17,
                                                "title": "Failed Keys",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "failed_keys"
                                            },
                                            {
                                                "fieldName": "failed_query",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 18,
                                                "title": "Query",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "failed_query"
                                            },
                                            {
                                                "fieldName": "test_case_comments",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 19,
                                                "title": "Comments",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "test_case_comments"
                                            },
                                            {
                                                "fieldName": "remarks",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 20,
                                                "title": "Remarks",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "remarks"
                                            },
                                            {
                                                "fieldName": "last_modified_ts",
                                                "dateTimeFormat": "YYYY-MM-DD HH:mm:ss.SSS",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "datetime",
                                                "displayAs": "datetime",
                                                "visible": True,
                                                "order": 21,
                                                "title": "Last Modified Time",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "last_modified_ts"
                                            }
                                            ]
                                        },
                                        "invisibleColumns": [
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "execution_id",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 1,
                                            "title": "execution_id",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "status",
                                            "type": "string",
                                            "displayAs": "string",
                                            "order": 12,
                                            "title": "status",
                                            "allowSearch": False,
                                            "alignContent": "left",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "pass_percentage",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 15,
                                            "title": "pass_percentage",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "threshold",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 16,
                                            "title": "threshold",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "passed_test",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 22,
                                            "title": "passed_test",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "failed_test",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 23,
                                            "title": "failed_test",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0.00",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "passed_percentage",
                                            "type": "float",
                                            "displayAs": "number",
                                            "order": 24,
                                            "title": "passed_percentage",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "rule_Category",
                                            "type": "string",
                                            "displayAs": "string",
                                            "order": 25,
                                            "title": "rule_Category",
                                            "allowSearch": False,
                                            "alignContent": "left",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            }
                                        ],
                                        "allowHTMLByDefault": False,
                                        "itemsPerPage": 10,
                                        "paginationSize": "default",
                                        "condensed": True,
                                        "withRowNumber": False,
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Test case Execution",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 29,
                                        "width": 6,
                                        "height": 8
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "d8425932",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "count(status)",
                                                "expression": "COUNT(`status`)"
                                                }
                                            ],
                                            "filters": [
                                                {
                                                "expression": "`last_modified_ts` IN (`last_modified_ts`) OR True"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "count(status)",
                                            "displayName": "Count of status"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Tests",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "c119600d",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "sum(passed_test)",
                                                "expression": "SUM(`passed_test`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(passed_test)",
                                            "displayName": "Sum of passed_test"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": " # Pass Tests",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 1,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "87a93e61",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "sum(failed_test)",
                                                "expression": "SUM(`failed_test`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(failed_test)",
                                            "displayName": "Sum of failed_test"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Fail Tests ",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 2,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "d949a491",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "avg(passed_percentage)",
                                                "expression": "AVG(`passed_percentage`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "avg(passed_percentage)",
                                            "displayName": "Average passed_percentage"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Pass Percentage (%)",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 4,
                                        "y": 3,
                                        "width": 2,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "6d988d1e",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "minutely(last_modified_ts)",
                                                "expression": "DATE_TRUNC(\"MINUTE\", `last_modified_ts`)"
                                                },
                                                {
                                                "name": "sum(fail_record_count)",
                                                "expression": "SUM(`fail_record_count`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "minutely(last_modified_ts)",
                                            "axis": {
                                                "labelAngle": 0
                                            },
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "natural-order-reversed"
                                                }
                                            },
                                            "displayName": "Execution Date"
                                            },
                                            "y": {
                                            "fieldName": "sum(fail_record_count)",
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "displayName": "# Fail Records"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Failed Record Count on Each Execution",
                                            "headerAlignment": "center"
                                        },
                                        "mark": {
                                            "colors": [
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 2
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 5
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 6
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 7
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 8
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 9
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            }
                                            ]
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 23,
                                        "width": 6,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "ebfe3fce",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "Test_Status",
                                                "expression": "`Test_Status`"
                                                },
                                                {
                                                "name": "severity",
                                                "expression": "`severity`"
                                                },
                                                {
                                                "name": "count(severity)",
                                                "expression": "COUNT(`severity`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "severity",
                                            "scale": {
                                                "type": "categorical"
                                            },
                                            "axis": {
                                                "hideTitle": True
                                            },
                                            "displayName": "severity"
                                            },
                                            "y": {
                                            "fieldName": "count(severity)",
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "displayName": "Severity"
                                            },
                                            "color": {
                                            "fieldName": "Test_Status",
                                            "scale": {
                                                "type": "categorical",
                                                "mappings": [
                                                {
                                                    "value": "Failed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 4
                                                    }
                                                },
                                                {
                                                    "value": "Passed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 3
                                                    }
                                                }
                                                ]
                                            },
                                            "displayName": "Status"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "headerAlignment": "center",
                                            "title": "Severity"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 3,
                                        "y": 11,
                                        "width": 3,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "fd529a35",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "Test_Status",
                                                "expression": "`Test_Status`"
                                                },
                                                {
                                                "name": "rule_category",
                                                "expression": "`rule_category`"
                                                },
                                                {
                                                "name": "count(rule_category)",
                                                "expression": "COUNT(`rule_category`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "rule_category",
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "y"
                                                }
                                            },
                                            "axis": {
                                                "hideTitle": True,
                                                "labelAngle": 0
                                            },
                                            "displayName": "Rule Category"
                                            },
                                            "y": {
                                            "fieldName": "count(rule_category)",
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "axis": {
                                                "hideTitle": True
                                            },
                                            "displayName": "Count of rule_category"
                                            },
                                            "color": {
                                            "fieldName": "Test_Status",
                                            "scale": {
                                                "type": "categorical",
                                                "mappings": [
                                                {
                                                    "value": "Failed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 4
                                                    }
                                                },
                                                {
                                                    "value": "Passed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 3
                                                    }
                                                }
                                                ]
                                            },
                                            "displayName": "Status"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "headerAlignment": "center",
                                            "title": "Rule Category"
                                        },
                                        "mark": {
                                            "colors": [
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 2
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 5
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 6
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 7
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 8
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 9
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            }
                                            ]
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 11,
                                        "width": 3,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "f373ca4c",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f04c1d17a5141f9b78e2b1a768ecf6_last_modified_ts",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "last_modified_ts",
                                                "expression": "`last_modified_ts`"
                                                },
                                                {
                                                "name": "last_modified_ts_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-date-range-picker",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "last_modified_ts",
                                                "displayName": "last_modified_ts",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f04c1d17a5141f9b78e2b1a768ecf6_last_modified_ts"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Execution Date Range",
                                            "showDescription": False,
                                            "headerAlignment": "center"
                                        },
                                        "selection": {
                                            "defaultSelection": {
                                            "range": {
                                                "dataType": "DATETIME",
                                                "min": {
                                                "value": "now-30d/d"
                                                },
                                                "max": {
                                                "value": "now/d"
                                                }
                                            }
                                            }
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 4,
                                        "y": 1,
                                        "width": 2,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "113fbf91",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "sum(fail_record_count)",
                                                "expression": "SUM(`fail_record_count`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(fail_record_count)",
                                            "displayName": "Sum of fail_record_count"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Fail  Records",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 3,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "819945a8",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "67b76837",
                                            "fields": [
                                                {
                                                "name": "Test_Status",
                                                "expression": "`Test_Status`"
                                                },
                                                {
                                                "name": "count(*)",
                                                "expression": "COUNT(`*`)"
                                                },
                                                {
                                                "name": "rule_name",
                                                "expression": "`rule_name`"
                                                }
                                            ],
                                            "filters": [
                                                {
                                                "expression": "`rule_name` IN (`rule_name`) OR True"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "count(*)",
                                            "axis": {
                                                "labelAngle": 0
                                            },
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "displayName": "Tests"
                                            },
                                            "y": {
                                            "fieldName": "rule_name",
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "x-reversed"
                                                }
                                            },
                                            "displayName": "Rules"
                                            },
                                            "color": {
                                            "fieldName": "Test_Status",
                                            "scale": {
                                                "type": "categorical",
                                                "mappings": [
                                                {
                                                    "value": "Failed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 4
                                                    }
                                                },
                                                {
                                                    "value": "Passed",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 3
                                                    }
                                                }
                                                ]
                                            },
                                            "displayName": "Test_Status"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 17,
                                        "width": 6,
                                        "height": 6
                                    }
                                    }
                                ],
                                "pageType": "PAGE_TYPE_CANVAS"
                                },
                                {
                                "name": "2ea53383",
                                "displayName": "Data Parity Check",
                                "layout": [
                                    {
                                    "widget": {
                                        "name": "482222bd",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_rule_name",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "rule_name",
                                                "expression": "`rule_name`"
                                                },
                                                {
                                                "name": "rule_name_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "rule_name",
                                                "displayName": "rule_name",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_rule_name"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Rule Name"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 1,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "d438ac66",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_execution_id",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "execution_id",
                                                "expression": "`execution_id`"
                                                },
                                                {
                                                "name": "execution_id_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "execution_id",
                                                "displayName": "execution_id",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_execution_id"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Execution ID"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 2,
                                        "y": 2,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "3b98c182",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_table_name",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "table_name",
                                                "expression": "`table_name`"
                                                },
                                                {
                                                "name": "table_name_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "table_name",
                                                "displayName": "table_name",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_table_name"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Table Name"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 2,
                                        "y": 1,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "e6398133",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_data_domain",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "data_domain",
                                                "expression": "`data_domain`"
                                                },
                                                {
                                                "name": "data_domain_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-single-select",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "data_domain",
                                                "displayName": "data_domain",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_data_domain"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Data Domain"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 2,
                                        "width": 2,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "68a19097",
                                        "queries": [
                                        {
                                            "name": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_execution_date",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "execution_date",
                                                "expression": "`execution_date`"
                                                },
                                                {
                                                "name": "execution_date_associativity",
                                                "expression": "COUNT_IF(`associative_filter_predicate_group`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "filter-date-range-picker",
                                        "encodings": {
                                            "fields": [
                                            {
                                                "fieldName": "execution_date",
                                                "displayName": "execution_date",
                                                "queryName": "dashboards/01f04c1d17a41c68ae6eec939fba24d5/datasets/01f05c949c4417cd875839cfeefd9157_execution_date"
                                            }
                                            ]
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Execution Date Range",
                                            "headerAlignment": "center"
                                        },
                                        "selection": {
                                            "defaultSelection": {
                                            "range": {
                                                "dataType": "DATETIME",
                                                "min": {
                                                "value": "now-7d/d"
                                                },
                                                "max": {
                                                "value": "now/d"
                                                }
                                            }
                                            }
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 4,
                                        "y": 1,
                                        "width": 2,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "02eaaeec",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "count(execution_id)",
                                                "expression": "COUNT(`execution_id`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "count(execution_id)",
                                            "displayName": "Count of execution_id"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Tests",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "08f32e81",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "sum(fail_records)",
                                                "expression": "SUM(`fail_records`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(fail_records)",
                                            "displayName": "Sum of fail_records"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Fail Tests",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 1,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "39cfa845",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "avg(pass_test_percentage)",
                                                "expression": "AVG(`pass_test_percentage`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "avg(pass_test_percentage)",
                                            "displayName": "Average pass_test_percentage"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Pass Percentage (%)",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 2,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "b1aa7b63",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "sum(attributes_check)",
                                                "expression": "SUM(`attributes_check`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(attributes_check)",
                                            "format": {
                                                "type": "number-plain",
                                                "abbreviation": "compact",
                                                "decimalPlaces": {
                                                "type": "max",
                                                "places": 2
                                                }
                                            },
                                            "displayName": "Sum of attributes_check"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Checked Attribute",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 3,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "68d3af33",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "sum(attributes_not_matched)",
                                                "expression": "SUM(`attributes_not_matched`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "sum(attributes_not_matched)",
                                            "displayName": "Sum of attributes_not_matched"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "# Fail Attributes",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 4,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "2c9d0227",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "avg(attributes_matched_percentage)",
                                                "expression": "AVG(`attributes_matched_percentage`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 2,
                                        "widgetType": "counter",
                                        "encodings": {
                                            "value": {
                                            "fieldName": "avg(attributes_matched_percentage)",
                                            "displayName": "Average attributes_matched_percentage"
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Pass Attribute (%)",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 5,
                                        "y": 3,
                                        "width": 1,
                                        "height": 2
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "e2022d26",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "status",
                                                "expression": "`status`"
                                                },
                                                {
                                                "name": "daily(execution_date)",
                                                "expression": "DATE_TRUNC(\"DAY\", `execution_date`)"
                                                },
                                                {
                                                "name": "count(execution_id)",
                                                "expression": "COUNT(`execution_id`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "fieldName": "daily(execution_date)",
                                            "axis": {
                                                "hideLabels": False,
                                                "hideTitle": False,
                                                "labelAngle": 0
                                            },
                                            "format": {
                                                "type": "date-time",
                                                "date": "locale-short-month",
                                                "time": "locale-hour-minute"
                                            },
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "natural-order-reversed"
                                                }
                                            },
                                            "displayName": "Execution Date"
                                            },
                                            "y": {
                                            "fieldName": "count(execution_id)",
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "displayName": "# Tests"
                                            },
                                            "color": {
                                            "fieldName": "status",
                                            "scale": {
                                                "type": "categorical",
                                                "mappings": [
                                                {
                                                    "value": "True",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 3
                                                    }
                                                },
                                                {
                                                    "value": "False",
                                                    "color": {
                                                    "themeColorType": "visualizationColors",
                                                    "position": 4
                                                    }
                                                }
                                                ]
                                            },
                                            "legend": {
                                                "position": "bottom"
                                            },
                                            "displayName": "status"
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "headerAlignment": "center",
                                            "title": "Test Case Execution Over Time"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 5,
                                        "width": 6,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "42b861ed",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "sum(records_matched)",
                                                "expression": "SUM(`records_matched`)"
                                                },
                                                {
                                                "name": "sum(records_not_matched)",
                                                "expression": "SUM(`records_not_matched`)"
                                                },
                                                {
                                                "name": "secondly(execution_date)",
                                                "expression": "DATE_TRUNC(\"SECOND\", `execution_date`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "fields": [
                                                {
                                                "fieldName": "sum(records_matched)",
                                                "displayName": "Records Matched"
                                                },
                                                {
                                                "fieldName": "sum(records_not_matched)",
                                                "displayName": "Records Not Matched"
                                                }
                                            ],
                                            "axis": {
                                                "title": "# Records"
                                            }
                                            },
                                            "y": {
                                            "fieldName": "secondly(execution_date)",
                                            "axis": {
                                                "labelAngle": 0
                                            },
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "natural-order-reversed"
                                                }
                                            },
                                            "displayName": "Executions"
                                            },
                                            "color": {
                                            "legend": {
                                                "position": "bottom"
                                            }
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "headerAlignment": "center",
                                            "title": "Records Over Execution"
                                        },
                                        "mark": {
                                            "colors": [
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 5
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 6
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 7
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 8
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 9
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            }
                                            ]
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 11,
                                        "width": 3,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "8f220a6e",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "execution_id",
                                                "expression": "`execution_id`"
                                                },
                                                {
                                                "name": "unique_rule_identifier",
                                                "expression": "`unique_rule_identifier`"
                                                },
                                                {
                                                "name": "execution_date",
                                                "expression": "`execution_date`"
                                                },
                                                {
                                                "name": "rule_name",
                                                "expression": "`rule_name`"
                                                },
                                                {
                                                "name": "table_name",
                                                "expression": "`table_name`"
                                                },
                                                {
                                                "name": "data_domain",
                                                "expression": "`data_domain`"
                                                },
                                                {
                                                "name": "status",
                                                "expression": "`status`"
                                                },
                                                {
                                                "name": "source_records",
                                                "expression": "`source_records`"
                                                },
                                                {
                                                "name": "target_found",
                                                "expression": "`target_found`"
                                                },
                                                {
                                                "name": "target_rows_matched",
                                                "expression": "`target_rows_matched`"
                                                },
                                                {
                                                "name": "records_not_matched",
                                                "expression": "`records_not_matched`"
                                                },
                                                {
                                                "name": "percent_rows_matched",
                                                "expression": "`percent_rows_matched`"
                                                },
                                                {
                                                "name": "start_date",
                                                "expression": "`start_date`"
                                                },
                                                {
                                                "name": "end_date",
                                                "expression": "`end_date`"
                                                },
                                                {
                                                "name": "attributes_checked",
                                                "expression": "`attributes_checked`"
                                                },
                                                {
                                                "name": "attributes_matched",
                                                "expression": "`attributes_matched`"
                                                },
                                                {
                                                "name": "attributes_not_matched",
                                                "expression": "`attributes_not_matched`"
                                                },
                                                {
                                                "name": "comments",
                                                "expression": "`comments`"
                                                },
                                                {
                                                "name": "remarks",
                                                "expression": "`remarks`"
                                                }
                                            ],
                                            "disaggregated": True
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 1,
                                        "widgetType": "table",
                                        "encodings": {
                                            "columns": [
                                            {
                                                "fieldName": "execution_id",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 0,
                                                "title": "Execution ID",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "execution_id"
                                            },
                                            {
                                                "fieldName": "unique_rule_identifier",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 1,
                                                "title": "Unique Rule Identifier",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "unique_rule_identifier"
                                            },
                                            {
                                                "fieldName": "execution_date",
                                                "dateTimeFormat": "YYYY-MM-DD HH:mm:ss.SSS",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "datetime",
                                                "displayAs": "datetime",
                                                "visible": True,
                                                "order": 2,
                                                "title": "Execution Date Time",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "execution_date"
                                            },
                                            {
                                                "fieldName": "rule_name",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 3,
                                                "title": "Rule Name",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "rule_name"
                                            },
                                            {
                                                "fieldName": "table_name",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 4,
                                                "title": "Table Name",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "table_name"
                                            },
                                            {
                                                "fieldName": "data_domain",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 5,
                                                "title": "Data Domain",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "data_domain"
                                            },
                                            {
                                                "fieldName": "status",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 6,
                                                "title": "Status",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "status"
                                            },
                                            {
                                                "fieldName": "source_records",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 7,
                                                "title": "Total Records Checked",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "source_records"
                                            },
                                            {
                                                "fieldName": "target_found",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 8,
                                                "title": "Target Records Found",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "target_found"
                                            },
                                            {
                                                "fieldName": "target_rows_matched",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 9,
                                                "title": "Target Records Matched",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "target_rows_matched"
                                            },
                                            {
                                                "fieldName": "records_not_matched",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 10,
                                                "title": "Records Not Matched",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "records_not_matched"
                                            },
                                            {
                                                "fieldName": "percent_rows_matched",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 11,
                                                "title": "Matched Records (%)",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "percent_rows_matched"
                                            },
                                            {
                                                "fieldName": "start_date",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 12,
                                                "title": "Bookmark Start Date",
                                                "allowSearch": False,
                                                "alignContent": "left",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "start_date"
                                            },
                                            {
                                                "fieldName": "end_date",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 13,
                                                "title": "Bookmark End Date",
                                                "allowSearch": False,
                                                "alignContent": "left",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "end_date"
                                            },
                                            {
                                                "fieldName": "attributes_checked",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 14,
                                                "title": "Attributes Checked",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "attributes_checked"
                                            },
                                            {
                                                "fieldName": "attributes_matched",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 15,
                                                "title": "Attributes Matched",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "attributes_matched"
                                            },
                                            {
                                                "fieldName": "attributes_not_matched",
                                                "numberFormat": "0",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "integer",
                                                "displayAs": "number",
                                                "visible": True,
                                                "order": 16,
                                                "title": "Attributes Not Matched",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "attributes_not_matched"
                                            },
                                            {
                                                "fieldName": "comments",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "string",
                                                "displayAs": "string",
                                                "visible": True,
                                                "order": 17,
                                                "title": "Comments",
                                                "allowSearch": False,
                                                "alignContent": "center",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "comments"
                                            },
                                            {
                                                "fieldName": "remarks",
                                                "booleanValues": [
                                                "False",
                                                "True"
                                                ],
                                                "imageUrlTemplate": "{{ @ }}",
                                                "imageTitleTemplate": "{{ @ }}",
                                                "imageWidth": "",
                                                "imageHeight": "",
                                                "linkUrlTemplate": "{{ @ }}",
                                                "linkTextTemplate": "{{ @ }}",
                                                "linkTitleTemplate": "{{ @ }}",
                                                "linkOpenInNewTab": True,
                                                "type": "complex",
                                                "displayAs": "json",
                                                "visible": True,
                                                "order": 18,
                                                "title": "Remarks",
                                                "allowSearch": False,
                                                "alignContent": "left",
                                                "allowHTML": False,
                                                "highlightLinks": False,
                                                "useMonospaceFont": False,
                                                "preserveWhitespace": False,
                                                "displayName": "remarks"
                                            }
                                            ]
                                        },
                                        "invisibleColumns": [
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "attributes_match",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 19,
                                            "title": "attributes_match",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "attributes_check",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 20,
                                            "title": "attributes_check",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "records_matched",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 21,
                                            "title": "records_matched",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "percent_records_found",
                                            "type": "string",
                                            "displayAs": "string",
                                            "order": 22,
                                            "title": "Matched Records (%)",
                                            "allowSearch": False,
                                            "alignContent": "center",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0.00",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "attributes_matched_percentage",
                                            "type": "float",
                                            "displayAs": "number",
                                            "order": 23,
                                            "title": "attributes_matched_percentage",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "pass_test_percentage",
                                            "type": "decimal",
                                            "displayAs": "number",
                                            "order": 24,
                                            "title": "pass_test_percentage",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "fail_records",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 25,
                                            "title": "fail_records",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            },
                                            {
                                            "numberFormat": "0",
                                            "booleanValues": [
                                                "False",
                                                "True"
                                            ],
                                            "imageUrlTemplate": "{{ @ }}",
                                            "imageTitleTemplate": "{{ @ }}",
                                            "imageWidth": "",
                                            "imageHeight": "",
                                            "linkUrlTemplate": "{{ @ }}",
                                            "linkTextTemplate": "{{ @ }}",
                                            "linkTitleTemplate": "{{ @ }}",
                                            "linkOpenInNewTab": True,
                                            "name": "pass_records",
                                            "type": "integer",
                                            "displayAs": "number",
                                            "order": 26,
                                            "title": "pass_records",
                                            "allowSearch": False,
                                            "alignContent": "right",
                                            "allowHTML": False,
                                            "highlightLinks": False,
                                            "useMonospaceFont": False,
                                            "preserveWhitespace": False
                                            }
                                        ],
                                        "allowHTMLByDefault": False,
                                        "itemsPerPage": 15,
                                        "paginationSize": "default",
                                        "condensed": True,
                                        "withRowNumber": False,
                                        "frame": {
                                            "showTitle": True,
                                            "title": "Test Case Execution",
                                            "headerAlignment": "center"
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 17,
                                        "width": 6,
                                        "height": 7
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "18428ec1",
                                        "queries": [
                                        {
                                            "name": "main_query",
                                            "query": {
                                            "datasetName": "f411e3c1",
                                            "fields": [
                                                {
                                                "name": "sum(attributes_match)",
                                                "expression": "SUM(`attributes_match`)"
                                                },
                                                {
                                                "name": "sum(attributes_not_matched)",
                                                "expression": "SUM(`attributes_not_matched`)"
                                                },
                                                {
                                                "name": "secondly(execution_date)",
                                                "expression": "DATE_TRUNC(\"SECOND\", `execution_date`)"
                                                }
                                            ],
                                            "disaggregated": False
                                            }
                                        }
                                        ],
                                        "spec": {
                                        "version": 3,
                                        "widgetType": "bar",
                                        "encodings": {
                                            "x": {
                                            "scale": {
                                                "type": "quantitative"
                                            },
                                            "fields": [
                                                {
                                                "fieldName": "sum(attributes_match)",
                                                "displayName": "Attributes Matched"
                                                },
                                                {
                                                "fieldName": "sum(attributes_not_matched)",
                                                "displayName": "Attributes Not Matched"
                                                }
                                            ],
                                            "axis": {
                                                "title": "# Attributes"
                                            }
                                            },
                                            "y": {
                                            "fieldName": "secondly(execution_date)",
                                            "axis": {
                                                "labelAngle": 0
                                            },
                                            "scale": {
                                                "type": "categorical",
                                                "sort": {
                                                "by": "natural-order-reversed"
                                                }
                                            },
                                            "displayName": "Executions"
                                            },
                                            "color": {
                                            "legend": {
                                                "position": "bottom"
                                            }
                                            },
                                            "label": {
                                            "show": True
                                            }
                                        },
                                        "frame": {
                                            "showTitle": True,
                                            "headerAlignment": "center",
                                            "title": "Attributes Over Execution"
                                        },
                                        "mark": {
                                            "colors": [
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 3
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 4
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 5
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 6
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 7
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 8
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 9
                                            },
                                            {
                                                "themeColorType": "visualizationColors",
                                                "position": 10
                                            }
                                            ]
                                        }
                                        }
                                    },
                                    "position": {
                                        "x": 3,
                                        "y": 11,
                                        "width": 3,
                                        "height": 6
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "2045d338",
                                        "multilineTextboxSpec": {
                                        "lines": [
                                            "# Data Parity Check"
                                        ]
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 0,
                                        "width": 6,
                                        "height": 1
                                    }
                                    },
                                    {
                                    "widget": {
                                        "name": "c82eb74f",
                                        "multilineTextboxSpec": {
                                        "lines": [
                                            "***Note :***\n",
                                            "To identify which records are failing data parity validations, please refer to the table ***pydpc_attribute_mismatch_details***. This table contains detailed information about attribute-level mismatches, including the specific fields and values that did not match during validation."
                                        ]
                                        }
                                    },
                                    "position": {
                                        "x": 0,
                                        "y": 24,
                                        "width": 6,
                                        "height": 1
                                    }
                                    }
                                ],
                                "pageType": "PAGE_TYPE_CANVAS"
                                }
                            ],
                            "uiSettings": {
                                "theme": {
                                "canvasBackgroundColor": {
                                    "light": "#FFFFFF",
                                    "dark": "#11171C"
                                },
                                "widgetBackgroundColor": {
                                    "light": "#FFFFFF",
                                    "dark": "#11171C"
                                },
                                "fontColor": {
                                    "light": "#11171C",
                                    "dark": "#E8ECF0"
                                },
                                "selectionColor": {
                                    "light": "#2272B4",
                                    "dark": "#8ACAFF"
                                },
                                "visualizationColors": [
                                    "#077A9D",
                                    "#FFAB00",
                                    "#4DB893",
                                    "#E06357",
                                    "#8BCAE7",
                                    "#AB4057",
                                    "#99DDB4",
                                    "#FCA4A1",
                                    "#919191",
                                    "#BF7080"
                                ],
                                "widgetHeaderAlignment": "LEFT"
                                }
                            }
                            }

                    },
                    "sql": {
                        "data_parity_sql": {
                            "source.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;""",
                            "target.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;"""
                        }
                    }
                }
            }
        }

        # ✅ Create actual folders/files
        self._create_items(base_path, structure)
        print(f"✅ Data Parity structure created at: {os.path.abspath(base_path)}")

    def _create_items(self, path, items):
        """
        Helper function to create directories and files.
        Handles both local and Databricks (DBFS).
        """
        for name, content in items.items():
            new_path = os.path.join(path, name)

            # If running in Databricks, map paths to DBFS
            if self.engine_type == "databricks":
                if new_path.startswith("/Workspace"):
                    raise NotImplementedError("Writing to /Workspace requires Databricks Workspace API.")
                elif not new_path.startswith("/dbfs"):
                    new_path = f"/dbfs{new_path}"

            if isinstance(content, dict):
                if name.endswith(".json"):
                    os.makedirs(path, exist_ok=True)
                    with open(new_path, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=4)
                else:
                    os.makedirs(new_path, exist_ok=True)
                    self._create_items(new_path, content)

            elif isinstance(content, list):
                with open(new_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4)

            elif isinstance(content, str):
                os.makedirs(path, exist_ok=True)
                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(content)

            else:
                raise TypeError(f"Unsupported content type {type(content)} for {new_path}")
