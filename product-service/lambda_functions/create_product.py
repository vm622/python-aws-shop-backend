import json
import os
import uuid
import boto3
import logging
from jsonschema import validate, ValidationError

from items_schemas import product_schema

logger = logging.getLogger()
logger.setLevel("INFO")

def handler(event, context):
    try:
        logger.info(event)
        dynamodb = boto3.client('dynamodb', region_name=os.getenv('REGION'))

        body = json.loads(event['body'])
        product_id = str(uuid.uuid4())
        title = body['title']
        description = body['description']
        price = body['price']
        count = body['count']

        product = {
            'id': product_id,
            'title': title,
            'description': description,
            'price': price,
            'count': count
        }

        validate(instance=product, schema=product_schema)

        transaction_items = [
            {
                'Put': {
                    'TableName': os.getenv('PRODUCTS_TABLE_NAME'),
                    'Item': {
                        'id': {'S': product['id']},
                        'title': {'S': product['title']},
                        'description': {'S': product['description']},
                        'price': {'N': str(product['price'])}
                        }
                }
            },
            {
                'Put': {
                    'TableName': os.getenv('STOCKS_TABLE_NAME'),
                    'Item': {
                        'product_id': {'S': product['id']},
                        'count': {'N': str(product['count'])}
                        }
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
    except KeyError as e:
        logger.exception(f"{e} is absent")
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": f"{e} is absent"})
        } 
    except json.JSONDecodeError as e:
        logger.exception(e)
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Request body is not valid"})
        }
    except ValidationError as e:
        logger.exception(e)
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": f"Product validation failed:\n{str(e)}"})
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
