from typing import Literal, Optional

from .job import JobInputs, JobOutputs, Job, JobType

class NoOpJobInputs(JobInputs):
    pass

class NoOpJobOutputs(JobOutputs):
    pass

class NoOpJob(Job):
    job_type: Literal[JobType.NO_OP] = JobType.NO_OP
    inputs: NoOpJobInputs
    outputs: Optional[NoOpJobOutputs] = None