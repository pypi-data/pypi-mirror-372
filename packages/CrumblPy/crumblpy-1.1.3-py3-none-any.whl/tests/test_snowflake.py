import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from CrumblPy.snowflake import SnowflakeToolKit


class TestSnowflakeToolKit:
    
    @patch('snowflake.connector.connect')
    def test_init_with_explicit_credentials(self, mock_connect):
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        
        assert sf.user == 'test_user'
        assert sf.password == 'test_password'
        assert sf.role == 'test_role'
        assert sf.private_key is None
        assert sf.account == 're29130.us-east-2.aws'
        assert sf.database == 'ANALYTICS'
        assert sf.schema == 'DATA_SCIENCE'
        assert sf.warehouse == 'DATA_SCIENCE_TEAM'
    
    @patch.dict('os.environ', {
        'SNOWFLAKE_SCRIPT_USER': 'env_user',
        'SNOWFLAKE_PRIVATE_KEY': '''-----BEGIN RSA PRIVATE KEY-----
test_private_key
-----END RSA PRIVATE KEY-----'''
    })
    @patch('cryptography.hazmat.primitives.serialization.load_pem_private_key')
    def test_init_with_env_vars(self, mock_load_key):
        mock_private_key = Mock()
        mock_private_key.private_bytes.return_value = b'mock_private_key_bytes'
        mock_load_key.return_value = mock_private_key
        
        sf = SnowflakeToolKit()
        
        assert sf.user == 'env_user'
        assert sf.password is None
        assert sf.role == 'DATA_SCIENCE_SCRIPT_WRITE'
        mock_load_key.assert_called_once()
    
    @patch('snowflake.connector.connect')
    def test_connect_with_password(self, mock_connect):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        
        result = sf.connect()
        
        assert result == mock_connection
        assert sf.connection == mock_connection
        mock_connect.assert_called_once_with(
            account='re29130.us-east-2.aws',
            user='test_user',
            password='test_password',
            role='test_role',
            warehouse='DATA_SCIENCE_TEAM',
            database='ANALYTICS'
        )
    
    @patch('snowflake.connector.connect')
    def test_connect_with_private_key(self, mock_connect):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        sf.private_key = b'mock_private_key'  # Simulate private key
        sf.password = None
        
        result = sf.connect()
        
        assert result == mock_connection
        assert sf.connection == mock_connection
        mock_connect.assert_called_once_with(
            account='re29130.us-east-2.aws',
            user='test_user',
            private_key=b'mock_private_key',
            role='test_role',
            warehouse='DATA_SCIENCE_TEAM',
            database='ANALYTICS'
        )
    
    @patch('pandas.read_sql')
    @patch('snowflake.connector.connect')
    def test_fetch_data(self, mock_connect, mock_read_sql):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_sql.return_value = mock_df
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        
        result = sf.fetch_data("SELECT * FROM test_table")
        
        assert isinstance(result, pd.DataFrame)
        assert result.equals(mock_df)
        mock_read_sql.assert_called_once_with("SELECT * FROM test_table", mock_connection)
        assert sf.connection == mock_connection
    
    @patch('pandas.read_sql')
    @patch('snowflake.connector.connect')
    def test_fetch_data_auto_connect(self, mock_connect, mock_read_sql):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        mock_df = pd.DataFrame({'col1': [1, 2]})
        mock_read_sql.return_value = mock_df
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        sf.connection = None  # Ensure connection is None
        
        result = sf.fetch_data("SELECT * FROM test_table")
        
        mock_connect.assert_called_once()
        mock_read_sql.assert_called_once_with("SELECT * FROM test_table", mock_connection)
    
    @patch('CrumblPy.snowflake.write_pandas')
    @patch('snowflake.connector.connect')
    def test_insert_data(self, mock_connect, mock_write_pandas):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        mock_write_pandas.return_value = (True, 1, 2, [])  # Mock return value
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        sf.insert_data(test_df, 'test_table', auto_create_table=True)
        
        mock_write_pandas.assert_called_once_with(
            conn=mock_connection,
            df=test_df,
            table_name='test_table',
            database='ANALYTICS',
            schema='DATA_SCIENCE',
            auto_create_table=True
        )
        assert sf.connection == mock_connection
    
    @patch('CrumblPy.snowflake.write_pandas')
    @patch('snowflake.connector.connect')
    def test_insert_data_auto_connect(self, mock_connect, mock_write_pandas):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        mock_write_pandas.return_value = (True, 1, 2, [])  # Mock return value
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        sf.connection = None  # Ensure connection is None
        
        test_df = pd.DataFrame({'col1': [1, 2]})
        sf.insert_data(test_df, 'test_table')
        
        mock_connect.assert_called_once()
        mock_write_pandas.assert_called_once()
    
    @patch('snowflake.connector.connect')
    def test_execute_query(self, mock_connect):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        
        sf.execute_query("UPDATE test_table SET col1 = 1")
        
        mock_cursor.execute.assert_called_once_with("UPDATE test_table SET col1 = 1")
        assert sf.connection == mock_connection
    
    @patch('snowflake.connector.connect')
    def test_execute_query_auto_connect(self, mock_connect):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role'
        )
        sf.connection = None  # Ensure connection is None
        
        sf.execute_query("UPDATE test_table SET col1 = 1")
        
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once_with("UPDATE test_table SET col1 = 1")
    
    @patch('snowflake.connector.connect')
    def test_custom_schema_and_warehouse(self, mock_connect):
        sf = SnowflakeToolKit(
            user='test_user',
            password='test_password',
            role='test_role',
            schema='CUSTOM_SCHEMA',
            warehouse='CUSTOM_WAREHOUSE'
        )
        
        assert sf.schema == 'CUSTOM_SCHEMA'
        assert sf.warehouse == 'CUSTOM_WAREHOUSE'