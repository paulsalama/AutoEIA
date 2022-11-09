from typing import Literal, Optional

from pydantic import AnyUrl, BaseModel

from .job import BaseJob, JobType


class ShadowStudyJobInputs(BaseModel):
    building_3d_model_uri: AnyUrl
    building_location_lat_long: tuple[float, float]


class ShadowStudyJobOutputs(BaseModel):
    shadow_study_illustration_uris: list[AnyUrl]
    shadow_study_interactive_uri: AnyUrl


class ShadowStudyJob(BaseJob):
    job_type: Literal[JobType.SHADOW_STUDY] = JobType.SHADOW_STUDY
    inputs: ShadowStudyJobInputs
    outputs: Optional[ShadowStudyJobOutputs] = None
