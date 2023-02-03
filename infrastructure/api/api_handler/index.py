import json
import os
from decimal import Decimal
from typing import Callable

import boto3
from boto3.dynamodb.conditions import Key
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel, parse_obj_as

from .models import Job, JobStatus, CreateJobInput, CompleteJobInput


class JobWrapper(BaseModel):
    job: Job


def ddb_encode(item: BaseModel):
    return json.loads(item.json(), parse_float=Decimal)


def create_app(job_table) -> tuple[FastAPI, dict[str, Callable]]:
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
        item = JobWrapper(job={"parent_id": body.parent_id, "job_type": body.job_type, "inputs": body.inputs})  # type: ignore
        job_table.put_item(Item=ddb_encode(item.job))
        return item

    @app.get("/jobs/group/{parent_id}", response_model=list[JobWrapper])
    def get_job_group(parent_id: str) -> list[JobWrapper]:
        response = job_table.query(
            IndexName="ParentIDIndex",
            KeyConditionExpression=Key("parent_id").eq(parent_id),
        )
        return [parse_obj_as(JobWrapper, {"job": item}) for item in response["Items"]]

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

    return app, {
        "create_job": create_job,
        "get_job": get_job,
        "complete_job": complete_job,
        "get_job_group": get_job_group,
    }


if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None:
    JOB_TABLE_NAME = os.environ["JOB_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    job_table = dynamodb.Table(JOB_TABLE_NAME)

    app, _ = create_app(job_table)
    handler = Mangum(app)
