from pathlib import Path

import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as lambda_
from aws_cdk import Stack, Tags, DockerImage
from aws_cdk.aws_lambda_python_alpha import PythonFunction, BundlingOptions
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

        # Allow querying for all jobs that are grouped by a parent ID
        table.add_global_secondary_index(
            index_name="ParentIDIndex",
            partition_key=dynamodb.Attribute(
                name="parent_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        )

        api_handler = PythonFunction(
            self,
            "APIHandler",
            entry=str(DIR / "api"),
            index="api_handler/index.py",
            architecture=lambda_.Architecture.ARM_64,
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={"JOB_TABLE_NAME": table.table_name},
            bundling=BundlingOptions(
                image=DockerImage.from_registry(
                    "public.ecr.aws/sam/build-python3.9:1.61.0-20221103213531"
                )
            ),
        )

        table.grant_read_write_data(api_handler)

        apigw.LambdaRestApi(self, "AutoEIARESTAPI", handler=api_handler)  # type: ignore
