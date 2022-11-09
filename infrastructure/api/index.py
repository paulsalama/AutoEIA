import json
import os
from decimal import Decimal
from typing import Annotated, Literal, Union

import boto3
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel, Field, parse_obj_as

from .types.job import JobStatus, JobType
from .types.noop_job import NoOpJob, NoOpJobInputs, NoOpJobOutputs
from .types.shadow_study_job import (
    ShadowStudyJob,
    ShadowStudyJobInputs,
    ShadowStudyJobOutputs,
)

Job = Annotated[Union[NoOpJob, ShadowStudyJob], Field(discriminator="job_type")]


class JobWrapper(BaseModel):
    job: Job


JOB_TABLE_NAME = os.environ["JOB_TABLE_NAME"]

app = FastAPI(
    title="EIA REST API",
    version="0.1.0",
    license_info={
        "name": "GPL-3.0-or-later",
    },
)

dynamodb = boto3.resource("dynamodb")

job_table = dynamodb.Table(JOB_TABLE_NAME)  # type: ignore


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


def ddb_encode(item: BaseModel):
    return json.loads(item.json(), parse_float=Decimal)


@app.post("/jobs", status_code=201)
def create_job(body: CreateJobInput):
    item = JobWrapper(job={"job_type": body.job_type, "inputs": body.inputs})  # type: ignore
    job_table.put_item(Item=ddb_encode(item.job))
    return item


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    response = job_table.get_item(Key={"id": job_id})
    return parse_obj_as(JobWrapper, {"job": response["Item"]})


class CompleteJobInput(BaseModel):
    outputs: Union[NoOpJobOutputs, ShadowStudyJobOutputs]

    class Config:
        smart_union = True


@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str, body: CompleteJobInput):
    response = job_table.get_item(Key={"id": job_id})
    item = parse_obj_as(JobWrapper, {"job": response["Item"]})
    item.job.outputs = body.outputs  # type: ignore
    item.job.job_status = JobStatus.SUCCEEDED
    job_table.put_item(Item=ddb_encode(item.job))
    return item


handler = Mangum(app)
