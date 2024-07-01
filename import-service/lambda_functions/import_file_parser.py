import boto3
import os
import logging
import csv
from io import StringIO

logger = logging.getLogger()
logger.setLevel("INFO")

s3_client = boto3.client("s3")

def handler(event, context):
    bucket_name = os.environ['IMPORT_BUCKET']

    for record in event['Records']:
        key = record['s3']['object']['key']

        response = s3_client.get_object(Bucket=bucket_name, Key=key)

        csv_file = csv.DictReader(StringIO(response['Body'].read().decode('utf-8')))

        for row in csv_file:
            logger.info(row)
    
        copy_source = {'Bucket': bucket_name, 'Key': key}
        parsed_key = key.replace('uploaded/', 'parsed/')
        s3_client.copy_object(CopySource=copy_source, Bucket=bucket_name, Key=parsed_key)

        if key != 'uploaded/':
            s3_client.delete_object(Bucket=bucket_name, Key=key)
