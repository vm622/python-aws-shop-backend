import os
import csv
from moto import mock_aws
import boto3
import pytest
from botocore.exceptions import ClientError
from io import StringIO

from lambda_functions.import_file_parser import handler

@mock_aws
def test_import_file_parser():
    csv_data = "id,title,description,price,count\n0cf6839b-d56b-4d90-b14f-c4f65bb4d4b1,Mock product,Mock product description,1.561,1\n"

    mock_bucket_name = 'test-aws-import-bucket'
    os.environ['IMPORT_BUCKET'] = mock_bucket_name

    s3 = boto3.client('s3', region_name='eu-west-1')
    s3.create_bucket(Bucket=mock_bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

    csv_key = 'uploaded/test.csv'
    s3.put_object(Bucket=mock_bucket_name, Key=csv_key, Body=csv_data.encode('utf-8'))

    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': mock_bucket_name
                    },
                    'object': {
                        'key': 'uploaded/test.csv'
                    }
                }
            }
        ]
    }

    handler(event, None)

    parsed_key = 'parsed/test.csv'
    response = s3.get_object(Bucket=mock_bucket_name, Key=parsed_key)
    parsed_csv = csv.reader(StringIO(response['Body'].read().decode('utf-8')))
    rows = [','.join(row) for row in parsed_csv]
    csv_parsed_result = '\n'.join(rows) + '\n' 

    assert csv_parsed_result == csv_data, "Parsed CSV data doesn't match original CSV data"

    # Check that csv file was deleted from `uploaded`
    with pytest.raises(ClientError):
        s3.get_object(Bucket=mock_bucket_name, Key='uploaded/test.csv')

if __name__ == '__main__':
    pytest.main()
