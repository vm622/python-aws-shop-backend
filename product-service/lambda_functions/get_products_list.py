import json
import os 
import boto3

def handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('REGION'))
        products_table = dynamodb.Table(os.getenv('PRODUCTS_TABLE_NAME'))
        stocks_table = dynamodb.Table(os.getenv('STOCKS_TABLE_NAME'))

        products_response = products_table.scan()
        products_items = products_response.get('Items', [])

        stocks_response = stocks_table.scan()
        stocks_items = stocks_response.get('Items', [])

        if not products_items:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": "No products found"})
            }

        products_dict = {item['id']: item for item in products_items}

        for item in stocks_items:
            product_id = item['product_id']
            if product_id in products_dict:
                products_dict[product_id]['count'] = int(item['count'])
                products_dict[product_id]['price'] = int(products_dict[product_id]['price'])

        products = list(products_dict.values())
        return {
        "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps(products)
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
