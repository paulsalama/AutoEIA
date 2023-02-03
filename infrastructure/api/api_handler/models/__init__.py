from typing import Annotated, Union
from pydantic import BaseModel, Field

from .job import JobStatus, JobType

from .noop_job import NoOpJob, NoOpJobInputs, CreateNoOpJobInput, NoOpJobOutputs
from .shadow_study_job import (
    ShadowStudyJob,
    ShadowStudyJobInputs,
    CreateShadowStudyJobInput,
    ShadowStudyJobOutputs,
)

JobInput = Union[NoOpJobInputs, ShadowStudyJobInputs]
JobOutput = Union[NoOpJobOutputs, ShadowStudyJobOutputs]

CreateJobInput = Annotated[
    Union[CreateNoOpJobInput, CreateShadowStudyJobInput],
    Field(discriminator="job_type"),
]


class CompleteJobInput(BaseModel):
    outputs: JobOutput

    class Config:
        smart_union = True


Job = Annotated[Union[NoOpJob, ShadowStudyJob], Field(discriminator="job_type")]
