import os

os.environ["JOB_TABLE_NAME"] = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"

from infrastructure.api.index import complete_job, create_job, get_job, JobStatus


def test_jobs_handler():
    response = create_job()
    job_id = response["job"].id

    response = get_job(job_id)
    assert response["job"].status == JobStatus.NOT_STARTED

    response = complete_job(job_id)
    assert response["job"].status == JobStatus.SUCCEEDED
