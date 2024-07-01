import os
import boto3
import pytest
import json
from moto import mock_aws

from lambda_functions.import_products_file import handler

@mock_aws
def test_import_file_lambda_returns_signed_url():
    bucket_name = 'test-aws-import-bucket'
    os.environ['IMPORT_BUCKET'] = bucket_name

    # Create a mock S3 client and bucket
    with mock_aws():
        s3 = boto3.client('s3', region_name='eu-west-1')
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

    event = {
        'queryStringParameters': {
            'name': 'test.csv'
        }
    }

    response = handler(event, None)
    assert response['statusCode'] == 200
    assert 'body' in response
    assert json.loads(response['body'])['url'].startswith('https://test-aws-import-bucket.s3.amazonaws.com/uploaded/test.csv?AWSAccessKeyId')

if __name__ == '__main__':
    pytest.main()
