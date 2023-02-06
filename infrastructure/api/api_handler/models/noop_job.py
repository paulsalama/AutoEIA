from typing import Literal, Optional

from pydantic import BaseModel, Extra

from .job import BaseJob, JobType, BaseJobInput


class NoOpJobInputs(BaseModel):
    pass


class CreateNoOpJobInput(BaseJobInput):
    job_type: Literal[JobType.NO_OP] = JobType.NO_OP
    inputs: NoOpJobInputs


class NoOpJobOutputs(BaseModel):
    class Config:
        extra = Extra.forbid


class NoOpJob(BaseJob):
    job_type: Literal[JobType.NO_OP] = JobType.NO_OP
    inputs: NoOpJobInputs
    outputs: Optional[NoOpJobOutputs] = None
