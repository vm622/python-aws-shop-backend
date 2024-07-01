import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

s3_client = boto3.client("s3")

def handler(event, context):
    try:   
        if event['queryStringParameters'] is None or 'name' not in event.get('queryStringParameters', {}):
            raise ValueError('name is required')
        
        file_name = event['queryStringParameters']['name']

        if not file_name:
            raise ValueError('name should not be empty')
        
        bucket_name = os.environ['IMPORT_BUCKET']
        object_key = f"uploaded/{file_name}"

        s3_object_params = {
            'Bucket': bucket_name,
            'Key': object_key,
            'ContentType': 'application/vnd.ms-excel'
        }

        presigned_url = s3_client.generate_presigned_url('put_object', Params=s3_object_params, ExpiresIn=600)

        logger.info(f"Presigned url sucessfully created: {presigned_url}")
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"url": presigned_url})
        }

    except Exception as e:
        logger.exception(f"Error while creating presigned url: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Error while creating presigned url": str(e)})
        }

