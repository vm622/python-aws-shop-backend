import json
import os
import uuid
import boto3
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel("INFO")

def handler(event, context):
    try:
        logger.info(event)

        dynamodb = boto3.client('dynamodb', region_name=os.getenv('REGION'))

        body = json.loads(event['body'])
        title = body['title']
        description = body['description']
        price = body['price']
        count = body['count']

        product_id = uuid.uuid4()

        product_item = {
            'id': {'S': str(product_id)},
            'title': {'S': title},
            'description': {'S': description},
            'price': {'N': Decimal(str(price))},
        }

        stock_item = {
            'product_id': {'S': str(product_id)},
            'count': {'N': str(count)}
        }

        transaction_items = [
            {
                'Put': {
                    'TableName': os.getenv('PRODUCTS_TABLE_NAME'),
                    'Item': product_item
                }
            },
            {
                'Put': {
                    'TableName': os.getenv('STOCKS_TABLE_NAME'),
                    'Item': stock_item
                }
            }
        ]

        dynamodb.transact_write_items(TransactItems=transaction_items)

        logger.info(f"Product {product_id} is sucessfully added")
        return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Content-Type": "application/json"
                },
                "body": f"Product {product_id} is sucessfully added"
        }
        
    except Exception as e:
        logger.exception(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": str(e)})
        } 
