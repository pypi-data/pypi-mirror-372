import os
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import snowflake.connector
import cryptography.hazmat.primitives.serialization as serialization
from cryptography.hazmat.backends import default_backend
from prefect.blocks.system import Secret
from snowflake.connector.pandas_tools import write_pandas

class SnowflakeToolKit:

    def __init__(self, prefect=False, user=None, password=None, role=None, schema='DATA_SCIENCE', warehouse='DATA_SCIENCE_TEAM'):
        if user and password and role:
            # If user, password, and role are provided as input, use them
            self.user = user
            self.password = password
            self.role = role
            self.private_key = None
        elif prefect:
            # If `prefect` is True, load credentials from Prefect secrets
            self.user = Secret.load("snowflake-script-user").get()
            self.private_key = serialization.load_pem_private_key(
                Secret.load("snowflake-script-key").get().encode('utf-8'),
                password=None, 
                backend=default_backend()
            ).private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            self.password = None
            self.role = 'DATA_SCIENCE_SCRIPT_WRITE'
        else:
            # Default case: use environment variables
            self.user = os.environ['SNOWFLAKE_SCRIPT_USER']
            self.private_key = serialization.load_pem_private_key(
                os.environ['SNOWFLAKE_PRIVATE_KEY'].encode('utf-8'),
                password=None, 
                backend=default_backend()
            )
            self.password = None
            self.role = 'DATA_SCIENCE_SCRIPT_WRITE'

        self.account = 're29130.us-east-2.aws' # Connect to the Crumbl SF account only
        self.warehouse = warehouse
        self.database = 'ANALYTICS'
        self.schema = schema
        self.prefect = prefect
        self.connection = None

    def connect(self):
        if self.private_key:
            # Use private key authentication
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                private_key=self.private_key,
                role=self.role,
                warehouse=self.warehouse,
                database=self.database
            )
        else:
            # Use password authentication
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                role=self.role,
                warehouse=self.warehouse,
                database=self.database
            )
        return self.connection

    def fetch_data(self, sql_query):
        """
        Fetch data from Snowflake using a SQL query
        """
        if self.connection is None:
            self.connect()
        return pd.read_sql(sql_query, self.connection)

    def insert_data(self, df, table_name, auto_create_table=False):
        """
        Insert pandas DataFrame into Snowflake table
        """
        if self.connection is None:
            self.connect()
        write_pandas(
            conn=self.connection, 
            df=df, 
            table_name=table_name,
            database=self.database, 
            schema=self.schema,
            auto_create_table=auto_create_table)

    def execute_query(self, sql_query):
        """
        Execute a SQL query in Snowflake. Useful for DML queries.
        """
        if self.connection is None:
            self.connect()
        self.connection.cursor().execute(sql_query)