from pathlib import Path

import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as lambda_
from aws_cdk import Stack, Tags
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct

DIR = Path(__file__).parent.resolve()


class InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add("Application", "AutoEIA")

        table = dynamodb.Table(
            self,
            "Table",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        api_handler = PythonFunction(
            self,
            "APIHandler",
            entry=str(DIR / "api"),
            architecture=lambda_.Architecture.ARM_64,
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={"JOB_TABLE_NAME": table.table_name},
        )

        table.grant_read_write_data(api_handler)

        http_api = apigw.LambdaRestApi(self, "AutoEIARESTAPI", handler=api_handler)
