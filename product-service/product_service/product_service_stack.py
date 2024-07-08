from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs, 
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_lambda_event_sources as lambda_events,
    RemovalPolicy,
    Fn,
    Stack
)
import boto3
from botocore.exceptions import ClientError
from constructs import Construct
import os
from dotenv import load_dotenv

class ProductServiceStack(Stack):
    @staticmethod
    def table_exists(table_name):
        dynamodb = boto3.client('dynamodb')
        try:
            dynamodb.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                raise

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        load_dotenv()
        EMAIL = os.getenv('EMAIL')
        
        products_table_name = "products"
        stocks_table_name = "stocks"

        lambdas_env = {
            "PRODUCTS_TABLE_NAME": products_table_name,
            "STOCKS_TABLE_NAME": stocks_table_name
        }  

        catalog_items_queue_arn = Fn.import_value("CatalogItemsQueueArn")
        catalog_items_queue = sqs.Queue.from_queue_arn(self, 'CatalogItemsQueue', catalog_items_queue_arn)

        create_product_sns_topic = sns.Topic(self, "CreateProductTopic")
        create_product_sns_topic.add_subscription(sns_subscriptions.EmailSubscription(EMAIL))

        if ProductServiceStack.table_exists(products_table_name):
            products_table = dynamodb.Table.from_table_name(self, "ProductsTable", products_table_name)
        else:
            products_table = dynamodb.Table(
                self,
                "ProductsTable",
                table_name=products_table_name,
                partition_key=dynamodb.Attribute(
                    name="id",
                    type=dynamodb.AttributeType.STRING
                ),
                billing_mode=dynamodb.BillingMode.PROVISIONED,
                removal_policy=RemovalPolicy.DESTROY 
            )
        
        if ProductServiceStack.table_exists(stocks_table_name):
            stocks_table = dynamodb.Table.from_table_name(self, "StocksTable", stocks_table_name)
        else:
            stocks_table = dynamodb.Table(
                self,
                "StocksTable",
                table_name=stocks_table_name,
                partition_key=dynamodb.Attribute(
                    name="product_id",
                    type=dynamodb.AttributeType.STRING
                ),
                billing_mode=dynamodb.BillingMode.PROVISIONED,
                removal_policy=RemovalPolicy.DESTROY
            )    

        api = apigw.RestApi(self, "ProductServiceApi", rest_api_name="product service")

        get_products_list_function = _lambda.Function(
            self,
            "GetProductsListHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "get_products_list.handler", 
            environment = lambdas_env
        )

        get_product_by_id_function = _lambda.Function(
            self,
            "GetProductByIdHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "get_product_by_id.handler", 
            environment= lambdas_env
        )

        create_product_layer_name = "create_product_layer"
        create_product_layer = _lambda.LayerVersion(
            self, 
            "CreateProductHandlerLayer", 
            code=_lambda.Code.from_asset(f"lambda_functions/layers/{create_product_layer_name}.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="A layer for CreateProductHandler with jsonschema"
        )

        create_product_function = _lambda.Function(
            self,
            "CreateProductHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "create_product.handler", 
            environment= lambdas_env,
            layers=[create_product_layer]
        )

        catalog_batch_process_function = _lambda.Function(
            self, 
            'CatalogBatchProcessHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='catalog_batch_process.handler',
            environment={
                **lambdas_env,
                "CREATE_PRODUCT_SNS": create_product_sns_topic.topic_arn
            },
            layers=[create_product_layer]
        )

        products_resource = api.root.add_resource("products")
        products_resource.add_method("GET", apigw.LambdaIntegration(get_products_list_function))
        products_resource.add_method('POST', apigw.LambdaIntegration(create_product_function))

        product_by_id_resource = products_resource.add_resource("{id}")
        product_by_id_resource.add_method("GET", apigw.LambdaIntegration(get_product_by_id_function))

        products_table.grant_read_write_data(get_product_by_id_function)
        products_table.grant_read_write_data(get_products_list_function)
        products_table.grant_read_write_data(create_product_function)
        stocks_table.grant_read_write_data(get_product_by_id_function)
        stocks_table.grant_read_write_data(get_products_list_function)
        stocks_table.grant_read_write_data(create_product_function)
        products_table.grant_read_write_data(catalog_batch_process_function)
        stocks_table.grant_read_write_data(catalog_batch_process_function)

        catalog_items_queue.grant_consume_messages(catalog_batch_process_function)
        create_product_sns_topic.grant_publish(catalog_batch_process_function)
        catalog_batch_process_function.add_event_source(lambda_events.SqsEventSource(catalog_items_queue, batch_size=5))
