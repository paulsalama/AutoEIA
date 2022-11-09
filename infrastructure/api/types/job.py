from abc import ABC
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class JobInputs(BaseModel, ABC):
    pass


class JobOutputs(BaseModel, ABC):
    pass


class JobStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class JobType(Enum):
    NO_OP = "NO_OP"
    SHADOW_STUDY = "SHADOW_STUDY"


class Job(BaseModel, ABC):
    id: str = str(uuid4())
    job_status: JobStatus = JobStatus.NOT_STARTED
    job_type: JobType = JobType.NO_OP
    inputs: JobInputs
    outputs: Optional[JobOutputs] = None
