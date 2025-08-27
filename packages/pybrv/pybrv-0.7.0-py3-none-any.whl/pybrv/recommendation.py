# pybrv_recommendation.py

from openai import OpenAI
from pyspark.sql.functions import col, countDistinct, count, min, max
from typing import List
from pyspark.sql import SparkSession
import os

# class pybrv_recommendation:
#     def __init__(self,dbutils,spark: SparkSession):
#         self.spark = spark.getActiveSession()
#         self.DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
#         self.client = OpenAI(
#             api_key=self.DATABRICKS_TOKEN,
#             base_url="https://adb-7837506776017759.19.azuredatabricks.net/serving-endpoints"
#         )
class PybrvRecommendation:
    def __init__(self, spark: SparkSession, dbutils,base_url,models):
        self.spark = spark.getActiveSession()
        self.dbutils = dbutils
        self.base_url = base_url
        self.models = models
        self.DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
        self.client = OpenAI(
            api_key=self.DATABRICKS_TOKEN,
            base_url=self.base_url
        )

    def detect_relationships(self, dfs: dict) -> list:
        """Detect potential foreign key relationships between tables."""
        relationships = []
        for src_table, src_df in dfs.items():
            for src_col in src_df.columns:
                for tgt_table, tgt_df in dfs.items():
                    if src_table == tgt_table:
                        continue
                    if src_col in tgt_df.columns:
                        src_unique = src_df.select(src_col).distinct().count()
                        join_match = src_df.join(tgt_df, on=src_col, how="left_anti").count()
                        if src_unique > 1 and join_match == 0:
                            relationships.append((src_table, src_col, tgt_table, src_col))
        return relationships

    def analyze_multiple_tables(self, table_names: List[str]) -> str:
        dfs = {table: self.spark.table(table) for table in table_names}
        report = []

        for table_name, df in dfs.items():
            report.append(f"\n=== Table: `{table_name}` ===")
            for col_name, dtype in df.dtypes:
                stats = df.select(
                    count("*").alias("total_rows"),
                    count(col(col_name)).alias("non_nulls"),
                    countDistinct(col(col_name)).alias("unique_values"),
                    min(col(col_name)).alias("min_val"),
                    max(col(col_name)).alias("max_val")
                ).first()

                report.append(f"""
  Column: `{col_name}`
    - Type: {dtype}
    - Non-null Count: {stats['non_nulls']}
    - Unique Values: {stats['unique_values']}
    - Min: {stats['min_val']}
    - Max: {stats['max_val']}
                """)

        relationships = self.detect_relationships(dfs)
        report.append("\n=== Detected Relationships (FK-like) ===")
        if relationships:
            for src_table, src_col, tgt_table, tgt_col in relationships:
                report.append(f"- `{src_table}.{src_col}` → `{tgt_table}.{tgt_col}` (Valid)")
        else:
            report.append("No relationships detected.")

        return "\n".join(report)

    def get_test_cases_for_tables(self, table_names: list, metadata: str) -> str:
        prompt = f"""
        You are a data quality expert.
    
        Your task is to review the metadata of the tables `{', '.join(table_names)}` and generate data quality test cases as SQL queries. Suggest test cases to validate data integrity, consistency, and relationships.
        This is a Business rule validator so give the test cases according to check the business rules.
        Also 

        ### Requirements:
        - Give the pass sql and fail sql for each test cases.
            -Pass sql should return all records which are matching the condition.
            -Fail sql should return all records which are not matching the condition. 
        - Also give the severity of each test case (low, medium, high, critical).
        - Cover at least two test cases from each of the following categories:
        - Null checks
        - Uniqueness checks
        - Completeness checks
        - Duplicate checks
        - Accuracy checks
        - validation checks
        - Output format:
            - Each test case should be a commented explanation followed by the SQL query.
        
        -For Each Test Cases create a rule configuration in json format with the following keys:
            -"RULE_ID": 1,
                "RULE_NAME": "",
                "FAIL_SQL": "",
                "PASS_SQL":"",
                "SEVERITY":"",
                "RULE_CATEGORY":"",
                "TABLES_CHECKED": "",
                "INVENTORY": "",
                "COMMENTS": "",
                "PASS_THRESHOLD": 
                
    -fail_sql and pass_sql will contain the path of the sql_scripts in the test_scripts directory.
        ### Table Metadata:
        {', '.join(table_names)}\n\n{metadata}
        """

        response = self.client.chat.completions.create(
            model=self.models,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def suggest_tests(self, table_names: List[str]):
        print("🔍 Analyzing table...")
        metadata = self.analyze_multiple_tables(table_names)
        print(metadata)

        print("\n🧠 Generating test cases using AI model...\n")
        test_cases = self.get_test_cases_for_tables(table_names, metadata)
        print(test_cases)
