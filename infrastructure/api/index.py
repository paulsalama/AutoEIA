import os
from uuid import uuid4
from typing import Optional

import boto3
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from mangum import Mangum
from pydantic import BaseModel
from enum import Enum

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


class JobStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class JobType(Enum):
    NO_OP = "NO_OP"


class Job(BaseModel):
    id: str = str(uuid4())
    status: JobStatus = JobStatus.NOT_STARTED
    job_type: JobType = JobType.NO_OP
    inputs: Optional[dict] = None
    outputs: Optional[dict] = None


@app.post("/jobs", status_code=201)
def create_job():
    item = Job()
    job_table.put_item(Item=jsonable_encoder(item))
    return {"job": item}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    response = job_table.get_item(Key={"id": job_id})
    return {"job": Job(**response["Item"])}


@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str):
    response = job_table.update_item(
        Key={"id": job_id},
        UpdateExpression="SET #status = :val, outputs = :empty",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":val": "SUCCEEDED", ":empty": {}},
        ReturnValues="ALL_NEW",
    )
    return {"job": Job(**response["Attributes"])}


handler = Mangum(app)
