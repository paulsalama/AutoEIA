from typing import Literal, Optional

from pydantic import AnyUrl

from .job import Job, JobInputs, JobOutputs, JobType


class ShadowStudyJobInputs(JobInputs):
    building_3d_model_uri: AnyUrl
    building_location_lat_long: tuple[float, float]


class ShadowStudyJobOutputs(JobOutputs):
    shadow_study_illustration_uris: list[AnyUrl]
    shadow_study_interactive_uri: AnyUrl


class ShadowStudyJob(Job):
    job_type: Literal[JobType.SHADOW_STUDY] = JobType.SHADOW_STUDY
    inputs: ShadowStudyJobInputs
    outputs: Optional[ShadowStudyJobOutputs] = None
