from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_s3 as s3, 
    aws_lambda as _lambda,
    RemovalPolicy,
    aws_s3_notifications as s3_notifications 
)
from constructs import Construct

import boto3
from botocore.exceptions import ClientError

class ImportServiceStack(Stack):
    @staticmethod
    def s3_bucket_exists(bucket_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "rs-task5-bucket-vm622"

        if ImportServiceStack.s3_bucket_exists(bucket_name):
            bucket = s3.Bucket.from_bucket_name(self, 'ProductImportBucket', bucket_name)
        else:
            bucket = s3.Bucket(
                self, 
                "RsTask5BucketVm622", 
                bucket_name=bucket_name, 
                removal_policy=RemovalPolicy.DESTROY,
                cors=[
                    {
                        "allowedMethods": [
                            s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.GET
                        ],
                        "allowedOrigins": ["*"],
                        "allowedHeaders": ["*"],
                    }
                ]
            )

        lambdas_env = {
            'IMPORT_BUCKET': bucket_name
        }

        api = apigw.RestApi(self, "ImportServiceApi", rest_api_name="import service")

        import_products_file_function = _lambda.Function(
            self,
            "ImportProductsFileHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "import_products_file.handler", 
            environment = lambdas_env
        )

        import_file_parser_function = _lambda.Function(
            self, 
            'ImportFileParserHandler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='import_file_parser.handler',
            environment=lambdas_env
        )

        products_resource = api.root.add_resource("import")
        products_resource.add_method("GET", apigw.LambdaIntegration(import_products_file_function))

        bucket.grant_put(import_products_file_function)
        bucket.grant_read_write(import_products_file_function)

        bucket.grant_put(import_file_parser_function)
        bucket.grant_read_write(import_file_parser_function)

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, 
            s3_notifications.LambdaDestination(import_file_parser_function), 
            s3.NotificationKeyFilter(prefix="uploaded/")
        )
