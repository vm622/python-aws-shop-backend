import json
from lambda_functions.products import products_list

def handler(event, context):
    product_id = event["pathParameters"]["id"]

    if not product_id:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Product ID is required"})
        }
    
    product = next((p for p in products_list if p["id"] == product_id), None)

    if not product:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Product not found"})
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
