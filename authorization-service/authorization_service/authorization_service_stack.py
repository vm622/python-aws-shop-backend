from aws_cdk import (
    Stack,
    aws_lambda as _lambda
)
from constructs import Construct

import os
from dotenv import load_dotenv

class AuthorizationServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        load_dotenv()
        login="vm622"

        _lambda.Function(
            self, 
            'BasicAuthorizerHandler',
            function_name="BasicAuthorizerFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='basic_authorizer.handler',
            environment={
                login: os.getenv(login)
            }
        )
