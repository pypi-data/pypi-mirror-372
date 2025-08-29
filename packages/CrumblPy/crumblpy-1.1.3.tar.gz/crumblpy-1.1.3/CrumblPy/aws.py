import boto3
import gzip
import json
import os
import pandas as pd
from prefect.blocks.system import Secret

class AWSToolKit:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, prefect=False):
        if aws_access_key_id and aws_secret_access_key:
            self.aws_access_key_id = aws_access_key_id
            self.aws_secret_access_key = aws_secret_access_key
        elif prefect: 
            self.aws_access_key_id = Secret.load("aws-access-key-id").get()
            self.aws_secret_access_key = Secret.load("aws-secret-access-key").get()
        else:
            self.aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            self.aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def write_to_s3(self, df, bucket_name, key):
        """df to gzip json and upload to s3"""
        compressed_data = gzip.compress(df.to_json(orient='records', lines=True).encode('utf-8'))
        self.s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=compressed_data,
            ContentType='application/gzip',
            ContentEncoding='gzip'
        )
    
    def read_from_s3(self, bucket_name, key):
        """read gzip json from s3 and return pandas dataframe"""
        response = self.s3.get_object(Bucket=bucket_name, Key=key)
        json_data = gzip.decompress(response['Body'].read()).decode('utf-8')
        json_objects = [json.loads(line) for line in json_data.strip().split('\n') if line.strip()]

        return pd.DataFrame(json_objects)
    
    def scan_dynamodb_table(self, table_name, filter_expression=None, expression_attribute_values=None, 
                           projection_expression=None, expression_attribute_names=None):
        """Scan DynamoDB table completely using pagination and return pandas dataframe"""
        table = self.dynamodb.Table(table_name)
        
        scan_kwargs = {}
        if filter_expression:
            scan_kwargs['FilterExpression'] = filter_expression
        if expression_attribute_values:
            scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
        if projection_expression:
            scan_kwargs['ProjectionExpression'] = projection_expression
        if expression_attribute_names:
            scan_kwargs['ExpressionAttributeNames'] = expression_attribute_names
        
        all_items = []
        while True:
            response = table.scan(**scan_kwargs)
            all_items.extend(response.get('Items', []))
            
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        return pd.DataFrame(all_items)