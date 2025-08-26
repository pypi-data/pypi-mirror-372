import logging
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from retry import retry
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from databricks import sql as databricks_sql
from pyspark.sql import SparkSession




def find_env_file():
    """Find .env file in current directory or parent directories."""
    # First try the default location
    env_path = find_dotenv(usecwd=True)
    if env_path:
        return env_path
        
    # Try searching up from the current directory
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        env_file = current_dir / '.env'
        if env_file.exists():
            return str(env_file)
        current_dir = current_dir.parent
    
    # Finally check package directory
    package_dir = Path(__file__).parent.parent
    env_file = package_dir / '.env'
    if env_file.exists():
        return str(env_file)
        
    return None

# Load environment variables
env_path = find_env_file()
if env_path:
    load_dotenv(env_path)
else:
    logging.warning("No .env file found. Using system environment variables.")

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



from databricks import sql as databricks_sql
from pyspark.sql import SparkSession

import os
import logging

logger = logging.getLogger(__name__)

def execute_run_databricks(
    query,
    retrieve_result=True,
    load_data=False,
    server_hostname: Optional[str] = None,
    http_path: Optional[str] = None,
    access_token: Optional[str] = None
):
    """
    Run a SQL query using Databricks SQL Connector or SparkSession as fallback.

    Credentials order:
    1. Use explicit args if provided.
    2. Fallback to env vars.
    3. If still missing, fallback to SparkSession in notebook.
    """
    import os
    from pyspark.sql import SparkSession
    from databricks import sql as databricks_sql

    logger = logging.getLogger(__name__)

    result = None
    query = query.strip()
    spark = SparkSession.getActiveSession()
    # server_hostname = spark.conf.get("spark.databricks.workspaceUrl")
    # access_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
    # http_path = "/sql/1.0/warehouses/5e9b464343b6fd9f"

    try:
        server_hostname = server_hostname or os.getenv("DATABRICKS_SERVER_HOSTNAME")
        http_path = http_path or os.getenv("DATABRICKS_HTTP_PATH")
        access_token = access_token or os.getenv("DATABRICKS_ACCESS_TOKEN")

        if server_hostname and http_path and access_token:
            logger.info("Connecting to Databricks via SQL Connector...")

            conn = databricks_sql.connect(
                server_hostname=server_hostname,
                http_path=http_path,
                access_token=access_token
            )

            cursor = conn.cursor()

            if retrieve_result:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [tuple(columns)] + rows

            elif load_data:
                return conn  # Return raw connection if needed

            else:
                # Run multiple queries split by semicolon
                for single_query in query.split(";"):
                    if single_query.strip():
                        cursor.execute(single_query)

            cursor.close()
            conn.close()
            return result

        else:
            logger.info("No explicit credentials or env vars. Using SparkSession...")
            spark = SparkSession.getActiveSession()

            if not spark:
                raise RuntimeError("No Databricks connection and no active SparkSession available.")

            if retrieve_result:
                df = spark.sql(query)
                columns = df.columns
                rows = df.collect()
                result = [tuple(columns)] + [tuple(row) for row in rows]
                return result
            else:
                spark.sql(query)
                return None

    except Exception as e:
        logger.error("Error occurred while executing query on Databricks")
        logger.exception(e)
        raise


        


class DbConnections:
    """Manages PostgreSQL database connections using credentials from .env or direct configuration."""

    DEFAULT_CONFIG_PATHS = [
        "config.json",
        ".env",
        "../.env",
        "../../.env",
    ]

    def __init__(self, credentials: Dict[str, Any] = None, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        if credentials:
            self.connection_credentials = self._validate_credentials(credentials)
        else:
            self.connection_credentials = self._load_credentials(config_path)

    def _load_credentials(self, config_path: str = None) -> Dict[str, Any]:
        """Try loading credentials from multiple sources."""
        # 1. Try specific config path if provided
        if config_path and os.path.exists(config_path):
            self.logger.info(f"Loading credentials from {config_path}")
            if config_path.endswith('.json'):
                with open(config_path) as f:
                    return self._validate_credentials(json.load(f))
            else:
                load_dotenv(config_path)

        # 2. Try default locations
        for path in self.DEFAULT_CONFIG_PATHS:
            if os.path.exists(path):
                self.logger.info(f"Loading credentials from {path}")
                if path.endswith('.json'):
                    with open(path) as f:
                        return self._validate_credentials(json.load(f))
                else:
                    load_dotenv(path)

        # 3. Try environment variables
        return self.get_config_credentials()

    def _validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process database credentials."""
        required_fields = ["host", "database", "user", "password"]
        missing = [field for field in required_fields if field not in credentials]
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
        
        # Add default values for optional fields
        credentials.setdefault("schema", "public")
        credentials.setdefault("port", 5432)
        
        return credentials

    def get_config_credentials(self) -> dict:
        """Fetch PostgreSQL credentials from environment."""
        credentials = {
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_DATABASE"),
            "schema": os.getenv("DB_SCHEMA", "public"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": int(os.getenv("DB_PORT", "5432") if os.getenv("DB_PORT") else 5432),
        }

        missing = [k for k, v in credentials.items() if v is None]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        return credentials

    @retry(exceptions=Exception, tries=3, delay=10, backoff=2)
    def postgres_engine(self):
        """Create SQLAlchemy engine for PostgreSQL."""
        try:
            pg = self.connection_credentials
            connection_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
            engine = create_engine(connection_url)
            self.logger.info(f"Connected to PostgreSQL: {pg['database']}")
            return engine
        except Exception as e:
            self.logger.error(f"Failed to create PostgreSQL engine: {e}")
            raise


def execute_run_postgres(query: str, engine, retrieve_result: bool = False, load_data: bool = False, load_script: bool =False):
    result = []
    connection = None

    try:
        connection = engine.connect()
        logger.info("Connected to PostgreSQL")
        
        query_list = [q.strip() for q in query.strip().split(";") if q.strip()]

        if retrieve_result:
            with connection.begin():
                for single_query in query_list:
                    result_proxy = connection.execute(text(single_query))
                    
                    if result_proxy.returns_rows:
                        column_names = result_proxy.keys()
                        result_set = result_proxy.fetchall()
                        result.append([tuple(column_names)] + result_set)
                    # no else block here - do not overwrite result

        elif load_data:
            return connection  # Used by Pandas .to_sql
        
        elif load_script:
            connection.exec_driver_sql(query)

        else:
            for single_query in query_list:
                connection.execute(text(single_query))

        connection.commit()

    except SQLAlchemyError as e:
        logger.error("PostgreSQL execution error")
        logger.error(e)
        raise

    finally:
        if connection:
            connection.close()

    if retrieve_result:
        if result:
            return result
        else:
            return {"info": "No result (DDL/DML executed successfully)"}
    else:
        return None

