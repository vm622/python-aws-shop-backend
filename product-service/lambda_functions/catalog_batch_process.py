import boto3
import os
import uuid
import json
import logging
from jsonschema import validate
from items_schemas import product_schema

logger = logging.getLogger()
logger.setLevel("INFO")

dynamodb_client = boto3.client('dynamodb')
sns_client = boto3.client('sns')

def handler(event, context):
    logger.info(event)

    products = []
    try:
        for record in event['Records']:
            message = json.loads(record['body'])

            product_id = str(uuid.uuid4())
            title = message.get('title', '')
            description = message.get('description', '')
            price = float(message.get('price', 0))
            count = int(message.get('count', 0))

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

            dynamodb_client.transact_write_items(TransactItems=transaction_items)
            products.append(product)
        logger.info(f"Products successfully created: {products}")

        sns_client.publish(
            TopicArn=os.getenv('CREATE_PRODUCT_SNS'),
            Subject='Products creation notification',
            Message= json.dumps({
                'default': json.dumps({
                    'message': "Products successfully created",
                    'products': products,
                })
            }),
            MessageStructure='json',
            MessageAttributes={
                    'price': {
                        'DataType': 'Number',
                        'StringValue': str(price)
                    }
                }
        )

    except Exception as e:
        logger.exception(e)
