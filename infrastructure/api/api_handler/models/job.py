from abc import ABC
from enum import Enum
from typing import Optional
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


class BaseJobInput(BaseModel):
    parent_id: Optional[str]


class BaseJob(BaseModel, ABC):
    id: str = str(uuid4())
    """The unique identifier for this Job. Auto-populated as a UUIDV4."""
    parent_id: Optional[str]
    """The identifier for the parent Submission of this Job. This is currently used only to
    group Jobs. This identifier does not reference another Job."""
    job_status: JobStatus = JobStatus.NOT_STARTED
    """The status of the Job. Status is JobStatus.SUCCEEDED when a Worker has
    submitted outputs for this Job."""

    class Config:
        validate_assignment = True
