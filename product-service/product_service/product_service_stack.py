from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Stack
)
from constructs import Construct

class ProductServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigw.RestApi(self, "ProductServiceApi", rest_api_name="product service")

        get_products_list_function = _lambda.Function(
            self,
            "GetProductsListHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "get_products_list.handler", 
        )

        get_product_by_id_function = _lambda.Function(
            self,
            "GetProductByIdHandler",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("lambda_functions"),
            handler = "get_product_by_id.handler", 
        )

        products_resource = api.root.add_resource("products")
        products_resource.add_method("GET", apigw.LambdaIntegration(get_products_list_function))

        product_by_id_resource = products_resource.add_resource("{id}")
        product_by_id_resource.add_method("GET", apigw.LambdaIntegration(get_product_by_id_function))
