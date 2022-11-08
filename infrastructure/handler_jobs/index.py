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


def handler(event, context):
    rk = event["routeKey"]
    if rk == "POST /jobs":
        item = {
            "id": str(uuid4()),
            "status": "NOT_STARTED",
            "inputs": {},
            "type": "NO_OP",
        }
        job_table.put_item(Item=item)
        return json_response(201, {"job": item})
    elif rk == "GET /jobs/{id}":
        response = job_table.get_item(Key={"id": event["pathParameters"]["id"]})
        return json_response(200, {"job": response["Item"]})
    elif rk == "POST /jobs/{id}/complete":
        response = job_table.update_item(
            Key={"id": event["pathParameters"]["id"]},
            UpdateExpression="SET #status = :val, outputs = :empty",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":val": "SUCCEEDED", ":empty": {}},
            ReturnValues="ALL_NEW",
        )
        return json_response(200, {"job": response["Attributes"]})
    else:
        return json_response(400, {"message": f"Unsupported route: {rk}."})
