from uuid import uuid4

import boto3
from pydantic import parse_obj_as

from infrastructure.api.api_handler.models import (
    CreateJobInput,
    CompleteJobInput,
    JobStatus,
    JobType,
)
from infrastructure.api.api_handler.index import create_app

JOB_TABLE_NAME = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"


def test_api_handler():
    dynamodb = boto3.resource("dynamodb")
    job_table = dynamodb.Table(JOB_TABLE_NAME)
    _, ops = create_app(job_table)

    response = ops["create_job"](
        body=parse_obj_as(
            CreateJobInput,
            dict(
                parent_id=str(uuid4()),
                job_type=JobType.SHADOW_STUDY,
                inputs=dict(
                    building_3d_model_uri="s3://sample/example/file.obj",
                    building_location_lat_long=(43.3242, 45.3324124),
                ),
            ),
        )
    )
    job_id = response.job.id
    parent_id = response.job.parent_id

    response = ops["get_job"](job_id)
    assert response.job.job_type == JobType.SHADOW_STUDY
    assert response.job.job_status == JobStatus.NOT_STARTED

    response = ops["get_job_group"](parent_id)
    assert len(response) == 1
    assert response[0].job.id == job_id

    response = ops["complete_job"](
        job_id,
        parse_obj_as(
            CompleteJobInput,
            dict(
                outputs=dict(
                    shadow_study_illustration_uris=["s3://sample/example/file.obj"],
                    shadow_study_interactive_uri="s3://sample/example/file.obj",
                )
            ),
        ),
    )
    assert response.job.job_status == JobStatus.SUCCEEDED
