import json
import os
from uuid import uuid4

import boto3

JOB_TABLE_NAME = os.environ["JOB_TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")

job_table = dynamodb.Table(JOB_TABLE_NAME)


def json_response(status, body=None):
    return {
        "statusCode": status,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }


def create_job():
    item = {
        "id": str(uuid4()),
        "status": "NOT_STARTED",
        "inputs": {},
        "type": "NO_OP",
    }
    job_table.put_item(Item=item)
    return json_response(201, {"job": item})


def get_job(job_id):
    response = job_table.get_item(Key={"id": job_id})
    return json_response(200, {"job": response["Item"]})


def complete_job(job_id):
    response = job_table.update_item(
        Key={"id": job_id},
        UpdateExpression="SET #status = :val, outputs = :empty",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":val": "SUCCEEDED", ":empty": {}},
        ReturnValues="ALL_NEW",
    )
    return json_response(200, {"job": response["Attributes"]})


handler_mapping = {
    "POST /jobs": lambda event, context: create_job(),
    "GET /jobs/{id}": lambda event, context: get_job(event["pathParameters"]["id"]),
    "POST /jobs/{id}/complete": lambda event, context: complete_job(
        event["pathParameters"]["id"]
    ),
}


def handler(event, context):
    route_handler = handler_mapping.get(event["routeKey"], None)
    if route_handler is None:
        return json_response(
            400, {"message": f"Unsupported route: {event['routeKey']}."}
        )

    return route_handler(event, context)
