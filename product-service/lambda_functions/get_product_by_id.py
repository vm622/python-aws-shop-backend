import json
import os
import boto3

def handler(event, context):
    try:
        product_id = event["pathParameters"]["id"]

        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION'))

        products_table_name = os.getenv('PRODUCTS_TABLE_NAME')
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME')

        products_table = dynamodb.Table(products_table_name)
        stocks_table = dynamodb.Table(stocks_table_name)

        product_item = products_table.get_item(Key={'id': product_id})
        stock_item = stocks_table.get_item(Key={'product_id': product_id})

        if 'Item' in product_item and 'Item' in stock_item:
            product = {
                'id': product_item['Item']['id'],
                'title': product_item['Item']['title'],
                'description': product_item['Item']['description'],
                'price': str(product_item['Item']['price']),
                'count': str(stock_item['Item']['count']),
            }

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Content-Type": "application/json"
                },
                "body": json.dumps(product)
            }
        else:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Content-Type": "application/json"
                },
                "body": json.dumps(f"'message': 'Product {product_id} not found'")
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": str(e)})
        } 
