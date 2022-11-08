import json
import os

os.environ["JOB_TABLE_NAME"] = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"

from infrastructure.handler_jobs.index import handler


def simulate_request(method, path, path_id=None):
    return {
        "routeKey": f"{method} {path}",
        "pathParameters": {"id": path_id} if path_id is not None else None,
    }


def test_jobs_handler():
    response = handler(simulate_request("POST", "/jobs"), {})
    job_id = json.loads(response["body"])["job"]["id"]
    assert response["statusCode"] == 201

    response = handler(simulate_request("GET", "/jobs/{id}", job_id), {})
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["job"]["status"] == "NOT_STARTED"

    response = handler(simulate_request("POST", "/jobs/{id}/complete", job_id), {})
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["job"]["status"] == "SUCCEEDED"
