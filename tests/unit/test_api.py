import os

from pydantic import AnyUrl

from infrastructure.api.types.shadow_study_job import ShadowStudyJobOutputs

os.environ["JOB_TABLE_NAME"] = "AutoEIAStack-TableCD117FA1-1IYIL0D055FND"

from infrastructure.api.index import (
    CompleteJobInput,
    CreateJobInput,
    JobStatus,
    JobType,
    ShadowStudyJobInputs,
    complete_job,
    create_job,
    get_job,
)


def test_jobs_handler():
    response = create_job(
        CreateJobInput(
            job_type=JobType.SHADOW_STUDY,
            inputs=ShadowStudyJobInputs(
                building_3d_model_uri=AnyUrl(
                    "s3://sample/example/file.obj", scheme="s3"
                ),
                building_location_lat_long=(43.3242, 45.3324124),
            ),
        )
    )
    job_id = response["job"].id

    response = get_job(job_id)
    assert response["job"].job_type == JobType.SHADOW_STUDY
    assert response["job"].job_status == JobStatus.NOT_STARTED

    response = complete_job(
        job_id,
        CompleteJobInput(
            outputs=ShadowStudyJobOutputs(
                shadow_study_illustration_uris=[
                    AnyUrl("s3://sample/example/file.obj", scheme="s3")
                ],
                shadow_study_interactive_uri=AnyUrl(
                    "s3://sample/example/file.obj", scheme="s3"
                ),
            )
        ),
    )
    assert response["job"].job_status == JobStatus.SUCCEEDED
