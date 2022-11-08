from pathlib import Path

import aws_cdk.aws_apigatewayv2_alpha as apigwv2
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

        jobs_handler = PythonFunction(
            self,
            "JobsHandler",
            entry=str(DIR / "handler_jobs"),
            architecture=lambda_.Architecture.ARM_64,
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={"JOB_TABLE_NAME": table.table_name},
        )

        table.grant_read_write_data(jobs_handler)

        job_handler_integration = HttpLambdaIntegration(
            "JobsHandlerIntegration", jobs_handler
        )

        http_api = apigwv2.HttpApi(self, "AutoEIAAPI")

        http_api.add_routes(
            path="/jobs",
            methods=[apigwv2.HttpMethod.POST],
            integration=job_handler_integration,
        )

        http_api.add_routes(
            path="/jobs/{id}",
            methods=[apigwv2.HttpMethod.GET],
            integration=job_handler_integration,
        )

        http_api.add_routes(
            path="/jobs/{id}/complete",
            methods=[apigwv2.HttpMethod.POST],
            integration=job_handler_integration,
        )
