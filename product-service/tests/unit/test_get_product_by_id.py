import json
import pytest

from lambda_functions.get_product_by_id import handler
from lambda_functions.products import products_list

@pytest.fixture
def context():
    return {}

def test_handler_with_valid_product_id(context):
    event = {
        "pathParameters": {
            "id": str(products_list[0]["id"])
        }
    }
    expected_response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json"
        },
        "body": json.dumps(products_list[0])
    }

    actual_response = handler(event, context)
    assert actual_response == expected_response

def test_handler_with_nonexistent_product_id(context):
    event = {
        "pathParameters": {
            "id": "100"
        }
    }
    expected_response = {
        "statusCode": 404,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": "Product not found"})
    }

    actual_response = handler(event, context)
    assert actual_response == expected_response
