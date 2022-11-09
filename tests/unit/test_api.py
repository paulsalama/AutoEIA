import os

from pydantic import parse_obj_as

os.environ["JOB_TABLE_NAME"] = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"

from infrastructure.api.index import (
    CompleteJobInput,
    CreateJobInput,
    JobStatus,
    JobType,
    complete_job,
    create_job,
    get_job,
)


def test_jobs_handler():
    response = create_job(
        body=parse_obj_as(
            CreateJobInput,
            dict(
                job_type=JobType.SHADOW_STUDY,
                inputs=dict(
                    building_3d_model_uri="s3://sample/example/file.obj",
                    building_location_lat_long=(43.3242, 45.3324124),
                ),
            ),
        )
    )
    job_id = response.job.id

    response = get_job(job_id)
    assert response.job.job_type == JobType.SHADOW_STUDY
    assert response.job.job_status == JobStatus.NOT_STARTED

    response = complete_job(
        job_id,
        parse_obj_as(
            CompleteJobInput,
            dict(
                outputs=dict(
                    shadow_study_illustration_uris=["s3://sample/example/file.obj"],
                    shadow_study_interactive_uri="s3://sample/example/file.obj",
                )
            ),
        ),
    )
    assert response.job.job_status == JobStatus.SUCCEEDED
