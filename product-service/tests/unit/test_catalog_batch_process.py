import pytest
import os
import json
import boto3
from moto import mock_aws

from lambda_functions.catalog_batch_process import handler

@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(autouse=True, scope="module")
def environment_variables():
    os.environ['PRODUCTS_TABLE_NAME'] = 'mock-products-table'
    os.environ['STOCKS_TABLE_NAME'] = 'mock-stocks-table'
    os.environ['CREATE_PRODUCT_SNS'] = 'mock-create-product-sns-topic'
    os.environ['FIRST_EMAIL'] = 'first-mail@mail.com'
    os.environ['SECOND_EMAIL'] = 'second-mail@mail.com'

@pytest.fixture
def dynamodb_resource(aws_credentials):
    with mock_aws():
        yield boto3.resource("dynamodb", region_name="us-east-1")

@pytest.fixture
def products_table(dynamodb_resource):
    dynamodb_resource.create_table(
        TableName=os.getenv('PRODUCTS_TABLE_NAME'),
        KeySchema=[{'AttributeName': 'id','KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id','AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

@pytest.fixture
def stocks_table(dynamodb_resource):
    dynamodb_resource.create_table(
        TableName=os.getenv('STOCKS_TABLE_NAME'),
        KeySchema=[{'AttributeName': 'product_id','KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'product_id','AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )


@pytest.mark.parametrize("event",
    [
        {
            'Records': [
                {
                    'body': '{"title": "Test title", "description": "Test description", "price": 41.1, "count": 17}', 
                },
                {
                    'body': '{"title": "Test title", "description": "Test description", "price": 41.1, "count": 17}', 
                }
            ]
        },
    ]
)
def test_dynamodb_write_products(products_table, stocks_table, dynamodb_resource, event):
    handler(event, None)
    test_products = [json.loads(product['body']) for product in event['Records']]
    
    products_table = dynamodb_resource.Table(os.getenv('PRODUCTS_TABLE_NAME'))
    stocks_table = dynamodb_resource.Table(os.getenv('STOCKS_TABLE_NAME'))

    products_items = products_table.scan().get('Items', [])
    stocks_items = stocks_table.scan().get('Items', [])

    products_dict = {item['id']: item for item in products_items}

    for item in stocks_items:
        product_id = item['product_id']
        if product_id in products_dict:
            products_dict[product_id]['count'] = int(item['count'])
            products_dict[product_id]['price'] = float(products_dict[product_id]['price'])
            del products_dict[product_id]['id']
    products = list(products_dict.values())

    assert test_products == products


@pytest.mark.parametrize("event",
    [
        {
            'Records': [
                {
                    'body': '{"title": "Test title", "description": "Test description", "price": 41.1, "count": 17}', 
                },
                {
                    'body': '{"title": "Test title 2", "description": "Test description 2", "price": 7467.23, "count": 2}', 
                },
            ]
        },
    ]
)
def test_dynamodb_products_count(products_table, stocks_table, dynamodb_resource, event):
    handler(event, None)
    products_table = dynamodb_resource.Table(os.getenv('PRODUCTS_TABLE_NAME'))
    products_count = len(products_table.scan().get('Items', []))
    assert len(event['Records']) == products_count

@pytest.fixture
def sns_client(aws_credentials):
    with mock_aws():
        yield boto3.client("sns", region_name="us-east-1")

@pytest.fixture
def sns_topic(sns_client):
    response = sns_client.create_topic(Name=os.getenv('CREATE_PRODUCT_SNS'))
    topic_arn = response['TopicArn']

    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=os.getenv('FIRST_EMAIL')
    )
    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=os.getenv('SECOND_EMAIL')
    )

    return topic_arn

def test_sns_subscribers_count(sns_client, sns_topic):
    topic_arn = sns_topic
    subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
    assert len(subscriptions['Subscriptions']) == 2
