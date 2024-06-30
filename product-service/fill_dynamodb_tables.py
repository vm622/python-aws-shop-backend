import boto3
import logging
import random
import json
import uuid

logger = logging.getLogger()
logger.setLevel("INFO")

dynamodb = boto3.resource('dynamodb')

products_table = dynamodb.Table('products')
stocks_table = dynamodb.Table('stocks')

def create_product(title, description, price):
    product_id = uuid.uuid4()

    products_table.put_item(
        Item={
            'id': str(product_id),
            'title': title,
            'description': description,
            'price': (str(price))
        }
    )

    return product_id

def create_stock(product_id, count):
    stocks_table.put_item(
        Item={
            'product_id': str(product_id),
            'count': count
        }
    )

def fill_tables():
    try:
        with open('products.json', 'r') as products_json:
            products_list = json.load(products_json)
            for product in products_list:
                product_id = create_product( product['title'], product['description'], product['price'])
                create_stock(product_id, random.randint(1, 10))
        print("Tables filled successfully")
        logger.info("Tables filled successfully")
    except Exception as e:
        print(e)
        logger.exception(e)

fill_tables()
