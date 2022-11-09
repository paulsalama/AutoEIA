import os
from uuid import uuid4

import boto3
from fastapi import FastAPI
from mangum import Mangum

JOB_TABLE_NAME = os.environ["JOB_TABLE_NAME"]

app = FastAPI(
    title="EIA REST API",
    version="0.1.0",
    license_info={
        "name": "GPL-3.0-or-later",
    },
)

dynamodb = boto3.resource("dynamodb")

job_table = dynamodb.Table(JOB_TABLE_NAME)


@app.post("/jobs", status_code=201)
def create_job():
    item = {
        "id": str(uuid4()),
        "status": "NOT_STARTED",
        "inputs": {},
        "type": "NO_OP",
    }
    job_table.put_item(Item=item)
    return {"job": item}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    response = job_table.get_item(Key={"id": job_id})
    return {"job": response["Item"]}


@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str):
    response = job_table.update_item(
        Key={"id": job_id},
        UpdateExpression="SET #status = :val, outputs = :empty",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":val": "SUCCEEDED", ":empty": {}},
        ReturnValues="ALL_NEW",
    )
    return {"job": response["Attributes"]}


handler = Mangum(app)
