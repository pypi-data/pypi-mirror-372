import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from CrumblPy.aws import AWSToolKit


class TestAWSToolKit:
    
    @patch.dict('os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_init_with_env_vars(self, mock_resource, mock_client):
        aws = AWSToolKit()
        assert aws.aws_access_key_id == 'test_key'
        assert aws.aws_secret_access_key == 'test_secret'
        mock_client.assert_called()
        mock_resource.assert_called()
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_init_with_explicit_credentials(self, mock_resource, mock_client):
        aws = AWSToolKit(aws_access_key_id='explicit_key', aws_secret_access_key='explicit_secret')
        assert aws.aws_access_key_id == 'explicit_key'
        assert aws.aws_secret_access_key == 'explicit_secret'
        mock_client.assert_called()
        mock_resource.assert_called()
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_write_to_s3(self, mock_resource, mock_client):
        mock_s3 = Mock()
        mock_client.return_value = mock_s3
        
        aws = AWSToolKit(aws_access_key_id='test_key', aws_secret_access_key='test_secret')
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        
        aws.write_to_s3(df, 'test-bucket', 'test-key')
        
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        assert call_args['Bucket'] == 'test-bucket'
        assert call_args['Key'] == 'test-key'
        assert call_args['ContentType'] == 'application/gzip'
        assert call_args['ContentEncoding'] == 'gzip'
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_read_from_s3(self, mock_resource, mock_client):
        mock_s3 = Mock()
        mock_client.return_value = mock_s3
        
        # Mock S3 response with compressed JSON data
        import gzip
        test_data = '{"col1": 1, "col2": "a"}\n{"col1": 2, "col2": "b"}'
        compressed_data = gzip.compress(test_data.encode('utf-8'))
        
        mock_response = {'Body': Mock()}
        mock_response['Body'].read.return_value = compressed_data
        mock_s3.get_object.return_value = mock_response
        
        aws = AWSToolKit(aws_access_key_id='test_key', aws_secret_access_key='test_secret')
        result_df = aws.read_from_s3('test-bucket', 'test-key')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert list(result_df.columns) == ['col1', 'col2']
        mock_s3.get_object.assert_called_once_with(Bucket='test-bucket', Key='test-key')
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_scan_dynamodb_table_basic(self, mock_resource, mock_client):
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        # Mock scan response without pagination
        mock_table.scan.return_value = {
            'Items': [{'id': 1, 'name': 'test1'}, {'id': 2, 'name': 'test2'}]
        }
        
        aws = AWSToolKit(aws_access_key_id='test_key', aws_secret_access_key='test_secret')
        result_df = aws.scan_dynamodb_table('test-table')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        mock_table.scan.assert_called_once()
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_scan_dynamodb_table_with_pagination(self, mock_resource, mock_client):
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        # Mock scan responses with pagination
        mock_table.scan.side_effect = [
            {
                'Items': [{'id': 1, 'name': 'test1'}],
                'LastEvaluatedKey': {'id': 1}
            },
            {
                'Items': [{'id': 2, 'name': 'test2'}]
            }
        ]
        
        aws = AWSToolKit(aws_access_key_id='test_key', aws_secret_access_key='test_secret')
        result_df = aws.scan_dynamodb_table('test-table')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert mock_table.scan.call_count == 2
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_scan_dynamodb_table_with_filters(self, mock_resource, mock_client):
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        mock_table.scan.return_value = {
            'Items': [{'id': 1, 'status': 'active'}]
        }
        
        aws = AWSToolKit(aws_access_key_id='test_key', aws_secret_access_key='test_secret')
        result_df = aws.scan_dynamodb_table(
            'test-table',
            filter_expression='#status = :status',
            expression_attribute_names={'#status': 'status'},
            expression_attribute_values={':status': 'active'}
        )
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 1
        
        call_args = mock_table.scan.call_args[1]
        assert call_args['FilterExpression'] == '#status = :status'
        assert call_args['ExpressionAttributeNames'] == {'#status': 'status'}
        assert call_args['ExpressionAttributeValues'] == {':status': 'active'}