"""SubmitRequest type."""

from dataclasses import dataclass

from pydantic import BaseModel
from strangeworks_core.types.job import Job


class SubmitRequest(BaseModel):
    """Submit Request type.

    Used for making requests to start a job. Allows caller to
    create the job entry on the platform first.
    """

    slug: str | None = None
    input: dict | None = None
    file_url: list[str] | None = None


class JobRequest(BaseModel):
    """Job Request model.

    Used for making requests for existing jobs.

    Parameters
    ----------
    slug: str
        job identifier.
    """

    slug: str


@dataclass
class JobResponse:
    """Submit Response type.

    Purpose is to allow the response to expand if needed beyond platform job info in
    the future.
    """

    job: Job
