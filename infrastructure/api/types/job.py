from abc import ABC
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel


class JobStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class JobType(str, Enum):
    NO_OP = "NO_OP"
    SHADOW_STUDY = "SHADOW_STUDY"


class BaseJob(BaseModel, ABC):
    id: str = str(uuid4())
    job_status: JobStatus = JobStatus.NOT_STARTED

    class Config:
        validate_assignment = True
