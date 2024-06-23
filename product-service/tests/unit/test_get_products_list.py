import json
import pytest
from unittest.mock import patch

from lambda_functions.get_products_list import handler
from lambda_functions.products import products_list

@pytest.fixture
def event():
    return {}

@pytest.fixture
def context():
    return {}

def test_handler_with_products(event, context):

    expected_response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json"
        },
        "body": json.dumps(products_list)
    }

    actual_response = handler(event, context)
    assert actual_response == expected_response

def test_handler_with_empty_products_list(context):
    with patch('lambda_functions.get_products_list.products_list', []):
        event = {}
        expected_response = {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "No products found"})
        }

        actual_response = handler(event, context)
        assert actual_response == expected_response
