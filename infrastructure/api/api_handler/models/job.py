from abc import ABC
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class JobStatus(str, Enum):
    """
    The possible statuses in which a Job may exist.
    """

    NOT_STARTED = "NOT_STARTED"
    """The Job has been submitted but no Worker has yet indicated that they are
    working on it."""

    IN_PROGRESS = "IN_PROGRESS"
    """At least one Worker has indicated that they are working on the Job, but
    no Worker has completed the Job."""

    SUCCEEDED = "SUCCEEDED"
    """All work has been completed on the Job, and the resulting outputs are
    available."""

    FAILED = "FAILED"
    """The Job was unable to transition to the SUCCEEDED status for some
    reason."""


class JobType(str, Enum):
    """
    The enumerated types that a Job can be. This field is used as a
    discriminator to identify which schema to use in various classes. When
    adding a new subclass of BaseJob, a corresponding new value should be added
    here.
    """

    NO_OP = "NO_OP"
    SHADOW_STUDY = "SHADOW_STUDY"


class BaseJobInput(BaseModel, ABC):
    """
    Base model for the subset of fields that are required when creating any new
    Job. This is an abstract class and cannot be instantiated directly.
    Subclasses will specify further fields.
    """

    parent_id: Optional[str]


class BaseJob(BaseModel, ABC):
    """
    Base model for a Job as it will be stored in the Job Database. This is an
    abstract class and cannot be instantiated directly. Subclasses specify further fields.
    """

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
