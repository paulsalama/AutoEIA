import os
from typing import cast
import json
from decimal import Decimal

import boto3
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from mangum import Mangum
from pydantic import BaseModel

from .types.job import Job, JobInputs, JobOutputs, JobType, JobStatus
from .types.noop_job import NoOpJob, NoOpJobInputs, NoOpJobOutputs
from .types.shadow_study_job import (
    ShadowStudyJob,
    ShadowStudyJobInputs,
    ShadowStudyJobOutputs,
)

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


class CreateJobInput(BaseModel):
    job_type: JobType
    inputs: JobInputs


def ddb_encode(item: BaseModel):
    return json.loads(item.json(), parse_float=Decimal)


@app.post("/jobs", status_code=201)
def create_job(body: CreateJobInput):
    item: Job
    if body.job_type == JobType.SHADOW_STUDY:
        item = ShadowStudyJob(inputs=cast(ShadowStudyJobInputs, body.inputs))
    else:
        item = NoOpJob(inputs=cast(NoOpJobInputs, body.inputs))
    job_table.put_item(Item=ddb_encode(item))
    return {"job": item}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    response = job_table.get_item(Key={"id": job_id})
    return {"job": Job(**response["Item"])}


class CompleteJobInput(BaseModel):
    outputs: JobOutputs


@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str, body: CompleteJobInput):
    response = job_table.get_item(Key={"id": job_id})
    base_job = response["Item"]
    item: Job
    if base_job["job_type"] == JobType.SHADOW_STUDY.value:
        print(base_job)
        item = ShadowStudyJob.parse_raw(json.dumps(base_job))
        item.outputs = cast(ShadowStudyJobOutputs, body.outputs)
    else:
        item = NoOpJob.parse_obj(base_job)
        item.outputs = cast(NoOpJobOutputs, body.outputs)
    item.job_status = JobStatus.SUCCEEDED
    job_table.put_item(Item=ddb_encode(item))
    return {"job": item}


handler = Mangum(app)
