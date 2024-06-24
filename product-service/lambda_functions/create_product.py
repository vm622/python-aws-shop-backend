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

        dynamodb = boto3.resource('dynamodb')
        products_table_name = os.getenv('PRODUCTS_TABLE_NAME')
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME')

        products_table = dynamodb.Table(products_table_name)
        stocks_table = dynamodb.Table(stocks_table_name)

        body = json.loads(event['body'])
        title = body['title']
        description = body['description']
        price = body['price']
        count = body['count']

        product_id = uuid.uuid4()

        product_item = {
            'id': str(product_id),
            'title': title,
            'description': description,
            'price': Decimal(str(price))
        }

        stock_item = {
            'product_id': str(product_id),
            'count': count
        }

        products_table.put_item(Item=product_item)
        stocks_table.put_item(Item=stock_item)

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
