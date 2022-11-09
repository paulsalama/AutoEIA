import json
import os
from decimal import Decimal
from typing import Annotated, Literal, Union, Callable

import boto3
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel, Field, parse_obj_as

from .models.job import JobStatus, JobType
from .models.noop_job import NoOpJob, NoOpJobInputs, NoOpJobOutputs
from .models.shadow_study_job import (
    ShadowStudyJob,
    ShadowStudyJobInputs,
    ShadowStudyJobOutputs,
)

Job = Annotated[Union[NoOpJob, ShadowStudyJob], Field(discriminator="job_type")]


class JobWrapper(BaseModel):
    job: Job


class CreateShadowStudyJobInput(BaseModel):
    job_type: Literal[JobType.SHADOW_STUDY] = JobType.SHADOW_STUDY
    inputs: ShadowStudyJobInputs


class CreateNoOpJobInput(BaseModel):
    job_type: Literal[JobType.NO_OP] = JobType.NO_OP
    inputs: NoOpJobInputs


CreateJobInput = Annotated[
    Union[CreateNoOpJobInput, CreateShadowStudyJobInput],
    Field(discriminator="job_type"),
]


class CompleteJobInput(BaseModel):
    outputs: Union[NoOpJobOutputs, ShadowStudyJobOutputs]

    class Config:
        smart_union = True


def ddb_encode(item: BaseModel):
    return json.loads(item.json(), parse_float=Decimal)


def create_app(job_table) -> tuple[FastAPI, Callable, Callable, Callable]:
    app = FastAPI(
        title="EIA REST API",
        version="0.1.0",
        license_info={
            "name": "GPL-3.0-or-later",
        },
        root_path="/prod",
    )

    @app.post("/jobs", status_code=201, response_model=JobWrapper)
    def create_job(body: CreateJobInput) -> JobWrapper:
        item = JobWrapper(job={"job_type": body.job_type, "inputs": body.inputs})  # type: ignore
        job_table.put_item(Item=ddb_encode(item.job))
        return item

    @app.get("/jobs/{job_id}", response_model=JobWrapper)
    def get_job(job_id: str) -> JobWrapper:
        response = job_table.get_item(Key={"id": job_id})
        return parse_obj_as(JobWrapper, {"job": response["Item"]})

    @app.post("/jobs/{job_id}/complete", response_model=JobWrapper)
    def complete_job(job_id: str, body: CompleteJobInput) -> JobWrapper:
        response = job_table.get_item(Key={"id": job_id})
        item = parse_obj_as(JobWrapper, {"job": response["Item"]})
        item.job.outputs = body.outputs  # type: ignore
        item.job.job_status = JobStatus.SUCCEEDED
        job_table.put_item(Item=ddb_encode(item.job))
        return item

    return app, create_job, get_job, complete_job


if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    JOB_TABLE_NAME = os.environ["JOB_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    job_table = dynamodb.Table(JOB_TABLE_NAME)

    app, _, _, _ = create_app(job_table)
    handler = Mangum(app)
