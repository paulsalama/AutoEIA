import os

os.environ["JOB_TABLE_NAME"] = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"

from infrastructure.handler_jobs.index import get_job, create_job, complete_job


def test_jobs_handler():
    response = create_job()
    job_id = response["job"]["id"]

    response = get_job(job_id)
    assert response["job"]["status"] == "NOT_STARTED"

    response = complete_job(job_id)
    assert response["job"]["status"] == "SUCCEEDED"
